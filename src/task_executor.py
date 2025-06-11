# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "task_executor_py_g103",
    "g_annotation_last_modified": 215,
    "version_tag_of_host_at_annotation": "1.1.0"
  },
  "payload": {
    "authors_and_contributors": [
        {"g_contribution": 103, "identifier": "Cody"},
        {"g_contribution": 207, "identifier": "Cody"},
        {"g_contribution": 215, "identifier": "Cody", "contribution_summary": "Remediation (exec_plan_00005): Added `handle_create_snapshot` task handler to integrate the snapshotting utility into the execution engine."}
    ],
    "internal_dependencies": ["src.state_manager", "core.config", "core.paths", "core.atomic_io", "core.exceptions", "src.utils.snapshot_utils"],
    "linked_issue_ids": ["issue_00121", "pr_issue_phase1_mvp_patch"]
  }
}
# ANNOTATION_BLOCK_END

"""task_executor.py
~~~~~~~~~~~~~~~~~~~~
Contains the business logic for executing individual tasks from an
Execution Plan. Uses a type-based registry to dispatch to the
correct handler function. All path operations are sandboxed.
"""

import json
import shutil
import structlog
import time
from opentelemetry import trace
from pathlib import Path
from typing import Any, Callable, Dict

from core.config import Config
from core.atomic_io import file_lock, atomic_write
from core.exceptions import DataSafetyError, OSCoreError, PathEscapeError
from core.paths import safe_join
from utils import snapshot_utils
from utils.state_manager import StateManager

logger = structlog.get_logger()

def _load_registry(registry_path: Path) -> Dict:
    """Loads the global registry map into memory using a shared lock.

    If the registry file does **not** yet exist (first run, clean checkout, or
    isolated test fixture) we **do not** attempt to acquire a shared lock –
    that would raise ``FileNotFoundError`` by design.  Instead we lazily
    return a default, empty registry structure.  The first write-operation in
    ``_write_registry`` will then create the file using an atomic write with an
    *exclusive* lock, ensuring consistency across concurrent processes.
    """

    if not registry_path.exists():
        # No registry yet – return an empty skeleton.  The caller will
        # eventually persist this via _write_registry().
        logger.info("registry_map_missing", path=str(registry_path))
        return {"os_file_header": {}, "payload": {"artifact_registry_tree": {}}}

    try:
        with file_lock(registry_path, shared=True, create=False) as f:
            content = f.read()
            if not content:
                logger.warning("registry_map_empty", path=str(registry_path))
                return {"os_file_header": {}, "payload": {"artifact_registry_tree": {}}}
            return json.loads(content)
    except (json.JSONDecodeError, DataSafetyError) as e:
        logger.error("registry_map_load_failed", err=str(e))
        return {"os_file_header": {}, "payload": {"artifact_registry_tree": {}}}

def _write_registry(registry_path: Path, registry_data: Dict) -> None:
    """Writes the in-memory registry map back to disk atomically and with an exclusive lock."""
    try:
        atomic_write(registry_path, json.dumps(registry_data, indent=2))
    except DataSafetyError as e:
        logger.critical(
            "registry_map_write_failed",
            path=str(registry_path),
            err=str(e),
        )
        raise

def handle_create_directory(task: Dict[str, Any], config: Config, state_manager: StateManager, secrets: Dict[str, Any]) -> bool:
    # ... (code unchanged)
    try:
        dir_path_str = task.get("outputs", [{}])[0].get("path")
        if not dir_path_str:
            logger.error("task_missing_path", task_id=task["task_id"])
            return False

        full_path = safe_join(config.paths.project_workspace, dir_path_str)
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info("directory_created", task_id=task["task_id"], path=str(full_path))
        return True
    except Exception as e:
        logger.error(
            "create_directory_failed",
            task_id=task["task_id"],
            err=str(e),
            exc_info=True,
        )
        return False


def handle_create_file_from_template(task: Dict[str, Any], config: Config, state_manager: StateManager, secrets: Dict[str, Any]) -> bool:
    # ... (code unchanged)
    try:
        registry_path = config.paths.os_root / "global_registry_map.txt"
        registry_map = _load_registry(registry_path)

        output_def = task.get("outputs", [{}])[0]
        template_name = output_def.get("template")
        target_path_str = output_def.get("path")
        artifact_id = output_def.get("artifact_id_placeholder")

        if not all([template_name, target_path_str, artifact_id]):
            logger.error("task_missing_keys", task_id=task["task_id"])
            return False

        template_path = safe_join(config.paths.project_templates, template_name)
        target_path = safe_join(config.paths.project_workspace, target_path_str)
        
        if not template_path.exists():
            logger.error(
                "template_not_found",
                task_id=task["task_id"],
                path=str(template_path),
            )
            return False

        target_path.parent.mkdir(parents=True, exist_ok=True)
        template_content = template_path.read_text(encoding='utf-8')
        
        current_g = state_manager.read_state()['g']
        annotation = {
            "artifact_annotation_header": {
                "artifact_id_of_host": artifact_id,
                "g_annotation_created": current_g,
                "version_tag_of_host_at_annotation": "0.1.0",
                "trace_id": trace.get_current_span().get_span_context().trace_id,
            },
            "payload": {
                 "description": f"Scaffolded from template: {template_name}",
                 "artifact_type": "SCAFFOLDED_ARTIFACT",
                 "status_in_lifecycle": "SCAFFOLDED"
            }
        }
        annotation_str = f"/* ANNOTATION_BLOCK_START\n{json.dumps(annotation, indent=2)}\nANNOTATION_BLOCK_END */"
        
        final_content = f"{annotation_str}\n\n{template_content}"
        atomic_write(target_path, final_content)

        if "payload" not in registry_map: registry_map["payload"] = {"artifact_registry_tree": {}}
        
        registry_map["payload"]["artifact_registry_tree"][artifact_id] = {
            "primary_filepath": str(target_path.relative_to(config.project_root)),
            "g_created_in_registry": current_g,
            "history": [{"g_event": current_g, "event_type": "SCAFFOLDED"}]
        }
        _write_registry(registry_path, registry_map)
        
        logger.info(
            "file_from_template_created",
            task_id=task["task_id"],
            path=str(target_path),
        )
        return True

    except PathEscapeError:
        # Re-raise security violations so the engine can handle them with exit code 2
        raise
    except Exception as e:
        logger.error(
            "create_from_template_failed",
            task_id=task["task_id"],
            err=str(e),
            exc_info=True,
        )
        return False


def handle_create_snapshot(task: Dict[str, Any], config: Config, state_manager: StateManager, secrets: Dict[str, Any]) -> bool:
    """Handles creating a system state snapshot and updating relevant state files."""
    try:
        title = task.get("title", "Untitled System Snapshot")
        description = task.get("description", "Snapshot created by a CREATE_SNAPSHOT task.")
        plan_id = state_manager.read_state().get("cp_id")

        if not plan_id:
            logger.error("snapshot_missing_plan_id", task_id=task["task_id"])
            return False
        
        # 1. Create the snapshot file itself (this also registers it)
        g_current = state_manager.read_state().get('g', 0)
        snapshot_id = f"snapshot_g{g_current}"  # Use current g, not g+1
        triggering_event = {"type": "TASK_EXECUTION", "plan_id": plan_id, "task_id": task["task_id"]}
        
        snapshot_utils.create_snapshot(config, state_manager, triggering_event, title, description)

        # 2. Update the execution status file to log the created artifact
        initiatives_dir = config.paths.os_root / "initiatives"
        status_file_path = None
        for initiative_dir in initiatives_dir.iterdir():
            if not initiative_dir.is_dir(): continue
            try:
                plan_file_path = safe_join(initiative_dir.resolve(), f"{plan_id}.txt")
                if plan_file_path.exists():
                    status_file_path = plan_file_path.parent / f"exec_status_{plan_id.split('_')[-1]}.txt"
                    break
            except OSCoreError:
                continue
        
        if not status_file_path or not status_file_path.exists():
            logger.error(
                "snapshot_status_file_not_found",
                task_id=task["task_id"],
                plan_id=plan_id,
                status_file_path=str(status_file_path) if status_file_path else "None",
            )
            return True # The snapshot was made, so the task isn't a hard failure.

        # Perform read-modify-write safely: acquire exclusive lock, read JSON,
        # mutate in-memory, **release lock**, then atomically overwrite.  On
        # Windows the destination file must not be open during the final
        # ``os.replace`` inside ``atomic_write``.
        with file_lock(status_file_path, shared=False, create=False) as f:
            status_data = json.loads(f.read())
            artifacts = status_data["payload"].setdefault("artifacts_created", [])
            if snapshot_id not in artifacts:
                artifacts.append(snapshot_id)

        # Lock released – now safe to overwrite on Windows
        atomic_write(status_file_path, json.dumps(status_data, indent=2))

        logger.info(
            "snapshot_created",
            task_id=task["task_id"],
            snapshot_id=snapshot_id,
        )
        return True
    except Exception as e:
        logger.error(
            "create_snapshot_failed",
            task_id=task["task_id"],
            err=str(e),
            exc_info=True,
        )
        return False

def handle_generate_cost_report(task: Dict[str, Any], config: Config, state_manager: StateManager, secrets: Dict[str, Any]) -> bool:
    """Generates a cost report."""
    try:
        output_def = task.get("outputs", [{}])[0]
        target_path_str = output_def.get("path")
        if not target_path_str:
            logger.error("task_missing_path", task_id=task["task_id"])
            return False

        # This is a placeholder implementation. A real implementation would
        # query a database or parse exec_status files to generate a report.
        report_content = "# Weekly Cost Report\n\nThis is a placeholder for the weekly cost report."
        target_path = safe_join(config.paths.project_workspace, target_path_str)
        atomic_write(target_path, report_content)
        logger.info("cost_report_generated", task_id=task["task_id"], path=str(target_path))
        return True
    except Exception as e:
        logger.error(
            "generate_cost_report_failed",
            task_id=task["task_id"],
            err=str(e),
            exc_info=True,
        )
        return False

def handle_rotate_registry(task: Dict[str, Any], config: Config, state_manager: StateManager, secrets: Dict[str, Any]) -> bool:
    """Rotates the global registry map."""
    try:
        registry_path = config.paths.os_root / "global_registry_map.txt"
        if registry_path.exists():
            backup_path = registry_path.with_suffix(f".{int(time.time())}.bak")
            shutil.copy(registry_path, backup_path)
            logger.info("registry_rotated", backup_path=str(backup_path))
        
        # Create a new, empty registry
        new_registry = {"payload": {"artifact_registry_tree": {}}}
        atomic_write(registry_path, json.dumps(new_registry, indent=2))
        return True
    except Exception as e:
        logger.error(
            "rotate_registry_failed",
            task_id=task["task_id"],
            err=str(e),
            exc_info=True,
        )
        return False

# Task type to handler function mapping
task_registry: Dict[str, Callable[[Dict, Config, StateManager, Dict], bool]] = {
    "CREATE_DIRECTORY": handle_create_directory,
    "CREATE_FILE_FROM_TEMPLATE": handle_create_file_from_template,
    "CREATE_SNAPSHOT": handle_create_snapshot,
    "GENERATE_COST_REPORT": handle_generate_cost_report,
    "ROTATE_REGISTRY": handle_rotate_registry,
}

def execute_task(task: Dict[str, Any], config: Config, state_manager: StateManager, secrets: Dict[str, Any]) -> bool:
    """Main dispatcher for tasks. Looks up the task handler and executes it."""
    task_type = task.get("type")
    if not task_type:
        logger.error("task_missing_type", task_id=task.get("task_id", "Unknown"))
        return False
        
    handler = task_registry.get(task_type)
    if not handler:
        logger.error(
            "unhandled_task_type",
            task_type=task_type,
            task_id=task.get("task_id", "Unknown"),
        )
        return False
    
    logger.debug(
        "dispatching_task",
        task_id=task.get("task_id"),
        task_type=task_type,
    )
    return handler(task, config, state_manager, secrets)