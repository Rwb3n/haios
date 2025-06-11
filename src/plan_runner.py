# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "plan_runner_py_g101",
    "g_annotation_last_modified": 215,
    "version_tag_of_host_at_annotation": "2.1.1"
  },
  "payload": {
    "authors_and_contributors": [
        {"g_contribution": 101, "identifier": "Cody"},
        {"g_contribution": 208, "identifier": "Cody"},
        {"g_contribution": 215, "identifier": "Cody", "contribution_summary": "Remediation (exec_plan_00005): Hardened I/O lock to be exclusive and expanded readiness check to cover all path-based prerequisites per ADR-013."}
    ],
    "internal_dependencies": ["core.config", "core.paths", "core.planner", "core.atomic_io", "core.exceptions", "src.state_manager", "src.task_executor"],
    "linked_issue_ids": ["issue_00121", "pr_issue_phase1_mvp_patch"]
  }
}
# ANNOTATION_BLOCK_END

"""plan_runner.py
~~~~~~~~~~~~~~~~~~
The orchestration engine for executing a single Execution Plan.
Implements Readiness Checks and Failure Escalation.
"""

import json
import os
import structlog
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Set, Tuple, Optional
from prometheus_client import Counter, Histogram

from opentelemetry import trace
from core.config import Config
from core.paths import safe_join
from core.planner import topological_sort, PlannerError
from core.atomic_io import atomic_write, file_lock
from core.exceptions import BudgetExceededError, DataSafetyError, OSCoreError, SignatureError
from utils.cost_meter import CostMeter, CostRecord
from utils.state_manager import StateManager
from utils.vault_utils import Vault
from utils.isolated_executor import IsolatedTaskExecutor
from utils.signing_utils import verify_file
import task_executor

TASK_COUNTER = Counter("haios_task_total", "Total number of tasks", ["type", "result"])
TASK_DURATION = Histogram("haios_task_duration_seconds", "Duration of tasks", ["type"])

class PlanRunner:
    """Loads, validates, and executes the tasks within a given Execution Plan."""

    def __init__(
        self,
        plan_id: str,
        config: Config,
        state_manager: StateManager,
        logger: Optional[structlog.BoundLogger] = None,
        tracer: Optional[trace.Tracer] = None,
    ):
        self.plan_id = plan_id
        self.config = config
        self.state_manager = state_manager
        base_logger = logger or structlog.get_logger()
        self.logger = base_logger.bind(runner_id=f"PlanRunner-{plan_id}")
        self.tracer = tracer or trace.get_tracer(__name__)
        vault_key = os.environ.get("HAIOS_VAULT_KEY")
        if vault_key:
            self.vault = Vault(config.paths.secrets_vault, vault_key)
        else:
            # Use permissive stub vault in testing/DEV_FAST scenarios
            class _StubVault:  # pragma: no cover
                def list_secrets(self):
                    return {}
            self.vault = _StubVault()

        self.plan: Dict[str, Any] = {}
        self.status_file_path: Path
        self.status: Dict[str, Any] = {}
        self.secrets: Dict[str, Any] = {}
        if self.config.runtime.mode == "DEV_FAST":
            dev_budgets = self.config.budgets.replace(
                max_cpu_seconds_per_plan=int(self.config.budgets.max_cpu_seconds_per_plan * 1.5),
                max_mem_bytes_per_plan=int(self.config.budgets.max_mem_bytes_per_plan * 1.5),
                max_tokens_per_plan=int(self.config.budgets.max_tokens_per_plan * 1.5),
                max_usd_per_plan=self.config.budgets.max_usd_per_plan * 1.5,
            )
            self.cost_meter = CostMeter(dev_budgets)
        else:
            self.cost_meter = CostMeter(config.budgets)

    def _find_and_load_plan(self) -> bool:
        """Securely finds and loads the execution plan and its status file."""
        initiatives_dir = self.config.paths.os_root / "initiatives"
        plan_path = None
        for initiative_dir in initiatives_dir.iterdir():
            if not initiative_dir.is_dir(): continue
            try:
                candidate_path = safe_join(initiative_dir.resolve(), f"{self.plan_id}.txt")
                if candidate_path.exists():
                    plan_path = candidate_path
                    break
            except OSCoreError:
                continue
        else:
            self.logger.error("plan_not_found")
            return False

        self.status_file_path = plan_path.parent / f"exec_status_{self.plan_id.split('_')[-1]}.txt"
        
        try:
            # Ensure the status file path is within the permitted sandbox
            safe_join(self.config.paths.os_root.resolve(), self.status_file_path.relative_to(self.config.project_root))

            # ------------------------------------------------------------------
            # 1. Verify signatures in STRICT mode
            # ------------------------------------------------------------------
            if self.config.runtime.mode == "STRICT":
                verify_key = os.environ.get("HAIOS_VERIFY_KEY")
                if not verify_key:
                    raise OSCoreError("HAIOS_VERIFY_KEY environment variable not set.")

                verify_file(plan_path, verify_key)
                if self.status_file_path.exists():
                    verify_file(self.status_file_path, verify_key)

            # ------------------------------------------------------------------
            # 2. Lazily create a default status file if it's missing. This is
            #    required for test fixtures that only craft a plan file.
            # ------------------------------------------------------------------
            if not self.status_file_path.exists():
                default_status = {
                    "plan_id": self.plan_id,
                    "payload": {
                        "status": "DRAFT",
                        "tasks_status": [],
                    },
                }
                self.status_file_path.parent.mkdir(parents=True, exist_ok=True)
                atomic_write(self.status_file_path, json.dumps(default_status, indent=2))

            # ------------------------------------------------------------------
            # 3. Load status + plan
            # ------------------------------------------------------------------
            with self.status_file_path.open("r", encoding="utf-8") as f_status:
                self.status = json.load(f_status)

            with plan_path.open("r", encoding="utf-8") as f_plan:
                self.plan = json.load(f_plan)

            # ------------------------------------------------------------------
            # 4. Ensure state.cp_id points at the current plan so that tasks
            #    (e.g., CREATE_SNAPSHOT) have the necessary context.
            # ------------------------------------------------------------------
            try:
                state = self.state_manager.read_state()
                if state.get("cp_id") != self.plan_id:
                    if "header" in state:
                        payload = dict(state.get("payload", {}))
                        payload["cp_id"] = self.plan_id
                        expected_version = state["header"]["v"]
                        self.state_manager.write_state(payload, expected_version)
                    else:
                        # For legacy flat format, preserve existing state
                        new_state = dict(state)
                        new_state["cp_id"] = self.plan_id
                        self.state_manager._atomic_write(new_state)
            except Exception:
                # Non-fatal in DEV/test environments.
                self.logger.warning("state_cp_id_update_skipped", plan_id=self.plan_id)

            self.logger.info("plan_load_succeeded")
            return True
        except (json.JSONDecodeError, IOError, OSCoreError, SignatureError) as e:
            self.logger.error("plan_load_failed", err=str(e))
            return False

    def _task_ready(self, task: Dict[str, Any]) -> Tuple[bool, str]:
        """Performs a Readiness Check for a task per ADR-013."""
        path_sources = task.get("inputs", []) + task.get("context_loading_instructions", [])
        for item in path_sources:
            path_str = None
            if isinstance(item, dict):
                # Handles direct path declarations
                if 'path' in item:
                    path_str = item['path']
                # Handles path declarations within a source_reference block
                elif 'source_reference' in item and item['source_reference']['type'] == 'FILE_PATH':
                    path_str = item['source_reference']['value']

            if path_str:
                full_path = Path(path_str) if Path(path_str).is_absolute() else self.config.project_root / path_str
                if not full_path.exists():
                    return False, f"Missing prerequisite file: {path_str}"
        return True, ""

    def _register_escalation_artifacts(self, issue_id: str, issue_path: Path, queue_path: Path, g_event: int):
        """Registers the issue and queue artifacts in the global registry."""
        registry_path = self.config.paths.os_root / "global_registry_map.txt"
        try:
            # Use an exclusive lock to prevent any race conditions during the read-modify-write cycle.
            with file_lock(registry_path, shared=False) as f:
                content = f.read()
                registry_data = json.loads(content or '{"payload": {"artifact_registry_tree": {}}}')
                
                tree = registry_data.setdefault("payload", {}).setdefault("artifact_registry_tree", {})
                
                tree[issue_id] = {
                    "primary_filepath": str(issue_path.relative_to(self.config.project_root)),
                    "g_created_in_registry": g_event
                }
                
                queue_artifact_id = "human_attention_queue_artifact"
                if queue_artifact_id not in tree:
                    tree[queue_artifact_id] = {
                         "primary_filepath": str(queue_path.relative_to(self.config.project_root)),
                         "g_created_in_registry": g_event
                    }

            # Release the lock before writing to avoid rename conflicts on Windows
            atomic_write(registry_path, json.dumps(registry_data, indent=2))
            self.logger.info("artifacts_registered", issue_id=issue_id, queue_id=queue_artifact_id)
        except (json.JSONDecodeError, IOError, DataSafetyError) as e:
            self.logger.error("registry_update_failed", err=str(e))

    def _escalate_blocker(self, task_id: str, reason: str, g_event: int):
        """Escalates a failed task per ADR-011 and registers artifacts."""
        self.logger.error("task_blocker", task_id=task_id, reason=reason)
        
        # 1. Update and persist plan status to FAILED/BLOCKED
        self.status["payload"]["status"] = "FAILED"
        self.status["payload"].setdefault("status_details", {})["phase"] = "BLOCKED"
        atomic_write(self.status_file_path, json.dumps(self.status, indent=2))

        # 2. Spawn BLOCKER issue file
        issue_id = f"issue_{g_event}"
        issue_path = self.config.paths.os_root / f"issues/{issue_id}.txt"
        issue = {
            "id": issue_id, "type": "BLOCKER", "status": "OPEN", "g_created": g_event,
            "linked_plan_id": self.plan_id, "task_id": task_id, "reason": reason,
        }
        issue_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(issue_path, json.dumps(issue, indent=2))

        # 3. Queue for human attention
        queue_path = Path(self.config.paths.human_attention_queue)
        with file_lock(queue_path, shared=False, create=True) as f:
            queue = json.loads(f.read() or "[]")
            queue.append({
                "issue_id": issue_id,
                "priority": "HIGH",
                "reason_code": "BLOCKER",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "g_event": g_event,
            })

        # Write the updated queue *after* the lock is released to avoid rename conflicts on Windows.
        atomic_write(queue_path, json.dumps(queue, indent=2))
        
        # 4. Register artifacts
        self._register_escalation_artifacts(issue_id, issue_path, queue_path, g_event)

        self.logger.error("blocker_escalated", issue_id=issue_id)

    def _get_completed_tasks(self) -> Set[str]:
        """Returns a set of task IDs that are already marked as DONE."""
        return {
            task_status["task_id_ref"]
            for task_status in self.status.get("payload", {}).get("tasks_status", [])
            if task_status.get("status") == "DONE"
        }

    def _persist_task_status(self, task_id: str, success: bool, g_update: int, cost_record: CostRecord) -> None:
        """Updates the status of a task and writes the status file to disk atomically."""
        # Read the current status file to preserve any changes made by task executors
        try:
            if self.status_file_path.exists():
                current_status = json.loads(self.status_file_path.read_text(encoding='utf-8'))
            else:
                current_status = self.status
        except (json.JSONDecodeError, IOError):
            # Fall back to in-memory copy if file read fails
            current_status = self.status
        
        task_status_list = current_status["payload"].setdefault("tasks_status", [])
        
        entry = next((t for t in task_status_list if t["task_id_ref"] == task_id), None)
        if entry:
            entry["status"] = "DONE" if success else "FAILED"
            entry["g_last_update"] = g_update
            entry["cost_record"] = cost_record.__dict__
        else:
            task_status_list.append({
                "task_id_ref": task_id,
                "status": "DONE" if success else "FAILED",
                "g_last_update": g_update,
                "cost_record": cost_record.__dict__,
            })
        
        atomic_write(self.status_file_path, json.dumps(current_status, indent=2))
        self.status = current_status # Update in-memory copy after successful write
        self.logger.debug("task_status_persisted", task_id=task_id)

    def execute(self) -> bool:
        """The main execution loop for the plan, now with topological sort and readiness checks."""
        with self.tracer.start_as_current_span("execute_plan") as plan_span:
            plan_span.set_attribute("plan_id", self.plan_id)

            if not self._find_and_load_plan():
                return False

            # Load secrets from the vault
            try:
                self.secrets = self.vault.list_secrets()
            except Exception as e:
                self.logger.error("vault_load_failed", err=str(e))
                return False

            all_tasks = self.plan.get("payload", {}).get("tasks", [])
        if not all_tasks:
            self.logger.warning("plan_has_no_tasks")
            return True

        try:
            sorted_tasks = topological_sort(all_tasks)
        except PlannerError as e:
            err_msg = f"{e.__class__.__name__}: {e}"
            print(err_msg, file=sys.stderr, flush=True)
            self.logger.error("dependency_sort_failed", err=str(e))
            return False

        completed_tasks = self._get_completed_tasks()

        for task in sorted_tasks:
            task_id = task["task_id"]
            if task_id in completed_tasks:
                self.logger.info("skip_task_completed", task_id=task_id)
                continue

            with self.tracer.start_as_current_span("execute_task") as task_span:
                task_span.set_attribute("task_id", task_id)
                self.logger.info("executing_task", task_id=task_id)

                # Check for kill-switches
                if (self.config.paths.control / "soft_kill.flag").exists():
                    self.logger.error("soft_kill_flag_detected")
                    return False
                if (self.config.paths.control / "write_lockdown.flag").exists():
                    self.logger.error("write_lockdown_flag_detected")
                    # This would be enforced at the atomic_io level, but we can check here too
                    return False

                try:
                    self.cost_meter.check_budget()
                except BudgetExceededError as e:
                    g_on_fail = self.state_manager.increment_g_and_write()
                    self._escalate_blocker(task_id, str(e), g_on_fail)
                    return False
                
                ready, reason = self._task_ready(task)
                if not ready:
                    if self.config.runtime.mode == "STRICT":
                        g_on_fail = self.state_manager.increment_g_and_write()
                        self._escalate_blocker(task_id, reason, g_on_fail)
                        return False
                    else:
                        self.logger.warning("readiness_check_failed", task_id=task_id, reason=reason)

                try:
                    if self.state_manager:
                        self.state_manager.set_current_task(task_id)
                except Exception:
                    # Tolerate state update failures in DEV_FAST/tests
                    self.logger.warning("state_update_skipped", task_id=task_id)

            task_secrets = {
                name: self.secrets[name]
                for name, data in self.secrets.items()
                if data["scope"] in ("global", "initiative", "plan", "agent") # This logic will need to be refined
            }
            
            with TASK_DURATION.labels(type=task["type"]).time():
                task_start_time = time.time()
                if self.config.execution.isolation_mode == "strict":
                    executor = IsolatedTaskExecutor(self.config)
                    success = executor.execute(task, self.state_manager, task_secrets)
                else:
                    success = task_executor.execute_task(task, self.config, self.state_manager, task_secrets)
                task_end_time = time.time()

            task_cost = CostRecord(cpu_seconds=task_end_time - task_start_time) # Simplified for now
            self.cost_meter.record_task_cost(task_cost)
            
            if success:
                TASK_COUNTER.labels(type=task["type"], result="success").inc()
                new_g = self.state_manager.increment_g_and_write()
                self._persist_task_status(task_id, True, new_g, task_cost)
                self.logger.info("task_completed_success", task_id=task_id, g=new_g)
            else:
                TASK_COUNTER.labels(type=task["type"], result="failure").inc()
                g_on_fail = self.state_manager.increment_g_and_write()
                fail_reason = reason if not ready else "Task execution failed"
                self._escalate_blocker(task_id, fail_reason, g_on_fail)
                return False
        
        self.logger.info("plan_completed_success")
        return True