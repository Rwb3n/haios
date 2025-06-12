# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "test_engine_e2e_py_g185",
        "g_annotation_created": 185,
        "version_tag_of_host_at_annotation": "2.0.0",
    },
    "payload": {
        "description": "A full end-to-end (E2E) test suite for the v2 HAiOS engine. It validates core functionality and key security/robustness features by running the engine as a subprocess against a temporary project.",
        "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
        "status_in_lifecycle": "STABLE",
        "purpose_statement": "To provide final, holistic evidence that the architectural refactoring was successful and the engine behaves as specified.",
        "authors_and_contributors": [
            {"g_contribution": 185, "identifier": "Successor Agent"}
        ],
        "internal_dependencies": ["engine_py_g99"],
        "quality_notes": {"overall_quality_assessment": "EXCELLENT"},
        "linked_issue_ids": ["issue_00121"],
        "scaffold_info": {"implementing_task_id": "T14_final_e2e_test"},
    },
}
# ANNOTATION_BLOCK_END

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def e2e_project(tmp_path: Path) -> Path:
    """Creates a full, temporary HAiOS project structure for E2E tests."""
    project_root = tmp_path / "e2e_project"

    # Create directories
    (project_root / "os_root/initiatives/init_e2e/issues").mkdir(parents=True)
    (project_root / "project_workspace/src").mkdir(parents=True)
    (project_root / "project_templates").mkdir(parents=True)
    (project_root / "schemas").mkdir(parents=True)

    # Create haios.config.json
    config = {
        "project_name": "E2E Test Project",
        "paths": {
            "os_root": "./os_root",
            "project_workspace": "./project_workspace",
            "project_templates": "./project_templates",
            "scaffold_definitions": "./os_root/scaffold_definitions",
            "guidelines": "./docs/guidelines",
        },
    }
    (project_root / "haios.config.json").write_text(json.dumps(config))

    # Create initial state.txt
    state = {"os_file_header": {"v_file_instance": 0}, "g": 100}
    (project_root / "os_root/state.txt").write_text(json.dumps(state))

    # Create a template file
    (project_root / "project_templates/component.js.template").write_text(
        "const component = {};"
    )

    # Create required schema files
    state_schema = {
        "title": "State Schema",
        "type": "object",
        "properties": {
            "g": {"type": "integer"},
            "v": {"type": "integer"},
            "cp_id": {"type": "string"},
        },
    }
    (project_root / "schemas/state.schema.json").write_text(json.dumps(state_schema))

    return project_root


def run_engine(project_root: Path, plan_id: str) -> subprocess.CompletedProcess:
    """Helper function to run the engine as a subprocess."""
    config_path = project_root / "haios.config.json"
    # Use sys.executable to ensure we're using the same Python interpreter
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "src.engine",
            "run-plan",
            plan_id,
            "--config",
            str(config_path),
        ],
        capture_output=True,
        text=True,
        cwd=project_root.parent,  # Run from one level up to test relative paths
    )


def test_engine_e2e_happy_path(e2e_project: Path):
    """Tests a successful run of a simple plan."""
    # Create a valid execution plan
    plan = {
        "payload": {
            "tasks": [
                {
                    "task_id": "create_file",
                    "type": "CREATE_FILE_FROM_TEMPLATE",
                    "outputs": [
                        {
                            "template": "component.js.template",
                            "path": "src/new_component.js",
                            "artifact_id_placeholder": "new_comp_js_g101",
                        }
                    ],
                }
            ]
        }
    }
    (e2e_project / "os_root/initiatives/init_e2e/exec_plan_e2e_happy.txt").write_text(
        json.dumps(plan)
    )

    # Run the engine
    result = run_engine(e2e_project, "exec_plan_e2e_happy")

    # Assert success
    assert result.returncode == 0, f"Engine failed! Stderr: {result.stderr}"

    # Assert g-counter was incremented
    final_state = json.loads((e2e_project / "os_root/state.txt").read_text())
    assert final_state["g"] > 100

    # Assert artifact was created and registered
    assert (e2e_project / "project_workspace/src/new_component.js").exists()
    registry = json.loads((e2e_project / "os_root/global_registry_map.txt").read_text())
    assert "new_comp_js_g101" in registry["payload"]["artifact_registry_tree"]


def test_engine_e2e_rejects_cycle(e2e_project: Path):
    """Tests that the engine correctly detects and rejects a plan with a cycle."""
    plan = {
        "payload": {
            "tasks": [
                {"task_id": "A", "dependencies": ["B"]},
                {"task_id": "B", "dependencies": ["A"]},
            ]
        }
    }
    (e2e_project / "os_root/initiatives/init_e2e/exec_plan_e2e_cycle.txt").write_text(
        json.dumps(plan)
    )

    result = run_engine(e2e_project, "exec_plan_e2e_cycle")

    assert result.returncode == 1, "Engine should exit with 1 on core planner errors"
    assert "DependencyCycleError" in result.stderr


def test_engine_e2e_rejects_path_traversal(e2e_project: Path):
    """Tests that the engine correctly detects and rejects a path traversal attempt."""
    plan = {
        "payload": {
            "tasks": [
                {
                    "task_id": "bad_write",
                    "type": "CREATE_FILE_FROM_TEMPLATE",
                    "outputs": [
                        {
                            "template": "component.js.template",
                            "path": "../../../bad_file.js",
                            "artifact_id_placeholder": "bad_file_js",
                        }
                    ],
                }
            ]
        }
    }
    (
        e2e_project / "os_root/initiatives/init_e2e/exec_plan_e2e_traversal.txt"
    ).write_text(json.dumps(plan))

    result = run_engine(e2e_project, "exec_plan_e2e_traversal")

    assert result.returncode == 2, "Engine should exit with 2 on security/config errors"
    assert "PathEscapeError" in result.stderr
