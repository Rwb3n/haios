"""
Cycle phase auto-advancement for PostToolUse hook (WORK-168).

Follows session_end_actions.py pattern:
- Pure functions in lib/
- Fail-permissive (never raises)
- _default_project_root() for path derivation
- Testable without hook infrastructure
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Skill name -> CYCLE_PHASES key mapping
# Only lifecycle skills that have phase sequences are mapped.
# Ceremony skills (retro-cycle, close-work-cycle, etc.) are NOT mapped —
# they use CEREMONY_PHASES which is a separate concern.
SKILL_TO_CYCLE = {
    "implementation-cycle": "implementation-cycle",
    "investigation-cycle": "investigation-cycle",
    "plan-authoring-cycle": "plan-authoring-cycle",
}


def _default_project_root() -> Path:
    """Derive project root from this file's location.

    lib/ -> haios/ -> .claude/ -> project root.
    NOT Path.cwd() — hook subprocess cwd is not guaranteed.
    """
    return Path(__file__).parent.parent.parent.parent


def advance_cycle_phase(
    skill_name: str,
    project_root: Optional[Path] = None,
) -> bool:
    """Advance session_state to next phase after a lifecycle skill completes.

    Reads current phase from haios-status-slim.json, looks up next phase
    in CYCLE_PHASES, writes updated state. Appends to phase_history.

    Args:
        skill_name: Name of the completed skill (e.g., "implementation-cycle")
        project_root: Project root path. Defaults to derived path.

    Returns:
        True if phase was advanced, False if no advancement (unrecognized
        skill, already at last phase, missing file, cycle mismatch, or error).
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return False

        # Map skill name to cycle key
        cycle_key = SKILL_TO_CYCLE.get(skill_name)
        if cycle_key is None:
            return False

        # Get phase sequence
        # Import here to avoid circular imports in hook context
        _modules_dir = Path(__file__).parent.parent / "modules"
        if str(_modules_dir) not in sys.path:
            sys.path.insert(0, str(_modules_dir))
        from cycle_runner import CYCLE_PHASES

        phases = CYCLE_PHASES.get(cycle_key, [])
        if not phases:
            return False

        # Read current state
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        session_state = data.get("session_state", {})
        current_phase = session_state.get("current_phase")

        if current_phase is None:
            return False

        # Guard: active_cycle must match the skill being invoked (critique A5)
        active_cycle = session_state.get("active_cycle")
        if active_cycle != cycle_key:
            return False

        # Find next phase
        try:
            idx = phases.index(current_phase)
        except ValueError:
            return False  # Current phase not in sequence

        if idx >= len(phases) - 1:
            return False  # Already at last phase

        next_phase = phases[idx + 1]
        now = datetime.now().isoformat()

        # Update session_state (normalize to 6-field schema)
        session_state["current_phase"] = next_phase
        session_state["entered_at"] = now
        # Ensure phase_history exists (handles 4-field schema)
        history = session_state.setdefault("phase_history", [])
        history.append({"from": current_phase, "to": next_phase, "at": now})
        session_state.setdefault("active_queue", None)

        data["session_state"] = session_state
        slim_file.write_text(json.dumps(data, indent=4), encoding="utf-8")

        # Log governance event (fail-permissive)
        try:
            from governance_events import log_phase_transition

            work_id = session_state.get("work_id", "unknown")
            log_phase_transition(next_phase, work_id, "PostToolUse-auto")
        except Exception:
            pass  # Event logging failure is non-fatal

        return True

    except Exception:
        return False
