"""
Retro-before-close gate (WORK-253).

Checks governance-events.jsonl for RetroCycleCompleted event matching
work_id in the current session. Called by PreToolUse hook before
close-work-cycle is allowed to proceed.

Pattern: retro_scale.py (fail-permissive, _default_project_root,
pure function, no exceptions escape).
"""
import json
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root from this file's location.

    lib/ -> haios/ -> .claude/ -> project root.
    NOT Path.cwd() — hook subprocess cwd is not guaranteed.
    """
    return Path(__file__).parent.parent.parent.parent


def _read_session_id(project_root: Path) -> int:
    """Read current session number from .claude/session.

    Returns session number as int, or 0 if file missing/unreadable.
    Pattern: governance_events._read_session_id().
    """
    try:
        session_file = project_root / ".claude" / "session"
        if not session_file.exists():
            return 0
        for line in session_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                return int(line)
            except ValueError:
                continue
        return 0
    except Exception:
        return 0


def check_retro_gate(
    work_id: str,
    project_root: Optional[Path] = None,
) -> dict:
    """Check if retro-cycle completed for work_id in the current session.

    Scans governance-events.jsonl for a RetroCycleCompleted event
    matching the given work_id and current session_id.

    Args:
        work_id: Work item ID to check (e.g., "WORK-253"). May be empty
                 string if not parseable from Skill tool args.
        project_root: Project root. Defaults to derived path.

    Returns:
        dict with keys:
          - blocked: bool — True if close should be denied
          - reason: str — denial message (when blocked=True)
          - warning: str — warning message (when blocked=False but uncertain)
          - retro_found: bool — True if RetroCycleCompleted found

    Never raises — all exceptions handled fail-permissive.
    Fail-permissive means: if events file unreadable, returns
    blocked=False with a warning (WARN, not BLOCK).
    """
    try:
        root = project_root or _default_project_root()
        events_file = root / ".claude" / "haios" / "governance-events.jsonl"
        current_session = _read_session_id(root)

        # Edge case: work_id not parseable from tool args
        if not work_id:
            return {
                "blocked": False,
                "reason": "",
                "warning": (
                    "WARNING: close-work-cycle invoked but work_id could not "
                    "be determined. Verify retro-cycle ran before closing. "
                    "(WORK-253)"
                ),
                "retro_found": False,
            }

        # Read events file
        if not events_file.exists():
            # Fail-permissive: no events file -> warn but don't block
            return {
                "blocked": False,
                "reason": "",
                "warning": (
                    f"WARNING: governance-events.jsonl not found. "
                    f"Cannot verify retro-cycle ran for {work_id}. "
                    "Ensure retro-cycle completes before /close. (WORK-253)"
                ),
                "retro_found": False,
            }

        retro_found = False
        for line in events_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if (
                event.get("type") == "RetroCycleCompleted"
                and event.get("work_id") == work_id
            ):
                event_session = event.get("session_id") or event.get("session")
                # Match: same session, or no session tracking on event (legacy)
                if event_session is None or event_session == current_session:
                    retro_found = True
                    break

        if retro_found:
            return {
                "blocked": False,
                "reason": "",
                "warning": "",
                "retro_found": True,
            }

        # No RetroCycleCompleted found for this work_id in this session
        return {
            "blocked": True,
            "reason": (
                f"BLOCKED: retro-cycle must complete before closing {work_id}. "
                f"Run: Skill(skill='retro-cycle') with work_id='{work_id}'. "
                "Retro captures session learnings — skipping loses them "
                "permanently. (WORK-253, mem:89182)"
            ),
            "warning": "",
            "retro_found": False,
        }

    except Exception:
        # Fail-permissive: any unexpected error -> warn but don't block
        return {
            "blocked": False,
            "reason": "",
            "warning": (
                f"WARNING: retro gate check failed for {work_id}. "
                "Verify retro-cycle ran before closing. (WORK-253)"
            ),
            "retro_found": False,
        }
