# generated: 2026-01-24
# System Auto: last updated on: 2026-01-26T20:11:29
"""
Coldstart Orchestrator for Configuration Arc.

CH-007: Wires IdentityLoader, SessionLoader, WorkLoader into unified coldstart.
E2-236: Adds orphan session detection before context loading phases.
Follows sibling loader patterns (identity_loader.py, session_loader.py).

Usage:
    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator()
    output = orch.run()  # Returns full coldstart context with [BREATHE] markers
"""
from pathlib import Path
from typing import Any, Callable, Dict, Optional
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


class ColdstartOrchestrator:
    """
    Orchestrate coldstart phases with breathing room.

    Uses coldstart.yaml config to run loaders in sequence with [BREATHE] markers.
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

    def run(self) -> str:
        """
        Execute all phases with breathing room.

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

        phases = self.config.get("phases", [])

        for phase in phases:
            phase_id = phase.get("id")
            loader_factory = self._loaders.get(phase_id)

            if loader_factory:
                output.append(f"[PHASE: {phase_id.upper()}]")
                try:
                    # Instantiate and call loader
                    loader = loader_factory()
                    output.append(loader.load())
                except Exception as e:
                    logger.warning(f"Loader {phase_id} failed: {e}")
                    output.append(f"(Loader {phase_id} failed: {e})")

                if phase.get("breathe", False):
                    output.append("\n[BREATHE]\n")
            else:
                logger.warning(f"Unknown loader: {phase_id}")

        output.append("[READY FOR SELECTION]")
        return "\n".join(output)


# CLI entry point for `just coldstart-orchestrator`
if __name__ == "__main__":
    orch = ColdstartOrchestrator()
    print(orch.run())
