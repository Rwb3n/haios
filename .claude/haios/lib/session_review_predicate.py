# generated: 2026-02-23
"""
Session Review trigger predicate (WORK-209).

Computable predicate extracted from session-review-cycle SKILL.md.

Trigger condition (OR logic):
  - At least 1 work item CLOSED this session (event t="close" in session-log.jsonl)
  - OR at least 2 RetroCycleCompleted events in governance-events.jsonl

Public API:
    should_run_session_review()  -> bool
    _count_close_events()        -> int   (testable helper)
    _count_retro_completed()     -> int   (testable helper)

All functions are fail-permissive: they never raise exceptions.

Format dependency (critique A2): Close events depend on post_tool_use._append_session_event()
detecting "close" via Bash pattern match (regex: r"close.work|cli\\.py\\s+close").
If close is invoked differently, the close-event arm returns 0 silently.
The retro-count arm depends on RetroCycleCompleted events being logged by retro-cycle.
"""
import json
import sys
from pathlib import Path


def _get_lib_dir() -> Path:
    """Return lib directory path."""
    return Path(__file__).parent


def _count_close_events(session_log_path: Path = None) -> int:
    """Count work-close events in session-log.jsonl.

    Close events have t="close" in the compact JSONL format
    (produced by post_tool_use._append_session_event).

    Args:
        session_log_path: Override path for testing. If None, uses session_event_log.get_log_path().

    Returns:
        Count of close events. Returns 0 on any error.
    """
    try:
        lib_dir = _get_lib_dir()
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        from session_event_log import get_log_path

        actual_path = session_log_path if session_log_path is not None else get_log_path()
        if not actual_path.exists():
            return 0
        count = 0
        for line in actual_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get("t") == "close":
                    count += 1
            except (json.JSONDecodeError, AttributeError):
                pass
        return count
    except Exception:
        return 0


def _count_retro_completed(governance_events_path: Path = None) -> int:
    """Count RetroCycleCompleted events in governance-events.jsonl.

    Args:
        governance_events_path: Override Path for testing. If None, uses governance_events.EVENTS_FILE.

    Returns:
        Count of RetroCycleCompleted events. Returns 0 on any error.
    """
    try:
        lib_dir = _get_lib_dir()
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        if governance_events_path is not None:
            events_path = Path(governance_events_path)
        else:
            from governance_events import EVENTS_FILE

            events_path = EVENTS_FILE
        if not events_path.exists():
            return 0
        count = 0
        for line in events_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get("type") == "RetroCycleCompleted":
                    count += 1
            except (json.JSONDecodeError, AttributeError):
                pass
        return count
    except Exception:
        return 0


def should_run_session_review(
    session_log_path: Path = None,
    governance_events_path: Path = None,
) -> bool:
    """Evaluate session-review trigger predicate.

    Predicate (OR logic):
      - At least 1 close event in session-log.jsonl, OR
      - At least 2 RetroCycleCompleted in governance-events.jsonl

    Args:
        session_log_path: Override for testing session-log.jsonl path.
        governance_events_path: Override for testing governance-events.jsonl path.

    Returns:
        True if session review should run. False on any error (fail-permissive).
    """
    try:
        close_count = _count_close_events(session_log_path)
        if close_count >= 1:
            return True
        retro_count = _count_retro_completed(governance_events_path)
        if retro_count >= 2:
            return True
        return False
    except Exception:
        return False  # Fail-permissive: never trigger review on error
