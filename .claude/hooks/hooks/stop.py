# generated: 2025-12-20
# System Auto: last updated on: 2026-02-18T22:00:00
"""
Stop Hook Handler (E2-085, WORK-161).

Two responsibilities:
1. Extract learnings from completed sessions via MemoryBridge (requires transcript)
2. Run session-end actions unconditionally (WORK-161: Session Boundary Fix)

The ReasoningBank Loop:
    RETRIEVE (UserPromptSubmit) -> INJECT -> EXECUTE -> EXTRACT (Stop) -> STORE
                                                              ^
                                                              |
                                                        THIS HANDLER

E2-264: Module-first import via MemoryBridge.
WORK-161: Session-end actions (log event, clear cycle, detect changes).
"""
import sys
from pathlib import Path
from typing import Optional


def handle(hook_data: dict) -> Optional[str]:
    """
    Process Stop hook.

    Args:
        hook_data: Parsed JSON from Claude Code containing:
            - session_id: str
            - transcript_path: str (path to session JSONL)
            - stop_hook_active: bool (if True, previous stop hook already ran)

    Returns:
        Optional extraction status message.

    Side effects:
        - Invokes MemoryBridge.extract_learnings() to store learnings
        - Runs session-end actions (event logging, cycle clearing)
    """
    # CRITICAL: Check stop_hook_active to prevent infinite loops
    if hook_data.get("stop_hook_active", False):
        return None

    messages = []

    # Part 1: Learning extraction (separate try/except)
    # Only runs when transcript exists — transcript gates THIS block only
    transcript_path = hook_data.get("transcript_path", "")
    if transcript_path and Path(transcript_path).exists():
        try:
            # E2-264: Module-first import via MemoryBridge
            modules_dir = Path(__file__).parent.parent / "haios" / "modules"
            if str(modules_dir) not in sys.path:
                sys.path.insert(0, str(modules_dir))

            from memory_bridge import MemoryBridge
            bridge = MemoryBridge()
            result = bridge.extract_learnings(transcript_path)

            if result.success:
                messages.append(f"[LEARNING] Extracted from session (outcome: {result.outcome})")
        except Exception:
            pass  # Don't break on extraction errors

    # Part 2: Session-end actions (ALWAYS runs, own try/except)
    _run_session_end_actions()

    return "\n".join(messages) if messages else None


def _run_session_end_actions() -> None:
    """Run session-end housekeeping actions.

    WORK-161: These run unconditionally from the Stop hook, ensuring
    session-end cleanup happens even when the agent exhausts context.

    Each action is independently fail-permissive.
    """
    try:
        # Explicit lib/ path setup (stop.py only has modules/ on path)
        lib_dir = Path(__file__).parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from session_end_actions import (
            read_session_number,
            log_session_ended,
            clear_cycle_state,
            detect_uncommitted_changes,
        )

        session_num = read_session_number()
        if session_num is not None:
            log_session_ended(session_num, agent="Hephaestus")

        clear_cycle_state()

        # Session-review predicate check (WORK-209)
        _inject_session_review_reminder()

        changes = detect_uncommitted_changes()
        if changes:
            sys.stderr.write(f"[session-end] {len(changes)} uncommitted change(s)\n")
    except Exception:
        pass  # Fail-permissive


def _inject_session_review_reminder() -> None:
    """Check session-review predicate and inject reminder if it passes (WORK-209).

    If should_run_session_review() returns True, writes reminder to stderr
    so Claude Code displays it as context at session-end.

    Fail-permissive: never raises, never blocks session-end.
    """
    try:
        lib_dir = Path(__file__).parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        from session_review_predicate import should_run_session_review

        if should_run_session_review():
            sys.stderr.write(
                "[session-end] MUST run session-review-cycle before closing this session. "
                "Trigger predicate passed (work closed or retro completed this session).\n"
            )
    except Exception:
        pass  # Fail-permissive
