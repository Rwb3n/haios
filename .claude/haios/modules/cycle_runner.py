# generated: 2026-01-04
# System Auto: last updated on: 2026-02-05T22:05:28
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
from datetime import datetime
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


# =============================================================================
# WORK-093: Asset Types (REQ-ASSET-001) — replaces WORK-084 MVP stubs
# =============================================================================

try:
    from .assets import (
        Asset,
        ArtifactAsset,
        FindingsAsset,
        PriorityListAsset,
        SpecificationAsset,
        VerdictAsset,
    )
except ImportError:
    from assets import (
        Asset,
        ArtifactAsset,
        FindingsAsset,
        PriorityListAsset,
        SpecificationAsset,
        VerdictAsset,
    )

# Backward compatibility aliases (WORK-084 names)
LifecycleOutput = Asset
Findings = FindingsAsset
Specification = SpecificationAsset
Artifact = ArtifactAsset
Verdict = VerdictAsset
PriorityList = PriorityListAsset


# Lifecycle phase definitions (from S17.5 and existing skills)
# WORK-098: investigation-cycle aligned with L4 REQ-FLOW-002 (Session 304)
# WORK-118: Ceremony phases extracted to ceremony_runner.py (CH-013, REQ-CEREMONY-003)
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["EXPLORE", "HYPOTHESIZE", "VALIDATE", "CONCLUDE", "CHAIN"],
    "plan-authoring-cycle": ["ANALYZE", "AUTHOR", "VALIDATE", "CHAIN"],
}

# WORK-085: Pause phases per lifecycle (REQ-LIFECYCLE-002, S27 Breath Model)
# Pause = exhale complete, valid completion state per S27
# These are the phases where work can safely stop without being "incomplete"
# WORK-099: Added PROMOTE as alias for observation-triage-cycle (Session 304)
PAUSE_PHASES: Dict[str, List[str]] = {
    "investigation": ["CONCLUDE"],      # After exhale: findings committed
    "design": ["COMPLETE"],             # After exhale: spec committed
    "implementation": ["DONE"],         # After exhale: artifact committed
    "validation": ["REPORT"],           # After exhale: verdict committed
    "triage": ["COMMIT", "PROMOTE"],    # After exhale: priorities committed (PROMOTE is skill alias)
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

        Falls back to CEREMONY_PHASES for backward compatibility (WORK-118).
        Callers using ceremony IDs (e.g., "close-work-cycle") still get phases.

        Args:
            cycle_id: Cycle identifier (e.g., "implementation-cycle")

        Returns:
            List of phase names, or empty list if cycle not found.
        """
        phases = CYCLE_PHASES.get(cycle_id)
        if phases is not None:
            return phases
        # WORK-118: Backward compat — fall back to CEREMONY_PHASES
        try:
            from ceremony_runner import CEREMONY_PHASES
            return CEREMONY_PHASES.get(cycle_id, [])
        except ImportError:
            return []

    def check_phase_entry(
        self, cycle_id: str, phase: str, work_id: str
    ) -> GateResult:
        """
        Check if a phase can be entered (entry conditions met).

        WORK-088: Now validates input contract from phase template.

        Args:
            cycle_id: Cycle identifier
            phase: Target phase name
            work_id: Work item ID

        Returns:
            GateResult with allowed=True (MVP: soft gate, always allows)

        Side Effects:
            Emits PhaseEntered event via log_phase_transition()
            Logs validation warnings if contract not satisfied
        """
        # WORK-088: Validate input contract before entry
        input_result = self.validate_phase_input(phase, work_id)
        if not input_result.allowed:
            # Log warning but don't block (MVP soft gate)
            log_validation_outcome(
                work_id=work_id,
                gate="phase_entry",
                outcome="warn",
                reason=input_result.reason
            )
            # MVP: Allow anyway (soft gate)
            # Future CH-007: return input_result to hard block

        self._emit_phase_entered(cycle_id, phase, work_id)
        return GateResult(allowed=True, reason=f"Phase {phase} entry allowed")

    def check_phase_exit(
        self, cycle_id: str, phase: str, work_id: str
    ) -> GateResult:
        """
        Check if a phase can be exited (exit criteria met).

        WORK-088: Now validates output contract from phase template.
        Delegates to node_cycle.check_exit_criteria for node-bound cycles.

        Args:
            cycle_id: Cycle identifier
            phase: Current phase name
            work_id: Work item ID

        Returns:
            GateResult with allowed flag and reason
        """
        # WORK-088: Validate output contract before exit
        output_result = self.validate_phase_output(phase, work_id)
        if not output_result.allowed:
            # Log warning but don't block (MVP soft gate)
            log_validation_outcome(
                work_id=work_id,
                gate="phase_exit",
                outcome="warn",
                reason=output_result.reason
            )
            # MVP: Allow anyway (soft gate)

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

    # =========================================================================
    # WORK-093: Lifecycle Execution (REQ-ASSET-001, REQ-LIFECYCLE-001)
    # =========================================================================

    def run(self, work_id: str, lifecycle: str) -> Asset:
        """
        Execute lifecycle and return typed Asset. Does NOT auto-chain.

        This implements REQ-LIFECYCLE-001: Lifecycles are pure functions.
        Caller decides whether to chain to next lifecycle.

        Args:
            work_id: Work item ID (e.g., "WORK-093", "INV-001")
            lifecycle: Lifecycle name ("investigation", "design", "implementation",
                       "validation", "triage")

        Returns:
            Typed Asset subclass based on lifecycle type:
            - investigation -> FindingsAsset
            - design -> SpecificationAsset
            - implementation -> ArtifactAsset
            - validation -> VerdictAsset
            - triage -> PriorityListAsset
            - unknown -> Asset (base)

        Note:
            Returns typed output with default/empty values.
            Full content population requires integration with skill execution
            (see CH-005: PhaseTemplateContracts).
        """
        # Map lifecycle to asset type
        asset_types: Dict[str, type] = {
            "investigation": FindingsAsset,
            "design": SpecificationAsset,
            "implementation": ArtifactAsset,
            "validation": VerdictAsset,
            "triage": PriorityListAsset,
        }

        # Get asset type or default to base
        asset_class = asset_types.get(lifecycle, Asset)

        # Emit phase entered for observability
        self._emit_phase_entered(lifecycle, "RUN", work_id)

        # Create timestamp and deterministic asset_id
        now = datetime.now()
        asset_id = f"{lifecycle}-{work_id}-v1"

        # Common base fields for all assets
        base_fields = {
            "asset_id": asset_id,
            "type": lifecycle if asset_class == Asset else {
                FindingsAsset: "findings",
                SpecificationAsset: "specification",
                ArtifactAsset: "artifact",
                VerdictAsset: "verdict",
                PriorityListAsset: "priority_list",
            }.get(asset_class, lifecycle),
            "produced_by": lifecycle,
            "source_work": work_id,
            "version": 1,
            "timestamp": now,
            "author": "Hephaestus",
            "status": "success",
        }

        # Return base Asset for unknown lifecycles
        if asset_class == Asset:
            return Asset(**base_fields)

        # For typed assets, add default values for subclass fields
        if asset_class == FindingsAsset:
            return FindingsAsset(**base_fields)
        elif asset_class == SpecificationAsset:
            return SpecificationAsset(**base_fields)
        elif asset_class == ArtifactAsset:
            return ArtifactAsset(**base_fields)
        elif asset_class == VerdictAsset:
            return VerdictAsset(**base_fields)
        elif asset_class == PriorityListAsset:
            return PriorityListAsset(**base_fields)

        # Fallback (should not reach here)
        return Asset(**base_fields)

    # =========================================================================
    # WORK-086: Batch Execution (REQ-LIFECYCLE-003)
    # =========================================================================

    # Known lifecycles for validation
    VALID_LIFECYCLES = {"investigation", "design", "implementation", "validation", "triage"}

    def run_batch(
        self,
        work_ids: List[str],
        lifecycle: str,
        until_phase: Optional[str] = None,
    ) -> Dict[str, Asset]:
        """
        Execute lifecycle for multiple work items sequentially.

        Per-item error handling: if one item fails, it gets status="failure"
        and processing continues with remaining items.

        Args:
            work_ids: List of work item IDs to process
            lifecycle: Lifecycle name (must be one of 5 known lifecycles)
            until_phase: Accepted but no-ops in MVP (matches existing run() pattern)

        Returns:
            Dict mapping work_id to Asset for each item

        Raises:
            ValueError: If lifecycle is not a known lifecycle name
        """
        if lifecycle not in self.VALID_LIFECYCLES:
            raise ValueError(
                f"Unknown lifecycle '{lifecycle}'. "
                f"Must be one of: {sorted(self.VALID_LIFECYCLES)}"
            )

        if not work_ids:
            return {}

        results: Dict[str, Asset] = {}

        for work_id in work_ids:
            try:
                output = self.run(work_id, lifecycle)
                results[work_id] = output
            except Exception:
                # Per-item error handling: set failure status, continue
                results[work_id] = Asset(
                    asset_id=f"{lifecycle}-{work_id}-v1",
                    type=lifecycle,
                    produced_by=lifecycle,
                    source_work=work_id,
                    version=1,
                    timestamp=datetime.now(),
                    author="Hephaestus",
                    status="failure",
                )

        return results

    # =========================================================================
    # WORK-088: Phase Template Contract Validation (REQ-TEMPLATE-001)
    # =========================================================================

    def _load_phase_template(self, phase: str) -> Dict[str, Any]:
        """Load phase template frontmatter.

        Args:
            phase: Phase name (e.g., "EXPLORE", "HYPOTHESIZE")

        Returns:
            Dict with frontmatter fields, empty dict if not found.
        """
        # Map phase to template path
        template_paths = {
            "EXPLORE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "EXPLORE.md",
            "HYPOTHESIZE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "HYPOTHESIZE.md",
            "VALIDATE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "VALIDATE.md",
            "CONCLUDE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "CONCLUDE.md",
        }

        path = template_paths.get(phase)
        if not path or not path.exists():
            return {}

        try:
            content = path.read_text(encoding="utf-8")
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    frontmatter = content[3:end].strip()
                    return yaml.safe_load(frontmatter) or {}
        except (yaml.YAMLError, OSError) as e:
            # Log warning but return empty dict (graceful degradation)
            log_validation_outcome(
                work_id="system",
                gate="template_load",
                outcome="warn",
                reason=f"Failed to load template {phase}: {e}"
            )
        return {}

    def validate_phase_input(self, phase: str, work_id: str) -> GateResult:
        """Validate input contract for phase entry (REQ-TEMPLATE-001).

        Args:
            phase: Target phase name
            work_id: Work item ID

        Returns:
            GateResult - allowed if all required inputs present, blocked otherwise.
        """
        template = self._load_phase_template(phase)
        contract = template.get("input_contract", [])

        if not contract:
            # No contract defined, allow entry (backward compatible)
            return GateResult(allowed=True, reason=f"No input contract for {phase}")

        # Check each required item
        for item in contract:
            if item.get("required", False):
                if not self._check_work_has_field(work_id, item["field"]):
                    return GateResult(
                        allowed=False,
                        reason=f"Missing required input: {item['field']} - {item.get('description', '')}"
                    )

        return GateResult(allowed=True, reason=f"Input contract satisfied for {phase}")

    def validate_phase_output(self, phase: str, work_id: str) -> GateResult:
        """Validate output contract for phase exit (REQ-TEMPLATE-001).

        Args:
            phase: Current phase name
            work_id: Work item ID

        Returns:
            GateResult - allowed if all required outputs present, blocked otherwise.
        """
        template = self._load_phase_template(phase)
        contract = template.get("output_contract", [])

        if not contract:
            return GateResult(allowed=True, reason=f"No output contract for {phase}")

        for item in contract:
            if item.get("required", False):
                if not self._check_work_has_field(work_id, item["field"]):
                    return GateResult(
                        allowed=False,
                        reason=f"Missing required output: {item['field']} - {item.get('description', '')}"
                    )

        return GateResult(allowed=True, reason=f"Output contract satisfied for {phase}")

    def _check_work_has_field(self, work_id: str, field: str) -> bool:
        """Check if work item has a populated field.

        MVP: Returns True (actual field checking requires WorkEngine integration).
        Full implementation will read work file and check field presence.

        Args:
            work_id: Work item ID
            field: Field name to check

        Returns:
            True if field exists and is populated.
        """
        # MVP: Always return True - field validation is soft gate
        # Future: Use WorkEngine to read work file and verify field
        if self._work_engine is None:
            return True

        # TODO: Implement actual field checking when WorkEngine supports it
        return True
