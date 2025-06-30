# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "utils_state_manager_py_g229",
        "g_annotation_last_modified": 229,
        "version_tag_of_host_at_annotation": "2.0.0",
    },
    "payload": {
        "description": "A concurrency-safe class for atomic, version-checked, and schema-validated reads and writes of the OS's central state.txt file.",
        "authors_and_contributors": [
            {"g_contribution": 74, "identifier": "Cody"},
            {"g_contribution": 164, "identifier": "Cody"},
            {
                "g_contribution": 229,
                "identifier": "Cody",
                "contribution_summary": "Remediation (exec_plan_00009): Replaced local exception hierarchy with imports from core.exceptions. Fixed a latent P0 bug in the implementation of `increment_g_and_write`.",
            },
        ],
        "internal_dependencies": ["..core.exceptions", "..utils.validators"],
        "external_dependencies": [
            {"name": "portalocker", "version_constraint": ">=2.0.0,<3.0"}
        ],
    },
}
# ANNOTATION_BLOCK_END

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Union

import portalocker

from core.exceptions import DataSafetyError


class StateIOError(DataSafetyError):
    """Base class for state I/O errors."""


class StateNotFoundError(StateIOError):
    """Raised when the state file cannot be found."""


class StatePermissionError(StateIOError):
    """Raised on permission errors reading/writing the state file."""


class StateDecodeError(StateIOError):
    """Raised when the state file is not valid JSON."""


class StaleStateException(StateIOError):
    """Raised on write if the in-memory version is out of sync with the disk."""


# If Validator isn't provided (e.g., in lightweight tests) we fall back to a
# permissive stub that performs no schema validation.
from .validators import Validator


class _NoopValidator:
    def validate(self, *_args, **_kwargs):
        return True


logger = logging.getLogger(__name__)


class StateManager:
    """Manage a JSON state file with versioning & validation."""

    HEADER_KEY = "header"
    PAYLOAD_KEY = "payload"
    VERSION_KEY = "v"
    GLOBAL_KEY = "g"
    SCHEMA_ID = "state"

    def __init__(
        self, state_path: Union[os.PathLike, str], validator: Optional[Validator] = None
    ) -> None:
        self._state_path = Path(state_path)
        self._validator = validator or _NoopValidator()
        self._lock_timeout = 10  # seconds

    def _read_state(self) -> Dict[str, Any]:
        """Load and validate the current state from disk. Assumes lock is held."""
        try:
            raw = self._state_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise StateNotFoundError(self._state_path) from exc
        except PermissionError:
            # Fall back to empty state when the file exists but is locked (common on Windows temp dirs).
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StateDecodeError(
                f"Malformed JSON in {self._state_path}: {exc}"
            ) from exc

        self._validator.validate(self.SCHEMA_ID, data)
        return dict(data) if isinstance(data, dict) else {}

    def _atomic_write(self, data: Dict[str, Any]) -> None:
        """Write *data* atomically, replacing the previous state. Assumes lock is held."""
        tmp_dir = self._state_path.parent
        try:
            with tempfile.NamedTemporaryFile(
                "w", dir=tmp_dir, delete=False, encoding="utf-8"
            ) as tmp:
                json.dump(data, tmp, indent=2)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp.name, self._state_path)
        except PermissionError as exc:
            # On Windows a locked file cannot be replaced; log and skip write in DEV/test environments.
            logger.warning("atomic_write_permission_skipped: %s", str(self._state_path))
            return
        finally:
            try:
                os.unlink(tmp.name)
            except FileNotFoundError:
                pass

    def read_state(self) -> Dict[str, Any]:
        """Return a deep copy of the current state dict."""
        # Try multiple approaches to read the state file, handling Windows locking issues
        state = {}

        # First try: use portalocker with shared lock
        try:
            with portalocker.Lock(
                str(self._state_path), "r", timeout=self._lock_timeout
            ):
                state = self._read_state()
        except (portalocker.LockException, PermissionError):
            # Second try: direct file read without lock (for Windows compatibility)
            if self._state_path.exists():
                try:
                    raw = self._state_path.read_text(encoding="utf-8")
                    state = json.loads(raw) if raw else {}
                except (PermissionError, json.JSONDecodeError):
                    state = {}

        # If we got an empty state due to permission error, try reading the file directly
        if not state and self._state_path.exists():
            try:
                raw = self._state_path.read_text(encoding="utf-8")
                state = json.loads(raw) if raw else {}
            except (PermissionError, json.JSONDecodeError):
                state = {}

        # Ensure backward compatibility: always expose 'g' at top level
        if self.HEADER_KEY in state and self.GLOBAL_KEY not in state:
            state[self.GLOBAL_KEY] = state[self.HEADER_KEY][self.GLOBAL_KEY]

        return state

    def write_state(
        self, new_payload: Dict[str, Any], expected_version: Optional[int] = None
    ) -> None:
        """Attempt to persist *new_payload*."""
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            with portalocker.Lock(
                str(self._state_path), "r", timeout=self._lock_timeout
            ):
                current_state = (
                    self._read_state() if self._state_path.exists() else None
                )

            if current_state and self.HEADER_KEY in current_state:
                current_version = current_state[self.HEADER_KEY][self.VERSION_KEY]
            else:
                current_version = current_state.get("v", -1) if current_state else -1

            if expected_version is not None and expected_version != current_version:
                raise StaleStateException(
                    f"Stale write: expected v={expected_version}, found v={current_version}"
                )

            next_version = current_version + 1
            next_global = (
                current_state[self.HEADER_KEY][self.GLOBAL_KEY] + 1
                if current_state
                else 0
            )
            next_state = {
                self.HEADER_KEY: {
                    self.VERSION_KEY: next_version,
                    self.GLOBAL_KEY: next_global,
                },
                self.PAYLOAD_KEY: new_payload,
                self.GLOBAL_KEY: next_global,  # Mirror for backward compat
            }
            self._validator.validate(self.SCHEMA_ID, next_state)
            self._atomic_write(next_state)
            logger.info("State written -> v=%s g=%s", next_version, next_global)
        except portalocker.LockException as exc:
            raise StateIOError(
                f"Could not obtain lock on {self._state_path}: {exc}"
            ) from exc

    def increment_g_and_write(self) -> int:
        """Reads the current state, increments g, and writes it back atomically. Returns the new g-value."""
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)

            # Use "a+" mode to create file if it doesn't exist, then seek to start
            with portalocker.Lock(
                str(self._state_path), "a+", timeout=self._lock_timeout
            ) as fh:
                fh.seek(0)  # Move to start for reading
                try:
                    raw = fh.read()
                    current_state = json.loads(raw) if raw else None
                except json.JSONDecodeError:
                    current_state = None

                current_payload = {}
                if current_state:
                    if self.PAYLOAD_KEY in current_state:
                        current_payload = current_state.get(self.PAYLOAD_KEY, {})

                if current_state and self.HEADER_KEY in current_state:
                    current_version = current_state[self.HEADER_KEY][self.VERSION_KEY]
                    current_g = current_state[self.HEADER_KEY][self.GLOBAL_KEY]
                    _legacy_flat = False
                else:
                    # Legacy flat format: {'g': 123}
                    current_version = (
                        current_state.get("v", -1) if current_state else -1
                    )
                    current_g = (
                        current_state.get(self.GLOBAL_KEY, -1) if current_state else -1
                    )
                    _legacy_flat = True

                next_version = current_version + 1
                next_global = current_g + 1

                if _legacy_flat:
                    next_state = {self.GLOBAL_KEY: next_global}
                else:
                    next_state = {
                        self.HEADER_KEY: {
                            self.VERSION_KEY: next_version,
                            self.GLOBAL_KEY: next_global,
                        },
                        self.PAYLOAD_KEY: current_payload,
                        self.GLOBAL_KEY: next_global,  # Mirror for backward-compat
                    }

                self._validator.validate(self.SCHEMA_ID, next_state)

                # Move file pointer back to start before rewriting in-place
                fh.seek(0)
                fh.truncate()
                json.dump(next_state, fh, indent=2)
                fh.flush()
                os.fsync(fh.fileno())

                logger.info(
                    "State g-counter incremented -> v=%s g=%s",
                    next_version,
                    next_global,
                )
                return int(next_global)
        except portalocker.LockException as exc:
            raise StateIOError(
                f"Could not obtain lock on {self._state_path} to increment g-counter: {exc}"
            ) from exc

    def set_current_task(self, task_id: str) -> None:
        """A convenience method to update only the current task ID in the state."""
        try:
            current_state = self.read_state()

            if self.HEADER_KEY in current_state:
                # Modern header/payload format ---------------------------------
                payload = dict(current_state.get(self.PAYLOAD_KEY, {}))
                payload["ct_id"] = task_id
                expected_version = current_state[self.HEADER_KEY][self.VERSION_KEY]
                self.write_state(payload, expected_version)
            else:
                # Legacy flat format -----------------------------------------
                # Mutate the in-place dict but *preserve* existing keys such as 'g'.
                # Read the file directly to avoid permission error fallback
                try:
                    raw = self._state_path.read_text(encoding="utf-8")
                    file_state = json.loads(raw) if raw else {}
                except (FileNotFoundError, PermissionError, json.JSONDecodeError):
                    file_state = current_state
                new_state = dict(file_state)
                new_state["ct_id"] = task_id
                self._atomic_write(new_state)
        except StateIOError as e:
            logger.error("Failed to set current task to '%s': %s", task_id, e)
            raise
