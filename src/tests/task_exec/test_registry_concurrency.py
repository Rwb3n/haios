# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "test_task_exec_registry_concurrency_py_g184",
    "g_annotation_created": 184,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "A concurrency stress test for the TaskExecutor's registry writing functionality. Spawns multiple processes to write to the same registry file simultaneously, verifying data integrity.",
    "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
    "status_in_lifecycle": "UNDER_DEVELOPMENT",
    "purpose_statement": "To provide evidence that the data safety primitives prevent race conditions and lost updates on the global_registry_map.txt, even under concurrent stress.",
    "authors_and_contributors": [{"g_contribution": 184, "identifier": "Successor Agent"}],
    "internal_dependencies": ["task_executor_py_g103", "core_config_py_g146"],
    "quality_notes": { "overall_quality_assessment": "NOT_ASSESSED" },
    "linked_issue_ids": ["issue_00121"],
    "scaffold_info": {
      "implementing_task_id": "T15_test_registry_concurrency"
    }
  }
}
# ANNOTATION_BLOCK_END

import json
import multiprocessing
from pathlib import Path
from typing import Any, Dict

import pytest

from src import task_executor
from src.core.config import Config, PathConfig
from src.utils.state_manager import StateManager

# --- Worker Function ---

def registry_writer_worker(
    config_dict: Dict[str, Any],
    mock_state_manager: Any,
    worker_id: int
):
    """
    This function simulates a single agent process executing a task
    that writes to the registry.
    """
    # Re-create the Config object in the new process
    project_root = Path(config_dict["project_root"])
    config = Config.from_dict(config_dict["raw_config"], project_root)

    # Define a unique task for this worker
    artifact_id = f"artifact_from_worker_{worker_id}"
    task = {
        "task_id": f"task_worker_{worker_id}",
        "type": "CREATE_FILE_FROM_TEMPLATE", # This is the task type that writes to the registry
        "outputs": [{
            "template": "dummy_template.txt",
            "path": f"src/worker_{worker_id}.js",
            "artifact_id_placeholder": artifact_id
        }]
    }
    
    # Execute the task, which will trigger a write to the registry map
    task_executor.execute_task(task, config, mock_state_manager)

# --- Test Case ---

def test_concurrent_registry_writes_are_safe(tmp_path: Path):
    """
    Spawns multiple processes that all execute tasks writing to the same
    registry file, and asserts that no writes are lost.
    """
    num_processes = 5
    project_root = tmp_path
    
    # 1. Setup a realistic project structure in the temp directory
    os_root = project_root / "os_root"
    workspace = project_root / "project_workspace"
    templates = project_root / "project_templates"
    os_root.mkdir()
    workspace.mkdir()
    templates.mkdir()

    # Create a dummy template file for the task to use
    (templates / "dummy_template.txt").write_text("dummy content")
    
    # Create a dummy state file
    state_file = os_root / "state.txt"
    state_file.write_text(json.dumps({"g": 100})) # A simplified mock

    # 2. Setup the configuration
    raw_config = {
        "project_name": "Concurrency Test",
        "paths": {
            "os_root": "os_root",
            "project_workspace": "project_workspace",
            "project_templates": "project_templates",
            "scaffold_definitions": "scaffold_definitions", # Dummy
            "guidelines": "guidelines" # Dummy
        }
    }
    
    config_dict_for_worker = {
        "raw_config": raw_config,
        "project_root": str(project_root)
    }

    # 3. Create a mock StateManager that just returns the g-value
    class MockStateManager:
        def read_state(self):
            return {"g": 100}
    
    mock_state_manager = MockStateManager()

    # 4. Spawn and run worker processes
    processes = []
    for i in range(num_processes):
        # The 'spawn' start method is more robust for tests like this
        ctx = multiprocessing.get_context('spawn')
        p = ctx.Process(target=registry_writer_worker, args=(config_dict_for_worker, mock_state_manager, i))
        processes.append(p)
        p.start()

    # Wait for all processes to complete
    for p in processes:
        p.join(timeout=15)
        assert p.exitcode == 0, f"Process {p.pid} failed or timed out."

    # 5. Assert the final state of the registry file
    registry_path = os_root / "global_registry_map.txt"
    assert registry_path.exists()

    final_registry_data = json.loads(registry_path.read_text())
    registered_artifacts = final_registry_data["payload"]["artifact_registry_tree"]

    # Assert that the file is not corrupted and contains all expected entries
    assert len(registered_artifacts) == num_processes
    for i in range(num_processes):
        expected_artifact_id = f"artifact_from_worker_{i}"
        assert expected_artifact_id in registered_artifacts
        assert registered_artifacts[expected_artifact_id]["g_created_in_registry"] == 100