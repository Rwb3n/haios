from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "utils_cost_meter_py_g236",
    "g_annotation_created": 236,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "A utility for tracking and enforcing resource budgets.",
    "artifact_type": "UTILITY_MODULE_PYTHON",
    "status_in_lifecycle": "PROPOSED",
    "purpose_statement": "To provide a mechanism for monitoring and controlling resource usage (CPU, memory) during plan execution, as per ADR-OS-018.",
    "authors_and_contributors": [{"g_contribution": 236, "identifier": "Roo"}],
    "internal_dependencies": ["core.config", "core.exceptions"],
    "external_dependencies": [
        {"name": "psutil", "version_constraint": ">=5.9.0,<6.0.0"}
    ],
    "linked_issue_ids": ["issue_C4_roadmap"]
  }
}
# ANNOTATION_BLOCK_END

import os
import time
from dataclasses import dataclass, field

import psutil
from core.config import BudgetsConfig
from core.exceptions import BudgetExceededError

@dataclass
class CostRecord:
    """Represents the cost of a single task."""
    cpu_seconds: float = 0.0
    mem_bytes: int = 0
    tokens: int = 0
    usd: float = 0.0

class CostMeter:
    """Tracks and enforces resource budgets."""

    def __init__(self, budgets: BudgetsConfig):
        self.budgets = budgets
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        self.cpu_time_start = self._get_cpu_time()
        self.total_cost = CostRecord()

    def _get_cpu_time(self) -> float:
        """Gets the total CPU time of the process and its children."""
        return self.process.cpu_times().user + self.process.cpu_times().system

    def check_budget(self):
        """Checks if any budget has been exceeded."""
        current_cpu_time = self._get_cpu_time() - self.cpu_time_start
        if current_cpu_time > self.budgets.max_cpu_seconds_per_plan:
            raise BudgetExceededError(f"CPU time limit exceeded: {current_cpu_time}s > {self.budgets.max_cpu_seconds_per_plan}s")

        current_mem_bytes = self.process.memory_info().rss
        if current_mem_bytes > self.budgets.max_mem_bytes_per_plan:
            raise BudgetExceededError(f"Memory limit exceeded: {current_mem_bytes}B > {self.budgets.max_mem_bytes_per_plan}B")

    def record_task_cost(self, task_cost: CostRecord):
        """Adds the cost of a completed task to the total."""
        self.total_cost.cpu_seconds += task_cost.cpu_seconds
        self.total_cost.mem_bytes += task_cost.mem_bytes
        self.total_cost.tokens += task_cost.tokens
        self.total_cost.usd += task_cost.usd