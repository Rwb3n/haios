# generated: 2025-12-29
# System Auto: last updated on: 2026-01-26T20:10:22
"""
Governance event logging and threshold monitoring.

E2-108: Gate Observability for Implementation Cycle

Events are stored in .claude/governance-events.jsonl (append-only).
Thresholds trigger actions when patterns are detected.

Event Types:
- CyclePhaseEntered: Logged when agent enters a cycle phase (PLAN, DO, CHECK, DONE)
- ValidationOutcome: Logged when validation gate passes/blocks (preflight, dod, observation)
- SessionStarted: Logged when a session begins (E2-236)
- SessionEnded: Logged when a session ends (E2-236)

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


# =============================================================================
# E2-236: Session Lifecycle Events and Orphan Detection
# =============================================================================


def log_session_start(session_number: int, agent: str) -> dict:
    """
    Log session start event.

    Args:
        session_number: Current session number
        agent: Agent name (e.g., "Hephaestus")

    Returns:
        The logged event dict
    """
    event = {
        "type": "SessionStarted",
        "session": session_number,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)
    return event


def log_session_end(session_number: int, agent: str) -> dict:
    """
    Log session end event.

    Args:
        session_number: Current session number
        agent: Agent name

    Returns:
        The logged event dict
    """
    event = {
        "type": "SessionEnded",
        "session": session_number,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)
    return event


def detect_orphan_session(events_file: Optional[Path] = None) -> Optional[dict]:
    """
    Detect orphan session (started but never ended).

    Scans events for SessionStarted without matching SessionEnded.

    Args:
        events_file: Path to events JSONL (default: EVENTS_FILE constant)

    Returns:
        Dict with orphan_session, current_session if orphan found, else None
    """
    # Use read_events() which reads from EVENTS_FILE, or read custom path for testing
    if events_file is None:
        events = read_events()
    else:
        # For testing: read from custom path
        events = []
        if events_file.exists():
            with open(events_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

    # Track session starts and ends
    started = set()
    ended = set()
    latest_start = None

    for e in events:
        if e.get("type") == "SessionStarted":
            started.add(e.get("session"))
            latest_start = e.get("session")
        elif e.get("type") == "SessionEnded":
            ended.add(e.get("session"))

    # Find orphans (started but not ended, excluding current)
    orphans = started - ended
    if latest_start in orphans:
        orphans.discard(latest_start)  # Current session isn't orphan yet

    if orphans:
        orphan_session = max(orphans)  # Most recent orphan
        return {
            "orphan_session": orphan_session,
            "current_session": latest_start,
        }
    return None


def scan_incomplete_work(project_root: Path) -> list[dict]:
    """
    Scan WORK.md files for incomplete transitions (exited: null).

    Per INV-052 Section 2A: Scan for `exited: null` entries in node_history.

    Args:
        project_root: Project root path

    Returns:
        List of dicts with id, incomplete_node, path
    """
    import re

    work_dirs = [
        project_root / "docs" / "work" / "active",
        project_root / "docs" / "work" / "blocked",
    ]
    incomplete = []

    for dir_path in work_dirs:
        if not dir_path.exists():
            continue
        for subdir in dir_path.iterdir():
            if not subdir.is_dir():
                continue
            work_file = subdir / "WORK.md"
            if not work_file.exists():
                continue

            content = work_file.read_text(encoding="utf-8", errors="ignore")
            # Parse YAML frontmatter
            match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if not match:
                continue

            yaml_content = match.group(1)
            # Check for exited: null in node_history
            if "exited: null" in yaml_content or "exited: ~" in yaml_content:
                # Extract id
                id_match = re.search(r"id:\s*(\S+)", yaml_content)
                # Extract current node
                node_match = re.search(r"node:\s*(\S+)", yaml_content)
                if id_match:
                    incomplete.append({
                        "id": id_match.group(1).strip(),
                        "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
                        "path": str(work_file.relative_to(project_root)),
                    })

    return incomplete


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
