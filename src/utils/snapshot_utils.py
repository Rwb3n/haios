# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "utils_snapshot_utils_py_g234",
        "g_annotation_last_modified": 234,
        "version_tag_of_host_at_annotation": "1.1.0",
    },
    "payload": {
        "authors_and_contributors": [
            {"g_contribution": 210, "identifier": "Cody"},
            {
                "g_contribution": 234,
                "identifier": "Cody",
                "contribution_summary": "Remediation (exec_plan_00011): Fixed P0 blocking bug by correcting StateManager import to be package-relative.",
            },
        ],
        "internal_dependencies": [
            "src.core.config",
            "..state_manager",
            "src.core.atomic_io",
        ],
        "linked_issue_ids": [],
    },
}
# ANNOTATION_BLOCK_END

"""snapshot_utils.py
~~~~~~~~~~~~~~~~~~~~
Provides utilities for creating and managing system state snapshots.
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from core.atomic_io import atomic_write, file_lock
from core.config import Config
from utils.state_manager import StateManager

logger = logging.getLogger(__name__)


def _get_open_issue_count(config: Config) -> int:
    """Safely reads the global issue summary to count open issues."""
    summary_path = config.paths.os_root / "global_issues_summary.txt"
    if not summary_path.exists():
        return 0
    try:
        with summary_path.open("r", encoding="utf-8") as f:
            summary_data = json.load(f)

        count = 0
        # This logic needs to be aware of the summary schema.
        # Assuming a simple top-level count for now.
        return summary_data.get("payload", {}).get("open_issue_count", 0)

    except (IOError, json.JSONDecodeError):
        logger.warning(
            "Could not read or parse global issue summary. Reporting 0 open issues."
        )
        return 0


def _register_snapshot_artifact(
    config: Config, snapshot_id: str, snapshot_path: Path, g_event: int
):
    """Registers the new snapshot artifact in the global registry."""
    registry_path = config.paths.os_root / "global_registry_map.txt"
    try:
        # Acquire exclusive lock, read & mutate in-memory, then release lock
        with file_lock(registry_path, shared=False, create=True) as f:
            content = f.read()
            registry_data = json.loads(
                content or '{"payload": {"artifact_registry_tree": {}}}'
            )
            tree = registry_data.setdefault("payload", {}).setdefault(
                "artifact_registry_tree", {}
            )
            tree[snapshot_id] = {
                "primary_filepath": str(snapshot_path.relative_to(config.project_root)),
                "g_created_in_registry": g_event,
            }

        # Lock is now released – safe to overwrite atomically on Windows
        atomic_write(registry_path, json.dumps(registry_data, indent=2))
        logger.info("Registered new snapshot artifact: %s", snapshot_id)

    except Exception as e:
        logger.error(
            "Failed to register snapshot artifact %s. Error: %s",
            snapshot_id,
            e,
            exc_info=True,
        )


def _redact_snapshot_data(data: Any, redact_regexes: List[str]) -> Any:
    """Recursively redacts sensitive data from a snapshot."""
    if isinstance(data, dict):
        return {k: _redact_snapshot_data(v, redact_regexes) for k, v in data.items()}
    elif isinstance(data, list):
        return [_redact_snapshot_data(item, redact_regexes) for item in data]
    elif isinstance(data, str):
        for regex in redact_regexes:
            data = re.sub(regex, "[REDACTED]", data)
        return data
    else:
        return data


def create_snapshot(
    config: Config,
    state_manager: StateManager,
    triggering_event: Dict[str, Any],
    title: str,
    description: str,
):
    """
    Creates a system state snapshot, saves it as a versioned artifact,
    and registers it in the global map.
    """
    try:
        current_state = state_manager.read_state()
        # Use current g value - plan runner will increment after task success
        g_snapshot = current_state.get(state_manager.GLOBAL_KEY, 0)
        snapshot_id = f"snapshot_g{g_snapshot}"

        snapshots_dir = config.paths.os_root / "snapshots"
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = snapshots_dir / f"{snapshot_id}.txt"

        snapshot_data = {
            "os_file_header": {
                "file_schema_id": "snapshot_schema_v1.0",
                "file_id": snapshot_id,
                "g_created": g_snapshot,
                "v_this_file": 1,
            },
            "payload": {
                "snapshot_title": title,
                "g_of_snapshot": g_snapshot,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "description": description,
                "triggering_event": triggering_event,
                "key_state_summary": {
                    "os_phase": current_state.get(state_manager.PAYLOAD_KEY, {}).get(
                        "st", "UNKNOWN"
                    ),
                    "current_plan_id": current_state.get(
                        state_manager.PAYLOAD_KEY, {}
                    ).get("cp_id", "NONE"),
                    "open_issues_total": _get_open_issue_count(config),
                },
            },
        }

        redacted_snapshot_data = _redact_snapshot_data(
            snapshot_data, config.security.redact_regexes
        )
        atomic_write(snapshot_path, json.dumps(redacted_snapshot_data, indent=2))
        logger.info("Successfully created system snapshot: %s", snapshot_id)

        _register_snapshot_artifact(config, snapshot_id, snapshot_path, g_snapshot)

    except Exception as e:
        logger.critical("Failed to create system snapshot. Error: %s", e, exc_info=True)
        raise  # Re-raise the exception so the task executor can see it failed
