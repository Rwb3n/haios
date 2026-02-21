# generated: 2026-01-24
# System Auto: last updated on: 2026-02-21T00:35:00
"""
Coldstart Orchestrator for Configuration Arc.

CH-007: Wires IdentityLoader, SessionLoader, WorkLoader into unified coldstart.
E2-236: Adds orphan session detection before context loading phases.
WORK-154: Adds epoch transition validation phase after loaders.
WORK-180: Adds EpochLoader, OperationsLoader, tiered coldstart per ADR-047.
Follows sibling loader patterns (identity_loader.py, session_loader.py).

Usage:
    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator()
    output = orch.run()          # Auto-detect tier
    output = orch.run(tier="full")  # Explicit tier
"""
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import re
import sys
import time
import yaml
import logging

logger = logging.getLogger(__name__)

# Path setup (same pattern as session_loader.py)
CONFIG_DIR = Path(__file__).parent.parent / "config"
DEFAULT_CONFIG = CONFIG_DIR / "coldstart.yaml"

# Import loaders (same pattern as sibling modules)
from identity_loader import IdentityLoader
from session_loader import SessionLoader
from work_loader import WorkLoader
from epoch_loader import EpochLoader
from operations_loader import OperationsLoader


class ColdstartOrchestrator:
    """
    Orchestrate coldstart phases with breathing room.

    Uses coldstart.yaml config to run loaders in sequence with [BREATHE] markers.
    WORK-180: Supports tiered coldstart (full/light/minimal) per ADR-047.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize with config file.

        Args:
            config_path: Path to coldstart.yaml. Default: standard location.
        """
        self.config_path = config_path or DEFAULT_CONFIG
        # Loader classes - will be instantiated when needed
        # Using callables to allow test mocking
        self._loaders: Dict[str, Callable] = {
            "identity": IdentityLoader,
            "session": SessionLoader,
            "work": WorkLoader,
            "epoch": EpochLoader,
            "operations": OperationsLoader,
        }
        self._load_config()

    def _load_config(self) -> None:
        """Load config from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            logger.warning(f"Config not found: {self.config_path}")
            # Default phases (graceful degradation per plan)
            # Critique A3: Keep at 3 phases — this is the missing-config fallback,
            # not the tiered-config path. Existing test asserts len == 3.
            self.config = {
                "phases": [
                    {"id": "identity", "breathe": True},
                    {"id": "session", "breathe": True},
                    {"id": "work", "breathe": False},
                ]
            }

    def _check_for_orphans(self) -> Optional[str]:
        """
        Check for orphan sessions and incomplete work (E2-236).

        Returns:
            Warning message if orphans found, else None
        """
        try:
            # Import from sibling module (same directory)
            from governance_events import detect_orphan_session, scan_incomplete_work, log_session_end

            project_root = Path(__file__).parent.parent.parent.parent
            warnings = []

            # Check for orphan session
            orphan = detect_orphan_session()
            if orphan:
                warnings.append("=== ORPHAN SESSION DETECTED ===")
                warnings.append(f"Session {orphan['orphan_session']} started but never ended.")
                warnings.append(f"Current session: {orphan['current_session']}")
                # Log synthetic end for orphan
                log_session_end(orphan['orphan_session'], "SYNTHETIC_RECOVERY")
                warnings.append(f"(Logged synthetic session-end for session {orphan['orphan_session']})")

            # Check for incomplete work transitions
            incomplete = scan_incomplete_work(project_root)
            if incomplete:
                warnings.append("=== INCOMPLETE WORK DETECTED ===")
                for item in incomplete:
                    warnings.append(f"- {item['id']}: stuck in '{item['incomplete_node']}'")

            return "\n".join(warnings) if warnings else None
        except Exception as e:
            logger.warning(f"Orphan detection failed: {e}")
            return None

    def _make_work_status_fn(self):
        """Create work status lookup for staleness detection (WORK-156).

        Note: WorkEngine is in modules/, ColdstartOrchestrator is in lib/.
        Requires sys.path addition for cross-directory import (A2 critique fix).
        WorkEngine requires GovernanceLayer argument (A1 critique fix).

        Returns:
            Callable that takes WORK-ID and returns status string, or None on failure.
        """
        try:
            modules_path = str(Path(__file__).parent.parent / "modules")
            if modules_path not in sys.path:
                sys.path.insert(0, modules_path)
            from work_engine import WorkEngine
            from governance_layer import GovernanceLayer
            governance = GovernanceLayer()
            engine = WorkEngine(governance=governance)

            def lookup(work_id: str):
                work = engine.get_work(work_id)
                return work.status if work else None
            return lookup
        except Exception as e:
            logger.warning(f"Work status lookup unavailable: {e}")
            return None

    # =========================================================================
    # WORK-180: Tier Resolution (ADR-047)
    # =========================================================================

    def _find_latest_checkpoint(self) -> Optional[Path]:
        """Find most recent checkpoint file (reuses SessionLoader pattern)."""
        try:
            from config import ConfigLoader
            project_root = Path(__file__).parent.parent.parent.parent
            checkpoint_dir = project_root / ConfigLoader.get().get_path("checkpoints")
        except Exception:
            checkpoint_dir = Path(__file__).parent.parent.parent.parent / "docs" / "checkpoints"

        if not checkpoint_dir.exists():
            return None
        checkpoints = [cp for cp in checkpoint_dir.glob("*.md") if cp.name != "README.md"]
        if not checkpoints:
            return None

        def _session_number(path: Path) -> tuple:
            session_match = re.search(r"SESSION-(\d+)", path.name, re.IGNORECASE)
            session_num = int(session_match.group(1)) if session_match else 0
            date_match = re.match(r"(\d{4}-\d{2}-\d{2}-\d{2})", path.name)
            date_prefix = date_match.group(1) if date_match else ""
            return (session_num, date_prefix, path.name)

        return max(checkpoints, key=_session_number)

    def _get_checkpoint_age_hours(self) -> Optional[float]:
        """Get age of latest checkpoint in hours from file mtime."""
        cp = self._find_latest_checkpoint()
        if cp is None:
            return None
        try:
            mtime = cp.stat().st_mtime
            age_seconds = time.time() - mtime
            return age_seconds / 3600.0
        except Exception:
            return None

    def _has_pending_work(self) -> bool:
        """Check if latest checkpoint has pending work items. (Critique A1 fix)"""
        cp = self._find_latest_checkpoint()
        if cp is None:
            return False
        try:
            content = cp.read_text(encoding="utf-8")
            if not content.strip().startswith("---"):
                return False
            match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if not match:
                return False
            fm = yaml.safe_load(match.group(1)) or {}
            return bool(fm.get("pending", []))
        except Exception:
            return False

    def _resolve_tier(self, tier: str) -> str:
        """
        Resolve tier from explicit or auto-detection (ADR-047).

        Auto-detection heuristic:
        1. Stale checkpoint (>max_age_hours) -> full
        2. Fresh checkpoint with pending work -> light
        3. Default -> full

        Args:
            tier: "auto", "full", "light", or "minimal"

        Returns:
            Resolved tier name.
        """
        if tier != "auto":
            return tier

        age = self._get_checkpoint_age_hours()
        max_age = self.config.get("tier_detection", {}).get("max_age_hours", 24)

        if age is None or age > max_age:
            return "full"
        if self._has_pending_work():
            return "light"
        return "full"

    def _get_phases_for_tier(self, tier: str) -> List[Dict]:
        """
        Get phase list for resolved tier.

        Looks up tier definition in config. Falls back to all phases
        if tier is not found or has no phases defined.

        Args:
            tier: Resolved tier name.

        Returns:
            List of phase dicts (each has 'id' and optionally 'breathe').
        """
        tiers = self.config.get("tiers", {})
        tier_def = tiers.get(tier, {})
        phase_ids = tier_def.get("phases", [])

        if not phase_ids:
            # Fallback to all phases in config
            return self.config.get("phases", [])

        # Build phase entries from phase_ids
        all_phases = {p["id"]: p for p in self.config.get("phases", [])}
        return [all_phases[pid] for pid in phase_ids if pid in all_phases]

    # =========================================================================
    # Main Run
    # =========================================================================

    def run(self, tier: str = "auto") -> str:
        """
        Execute coldstart phases with breathing room.

        WORK-180: Supports tiered execution per ADR-047.

        Args:
            tier: "auto" (default), "full", "light", or "minimal".
                  "auto" uses checkpoint-based heuristic.

        Returns:
            Full coldstart context string with [PHASE:], [BREATHE], and
            [READY FOR SELECTION] markers.
        """
        output = []

        # PHASE 0: Orphan detection (E2-236)
        recovery_result = self._check_for_orphans()
        if recovery_result:
            output.append("[PHASE: RECOVERY]")
            output.append(recovery_result)
            output.append("\n[BREATHE]\n")

        # WORK-180: Tier resolution (ADR-047)
        resolved_tier = self._resolve_tier(tier)
        phases = self._get_phases_for_tier(resolved_tier)

        for phase in phases:
            phase_id = phase.get("id")
            loader_factory = self._loaders.get(phase_id)

            if loader_factory:
                output.append(f"[PHASE: {phase_id.upper()}]")
                try:
                    # WORK-156: Wire work_status_fn for session loader
                    if phase_id == "session":
                        try:
                            loader = loader_factory(work_status_fn=self._make_work_status_fn())
                        except TypeError:
                            # Graceful fallback if factory doesn't accept work_status_fn (e.g., mocks)
                            loader = loader_factory()
                    else:
                        loader = loader_factory()
                    output.append(loader.load())
                except Exception as e:
                    logger.warning(f"Loader {phase_id} failed: {e}")
                    output.append(f"(Loader {phase_id} failed: {e})")

                if phase.get("breathe", False):
                    output.append("\n[BREATHE]\n")
            else:
                logger.warning(f"Unknown loader: {phase_id}")

        # WORK-154: Epoch transition validation (after all loaders)
        # Only run for full tier — light/minimal skip epoch context
        if resolved_tier == "full":
            validation_output = self._run_epoch_validation()
            if validation_output:
                output.append("[PHASE: VALIDATION]")
                output.append(validation_output)
                output.append("\n[BREATHE]\n")

        output.append("[READY FOR SELECTION]")
        return "\n".join(output)

    def _run_epoch_validation(self) -> Optional[str]:
        """
        Run epoch transition validation (WORK-154).

        Validates queue config vs active_arcs and EPOCH.md status drift.
        Returns formatted warnings or None if clean.
        Surfaces error message on failure (Critique A8).
        """
        try:
            from epoch_validator import EpochValidator
            validator = EpochValidator()
            result = validator.validate()
            return result if result else None
        except Exception as e:
            logger.warning(f"Epoch validation failed: {e}")
            return f"(Epoch validation unavailable: {e})"


# CLI entry point for `just coldstart-orchestrator`
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Coldstart Orchestrator (ADR-047)")
    parser.add_argument("--tier", default="auto",
                        choices=["auto", "full", "light", "minimal"],
                        help="Coldstart tier (default: auto-detect)")
    parser.add_argument("--extend", nargs="*", default=None,
                        help="Extend with additional phases (not yet implemented)")
    args = parser.parse_args()

    if args.extend is not None:
        print("[EXTEND] --extend is not yet implemented. Use --tier instead.")
        sys.exit(0)

    orch = ColdstartOrchestrator()
    print(orch.run(tier=args.tier))
