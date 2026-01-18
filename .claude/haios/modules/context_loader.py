# generated: 2026-01-04
# System Auto: last updated on: 2026-01-18T10:42:20
"""
ContextLoader Module (E2-254)

Programmatic bootstrap for HAIOS sessions. Provides:
- L0-L4 context loading with typed return
- Session number computation
- Integration with WorkEngine and MemoryBridge

Interface:
- INPUT: trigger ("coldstart" | "session_recovery")
- OUTPUT: GroundedContext dataclass with L0-L4 manifesto content
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class GroundedContext:
    """Result of context loading - L0-L4 grounding."""

    session_number: int
    prior_session: Optional[int] = None
    l0_telos: str = ""           # WHY - Mission, Prime Directive
    l1_principal: str = ""       # WHO - Operator constraints
    l2_intent: str = ""          # WHAT - Goals, trade-offs
    l3_requirements: str = ""    # HOW - Principles, boundaries
    l4_implementation: str = ""  # WHAT to build - Architecture
    checkpoint_summary: str = ""
    strategies: List[Dict[str, Any]] = field(default_factory=list)
    ready_work: List[str] = field(default_factory=list)


class ContextLoader:
    """
    Bootstrap the agent with L0-L4 context grounding.

    Per INV-052 S17.3, ContextLoader:
    - Loads manifesto files (L0-L4)
    - Computes session number from status
    - Queries MemoryBridge for strategies
    - Gets ready work from WorkEngine
    """

    MANIFESTO_PATH = Path(".claude/haios/manifesto")
    STATUS_PATH = Path(".claude/haios-status.json")

    def __init__(
        self,
        work_engine=None,
        memory_bridge=None,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize ContextLoader with optional dependencies.

        Args:
            work_engine: WorkEngine instance for ready work
            memory_bridge: MemoryBridge instance for strategy query
            project_root: Project root path (default: auto-detect)
        """
        self._work_engine = work_engine
        self._memory_bridge = memory_bridge
        self._project_root = project_root or Path(__file__).parent.parent.parent.parent

    def compute_session_number(self) -> Tuple[int, Optional[int]]:
        """
        Compute current and prior session from status JSON.

        Returns:
            (current_session, prior_session) where prior may be None
        """
        status_path = self._project_root / self.STATUS_PATH
        try:
            with open(status_path, "r", encoding="utf-8") as f:
                status = json.load(f)
            # Try session_delta first (new format), fallback to last_session
            session_delta = status.get("session_delta", {})
            if session_delta:
                current = session_delta.get("current_session", 1)
                prior = session_delta.get("prior_session")
                return (current + 1, current)  # Next session, current becomes prior
            # Fallback to legacy format
            last_session = status.get("last_session", 0)
            return (last_session + 1, last_session if last_session > 0 else None)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read status: {e}")
            return (1, None)

    def load_context(self, trigger: str = "coldstart") -> GroundedContext:
        """
        Load L0-L4 context and session state.

        Args:
            trigger: "coldstart" for full bootstrap, "session_recovery" for minimal

        Returns:
            GroundedContext with all grounding fields populated
        """
        session, prior = self.compute_session_number()

        ctx = GroundedContext(
            session_number=session,
            prior_session=prior,
            l0_telos=self._read_manifesto_file("L0-telos.md"),
            l1_principal=self._read_manifesto_file("L1-principal.md"),
            l2_intent=self._read_manifesto_file("L2-intent.md"),
            l3_requirements=self._read_manifesto_file("L3-requirements.md"),
            l4_implementation=self._read_manifesto_file("L4-implementation.md"),
            checkpoint_summary=self._get_latest_checkpoint(),
            strategies=self._get_strategies(trigger),
            ready_work=self._get_ready_work(),
        )
        return ctx

    def _read_manifesto_file(self, filename: str) -> str:
        """Read a manifesto file, return empty string on error."""
        path = self._project_root / self.MANIFESTO_PATH / filename
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"Manifesto file not found: {filename}")
            return ""

    def _get_latest_checkpoint(self) -> str:
        """Get summary from latest checkpoint file."""
        checkpoint_dir = self._project_root / "docs" / "checkpoints"
        try:
            checkpoints = sorted(checkpoint_dir.glob("*.md"), reverse=True)
            # Filter out README.md
            checkpoints = [cp for cp in checkpoints if cp.name != "README.md"]
            if checkpoints:
                return checkpoints[0].read_text(encoding="utf-8")[:2000]
        except Exception as e:
            logger.warning(f"Could not read checkpoint: {e}")
        return ""

    def _get_strategies(self, trigger: str) -> List[Dict[str, Any]]:
        """Query MemoryBridge for session strategies."""
        if not self._memory_bridge:
            return []
        try:
            mode = "session_recovery" if trigger == "coldstart" else "semantic"
            result = self._memory_bridge.query("session strategies learnings", mode=mode)
            return result.concepts[:5] if result.concepts else []
        except Exception as e:
            logger.warning(f"Strategy query failed: {e}")
            return []

    def _get_ready_work(self) -> List[str]:
        """Get ready work items from WorkEngine."""
        if not self._work_engine:
            return []
        try:
            ready = self._work_engine.get_ready()
            return [w.id for w in ready[:10]]
        except Exception as e:
            logger.warning(f"Ready work query failed: {e}")
            return []

    def generate_status(self, slim: bool = True) -> Dict[str, Any]:
        """
        Generate status dict by delegating to lib/status.py.

        Args:
            slim: If True (default), generate slim status (~50 lines).
                  If False, generate full status (includes live_files, templates).

        Returns:
            Status dict with keys: generated, milestone, session_delta,
            work_cycle, active_work, blocked_items, counts, infrastructure.

        Note:
            This method delegates to existing lib/status.py functions.
            The delegation pattern maintains backward compatibility while
            enabling module-first imports per Epoch 2.2.
        """
        import sys
        lib_path = str(self._project_root / ".claude" / "lib")
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)

        from status import generate_slim_status, generate_full_status

        if slim:
            return generate_slim_status()
        else:
            return generate_full_status()
