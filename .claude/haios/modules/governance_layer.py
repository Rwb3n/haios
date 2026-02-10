# generated: 2026-01-03
# System Auto: last updated on: 2026-02-09T19:15:53
"""
GovernanceLayer Module (E2-240)

Stateless policy enforcement for HAIOS. Provides:
- Gate checks (DoD, preflight, observation)
- Transition validation (DAG node constraints)
- Handler loading (from config)
- Event routing (to registered handlers)

L4 Invariants:
- MUST NOT modify work files directly (that's WorkEngine's job)
- MUST log all gate decisions for audit
- MUST be stateless (no internal state between calls)

Usage:
    from governance_layer import GovernanceLayer, GateResult

    layer = GovernanceLayer()
    result = layer.check_gate("dod", {"work_id": "E2-240", "tests_pass": True})
    if result.allowed:
        print("Gate passed")
    else:
        print(f"Gate blocked: {result.reason}")
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List

import yaml

# Import existing governance_events for logging
# WORK-006: Use lib inside haios/ for portability
import sys

_lib_path = Path(__file__).parent.parent / "lib"  # .claude/haios/lib (sibling to modules/)
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from governance_events import log_validation_outcome


@dataclass
class GateResult:
    """Result of a gate check.

    Attributes:
        allowed: Whether the gate permits the operation
        reason: Human-readable explanation
        degraded: Whether governance is in degraded state (handler failures)
    """

    allowed: bool
    reason: str
    degraded: bool = False  # E2-248: Indicates governance system degradation


# Valid DAG transitions (from -> allowed_to_nodes)
# Based on work item lifecycle: backlog -> discovery/plan -> implement -> close -> complete
VALID_TRANSITIONS: Dict[str, List[str]] = {
    "backlog": ["discovery", "plan"],
    "discovery": ["backlog", "plan"],
    "plan": ["backlog", "implement"],
    "implement": ["plan", "close"],
    "close": ["implement", "complete"],  # E2-250: Allow backtrack for rework
    "complete": [],  # Terminal node - no transitions out
}


class GovernanceLayer:
    """
    Stateless policy enforcement module.

    Provides gate checking, transition validation, handler loading,
    and event routing for HAIOS governance.
    """

    def __init__(self):
        """Initialize with empty handler registry."""
        self._handlers: Dict[str, List[Callable]] = {}

    def check_gate(self, gate_id: str, context: Dict[str, Any]) -> GateResult:
        """
        Check if gate allows operation.

        Args:
            gate_id: Gate identifier (e.g., "dod", "preflight", "observation")
            context: Context dict with work_id and relevant state

        Returns:
            GateResult with allowed flag and reason

        Side Effects:
            Logs decision via governance_events.log_validation_outcome()
        """
        work_id = context.get("work_id", "unknown")

        # Dispatch to specific gate check
        if gate_id == "dod":
            result = self._check_dod_gate(context)
        elif gate_id == "preflight":
            result = self._check_preflight_gate(context)
        elif gate_id == "observation":
            result = self._check_observation_gate(context)
        else:
            result = GateResult(allowed=True, reason=f"Unknown gate '{gate_id}', allowing")

        # Log decision for audit (L4 invariant)
        log_validation_outcome(
            gate=gate_id,
            work_id=work_id,
            result="pass" if result.allowed else "block",
            reason=result.reason,
        )

        return result

    def _check_dod_gate(self, context: Dict[str, Any]) -> GateResult:
        """Check Definition of Done criteria."""
        tests_pass = context.get("tests_pass", False)
        why_captured = context.get("why_captured", False)
        docs_current = context.get("docs_current", False)

        if not tests_pass:
            return GateResult(allowed=False, reason="DoD incomplete: tests not passing")
        if not why_captured:
            return GateResult(allowed=False, reason="DoD incomplete: WHY not captured")
        if not docs_current:
            return GateResult(allowed=False, reason="DoD incomplete: docs not current")

        return GateResult(allowed=True, reason="DoD complete")

    def _check_preflight_gate(self, context: Dict[str, Any]) -> GateResult:
        """Check preflight criteria (plan readiness)."""
        plan_approved = context.get("plan_approved", False)
        file_count = context.get("file_count", 0)

        if not plan_approved:
            return GateResult(allowed=False, reason="Preflight: plan not approved")
        if file_count > 3:
            return GateResult(
                allowed=False,
                reason=f"Preflight: {file_count} files exceeds 3-file threshold",
            )

        return GateResult(allowed=True, reason="Preflight passed")

    def _check_observation_gate(self, context: Dict[str, Any]) -> GateResult:
        """Check observation pending threshold."""
        pending_count = context.get("pending_observations", 0)
        max_count = context.get("max_observations", 10)

        if pending_count > max_count:
            return GateResult(
                allowed=False,
                reason=f"Observation gate: {pending_count} pending > {max_count} threshold",
            )

        return GateResult(allowed=True, reason="Observation threshold OK")

    def validate_transition(self, from_node: str, to_node: str) -> bool:
        """
        Validate DAG transition is allowed.

        Args:
            from_node: Current node (e.g., "backlog")
            to_node: Target node (e.g., "discovery")

        Returns:
            True if transition is valid, False otherwise
        """
        allowed = VALID_TRANSITIONS.get(from_node, [])
        return to_node in allowed

    def validate_queue_transition(
        self, work_id: str, to_position: str, work_engine: Any = None
    ) -> "GateResult":
        """
        Validate queue position transition is allowed (CH-009).

        Args:
            work_id: Work item ID
            to_position: Target queue position
            work_engine: WorkEngine instance (to read current position)

        Returns:
            GateResult with allowed flag and reason
        """
        from work_engine import is_valid_queue_transition

        work = work_engine.get_work(work_id) if work_engine else None
        if work is None:
            result = GateResult(
                allowed=False, reason=f"Work item {work_id} not found"
            )
        else:
            from_pos = work.queue_position

            if from_pos == to_position:
                # No-op: already at target position
                result = GateResult(
                    allowed=True, reason=f"No-op: already at {to_position}"
                )
            elif is_valid_queue_transition(from_pos, to_position):
                result = GateResult(
                    allowed=True,
                    reason=f"Valid transition: {from_pos} -> {to_position}",
                )
            else:
                result = GateResult(
                    allowed=False,
                    reason=f"Invalid queue transition: {from_pos} -> {to_position}",
                )

        log_validation_outcome(
            gate="queue_transition",
            work_id=work_id,
            result="pass" if result.allowed else "block",
            reason=result.reason,
        )

        return result

    def load_handlers(self, config_path: str) -> Dict[str, Any]:
        """
        Load handler registry from config file.

        Args:
            config_path: Path to components.yaml

        Returns:
            Dict with handler registries (hooks, skills, agents)
        """
        path = Path(config_path)
        if not path.exists():
            return {}

        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            self._handlers = self._parse_handlers(config)
            return config
        except Exception as e:
            # E2-248: Log exception for visibility instead of silent failure
            import logging

            logging.warning(f"GovernanceLayer: Failed to load handlers from {config_path}: {e}")
            return {}

    def _parse_handlers(self, config: Dict[str, Any]) -> Dict[str, List[Callable]]:
        """Parse handler config into callable registry."""
        # For MVP, just store the config structure
        # Future: resolve handler paths to callables
        return {}

    def on_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Route event to registered handlers.

        Args:
            event_type: Event type (e.g., "work_transition", "gate_decision")
            payload: Event payload dict

        Side Effects:
            Calls registered handlers (may fail silently)
        """
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                # E2-248: Log exception for visibility instead of silent failure
                import logging

                logging.warning(f"GovernanceLayer: Handler failed for {event_type}: {e}")
                # Continue with other handlers

    # =========================================================================
    # E2-252: Template Validation and Scaffolding
    # =========================================================================

    def validate_template(self, file_path: str) -> dict:
        """
        Validate a template file against its schema.

        Delegates to .claude/lib/validate.validate_template().

        Args:
            file_path: Path to template file

        Returns:
            Validation result dict with is_valid, errors, warnings, etc.
        """
        from validate import validate_template as _validate_template

        return _validate_template(file_path)

    def scaffold_template(
        self,
        template: str,
        *,
        output_path: str = None,
        backlog_id: str = None,
        title: str = None,
        variables: dict = None,
    ) -> str:
        """
        Scaffold a new document from template.

        Delegates to .claude/lib/scaffold.scaffold_template().

        Args:
            template: Template type (checkpoint, implementation_plan, etc.)
            output_path: Optional explicit output path
            backlog_id: Backlog item ID
            title: Document title
            variables: Additional template variables

        Returns:
            Path to created file.
        """
        from scaffold import scaffold_template as _scaffold_template

        return _scaffold_template(
            template=template,
            output_path=output_path,
            backlog_id=backlog_id,
            title=title,
            variables=variables,
        )

    # =========================================================================
    # E2-260: Toggle Access
    # =========================================================================

    def get_toggle(self, name: str, default: Any = None) -> Any:
        """
        Get governance toggle value by name.

        Delegates to lib/config.ConfigLoader.toggles.

        Args:
            name: Toggle name (e.g., "block_powershell")
            default: Default value if toggle not found

        Returns:
            Toggle value from haios.yaml toggles section, or default.
        """
        from config import ConfigLoader

        return ConfigLoader.get().toggles.get(name, default)

    # =========================================================================
    # E2.4 CH-004: Governed Activities (State-Aware Governance)
    # =========================================================================

    def get_activity_state(self) -> str:
        """
        Get current ActivityMatrix state from cycle/phase.

        Uses `just get-cycle` to get current cycle state, maps to ActivityMatrix state.

        Returns:
            State name: EXPLORE, DESIGN, PLAN, DO, CHECK, or DONE
            Defaults to EXPLORE on failure (fail-permissive per CH-002)
        """
        import subprocess

        try:
            result = subprocess.run(
                ["just", "get-cycle"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(Path(__file__).parent.parent.parent.parent),  # Project root
            )
            cycle_info = result.stdout.strip()

            if not cycle_info:
                return "EXPLORE"  # No cycle = discovery mode

            # Parse "cycle/phase/work_id"
            parts = cycle_info.split("/")
            if len(parts) < 2:
                return "EXPLORE"

            cycle, phase = parts[0], parts[1]

            # Load phase-to-state mapping
            matrix = self._load_activity_matrix()
            mapping = matrix.get("phase_to_state", {})
            key = f"{cycle}/{phase}"

            return mapping.get(key, "EXPLORE")

        except Exception:
            return "EXPLORE"  # Fail-permissive

    def map_tool_to_primitive(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Map Claude Code tool name to ActivityMatrix primitive.

        Args:
            tool_name: Tool name (e.g., "AskUserQuestion", "Read", "Bash")
            tool_input: Tool input dict (for context-specific mapping)

        Returns:
            Primitive name (e.g., "user-query", "file-read")
        """
        # Direct mappings
        TOOL_TO_PRIMITIVE = {
            "AskUserQuestion": "user-query",
            "Read": "file-read",
            "Write": "file-write",
            "Edit": "file-edit",
            "Glob": "file-search",
            "Grep": "content-search",
            "Bash": "shell-execute",
            "WebFetch": "web-fetch",
            "WebSearch": "web-search",
            "Task": "task-spawn",
            "Skill": "skill-invoke",
            "NotebookEdit": "notebook-edit",
            "EnterPlanMode": "plan-enter",
            "ExitPlanMode": "plan-exit",
            "ListMcpResourcesTool": "mcp-list",
            "ReadMcpResourceTool": "mcp-read",
        }

        # MCP tools
        if tool_name.startswith("mcp__haios-memory__"):
            if "search" in tool_name:
                return "memory-search"
            if "ingest" in tool_name or "store" in tool_name:
                return "memory-store"
            if "schema" in tool_name:
                return "schema-query"
            if "db_query" in tool_name:
                return "db-query"

        return TOOL_TO_PRIMITIVE.get(tool_name, "unknown")

    def check_activity(
        self, primitive: str, state: str, context: Dict[str, Any]
    ) -> GateResult:
        """
        Check if activity is allowed in current state.

        Args:
            primitive: The primitive being invoked (e.g., "user-query")
            state: Current ActivityMatrix state (e.g., "DO")
            context: Additional context (file_path, skill_name, etc.)

        Returns:
            GateResult with allowed flag and reason message
        """
        matrix = self._load_activity_matrix()
        rules = matrix.get("rules", {})

        # Look up rule for (primitive, state)
        primitive_rules = rules.get(primitive, {})

        # Check _all_states shorthand first
        if "_all_states" in primitive_rules:
            rule = primitive_rules["_all_states"]
        elif state in primitive_rules:
            rule = primitive_rules[state]
        else:
            # Unknown primitive or state - use default (fail-open per CH-003)
            default = matrix.get("default_action", "allow")
            return GateResult(
                allowed=True, reason=f"Unknown primitive '{primitive}', defaulting to {default}"
            )

        # Evaluate action
        action = rule.get("action", "allow")
        message = rule.get("message", "")

        if action == "allow":
            return GateResult(allowed=True, reason="Activity allowed")

        if action == "warn":
            return GateResult(allowed=True, reason=message)

        if action == "block":
            return GateResult(allowed=False, reason=message)

        if action == "redirect":
            redirect_to = rule.get("redirect_to", "alternative")
            return GateResult(allowed=False, reason=message or f"Use {redirect_to} instead")

        return GateResult(allowed=True, reason="Activity allowed")

    def _check_skill_restriction(
        self, skill_name: str, state: str
    ) -> "GateResult | None":
        """
        Check if skill is allowed in current state.

        Args:
            skill_name: Name of skill being invoked
            state: Current ActivityMatrix state

        Returns:
            None if allowed, GateResult if blocked
        """
        import fnmatch

        matrix = self._load_activity_matrix()
        restrictions = matrix.get("skill_restrictions", {}).get(state, {})

        if not restrictions:
            return None

        allowed = restrictions.get("allowed", [])
        blocked = restrictions.get("blocked", [])
        block_message = restrictions.get("block_message", "Skill not allowed in this state")

        # Check explicit allow list
        for pattern in allowed:
            if fnmatch.fnmatch(skill_name, pattern):
                return None

        # Check blocked list
        for pattern in blocked:
            if fnmatch.fnmatch(skill_name, pattern):
                return GateResult(
                    allowed=False, reason=block_message.format(skill=skill_name)
                )

        return None  # Default: allow if not blocked

    def _load_activity_matrix(self) -> dict:
        """Load and cache activity_matrix.yaml."""
        # Use instance attribute for cache (allows test isolation)
        if hasattr(self, "_activity_matrix_cache") and self._activity_matrix_cache is not None:
            return self._activity_matrix_cache

        config_path = Path(__file__).parent.parent / "config" / "activity_matrix.yaml"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                self._activity_matrix_cache = yaml.safe_load(f) or {}
        else:
            self._activity_matrix_cache = {"default_action": "allow", "rules": {}}

        return self._activity_matrix_cache


# =========================================================================
# CH-012: Ceremony Context Manager (Side-Effect Boundaries)
# =========================================================================

import logging as _logging
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from typing import Optional

# Context variable for ceremony context (A1: contextvars over threading.local for async safety)
_ceremony_context_var: ContextVar[Optional["CeremonyContext"]] = ContextVar(
    "ceremony_context", default=None
)


class CeremonyRequiredError(Exception):
    """Raised when state change attempted outside ceremony context in block mode."""
    pass


class CeremonyNestingError(Exception):
    """Raised when ceremony_context opened within existing context."""
    pass


@dataclass
class CeremonyContext:
    """Active ceremony context with side-effect tracking.

    Attributes:
        ceremony_name: Name of the active ceremony
        side_effects: List of recorded side effects
    """
    ceremony_name: str
    side_effects: list = dataclass_field(default_factory=list)

    def log_side_effect(self, effect: str, details: dict = None) -> None:
        """Record a side effect within this ceremony."""
        self.side_effects.append({
            "effect": effect,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        })

    def execute_step(self, step_name: str, **kwargs) -> None:
        """Execute a ceremony step (composition, not nesting)."""
        self.log_side_effect(f"step:{step_name}", kwargs)


@contextmanager
def ceremony_context(ceremony_name: str):
    """Context manager for ceremony boundaries.

    All state changes within this context are logged.
    Nesting is forbidden (composition via execute_step instead).

    Args:
        ceremony_name: Name of the ceremony (e.g., "close-work")

    Yields:
        CeremonyContext with log_side_effect and execute_step methods

    Raises:
        CeremonyNestingError: If called within existing ceremony context
    """
    if in_ceremony_context():
        raise CeremonyNestingError(
            f"Cannot nest ceremony '{ceremony_name}' inside "
            f"'{_get_current_ceremony()}'. Use execute_step() for composition."
        )

    ctx = CeremonyContext(ceremony_name=ceremony_name)
    _set_ceremony_context(ctx)

    _log_ceremony_event({
        "type": "CeremonyStart",
        "ceremony": ceremony_name,
        "timestamp": datetime.now().isoformat(),
    })

    try:
        yield ctx
    finally:
        _log_ceremony_event({
            "type": "CeremonyEnd",
            "ceremony": ceremony_name,
            "side_effects": len(ctx.side_effects),
            "timestamp": datetime.now().isoformat(),
        })
        _clear_ceremony_context()


def in_ceremony_context() -> bool:
    """Check if currently within a ceremony context."""
    return _ceremony_context_var.get() is not None


def _get_current_ceremony() -> str:
    """Get name of current ceremony (or empty string)."""
    ctx = _ceremony_context_var.get()
    return ctx.ceremony_name if ctx else ""


def _set_ceremony_context(ctx: CeremonyContext) -> None:
    """Set ContextVar ceremony context."""
    _ceremony_context_var.set(ctx)


def _clear_ceremony_context() -> None:
    """Clear ContextVar ceremony context."""
    _ceremony_context_var.set(None)


def check_ceremony_required(operation: str) -> None:
    """Check if operation requires ceremony context.

    Public function (A2: crosses module boundary to work_engine.py).
    Enforcement mode from haios.yaml toggles.ceremony_context_enforcement:
    - 'warn': Log warning, allow operation
    - 'block': Raise CeremonyRequiredError

    Args:
        operation: Name of the operation being attempted (e.g., "close")
    """
    if in_ceremony_context():
        return  # Inside ceremony, allowed

    mode = _get_ceremony_enforcement()
    message = f"State change '{operation}' outside ceremony context"

    if mode == "block":
        raise CeremonyRequiredError(message)
    else:
        # Warn mode: log but allow
        _logging.warning(f"GovernanceLayer: {message}")


def _get_ceremony_enforcement() -> str:
    """Read ceremony_context_enforcement toggle via ConfigLoader. Default: 'warn'.

    Uses ConfigLoader (A5: no raw file I/O, respects REQ-CONFIG-001).
    """
    try:
        from config import ConfigLoader
        return ConfigLoader.get().toggles.get("ceremony_context_enforcement", "warn")
    except Exception:
        return "warn"


def _log_ceremony_event(event: dict) -> None:
    """Log ceremony event to governance-events.jsonl."""
    try:
        from governance_events import _append_event
        _append_event(event)
    except ImportError:
        pass  # Fail-permissive if events module unavailable
