# generated: 2026-02-09
"""
Tests for queue ceremony execution and event logging (CH-010, WORK-110).

Tests the queue_ceremonies module:
- log_queue_ceremony(): Append QueueCeremony events to JSONL
- execute_queue_transition(): Wrap set_queue_position with ceremony logging

Follows patterns from test_work_engine.py for module loading and fixtures.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock

# Add parent paths for module imports
import sys
import importlib.util

_root = Path(__file__).parent.parent

# Add parent paths for module imports (portal_manager, etc.)
sys.path.insert(0, str(_root / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(_root / ".claude" / "haios" / "lib"))


def _load_module(name: str, path: Path):
    """Load a module from a specific path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Load governance_layer first (dependency of work_engine)
_gov_path = _root / ".claude" / "haios" / "modules" / "governance_layer.py"
if "governance_layer" not in sys.modules:
    governance_layer = _load_module("governance_layer", _gov_path)
else:
    governance_layer = sys.modules["governance_layer"]
GovernanceLayer = governance_layer.GovernanceLayer

# Load work_engine
_work_path = _root / ".claude" / "haios" / "modules" / "work_engine.py"
if "work_engine" not in sys.modules:
    work_engine = _load_module("work_engine", _work_path)
else:
    work_engine = sys.modules["work_engine"]
WorkEngine = work_engine.WorkEngine

# Load queue_ceremonies (the module under test)
_qc_path = _root / ".claude" / "haios" / "lib" / "queue_ceremonies.py"
queue_ceremonies = _load_module("queue_ceremonies", _qc_path)


# =============================================================================
# Helpers
# =============================================================================


def _read_events(events_file: Path) -> list:
    """Read JSONL events file."""
    events = []
    with open(events_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def governance():
    """Create real GovernanceLayer for integration tests."""
    return GovernanceLayer()


@pytest.fixture
def engine(tmp_path, governance):
    """Create WorkEngine with real GovernanceLayer and tmp_path."""
    return WorkEngine(governance=governance, base_path=tmp_path)


@pytest.fixture(autouse=True)
def patch_events_file(tmp_path):
    """Redirect EVENTS_FILE to tmp_path for test isolation."""
    original = queue_ceremonies.EVENTS_FILE
    queue_ceremonies.EVENTS_FILE = tmp_path / "test-events.jsonl"
    yield
    queue_ceremonies.EVENTS_FILE = original


# =============================================================================
# Test 1: Log Queue Ceremony Event
# =============================================================================


def test_log_queue_ceremony_creates_event(tmp_path):
    """log_queue_ceremony() appends QueueCeremony event to JSONL."""
    event = queue_ceremonies.log_queue_ceremony(
        ceremony="Prioritize",
        items=["WORK-001", "WORK-002"],
        from_position="backlog",
        to_position="ready",
        rationale="Critical bugs",
        agent="Hephaestus",
    )

    assert event["type"] == "QueueCeremony"
    assert event["ceremony"] == "Prioritize"
    assert event["items"] == ["WORK-001", "WORK-002"]
    assert event["from"] == "backlog"
    assert event["to"] == "ready"
    assert event["rationale"] == "Critical bugs"
    assert event["agent"] == "Hephaestus"
    assert "timestamp" in event
    assert queue_ceremonies.EVENTS_FILE.exists()


# =============================================================================
# Test 2: Execute Queue Transition With Ceremony
# =============================================================================


def test_execute_queue_transition_logs_ceremony(tmp_path, engine):
    """execute_queue_transition() calls set_queue_position and logs event."""
    engine.create_work("WORK-TEST", "Test Work")

    result = queue_ceremonies.execute_queue_transition(
        work_engine=engine,
        work_id="WORK-TEST",
        to_position="ready",
        ceremony="Prioritize",
        rationale="Test",
        agent="Hephaestus",
    )

    assert result["success"] is True
    assert result["work"].queue_position == "ready"
    # Verify event logged
    events = _read_events(queue_ceremonies.EVENTS_FILE)
    assert len(events) == 1
    assert events[0]["type"] == "QueueCeremony"
    assert events[0]["ceremony"] == "Prioritize"


# =============================================================================
# Test 3: Unpark Ceremony (Parked -> Backlog)
# =============================================================================


def test_unpark_ceremony(tmp_path, engine):
    """Unpark moves item from parked to backlog."""
    engine.create_work("WORK-PARK", "Parked Work")
    engine.set_queue_position("WORK-PARK", "parked")

    result = queue_ceremonies.execute_queue_transition(
        engine, "WORK-PARK", "backlog", "Unpark", rationale="Bringing into scope"
    )

    assert result["success"] is True
    assert result["work"].queue_position == "backlog"
    event = _read_events(queue_ceremonies.EVENTS_FILE)[-1]
    assert event["ceremony"] == "Unpark"
    assert event["from"] == "parked"
    assert event["to"] == "backlog"


# =============================================================================
# Test 4: Park Ceremony (Backlog -> Parked)
# =============================================================================


def test_park_ceremony(tmp_path, engine):
    """Park moves item from backlog to parked."""
    engine.create_work("WORK-DEFER", "Deferred Work")

    result = queue_ceremonies.execute_queue_transition(
        engine, "WORK-DEFER", "parked", "Park", rationale="Deferring to E2.6"
    )

    assert result["success"] is True
    assert result["work"].queue_position == "parked"
    event = _read_events(queue_ceremonies.EVENTS_FILE)[-1]
    assert event["ceremony"] == "Park"
    assert event["from"] == "backlog"
    assert event["to"] == "parked"


# =============================================================================
# Test 5: Intake Ceremony (New -> Backlog)
# =============================================================================


def test_intake_ceremony_logs_event(tmp_path, engine):
    """Intake logs creation at backlog."""
    engine.create_work("WORK-NEW", "New Work")

    queue_ceremonies.log_queue_ceremony(
        ceremony="Intake",
        items=["WORK-NEW"],
        from_position="new",
        to_position="backlog",
        rationale="New work item created",
    )

    work = engine.get_work("WORK-NEW")
    assert work.queue_position == "backlog"
    event = _read_events(queue_ceremonies.EVENTS_FILE)[-1]
    assert event["ceremony"] == "Intake"
    assert event["from"] == "new"
    assert event["to"] == "backlog"


# =============================================================================
# Test 6: Prioritize Ceremony Batch
# =============================================================================


def test_prioritize_batch(tmp_path, engine):
    """Prioritize handles multiple items."""
    engine.create_work("WORK-001", "Work 1")
    engine.create_work("WORK-002", "Work 2")

    for wid in ["WORK-001", "WORK-002"]:
        queue_ceremonies.execute_queue_transition(
            engine, wid, "ready", "Prioritize", rationale="Critical batch"
        )

    assert engine.get_work("WORK-001").queue_position == "ready"
    assert engine.get_work("WORK-002").queue_position == "ready"
    events = [
        e
        for e in _read_events(queue_ceremonies.EVENTS_FILE)
        if e.get("ceremony") == "Prioritize"
    ]
    assert len(events) == 2


# =============================================================================
# Test 7: Commit Ceremony (Ready -> Working)
# =============================================================================


def test_commit_ceremony(tmp_path, engine):
    """Commit moves ready item to working."""
    engine.create_work("WORK-START", "Work to Start")
    engine.set_queue_position("WORK-START", "ready")

    result = queue_ceremonies.execute_queue_transition(
        engine, "WORK-START", "working", "Commit", rationale="Starting work"
    )

    assert result["success"] is True
    assert result["work"].queue_position == "working"
    event = _read_events(queue_ceremonies.EVENTS_FILE)[-1]
    assert event["ceremony"] == "Commit"
    assert event["from"] == "ready"
    assert event["to"] == "working"


# =============================================================================
# Test 8: Invalid Transition Blocked
# =============================================================================


def test_invalid_transition_blocked(tmp_path, engine):
    """Invalid transition returns error, no event logged."""
    engine.create_work("WORK-BAD", "Bad Transition")
    # backlog -> working is invalid (must go through ready)

    result = queue_ceremonies.execute_queue_transition(
        engine, "WORK-BAD", "working", "InvalidCommit", rationale="Skipping"
    )

    assert result["success"] is False
    assert "blocked" in result["error"].lower() or "invalid" in result["error"].lower()
    assert engine.get_work("WORK-BAD").queue_position == "backlog"
    # No event should be logged for failed transitions
    events_file = queue_ceremonies.EVENTS_FILE
    if events_file.exists():
        events = _read_events(events_file)
        assert len(events) == 0


# =============================================================================
# Test 9: Full Queue Lifecycle Integration
# =============================================================================


def test_full_queue_lifecycle_via_ceremonies(tmp_path, engine):
    """Integration: parked -> backlog -> ready -> working via ceremonies."""
    engine.create_work("WORK-FULL", "Full Lifecycle Test")
    engine.set_queue_position("WORK-FULL", "parked")

    # Unpark -> Prioritize -> Commit
    queue_ceremonies.execute_queue_transition(
        engine, "WORK-FULL", "backlog", "Unpark", "Into scope"
    )
    queue_ceremonies.execute_queue_transition(
        engine, "WORK-FULL", "ready", "Prioritize", "High priority"
    )
    queue_ceremonies.execute_queue_transition(
        engine, "WORK-FULL", "working", "Commit", "Starting"
    )

    assert engine.get_work("WORK-FULL").queue_position == "working"

    # Verify 3 ceremony events logged
    events = _read_events(queue_ceremonies.EVENTS_FILE)
    ceremonies = [e["ceremony"] for e in events if e["type"] == "QueueCeremony"]
    assert ceremonies == ["Unpark", "Prioritize", "Commit"]


# =============================================================================
# Test 10: Rationale Captured in Events
# =============================================================================


def test_rationale_captured(tmp_path, engine):
    """Rationale field preserved in ceremony events."""
    engine.create_work("WORK-SCOPE", "Scope Decision")

    queue_ceremonies.execute_queue_transition(
        engine,
        "WORK-SCOPE",
        "parked",
        "Park",
        rationale="Deferring to E2.6 - out of current scope",
    )

    event = _read_events(queue_ceremonies.EVENTS_FILE)[-1]
    assert "rationale" in event
    assert "E2.6" in event["rationale"]
