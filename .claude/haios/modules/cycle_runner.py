# generated: 2026-01-04
# System Auto: last updated on: 2026-01-21T20:31:23
"""
CycleRunner Module (E2-255)

Stateless phase gate validator for HAIOS cycle skills. Provides:
- Phase entry/exit gate checking
- Cycle phase sequence lookup
- Event emission for observability

L4 Invariants (from S17.5):
- MUST NOT execute skill content (Claude interprets markdown)
- MUST delegate gate checks to GovernanceLayer
- MUST emit events for observability (PhaseEntered, GatePassed)
- MUST NOT own persistent state

Design Decision: CycleRunner validates gates, does NOT orchestrate.
Skills remain markdown files that Claude interprets.

Usage:
    from cycle_runner import CycleRunner, CycleResult
    from governance_layer import GovernanceLayer

    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    phases = runner.get_cycle_phases("implementation-cycle")
    # ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]

    result = runner.check_phase_entry("implementation-cycle", "DO", "E2-255")
    if result.allowed:
        print("Phase entry allowed")
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import yaml

# Import sibling modules
# Use conditional import to support both package and standalone usage (E2-255 pattern)
try:
    from .governance_layer import GovernanceLayer, GateResult
except ImportError:
    from governance_layer import GovernanceLayer, GateResult

# Import event logging from lib
# WORK-006: Use lib inside haios/ for portability
import sys

_lib_path = Path(__file__).parent.parent / "lib"  # .claude/haios/lib (sibling to modules/)
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from governance_events import log_phase_transition, log_validation_outcome


@dataclass
class CycleResult:
    """Result of a cycle validation or execution."""

    cycle_id: str
    final_phase: str
    outcome: Literal["completed", "blocked", "chain"]
    gate_results: List[GateResult] = field(default_factory=list)
    next_cycle: Optional[str] = None


# Cycle phase definitions (from S17.5 and existing skills)
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["HYPOTHESIZE", "EXPLORE", "CONCLUDE", "CHAIN"],
    "close-work-cycle": ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"],
    "work-creation-cycle": ["VERIFY", "POPULATE", "READY"],
    "checkpoint-cycle": ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"],
    "plan-authoring-cycle": ["ANALYZE", "AUTHOR", "VALIDATE", "CHAIN"],
    "observation-triage-cycle": ["SCAN", "TRIAGE", "PROMOTE"],
}


class CycleRunner:
    """
    Stateless phase gate validator for cycle skills.

    Does NOT execute skills - validates that phases can be entered/exited.
    """

    def __init__(
        self,
        governance: GovernanceLayer,
        work_engine: Optional[Any] = None,
    ):
        """
        Initialize CycleRunner with dependencies.

        Args:
            governance: GovernanceLayer for gate checks
            work_engine: Optional WorkEngine for work state access
        """
        self._governance = governance
        self._work_engine = work_engine
        self._cycle_config = self._load_cycle_definitions()

    def _load_cycle_definitions(self) -> Dict[str, Any]:
        """Load cycle definitions from config."""
        config_path = Path(__file__).parent.parent / "config" / "cycles.yaml"
        if not config_path.exists():
            return {}
        try:
            with open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def get_cycle_phases(self, cycle_id: str) -> List[str]:
        """
        Return ordered phases for a cycle.

        Args:
            cycle_id: Cycle identifier (e.g., "implementation-cycle")

        Returns:
            List of phase names, or empty list if cycle not found.
        """
        return CYCLE_PHASES.get(cycle_id, [])

    def check_phase_entry(
        self, cycle_id: str, phase: str, work_id: str
    ) -> GateResult:
        """
        Check if a phase can be entered (entry conditions met).

        Entry conditions are currently defined in skill markdown.
        This method provides a hook for programmatic checks.

        Args:
            cycle_id: Cycle identifier
            phase: Target phase name
            work_id: Work item ID

        Returns:
            GateResult with allowed=True (MVP: always allow entry)

        Side Effects:
            Emits PhaseEntered event via log_phase_transition()
        """
        # For MVP: always allow entry (conditions in skill markdown)
        # Future: read entry conditions from skill and validate
        self._emit_phase_entered(cycle_id, phase, work_id)
        return GateResult(allowed=True, reason=f"Phase {phase} entry allowed")

    def check_phase_exit(
        self, cycle_id: str, phase: str, work_id: str
    ) -> GateResult:
        """
        Check if a phase can be exited (exit criteria met).

        Delegates to node_cycle.check_exit_criteria for node-bound cycles.

        Args:
            cycle_id: Cycle identifier
            phase: Current phase name
            work_id: Work item ID

        Returns:
            GateResult with allowed flag and reason
        """
        from node_cycle import check_exit_criteria

        # Map cycle to node (if node-bound)
        node = self._get_node_for_cycle(cycle_id)
        if not node:
            # Not node-bound, allow exit
            return GateResult(
                allowed=True, reason=f"Phase {phase} exit allowed (no node binding)"
            )

        # Check exit criteria from config
        failures = check_exit_criteria(node, work_id)
        if failures:
            return GateResult(
                allowed=False, reason=f"Exit blocked: {'; '.join(failures)}"
            )

        return GateResult(allowed=True, reason=f"Phase {phase} exit criteria met")

    def _get_node_for_cycle(self, cycle_id: str) -> Optional[str]:
        """Map cycle to DAG node (if any)."""
        nodes = self._cycle_config.get("nodes", {})
        for node_name, config in nodes.items():
            if config.get("cycle") == cycle_id:
                return node_name
        return None

    def _emit_phase_entered(
        self, cycle_id: str, phase: str, work_id: str
    ) -> None:
        """Emit PhaseEntered event for observability."""
        log_phase_transition(phase, work_id, "Hephaestus")

    # =========================================================================
    # E2-263: Scaffold Command
    # =========================================================================

    def build_scaffold_command(
        self, template: str, work_id: str, title: str
    ) -> str:
        """
        Build scaffold command from template.

        Delegates to node_cycle.build_scaffold_command().

        Args:
            template: Command template with {id} and {title} placeholders
            work_id: Work item ID (e.g., "E2-263")
            title: Work item title

        Returns:
            Complete command string with placeholders replaced.
        """
        from node_cycle import build_scaffold_command as _build_scaffold_command
        return _build_scaffold_command(template, work_id, title)
