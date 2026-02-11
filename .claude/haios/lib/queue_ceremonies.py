# generated: 2026-02-09
"""
Queue ceremony execution and event logging (CH-010, WORK-110).

Events stored in .claude/haios/governance-events.jsonl (append-only).

Event Types:
- QueueCeremony: Logged when queue ceremony executes

Ceremonies:
- Unpark: parked -> backlog (or Park: backlog -> parked)
- Intake: new -> backlog (creation event)
- Prioritize: backlog -> ready (batch capable)
- Commit: ready -> working
- Release: working -> done (IS close-work-cycle, CH-008)

Usage:
    from queue_ceremonies import log_queue_ceremony, execute_queue_transition

    # Log ceremony event directly (e.g., Intake)
    log_queue_ceremony("Intake", ["WORK-001"], "new", "backlog")

    # Execute transition with ceremony logging
    result = execute_queue_transition(engine, "WORK-001", "ready", "Prioritize",
                                      rationale="Critical bug fix")
"""
import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional


@contextmanager
def _ceremony_context_safe(name: str):
    """Import and use ceremony_context with fail-permissive fallback.

    Handles: ImportError (no governance module), already-inside-context
    (reuse outer context to avoid CeremonyNestingError).

    WORK-116: Wraps state-changing operations in ceremony boundaries
    so check_ceremony_required() guards are satisfied.
    """
    try:
        from governance_layer import ceremony_context, in_ceremony_context

        if in_ceremony_context():
            yield None  # Already inside ceremony — no-op (avoid nesting)
        else:
            with ceremony_context(name) as ctx:
                yield ctx
    except ImportError:
        yield None  # Fail-permissive: no governance module available

# Events file location (append-only JSONL, same as governance_events.py)
EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"


def log_queue_ceremony(
    ceremony: str,
    items: List[str],
    from_position: str,
    to_position: str,
    rationale: Optional[str] = None,
    agent: Optional[str] = None,
) -> dict:
    """Log queue ceremony execution to governance-events.jsonl.

    Args:
        ceremony: Ceremony name (Unpark, Park, Intake, Prioritize, Commit)
        items: List of work item IDs involved
        from_position: Source queue position
        to_position: Target queue position
        rationale: Optional reason for the transition
        agent: Optional agent name performing the ceremony

    Returns:
        The logged event dict
    """
    event = {
        "type": "QueueCeremony",
        "ceremony": ceremony,
        "items": items,
        "from": from_position,
        "to": to_position,
        "timestamp": datetime.now().isoformat(),
    }
    if rationale:
        event["rationale"] = rationale
    if agent:
        event["agent"] = agent
    _append_event(event)
    return event


def execute_queue_transition(
    work_engine: Any,
    work_id: str,
    to_position: str,
    ceremony: str,
    rationale: Optional[str] = None,
    agent: Optional[str] = None,
) -> dict:
    """Execute queue transition with ceremony logging.

    Wraps work_engine.set_queue_position() with QueueCeremony event logging.
    Validates transition BEFORE logging (fail fast). Events only logged for
    successful transitions.

    Args:
        work_engine: WorkEngine instance
        work_id: Work item ID to transition
        to_position: Target queue position
        ceremony: Ceremony name for logging
        rationale: Optional reason for the transition
        agent: Optional agent name performing the ceremony

    Returns:
        Dict with {success: bool, work: WorkState} on success,
        or {success: bool, error: str} on failure.
    """
    work = work_engine.get_work(work_id)
    if work is None:
        return {"success": False, "error": f"Work item {work_id} not found"}

    from_position = work.queue_position

    # WORK-128: Block same-state transitions (operator decision: block, not warn)
    if from_position == to_position:
        return {
            "success": False,
            "error": f"{work_id} is already at '{to_position}' — no transition needed",
        }

    try:
        with _ceremony_context_safe(f"queue-{ceremony.lower()}") as ctx:
            updated_work = work_engine.set_queue_position(work_id, to_position)
            if ctx:
                ctx.log_side_effect("queue_transition", {
                    "work_id": work_id, "from": from_position, "to": to_position,
                })
            log_queue_ceremony(
                ceremony=ceremony,
                items=[work_id],
                from_position=from_position,
                to_position=to_position,
                rationale=rationale,
                agent=agent,
            )
        return {"success": True, "work": updated_work}
    except ValueError as e:
        return {"success": False, "error": str(e)}


def _append_event(event: dict) -> None:
    """Append event to JSONL file."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
