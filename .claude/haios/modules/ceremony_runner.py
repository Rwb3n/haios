# generated: 2026-02-11
# WORK-118: CeremonyRunner (CH-013 CeremonyLifecycleDistinction)
"""
CeremonyRunner Module (WORK-118, CH-013)

Thin wrapper for ceremony phase validation and invocation.
Delegates state-change enforcement to ceremony_context() from governance_layer.

Ceremonies produce state changes (WHEN). Lifecycles produce artifacts (WHAT).
Per REQ-CEREMONY-003: these are distinct concepts.

CeremonyRunner wraps existing ceremony_context() infrastructure (CH-012).
It does NOT replace CycleRunner — CycleRunner handles lifecycles.

Usage:
    from ceremony_runner import CeremonyRunner, CeremonyResult
    from governance_layer import GovernanceLayer

    runner = CeremonyRunner(governance=GovernanceLayer())
    phases = runner.get_ceremony_phases("close-work-cycle")
    # ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"]

    result = runner.invoke("close-work", work_id="WORK-118")
    # CeremonyResult(ceremony_id="close-work", work_id="WORK-118", ...)
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal

# Sibling import pattern (matches cycle_runner.py — E2-255 learning)
try:
    from .governance_layer import GovernanceLayer, ceremony_context
except ImportError:
    from governance_layer import GovernanceLayer, ceremony_context

# Import event logging from lib (matches cycle_runner.py pattern)
import sys
from pathlib import Path

_lib_path = Path(__file__).parent.parent / "lib"  # .claude/haios/lib
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from governance_events import log_phase_transition


# =============================================================================
# CeremonyResult — state-change output (distinct from LifecycleOutput)
# =============================================================================

@dataclass
class CeremonyResult:
    """Result of a ceremony invocation.

    Unlike LifecycleOutput (which represents artifact production),
    CeremonyResult represents state changes with side-effect tracking.
    """
    ceremony_id: str
    work_id: str
    side_effects: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: Literal["success", "failure"] = "success"


# =============================================================================
# CEREMONY_PHASES — extracted from CYCLE_PHASES (cycle_runner.py)
# =============================================================================

# Ceremony phase definitions
# These were previously mixed into CYCLE_PHASES in cycle_runner.py.
# Separated per REQ-CEREMONY-003: ceremonies are distinct from lifecycles.
CEREMONY_PHASES: Dict[str, List[str]] = {
    "close-work-cycle": ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"],
    "work-creation-cycle": ["VERIFY", "POPULATE", "READY"],
    "checkpoint-cycle": ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"],
    "observation-triage-cycle": ["SCAN", "TRIAGE", "PROMOTE"],
}


# =============================================================================
# CeremonyRunner — thin wrapper around ceremony_context
# =============================================================================

class CeremonyRunner:
    """Ceremony phase validator and invoker.

    Thin wrapper around ceremony_context() (from governance_layer.py, CH-012).
    Validates ceremony phases and delegates state-change enforcement to
    the existing ceremony boundary infrastructure.

    Does NOT replace CycleRunner — CycleRunner handles lifecycles,
    CeremonyRunner handles ceremonies.
    """

    def __init__(self, governance: GovernanceLayer):
        """Initialize CeremonyRunner with governance dependency.

        Args:
            governance: GovernanceLayer for gate checks
        """
        self._governance = governance

    def get_ceremony_phases(self, ceremony_id: str) -> List[str]:
        """Return ordered phases for a ceremony.

        Args:
            ceremony_id: Ceremony identifier (e.g., "close-work-cycle")

        Returns:
            List of phase names, or empty list if ceremony not found.
        """
        return CEREMONY_PHASES.get(ceremony_id, [])

    def invoke(self, ceremony: str, work_id: str, **inputs: Any) -> CeremonyResult:
        """Invoke ceremony within ceremony_context boundary.

        Wraps the ceremony in ceremony_context() for side-effect tracking
        and boundary enforcement (CH-012 infrastructure).

        Args:
            ceremony: Ceremony name (e.g., "close-work")
            work_id: Work item ID
            **inputs: Ceremony-specific inputs

        Returns:
            CeremonyResult with side effects logged

        Raises:
            CeremonyNestingError: If called within existing ceremony context
        """
        with ceremony_context(ceremony) as ctx:
            ctx.log_side_effect("ceremony_invoked", {
                "work_id": work_id,
                **inputs,
            })
            log_phase_transition(ceremony, work_id, "Hephaestus")
            return CeremonyResult(
                ceremony_id=ceremony,
                work_id=work_id,
                side_effects=[str(se) for se in ctx.side_effects],
            )
