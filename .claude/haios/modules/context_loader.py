# generated: 2026-01-04
# System Auto: last updated on: 2026-02-02T19:00:19
"""
ContextLoader Module (E2-254, WORK-008)

Programmatic bootstrap for HAIOS sessions. Provides:
- Config-driven, role-based context loading
- Session number computation
- Integration with WorkEngine and MemoryBridge

Interface:
- INPUT: role ("main" | "builder" | "validator"), trigger ("coldstart" | "session_recovery")
- OUTPUT: GroundedContext dataclass with loaded_context from registered loaders

WORK-008: Refactored for config-driven loader dispatch per L4 principles.
Config in haios.yaml defines role -> loaders mapping. Extensible without code changes.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type
import json
import logging
import yaml

# Import ConfigLoader for centralized paths (WORK-080)
try:
    from ..lib.config import ConfigLoader
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
    from config import ConfigLoader

logger = logging.getLogger(__name__)


@dataclass
class GroundedContext:
    """
    Result of context loading - role-based composition.

    WORK-008: Refactored for config-driven loading.
    - role: Which role loaded this context
    - loaded_context: Dict of loader_name -> content from registered loaders

    DEPRECATED fields (L0-L4) kept for backward compatibility during transition.
    """

    session_number: int
    prior_session: Optional[int] = None
    role: str = "main"  # WORK-008: Role that was loaded
    loaded_context: Dict[str, str] = field(default_factory=dict)  # WORK-008: loader_name -> content
    # DEPRECATED - kept for backward compat, will be empty when using role-based loading
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
    Bootstrap the agent with config-driven, role-based context grounding.

    WORK-008: Refactored for config-driven loader dispatch per L4 principles.
    - haios.yaml defines role -> loaders mapping
    - Loader registry is extensible without code changes
    - Role parameter enables selective loading

    Per INV-052 S17.3, ContextLoader:
    - Loads context via registered loaders based on role
    - Computes session number from status
    - Queries MemoryBridge for strategies
    - Gets ready work from WorkEngine
    """

    # WORK-080: Path constants moved to haios.yaml, accessed via ConfigLoader

    # Loader registry - extensible via config (WORK-008)
    _loader_registry: Dict[str, type] = {}

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
        self._config: Dict[str, Any] = {}
        self._register_default_loaders()
        self._load_config()

    def _register_default_loaders(self) -> None:
        """Register built-in loaders."""
        try:
            # Import from sibling lib directory
            import sys
            lib_path = str(self._project_root / ".claude" / "haios" / "lib")
            if lib_path not in sys.path:
                sys.path.insert(0, lib_path)
            from identity_loader import IdentityLoader
            self._loader_registry["identity"] = IdentityLoader
        except ImportError as e:
            logger.warning(f"Could not import IdentityLoader: {e}")

        try:
            # CH-005: Register SessionLoader for session context
            from session_loader import SessionLoader
            self._loader_registry["session"] = SessionLoader
        except ImportError as e:
            logger.warning(f"Could not import SessionLoader: {e}")

        try:
            # CH-006: Register WorkLoader for work context
            from work_loader import WorkLoader
            self._loader_registry["work"] = WorkLoader
        except ImportError as e:
            logger.warning(f"Could not import WorkLoader: {e}")

    def _load_config(self) -> None:
        """Load context config from haios.yaml (WORK-080: via ConfigLoader)."""
        config = ConfigLoader.get()
        config_path = self._project_root / config.get_path("haios_config") / "haios.yaml"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        except (FileNotFoundError, yaml.YAMLError) as e:
            logger.warning(f"Could not load config: {e}")
            self._config = {}

    def _get_loaders_for_role(self, role: str) -> List[str]:
        """
        Get loader names for role from config.

        Args:
            role: Role name (e.g., "main", "builder", "validator")

        Returns:
            List of loader names to use for this role

        Raises:
            ValueError: If role not found in config (and config has roles defined)
        """
        context_config = self._config.get("context", {})
        roles = context_config.get("roles", {})

        # Graceful degradation: if no config or no roles, return empty list
        # This allows backward compat with tests using tmp_path without config
        if not roles:
            logger.debug("No context.roles in config, using empty loader list")
            return []

        if role not in roles:
            available = list(roles.keys())
            raise ValueError(f"Unknown role: {role}. Available: {available}")
        return roles[role].get("loaders", [])

    def compute_session_number(self) -> Tuple[int, Optional[int]]:
        """
        Compute current and prior session from status JSON (WORK-080: via ConfigLoader).

        Returns:
            (current_session, prior_session) where prior may be None
        """
        config = ConfigLoader.get()
        status_path = self._project_root / config.get_path("status")
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

    def load_context(self, role: str = "main", trigger: str = "coldstart") -> GroundedContext:
        """
        Load context based on role from config.

        WORK-008: Config-driven, role-based loading per L4 principles.
        haios.yaml defines role -> loaders mapping. Each loader is invoked
        and its output stored in loaded_context dict.

        Args:
            role: Role name defining which loaders to use (default: "main")
            trigger: "coldstart" for full bootstrap, "session_recovery" for minimal

        Returns:
            GroundedContext with loaded_context from registered loaders

        Raises:
            ValueError: If role not found in config
        """
        session, prior = self.compute_session_number()

        # Load context via registered loaders per role (WORK-008)
        loaded_context: Dict[str, str] = {}
        for loader_name in self._get_loaders_for_role(role):
            loader_class = self._loader_registry.get(loader_name)
            if loader_class:
                try:
                    loaded_context[loader_name] = loader_class().load()
                except Exception as e:
                    logger.warning(f"Loader {loader_name} failed: {e}")
                    loaded_context[loader_name] = ""
            else:
                logger.warning(f"Loader {loader_name} not in registry")

        ctx = GroundedContext(
            session_number=session,
            prior_session=prior,
            role=role,
            loaded_context=loaded_context,
            # DEPRECATED: Still read manifesto for backward compat when no loaders
            l0_telos=self._read_manifesto_file("L0-telos.md") if not loaded_context else "",
            l1_principal=self._read_manifesto_file("L1-principal.md") if not loaded_context else "",
            l2_intent=self._read_manifesto_file("L2-intent.md") if not loaded_context else "",
            l3_requirements=self._read_manifesto_file("L3-requirements.md") if not loaded_context else "",
            l4_implementation=self._read_manifesto_file("L4-implementation.md") if not loaded_context else "",
            checkpoint_summary=self._get_latest_checkpoint(),
            strategies=self._get_strategies(trigger),
            ready_work=self._get_ready_work(),
        )
        return ctx

    def _read_manifesto_file(self, filename: str) -> str:
        """Read a manifesto file, return empty string on error (WORK-080: via ConfigLoader)."""
        config = ConfigLoader.get()
        path = self._project_root / config.get_path("manifesto") / filename
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
        # WORK-006: Use lib inside haios/ for portability
        import sys
        lib_path = str(Path(__file__).parent.parent / "lib")  # .claude/haios/lib
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)

        from status import generate_slim_status, generate_full_status

        if slim:
            return generate_slim_status()
        else:
            return generate_full_status()
