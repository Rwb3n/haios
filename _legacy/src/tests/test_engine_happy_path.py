import json
from pathlib import Path

import pytest

# Mock necessary components for testing
from src.core.config import Config
from src.plan_runner import PlanRunner
from src.utils.state_manager import StateManager


@pytest.fixture
def happy_path_project(tmp_path):
    """Sets up a temporary project structure for a successful run."""
    project_root = tmp_path
    os_root = project_root / "os_root"
    workspace = project_root / "project_workspace"
    initiatives = os_root / "initiatives" / "init_1"

    initiatives.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(exist_ok=True)

    # Config
    config_path = project_root / "haios.config.json"
    config_data = {
        "paths": {"os_root": str(os_root), "project_workspace": str(workspace)}
    }
    config_path.write_text(json.dumps(config_data))

    # State
    state_path = os_root / "state.txt"
    state_path.write_text(json.dumps({"g": 100, "v": 1}))

    # Plan
    plan_path = initiatives / "exec_plan_001.txt"
    plan_data = {
        "plan_id": "exec_plan_001",
        "payload": {
            "tasks": [
                {
                    "task_id": "T1",
                    "type": "CREATE_DIRECTORY",
                    "dependencies": [],
                    "outputs": [{"path": "new_dir/subdir"}],
                }
            ]
        },
    }
    plan_path.write_text(json.dumps(plan_data))

    # Status
    status_path = initiatives / "exec_status_001.txt"
    status_data = {
        "plan_id": "exec_plan_001",
        "payload": {"status": "DRAFT", "tasks_status": []},
    }
    status_path.write_text(json.dumps(status_data))

    return project_root


def test_happy_path_execution(happy_path_project):
    """Tests a simple, successful execution of a CREATE_DIRECTORY plan."""
    config = Config.from_file(happy_path_project / "haios.config.json")
    state_manager = StateManager(config.paths.os_root / "state.txt")

    runner = PlanRunner("exec_plan_001", config, state_manager)
    success = runner.execute()

    assert success, "PlanRunner should report success."

    # Evidence: Check if the directory was created
    expected_dir = config.paths.project_workspace / "new_dir/subdir"
    assert expected_dir.is_dir(), "The target directory was not created."

    # Evidence: Check if state was updated
    final_state = state_manager.read_state()
    assert final_state["g"] > 100, "Global counter 'g' should have been incremented."

    # Evidence: Check if status file was updated
    status_file = config.paths.os_root / "initiatives/init_1/exec_status_001.txt"
    final_status = json.loads(status_file.read_text())
    assert final_status["payload"]["tasks_status"][0]["status"] == "DONE"
