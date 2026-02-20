# generated: 2026-02-20
"""
Critique injection for PreToolUse hook (WORK-169).

Pure function to compute tier-appropriate critique guidance for
inhale-to-exhale lifecycle transitions.

Pattern: session_end_actions.py / tier_detector.py (fail-permissive,
_default_project_root, no exceptions escape).
"""
import json
import sys
from pathlib import Path
from typing import Optional


# Inhale: gathering, exploring, planning, specifying (input phases)
INHALE_PHASES = {"EXPLORE", "PLAN", "DESIGN", "SCAN"}
# Exhale: committing, executing, producing, validating (output phases)
EXHALE_PHASES = {
    "DO", "HYPOTHESIZE", "CHECK", "DONE", "SPECIFY",
    "ASSESS", "RANK", "COMMIT", "VERIFY", "JUDGE", "REPORT",
}

# Skill-to-lifecycle mapping: which skills trigger transition detection.
# Only includes skills tracked by cycle_state.py SKILL_TO_CYCLE (PostToolUse
# writes phase data for these). design-review-validation excluded: not in
# SKILL_TO_CYCLE, so phase data would be stale (critique A2).
TRANSITION_SKILLS = {
    "implementation-cycle",
    "investigation-cycle",
    "plan-authoring-cycle",
}

# Tier -> injection content
TIER_INJECTIONS = {
    "trivial": None,  # No injection
    "small": (
        "[CRITIQUE CHECKPOINT] Before proceeding to the next phase, verify:\n"
        "- [ ] All acceptance criteria are achievable with current design\n"
        "- [ ] Source files referenced in WORK.md exist and are correct\n"
        "- [ ] No implicit assumptions about interfaces or data formats\n"
        "- [ ] Edge cases identified (empty inputs, missing files, permission errors)\n"
        "- [ ] Fail-permissive pattern applied where appropriate"
    ),
    "standard": (
        "[CRITIQUE REQUIRED] MUST invoke critique-agent before proceeding:\n"
        "Task(subagent_type='critique-agent', model='sonnet', "
        "prompt='Critique plan: docs/work/active/{work_id}/plans/PLAN.md')\n"
        "Apply critique-revise loop: PROCEED -> continue, REVISE -> fix + re-critique, "
        "BLOCK -> return to plan-authoring."
    ),
    "architectural": (
        "[CRITIQUE + OPERATOR REQUIRED] MUST invoke critique-agent AND get operator approval:\n"
        "1. Task(subagent_type='critique-agent', model='opus', "
        "prompt='Critique plan: docs/work/active/{work_id}/plans/PLAN.md')\n"
        "2. After critique passes, MUST use AskUserQuestion to confirm approach with operator.\n"
        "Architectural changes require explicit operator sign-off before DO phase."
    ),
}


def _default_project_root() -> Path:
    """Derive project root from this file's location.
    lib/ -> haios/ -> .claude/ -> project root."""
    return Path(__file__).parent.parent.parent.parent


def _get_current_phase(project_root: Optional[Path] = None) -> str:
    """Get current lifecycle phase from haios-status-slim.json.

    Returns phase string (e.g., "PLAN", "DO") or "unknown" on failure.
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return "unknown"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        phase = data.get("session_state", {}).get("current_phase")
        return phase if phase else "unknown"
    except Exception:
        return "unknown"


def _get_current_work_id_for_critique(project_root: Optional[Path] = None) -> str:
    """Get current work_id from haios-status-slim.json.

    Returns work_id string or "unknown" on failure.
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return "unknown"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        work_id = data.get("session_state", {}).get("work_id")
        return work_id if work_id else "unknown"
    except Exception:
        return "unknown"


def _is_inhale_to_exhale(current_phase: str, skill_name: str) -> bool:
    """Determine if invoking this skill at this phase is an inhale-to-exhale transition.

    The hook fires BEFORE the phase advances. So if we're in an inhale phase
    and the skill is a lifecycle skill, the next invocation will move to an
    exhale phase. This is the transition point where critique should fire.
    """
    if skill_name not in TRANSITION_SKILLS:
        return False
    if current_phase in INHALE_PHASES:
        return True
    return False


def compute_critique_injection(
    skill_name: str,
    project_root: Optional[Path] = None,
) -> Optional[str]:
    """Compute tier-appropriate critique injection text for a skill invocation.

    Called by PreToolUse hook when a lifecycle skill is invoked. Determines
    whether the current phase is an inhale-to-exhale transition, reads the
    governance tier, and returns the appropriate injection text.

    Args:
        skill_name: Name of the skill being invoked.
        project_root: Project root. Defaults to derived path.

    Returns:
        Injection text string for additionalContext, or None if no injection needed.
        Never raises -- all exceptions caught and handled fail-permissive.
    """
    try:
        root = project_root or _default_project_root()

        # 1. Get current phase
        current_phase = _get_current_phase(root)
        if current_phase == "unknown":
            return None  # Can't determine transition, fail-permissive

        # 2. Check if this is an inhale-to-exhale transition
        if not _is_inhale_to_exhale(current_phase, skill_name):
            return None

        # 3. Get work_id and tier
        work_id = _get_current_work_id_for_critique(root)

        # Import tier_detector (sibling in lib/)
        lib_dir = Path(__file__).parent
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        from tier_detector import detect_tier

        tier = detect_tier(work_id, project_root=root)

        # 4. Get injection template
        injection = TIER_INJECTIONS.get(tier)
        if injection is None:
            return None

        # 5. Format with work_id
        formatted = injection.replace("{work_id}", work_id)

        # 6. Log governance event (fail-permissive)
        _log_critique_injection(work_id, tier, current_phase, skill_name)

        return formatted

    except Exception:
        # Fail-permissive: on any error, default to standard injection
        try:
            work_id = _get_current_work_id_for_critique(project_root)
            _log_critique_warning(work_id, "exception_in_compute")
            injection = TIER_INJECTIONS.get("standard", "")
            return injection.replace("{work_id}", work_id) if injection else None
        except Exception:
            return None


def _log_critique_injection(work_id: str, tier: str, phase: str, skill: str) -> None:
    """Log CritiqueInjected governance event. Fail-permissive."""
    try:
        from governance_events import log_critique_injected
        log_critique_injected(work_id, tier, phase, skill)
    except Exception:
        pass


def _log_critique_warning(work_id: str, reason: str) -> None:
    """Log GovernanceWarning for critique injection failure. Fail-permissive."""
    try:
        from governance_events import log_gate_violation
        log_gate_violation("critique_injection", work_id, "warn", f"Critique injection fallback: {reason}")
    except Exception:
        pass
