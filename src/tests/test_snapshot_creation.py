# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "test_snapshot_creation_py_g216",
        "g_annotation_last_modified": 215,
        "version_tag_of_host_at_annotation": "1.0.0",
    },
    "payload": {
        "authors_and_contributors": [
            {
                "g_contribution": 215,
                "identifier": "Cody",
                "contribution_summary": "Creation (exec_plan_00005): Created integration test to provide evidence for the `CREATE_SNAPSHOT` task type, validating state file updates and artifact registration.",
            }
        ],
        "internal_dependencies": [
            "src.core.config",
            "src.state_manager",
            "src.plan_runner",
        ],
        "linked_issue_ids": [],
    },
}
# ANNOTATION_BLOCK_END

import json
from pathlib import Path

import pytest

from src.core.config import Config
from src.plan_runner import PlanRunner
from src.utils.state_manager import StateManager


@pytest.fixture
def snapshot_project(tmp_path):
    """Sets up an isolated temporary project to test snapshot creation."""
    project_root = tmp_path
    os_root = project_root / "os_root"
    workspace = project_root / "project_workspace"
    initiatives = os_root / "initiatives" / "init_1"
    snapshots_dir = os_root / "snapshots"

    initiatives.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(exist_ok=True)

    # Config
    config_path = project_root / "haios.config.json"
    config_data = {
        "paths": {
            "os_root": "os_root",
            "project_workspace": "project_workspace",
            "exec_plans": "os_root/initiatives/init_1",
            "state_file": "os_root/state.txt",
            "schema_dir": "docs/Document_2",
            "project_templates": "project_templates",
            "secrets_vault": "os_root/secrets.vault",
            "human_attention_queue": "os_root/human_attention_queue.txt",
            "global_registry_map": "os_root/global_registry_map.txt",
        },
        "runtime": {"mode": "DEV_FAST", "cli_override_allowed": True},
    }
    config_path.write_text(json.dumps(config_data))

    # State
    state_path = os_root / "state.txt"
    # Start at a high g to avoid collision with other tests
    state_path.write_text(json.dumps({"g": 300, "v": 1, "cp_id": "exec_plan_003"}))

    # Plan
    plan_path = initiatives / "exec_plan_003.txt"
    plan_data = {
        "plan_id": "exec_plan_003",
        "payload": {
            "tasks": [
                {
                    "task_id": "T-SNAPSHOT",
                    "type": "CREATE_SNAPSHOT",
                    "dependencies": [],
                    "title": "Test Completion Snapshot",
                    "description": "Snapshot taken after completing a test plan.",
                }
            ]
        },
    }
    plan_path.write_text(json.dumps(plan_data))

    # Status
    status_path = initiatives / "exec_status_003.txt"
    status_data = {
        "plan_id": "exec_plan_003",
        "payload": {"status": "DRAFT", "tasks_status": []},
    }
    status_path.write_text(json.dumps(status_data))

    return project_root


def test_snapshot_task_creates_and_registers_artifacts(snapshot_project):
    """
    Tests that the CREATE_SNAPSHOT task correctly creates the snapshot file,
    registers it in the global map, and updates the plan's execution status.
    """
    config = Config.from_file(snapshot_project / "haios.config.json")
    state_manager = StateManager(config.paths.os_root / "state.txt")

    runner = PlanRunner("exec_plan_003", config, state_manager)
    success = runner.execute()

    assert success, "PlanRunner should report success for a snapshot task."

    # The g-counter for the snapshot is the current state value (300)
    expected_snapshot_g = 300
    expected_snapshot_id = f"snapshot_g{expected_snapshot_g}"

    # Evidence 1: Snapshot file was created and is valid
    snapshot_path = config.paths.os_root / f"snapshots/{expected_snapshot_id}.txt"
    assert (
        snapshot_path.exists()
    ), "Snapshot file was not created in the correct directory."

    snapshot_data = json.loads(snapshot_path.read_text())
    assert snapshot_data["os_file_header"]["file_id"] == expected_snapshot_id
    assert snapshot_data["payload"]["snapshot_title"] == "Test Completion Snapshot"
    assert snapshot_data["payload"]["g_of_snapshot"] == expected_snapshot_g

    # Evidence 2: Snapshot was registered in the global map
    registry_path = Path(config.paths.global_registry_map)
    assert registry_path.exists(), "Global registry map was not created/updated."
    registry_data = json.loads(registry_path.read_text())
    registry_tree = registry_data.get("payload", {}).get("artifact_registry_tree", {})

    assert (
        expected_snapshot_id in registry_tree
    ), f"Snapshot artifact '{expected_snapshot_id}' was not registered."
    assert Path(
        registry_tree[expected_snapshot_id]["primary_filepath"]
    ) == snapshot_path.relative_to(config.project_root)

    # Evidence 3: Plan's execution status was updated to log the created artifact
    status_file = config.paths.os_root / "initiatives/init_1/exec_status_003.txt"
    final_status = json.loads(status_file.read_text())
    created_artifacts = final_status["payload"].get("artifacts_created", [])

    assert (
        expected_snapshot_id in created_artifacts
    ), "Snapshot ID was not logged in the plan's execution status."
