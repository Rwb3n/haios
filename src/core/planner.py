from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "core_planner_py_g224",
    "g_annotation_last_modified": 224,
    "version_tag_of_host_at_annotation": "1.1.0"
  },
  "payload": {
    "description": "Provides planning and dependency graph utilities for the HAiOS engine, including a topological sort for task execution.",
    "artifact_type": "CORE_MODULE_PYTHON",
    "purpose_statement": "To ensure deterministic and safe task execution order by correctly resolving dependencies and detecting cycles.",
    "authors_and_contributors": [
      {"g_contribution": 160, "identifier": "Cody"},
      {"g_contribution": 224, "identifier": "Cody", "contribution_summary": "Remediation (exec_plan_00007): Added upper-bound version pin to networkx dependency."}
    ],
    "external_dependencies": [
      {
        "name": "networkx",
        "version_constraint": ">=2.5,<4.0",
        "reason_or_usage": "Provides a robust, standard implementation of graph algorithms, including topological sort and cycle detection."
      }
    ],
    "internal_dependencies": ["core_exceptions_py_g137"],
    "linked_issue_ids": ["issue_00121"]
  }
}
# ANNOTATION_BLOCK_END
"""core.planner
~~~~~~~~~~~~~~~~
Execution plan dependency resolution and topological sorting.
"""
from typing import Any, Dict, List

import networkx as nx

from .exceptions import DependencyCycleError, PlannerError


def topological_sort(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Performs a topological sort on a list of tasks.

    Each task must be a dictionary with at least an 'task_id' key.
    Dependencies are specified in a 'dependencies' key, which should
    be a list of other task_ids.

    Args:
        tasks: A list of task dictionaries.

    Returns:
        A list of tasks in a linear, executable order.

    Raises:
        DependencyCycleError: If the task dependencies contain a cycle.
        PlannerError: If a task's dependency does not exist in the task list.
    """
    if not tasks:
        return []

    graph = nx.DiGraph()
    task_map = {task["task_id"]: task for task in tasks}

    # Add nodes (tasks) to the graph
    for task_id in task_map:
        graph.add_node(task_id)

    # Add edges (dependencies) to the graph
    for task_id, task in task_map.items():
        for dep_id in task.get("dependencies", []):
            if dep_id not in task_map:
                raise PlannerError(
                    f"Task '{task_id}' has an undefined dependency: '{dep_id}'"
                )
            # Add an edge from the dependency to the task
            # (A -> B means A must be completed before B can start)
            graph.add_edge(dep_id, task_id)

    # Check for cycles before attempting to sort
    if not nx.is_directed_acyclic_graph(graph):
        cycles = list(nx.simple_cycles(graph))
        raise DependencyCycleError(
            f"A dependency cycle was detected in the execution plan. "
            f"Cycles: {cycles}"
        )

    # Perform the topological sort
    sorted_task_ids = list(nx.topological_sort(graph))

    # Return the full task dictionaries in the sorted order
    return [task_map[task_id] for task_id in sorted_task_ids]