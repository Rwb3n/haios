# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "test_core_planner_py_g162",
        "g_annotation_created": 162,
        "version_tag_of_host_at_annotation": "1.0.0",
    },
    "payload": {
        "description": "Unit tests for the core.planner module, focusing on the topological_sort function.",
        "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
        "purpose_statement": "To provide evidence that the task dependency resolver correctly orders tasks, detects cycles, and handles invalid dependency references.",
        "internal_dependencies": ["core_planner_py_g160", "core_exceptions_py_g137"],
        "linked_issue_ids": ["issue_00121"],
    },
}
# ANNOTATION_BLOCK_END
"""tests.core.test_planner
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tests for the dependency graph and topological sort utilities.
"""
import pytest

from core import planner
from core.exceptions import DependencyCycleError, PlannerError

# --- Test Data ---

# A -> B -> D
# A -> C -> D
DIAMOND_GRAPH_TASKS = [
    {"task_id": "D", "dependencies": ["B", "C"]},
    {"task_id": "C", "dependencies": ["A"]},
    {"task_id": "B", "dependencies": ["A"]},
    {"task_id": "A"},
]

# A -> B -> C -> A
CYCLE_GRAPH_TASKS = [
    {"task_id": "C", "dependencies": ["B"]},
    {"task_id": "A", "dependencies": ["C"]},
    {"task_id": "B", "dependencies": ["A"]},
]

INVALID_DEP_TASKS = [
    {"task_id": "B", "dependencies": ["NON_EXISTENT"]},
    {"task_id": "A"},
]

# --- Happy Path Test ---


def test_topological_sort_correct_order_for_diamond_graph():
    """A valid 'diamond' dependency graph should be sorted correctly."""
    sorted_tasks = planner.topological_sort(DIAMOND_GRAPH_TASKS)
    sorted_ids = [task["task_id"] for task in sorted_tasks]

    # 'A' must be first
    assert sorted_ids[0] == "A"
    # 'D' must be last
    assert sorted_ids[-1] == "D"
    # The order of B and C is not guaranteed, but they must come after A and before D
    assert set(sorted_ids[1:3]) == {"B", "C"}
    assert len(sorted_ids) == 4


def test_topological_sort_with_no_dependencies():
    """Tasks with no dependencies should be returned, order doesn't matter."""
    tasks = [{"task_id": "A"}, {"task_id": "B"}, {"task_id": "C"}]
    sorted_tasks = planner.topological_sort(tasks)
    sorted_ids = {task["task_id"] for task in sorted_tasks}
    assert sorted_ids == {"A", "B", "C"}


def test_topological_sort_empty_list():
    """An empty list of tasks should return an empty list."""
    assert planner.topological_sort([]) == []


# --- Failure Path Tests ---


def test_topological_sort_detects_cycle():
    """A graph with a cycle must raise DependencyCycleError."""
    with pytest.raises(DependencyCycleError, match="A dependency cycle was detected"):
        planner.topological_sort(CYCLE_GRAPH_TASKS)


def test_topological_sort_detects_invalid_dependency():
    """A task depending on a non-existent task must raise PlannerError."""
    with pytest.raises(
        PlannerError, match="has an undefined dependency: 'NON_EXISTENT'"
    ):
        planner.topological_sort(INVALID_DEP_TASKS)
