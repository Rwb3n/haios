# generated: 2025-12-29
# System Auto: last updated on: 2026-01-26T23:48:26
"""
Governance event logging and threshold monitoring.

E2-108: Gate Observability for Implementation Cycle

Events are stored in .claude/haios/governance-events.jsonl (append-only).
Thresholds trigger actions when patterns are detected.

Event Types:
- CyclePhaseEntered: Logged when agent enters a cycle phase (PLAN, DO, CHECK, DONE)
- ValidationOutcome: Logged when validation gate passes/blocks (preflight, dod, observation)
- GateViolation: Logged when a MUST gate detects a violation (WORK-146, REQ-OBSERVE-005)
- SessionStarted: Logged when a session begins (E2-236)
- SessionEnded: Logged when a session ends (E2-236)
- TierDetected: Logged when governance tier is computed for a work item (WORK-167)

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

# Session file location — read to inject session_id on every event (WORK-215)
SESSION_FILE = Path(__file__).parent.parent.parent.parent / ".claude" / "session"


def log_phase_transition(phase: str, work_id: str, agent: str, *, context_pct: Optional[float] = None) -> dict:
    """
    Log cycle phase entry.

    Args:
        phase: Cycle phase (PLAN, DO, CHECK, DONE)
        work_id: Work item ID (e.g., E2-108)
        agent: Agent name (e.g., Hephaestus)
        context_pct: Optional context window remaining percentage (0-100)

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
    _append_event(event, context_pct=context_pct)
    return event


def log_validation_outcome(
    gate: str, work_id: str, result: str, reason: str, *, context_pct: Optional[float] = None
) -> dict:
    """
    Log validation outcome and check thresholds.

    Args:
        gate: Validation gate name (preflight, dod, observation)
        work_id: Work item ID (e.g., E2-108)
        result: Outcome (pass, warn, block)
        reason: Human-readable explanation
        context_pct: Optional context window remaining percentage (0-100)

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
    _append_event(event, context_pct=context_pct)

    # Check if repeated failure threshold exceeded
    if result == "block":
        _check_repeated_failure(gate, work_id)

    return event


def log_gate_violation(
    gate_id: str, work_id: str, violation_type: str, context: str, *, context_pct: Optional[float] = None
) -> dict:
    """
    Log gate violation event.

    Emitted when a MUST gate detects a violation and allows it (warn mode)
    or blocks it (block mode). Provides audit trail for governance bypasses.

    Args:
        gate_id: Gate/check identifier (e.g., "sql_block", "ceremony_contract",
                 "no_governance_cycle")
        work_id: Work item ID (e.g., "WORK-146") or "unknown" if outside
                 work context
        violation_type: "warn" (allowed but flagged) or "block" (denied)
        context: Human-readable description of the violation
        context_pct: Optional context window remaining percentage (0-100)

    Returns:
        The logged event dict
    """
    event = {
        "type": "GateViolation",
        "gate_id": gate_id,
        "work_id": work_id,
        "violation_type": violation_type,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event, context_pct=context_pct)
    return event


def get_gate_violations(work_id: str) -> list[dict]:
    """
    Get all gate violations for a work item.

    Args:
        work_id: Work item ID to filter by

    Returns:
        List of GateViolation event dicts
    """
    events = read_events()
    return [
        e
        for e in events
        if e.get("type") == "GateViolation" and e.get("work_id") == work_id
    ]


# =============================================================================
# E2-236: Session Lifecycle Events and Orphan Detection
# =============================================================================


def log_session_start(session_number: int, agent: str, *, context_pct: Optional[float] = None) -> dict:
    """
    Log session start event.

    Args:
        session_number: Current session number
        agent: Agent name (e.g., "Hephaestus")
        context_pct: Optional context window remaining percentage (0-100)

    Returns:
        The logged event dict
    """
    event = {
        "type": "SessionStarted",
        "session": session_number,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event, context_pct=context_pct)
    return event


def log_session_end(session_number: int, agent: str, *, context_pct: Optional[float] = None) -> dict:
    """
    Log session end event.

    Args:
        session_number: Current session number
        agent: Agent name
        context_pct: Optional context window remaining percentage (0-100)

    Returns:
        The logged event dict
    """
    event = {
        "type": "SessionEnded",
        "session": session_number,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event, context_pct=context_pct)
    return event


def log_tier_detected(work_id: str, tier: str, *, context_pct: Optional[float] = None) -> dict:
    """
    Log TierDetected governance event (WORK-167).

    Logged when governance tier is computed for a work item.
    Tiers: trivial, small, standard, architectural (REQ-CEREMONY-005).

    Args:
        work_id: Work item ID (e.g., "WORK-167")
        tier: Detected tier (trivial, small, standard, architectural)
        context_pct: Optional context window remaining percentage (0-100)

    Returns:
        The logged event dict
    """
    event = {
        "type": "TierDetected",
        "work_id": work_id,
        "tier": tier,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event, context_pct=context_pct)
    return event


def log_critique_injected(work_id: str, tier: str, phase: str, skill: str, *, context_pct: Optional[float] = None) -> dict:
    """
    Log CritiqueInjected governance event (WORK-169).

    Logged when critique injection fires for an inhale-to-exhale transition.

    Args:
        work_id: Work item ID (e.g., "WORK-169")
        tier: Governance tier (trivial, small, standard, architectural)
        phase: Current lifecycle phase (e.g., "PLAN", "EXPLORE")
        skill: Skill that triggered the injection (e.g., "implementation-cycle")
        context_pct: Optional context window remaining percentage (0-100)

    Returns:
        The logged event dict
    """
    event = {
        "type": "CritiqueInjected",
        "work_id": work_id,
        "tier": tier,
        "phase": phase,
        "skill": skill,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event, context_pct=context_pct)
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
        project_root: Project root path (accepts str or Path)

    Returns:
        List of dicts with id, incomplete_node, path
    """
    import re

    project_root = Path(project_root)  # WORK-129: Coerce string to Path

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

            # Extract status field and skip terminal statuses
            # Uses same terminal set as WorkEngine.get_ready() (Session 211)
            status_match = re.search(r"status:\s*(\S+)", yaml_content)
            status = status_match.group(1).strip() if status_match else ""
            terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}
            if status in terminal_statuses:
                continue

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


def _read_session_id() -> int:
    """Read current session number from .claude/session.

    Returns session number as int, or 0 if file missing, unreadable,
    or contains no parseable integer line.

    Pattern mirrors checkpoint_auto._read_session_number() and
    session_end_actions.read_session_number() (established in E2.8).
    """
    try:
        if not SESSION_FILE.exists():
            return 0
        for line in SESSION_FILE.read_text(encoding="utf-8").splitlines():
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


def _append_event(event: dict, context_pct: Optional[float] = None) -> None:
    """Append event to JSONL file, injecting session_id and optional context_pct."""
    event["session_id"] = _read_session_id()
    if context_pct is not None:
        event["context_pct"] = context_pct
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def archive_governance_events(prior_epoch_dir: Path) -> dict:
    """
    Archive governance-events.jsonl to prior epoch directory and start fresh.

    Called during open-epoch-ceremony SCAFFOLD phase after verifying the
    prior epoch directory exists. Copies the live events file to the epoch
    archive directory, then truncates the live file to empty so the new
    epoch starts with a clean log.

    Idempotency: if source is empty but archive already has content, the
    write is skipped to prevent overwriting the only durable copy (A4).

    Args:
        prior_epoch_dir: Path to the just-closed epoch directory.
                         E.g., Path(".claude/haios/epochs/E2_8")
                         Must exist before calling.

    Returns:
        dict with keys:
          - archived: bool — True if archive was written
          - archive_path: str — absolute path of archive file (or "" if skipped)
          - lines_archived: int — count of newline characters in archived file (or 0)
          - skipped: bool — True if source missing or idempotency guard triggered

    Raises:
        NotADirectoryError: if prior_epoch_dir does not exist or is not a directory
    """
    prior_epoch_dir = Path(prior_epoch_dir)
    if not prior_epoch_dir.is_dir():
        raise NotADirectoryError(
            f"archive_governance_events: prior_epoch_dir does not exist: {prior_epoch_dir}"
        )

    # Source file may not exist if system never logged any events
    if not EVENTS_FILE.exists():
        return {
            "archived": False,
            "archive_path": "",
            "lines_archived": 0,
            "skipped": True,
        }

    # Destination: <prior_epoch_dir>/governance-events.jsonl
    archive_path = prior_epoch_dir / "governance-events.jsonl"

    # Read source content once (atomic snapshot)
    source_content = EVENTS_FILE.read_bytes()

    # Idempotency guard (A4): if source is empty but archive already has content,
    # skip overwrite to prevent destroying the only durable copy
    if not source_content and archive_path.exists() and archive_path.stat().st_size > 0:
        return {
            "archived": False,
            "archive_path": "",
            "lines_archived": 0,
            "skipped": True,
        }

    lines_archived = source_content.count(b"\n")

    # Write archive (overwrites if re-run with same content)
    archive_path.write_bytes(source_content)

    # Truncate live file to empty (keep file handle; write empty string)
    EVENTS_FILE.write_text("", encoding="utf-8")

    return {
        "archived": True,
        "archive_path": str(archive_path.resolve()),
        "lines_archived": lines_archived,
        "skipped": False,
    }


def _check_repeated_failure(gate: str, work_id: str) -> None:
    """Log warning if repeated failure detected."""
    warnings = get_threshold_warnings(work_id)
    if gate in warnings:
        print(f"WARNING: {gate} has failed 3+ times for {work_id}")


def _top_failure_reasons(events: list[dict]) -> list[str]:
    """Return top 5 failure reasons."""
    failures = [e.get("reason") for e in events if e.get("result") == "block"]
    return [r for r, _ in Counter(failures).most_common(5)]
