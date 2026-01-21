# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T09:26:12
"""
Governance event logging and threshold monitoring.

E2-108: Gate Observability for Implementation Cycle

Events are stored in .claude/governance-events.jsonl (append-only).
Thresholds trigger actions when patterns are detected.

Event Types:
- CyclePhaseEntered: Logged when agent enters a cycle phase (PLAN, DO, CHECK, DONE)
- ValidationOutcome: Logged when validation gate passes/blocks (preflight, dod, observation)

Usage:
    from governance_events import log_phase_transition, log_validation_outcome

    # Log phase entry
    log_phase_transition("PLAN", "E2-108", "Hephaestus")

    # Log validation result
    log_validation_outcome("preflight", "E2-108", "pass", "All checks passed")
"""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

# Events file location (append-only JSONL)
EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"


def log_phase_transition(phase: str, work_id: str, agent: str) -> dict:
    """
    Log cycle phase entry.

    Args:
        phase: Cycle phase (PLAN, DO, CHECK, DONE)
        work_id: Work item ID (e.g., E2-108)
        agent: Agent name (e.g., Hephaestus)

    Returns:
        The logged event dict
    """
    event = {
        "type": "CyclePhaseEntered",
        "phase": phase,
        "work_id": work_id,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)
    return event


def log_validation_outcome(
    gate: str, work_id: str, result: str, reason: str
) -> dict:
    """
    Log validation outcome and check thresholds.

    Args:
        gate: Validation gate name (preflight, dod, observation)
        work_id: Work item ID (e.g., E2-108)
        result: Outcome (pass, warn, block)
        reason: Human-readable explanation

    Returns:
        The logged event dict
    """
    event = {
        "type": "ValidationOutcome",
        "gate": gate,
        "work_id": work_id,
        "result": result,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)

    # Check if repeated failure threshold exceeded
    if result == "block":
        _check_repeated_failure(gate, work_id)

    return event


def get_threshold_warnings(work_id: str) -> list[str]:
    """
    Return list of gates that exceeded failure threshold for work_id.

    Threshold: 3 failures of the same gate for the same work item.

    Args:
        work_id: Work item ID to check

    Returns:
        List of gate names that have 3+ failures
    """
    events = read_events()
    failures = [
        e
        for e in events
        if e.get("type") == "ValidationOutcome"
        and e.get("work_id") == work_id
        and e.get("result") == "block"
    ]

    # Count failures per gate
    gate_counts: dict[str, int] = {}
    for e in failures:
        gate = e.get("gate", "unknown")
        gate_counts[gate] = gate_counts.get(gate, 0) + 1

    # Return gates with 3+ failures
    return [g for g, c in gate_counts.items() if c >= 3]


def check_work_item_events(work_id: str) -> dict:
    """
    Check if work item has cycle events.

    Used by close-work-cycle to warn if work was closed without
    going through the proper cycle phases.

    Args:
        work_id: Work item ID to check

    Returns:
        Dict with has_events bool and optional warning
    """
    events = read_events()
    work_events = [e for e in events if e.get("work_id") == work_id]

    if not work_events:
        return {
            "has_events": False,
            "warning": f"No cycle events found for {work_id}. Was governance bypassed?",
        }
    return {"has_events": True, "event_count": len(work_events)}


def get_governance_metrics() -> dict:
    """
    Return governance health metrics.

    Returns:
        Dict with phase_transitions, validation_outcomes, pass_rate, failure_reasons
    """
    events = read_events()
    phase_events = [e for e in events if e.get("type") == "CyclePhaseEntered"]
    validation_events = [e for e in events if e.get("type") == "ValidationOutcome"]

    passes = len([e for e in validation_events if e.get("result") == "pass"])
    total_validations = len(validation_events)

    return {
        "phase_transitions": len(phase_events),
        "validation_outcomes": total_validations,
        "pass_rate": passes / total_validations if total_validations else 1.0,
        "failure_reasons": _top_failure_reasons(validation_events),
    }


def read_events() -> list[dict]:
    """
    Read all events from file.

    Returns:
        List of event dicts
    """
    if not EVENTS_FILE.exists():
        return []
    events = []
    with open(EVENTS_FILE, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue
    return events


def _append_event(event: dict) -> None:
    """Append event to JSONL file."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def _check_repeated_failure(gate: str, work_id: str) -> None:
    """Log warning if repeated failure detected."""
    warnings = get_threshold_warnings(work_id)
    if gate in warnings:
        print(f"WARNING: {gate} has failed 3+ times for {work_id}")


def _top_failure_reasons(events: list[dict]) -> list[str]:
    """Return top 5 failure reasons."""
    failures = [e.get("reason") for e in events if e.get("result") == "block"]
    return [r for r, _ in Counter(failures).most_common(5)]
