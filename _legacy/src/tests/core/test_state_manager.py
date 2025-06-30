# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {"artifact_id_of_host": "test_state_manager_py_g78"},
    "payload": {
        "description": "Unit tests for the StateManager module. Covers the optimistic locking protocol, atomic writes, and error handling.",
        "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
        "purpose_statement": "To provide evidence that the OS's live state can be managed with high integrity and safety.",
    },
}
# ANNOTATION_BLOCK_END

"""test_state_manager.py

Comprehensive pytest suite for the concurrent, schema‑validated
``StateManager``.  All tests run in an isolated temporary directory and
stub out the real file‑locking to keep execution fast and platform‑
independent.

Run with::

    pytest -q tests/test_state_manager.py

Dependencies
------------
* pytest
* pytest‑mock  (for the ``mocker`` fixture)  – optional; standard
  ``monkeypatch`` is also used.

The tests cover
~~~~~~~~~~~~~~~
* Happy‑path read‑‑>modify‑‑>write round‑trip.
* Stale‑write rejection when caller passes an outdated ``v``.
* Schema‑validation failure on read with corrupted state file.
* Permission error when the state file is read‑only.
* Temp‑file cleanup & atomic write path.
* Validator invocation count (ensures every read & write is validated).
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Union

import pytest

# ---------------------------------------------------------------------------
# Test‑local import helper: add the project root to PYTHONPATH dynamically
# so that `import state_manager` resolves regardless of CWD.
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils import state_manager
from utils.state_manager import StateManager
from utils.validators import Validator

# ---------------------------------------------------------------------------
# Helper / fixtures
# ---------------------------------------------------------------------------


class DummyValidator(Validator):
    """A minimal validator that can be instructed to pass or raise."""

    def __init__(self) -> None:
        self._should_raise = False
        self.calls: int = 0

    def set_invalid(self, raise_exc: Union[Exception, None]) -> None:
        self._should_raise = True
        self._exc = raise_exc

    def validate(self, schema_id: str, data_to_validate: Dict[str, Any]) -> None:
        self.calls += 1
        if self._should_raise:
            if self._exc is not None:
                raise self._exc
            else:
                raise Exception("Validation failed")


# All tests stub ``portalocker.lock`` to a no‑op to avoid the need for admin
# privileges on Windows CI agents and to keep runtimes low.
@pytest.fixture(autouse=True)
def _stub_portalocker(monkeypatch):
    monkeypatch.setattr(state_manager.portalocker, "Lock", DummyPortalocker)


import portalocker


class DummyPortalocker:
    class LockException(Exception):
        pass

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def lock(self, *_a, **_kw):
        return self


@pytest.fixture()
def validator():
    return DummyValidator()


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    return tmp_path / "state.json"


@pytest.fixture()
def manager(state_file: Path, validator: DummyValidator) -> StateManager:
    return StateManager(state_path=state_file, validator=validator)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_round_trip_read_write(manager: StateManager, validator: DummyValidator):
    """Initial write then read should succeed and bump version+g."""

    payload = {"foo": "bar"}
    # First write – expected_version = None means create‑or‑overwrite
    manager.write_state(payload, expected_version=None)

    state = manager.read_state()
    assert state["payload"] == payload
    assert state["header"]["v"] == 0
    assert state["header"]["g"] == 0

    # Verify validator was called twice (once on write, once on read)
    assert validator.calls == 2


def test_stale_write_rejected(manager: StateManager):
    """Writing with an outdated version raises ``StaleStateException``."""

    manager.write_state({"alpha": 1}, expected_version=None)  # v -> 1

    with pytest.raises(state_manager.StaleStateException):
        # Pass outdated version (=1) while the file is already at v=1, so the
        # manager will increment to 2 and the stale check fails.
        manager.write_state({"beta": 2}, expected_version=1)


def test_schema_validation_failure_on_read(
    manager: StateManager, validator: DummyValidator, state_file: Path
):
    """If the on‑disk JSON is invalid, ``SchemaValidationError`` bubbles up."""

    # Instruct the validator to raise on validation
    from utils.validators import SchemaValidationError

    validator.set_invalid(SchemaValidationError("payload must be object"))

    # Write a *valid* JSON bypassing StateManager so we can test the read path.
    state_file.write_text(json.dumps({"header": {"v": 1, "g": 1}, "payload": {}}))

    with pytest.raises(SchemaValidationError):
        manager.read_state()


@pytest.mark.skipif(os.name == "nt", reason="chmod 400 behaves differently on Windows")
def test_permission_error(manager: StateManager, state_file: Path):
    """Attempting to write to a read‑only file raises ``StatePermissionError``."""

    from utils.state_manager import StatePermissionError

    # Create an initial state file and make it read‑only.
    state_file.write_text(json.dumps({"header": {"v": 0, "g": 0}, "payload": {}}))
    state_file.chmod(0o400)

    with pytest.raises(StatePermissionError):
        manager.write_state({"x": "y"}, expected_version=0)


def test_atomic_temp_cleanup(manager: StateManager, tmp_path: Path):
    """The temp file should not persist after a successful write."""

    manager.write_state({"clean": True}, expected_version=None)

    # No temp *.tmp files should remain next to the state file
    leftover_tmp = list(tmp_path.glob("*.tmp"))
    assert not leftover_tmp
