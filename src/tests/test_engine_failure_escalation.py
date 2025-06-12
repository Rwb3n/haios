# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "test_engine_failure_escalation_py_g202",
        "g_annotation_last_modified": 215,
        "version_tag_of_host_at_annotation": "1.2.0",
    },
    "payload": {
        "authors_and_contributors": [
            {"g_contribution": 202, "identifier": "Cody"},
            {"g_contribution": 209, "identifier": "Cody"},
            {
                "g_contribution": 215,
                "identifier": "Cody",
                "contribution_summary": "Remediation (exec_plan_00005): Updated test to trigger readiness failure via `context_loading_instructions` path, exercising the newly hardened logic.",
            },
        ],
        "internal_dependencies": [
            "src.core.config",
            "src.state_manager",
            "src.plan_runner",
        ],
        "linked_issue_ids": ["pr_issue_phase1_mvp_patch"],
    },
}
# ANNOTATION_BLOCK_END

import json
from pathlib import Path

import pytest

from src.core.config import Config
from src.plan_runner import PlanRunner
from src.state_manager import StateManager


@pytest.fixture
def failure_path_project(tmp_path):
    """Sets up a project where a task is guaranteed to fail its readiness check."""
    project_root = tmp_path
    os_root = project_root / "os_root"
    workspace = project_root / "project_workspace"
    initiatives = os_root / "initiatives" / "init_1"

    (os_root / "issues").mkdir(parents=True, exist_ok=True)
    initiatives.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(exist_ok=True)

    config_path = project_root / "haios.config.json"
    config_data = {
        "paths": {
            "os_root": str(os_root),
            "project_workspace": str(workspace),
            "human_attention_queue": str(os_root / "human_attention_queue.txt"),
            "global_registry_map": str(os_root / "global_registry_map.txt"),
        }
    }
    config_path.write_text(json.dumps(config_data))

    state_path = os_root / "state.txt"
    state_path.write_text(json.dumps({"g": 200, "v": 1}))

    plan_path = initiatives / "exec_plan_002.txt"
    plan_data = {
        "plan_id": "exec_plan_002",
        "payload": {
            "tasks": [
                {
                    "task_id": "T-FAIL",
                    "type": "DUMMY_TYPE",
                    "dependencies": [],
                    "inputs": [],
                    "context_loading_instructions": [
                        {
                            "description": "Load a context file that does not exist.",
                            "source_reference": {
                                "type": "FILE_PATH",
                                "value": "non_existent_context_file.md",
                            },
                        }
                    ],
                }
            ]
        },
    }
    plan_path.write_text(json.dumps(plan_data))

    status_path = initiatives / "exec_status_002.txt"
    status_data = {
        "plan_id": "exec_plan_002",
        "payload": {"status": "DRAFT", "status_details": {}, "tasks_status": []},
    }
    status_path.write_text(json.dumps(status_data))

    return project_root


def test_failure_escalates_blocker_and_registers_artifacts(failure_path_project):
    """Tests that a readiness failure correctly triggers the ADR-011 escalation and registers the new artifacts."""
    config = Config.from_file(failure_path_project / "haios.config.json")
    state_manager = StateManager(config.paths.os_root / "state.txt")

    runner = PlanRunner("exec_plan_002", config, state_manager)
    success = runner.execute()

    assert not success, "PlanRunner should report failure."

    # Evidence 1: A BLOCKER issue was created
    issue_dir = config.paths.os_root / "issues"
    issue_files = list(issue_dir.glob("issue_*.txt"))
    assert (
        len(issue_files) == 1
    ), "A single BLOCKER issue file should have been created."
    issue_content = json.loads(issue_files[0].read_text())
    issue_id = issue_content["id"]
    assert issue_content["type"] == "BLOCKER"
    assert issue_content["task_id"] == "T-FAIL"
    assert (
        "Missing prerequisite file: non_existent_context_file.md"
        in issue_content["reason"]
    )

    # Evidence 2: The human attention queue was populated
    queue_path = Path(config.paths.human_attention_queue)
    assert queue_path.exists(), "Human attention queue file was not created."
    queue_content = json.loads(queue_path.read_text())
    assert len(queue_content) == 1
    assert queue_content[0]["issue_id"] == issue_id
    assert queue_content[0]["reason_code"] == "BLOCKER"

    # Evidence 3: The plan status was marked as FAILED
    status_file = config.paths.os_root / "initiatives/init_1/exec_status_002.txt"
    final_status = json.loads(status_file.read_text())
    assert final_status["payload"]["status"] == "FAILED"
    assert final_status["payload"].get("status_details", {}).get("phase") == "BLOCKED"

    # Evidence 4: The new artifacts were registered in the global map
    registry_path = Path(config.paths.global_registry_map)
    assert registry_path.exists(), "Global registry map was not created/updated."
    registry_data = json.loads(registry_path.read_text())
    registry_tree = registry_data.get("payload", {}).get("artifact_registry_tree", {})

    assert issue_id in registry_tree, f"Issue artifact '{issue_id}' was not registered."
    assert (
        "human_attention_queue_artifact" in registry_tree
    ), "Human attention queue artifact was not registered."
