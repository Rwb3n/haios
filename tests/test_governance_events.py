# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T09:25:04
"""
Tests for governance event logging and threshold monitoring.

E2-108: Gate Observability for Implementation Cycle
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
import sys

# Add .claude/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


@pytest.fixture
def temp_events_file(tmp_path):
    """Create a temporary events file for testing."""
    events_file = tmp_path / "governance-events.jsonl"
    with patch("governance_events.EVENTS_FILE", events_file):
        yield events_file


class TestPhaseTransitionLogging:
    """Test 1: Phase Transition Event Logged"""

    def test_log_phase_transition_creates_event(self, temp_events_file):
        """Verify phase transition creates structured event."""
        from governance_events import log_phase_transition, read_events

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            log_phase_transition("PLAN", "E2-108", "Hephaestus")

            events = read_events()
            assert len(events) == 1
            assert events[0]["type"] == "CyclePhaseEntered"
            assert events[0]["phase"] == "PLAN"
            assert events[0]["work_id"] == "E2-108"
            assert events[0]["agent"] == "Hephaestus"
            assert "timestamp" in events[0]


class TestValidationOutcomeLogging:
    """Test 2: Validation Outcome Event Logged"""

    def test_log_validation_outcome_creates_event(self, temp_events_file):
        """Verify validation outcome creates structured event with reason."""
        from governance_events import log_validation_outcome, read_events

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            log_validation_outcome("preflight", "E2-108", "block", "Plan incomplete")

            events = read_events()
            last = [e for e in events if e["type"] == "ValidationOutcome"][-1]
            assert last["gate"] == "preflight"
            assert last["result"] == "block"
            assert last["reason"] == "Plan incomplete"
            assert last["work_id"] == "E2-108"


class TestRepeatedFailureThreshold:
    """Test 3: Repeated Failure Triggers Warning"""

    def test_repeated_failure_triggers_threshold(self, temp_events_file):
        """Verify 3 failures of same gate triggers warning."""
        from governance_events import log_validation_outcome, get_threshold_warnings

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            for _ in range(3):
                log_validation_outcome("dod", "E2-108", "block", "Tests failing")

            warnings = get_threshold_warnings("E2-108")
            assert "dod" in warnings  # Should flag repeated dod failures

    def test_two_failures_no_warning(self, temp_events_file):
        """Verify 2 failures does not trigger threshold."""
        from governance_events import log_validation_outcome, get_threshold_warnings

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            for _ in range(2):
                log_validation_outcome("dod", "E2-108", "block", "Tests failing")

            warnings = get_threshold_warnings("E2-108")
            assert "dod" not in warnings


class TestGovernanceMetrics:
    """Test 4: Metrics Summary Returns Counts"""

    def test_governance_metrics_counts_events(self, temp_events_file):
        """Verify metrics recipe returns correct counts."""
        from governance_events import (
            log_phase_transition,
            log_validation_outcome,
            get_governance_metrics,
        )

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            # Create some events
            log_phase_transition("PLAN", "E2-108", "Hephaestus")
            log_phase_transition("DO", "E2-108", "Hephaestus")
            log_validation_outcome("preflight", "E2-108", "pass", "All checks passed")
            log_validation_outcome("dod", "E2-108", "block", "Tests failing")

            metrics = get_governance_metrics()
            assert "phase_transitions" in metrics
            assert metrics["phase_transitions"] == 2
            assert "validation_outcomes" in metrics
            assert metrics["validation_outcomes"] == 2
            assert "pass_rate" in metrics
            assert metrics["pass_rate"] == 0.5  # 1 pass out of 2


class TestCloseWithoutEvents:
    """Test 5: Close Without Events Warns"""

    def test_close_without_events_produces_warning(self, temp_events_file):
        """Verify closing work item with no cycle events produces warning."""
        from governance_events import check_work_item_events

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            result = check_work_item_events("E2-999")  # No events for this ID
            assert result["has_events"] == False
            assert "warning" in result

    def test_close_with_events_no_warning(self, temp_events_file):
        """Verify closing work item with events does not produce warning."""
        from governance_events import log_phase_transition, check_work_item_events

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            log_phase_transition("PLAN", "E2-108", "Hephaestus")

            result = check_work_item_events("E2-108")
            assert result["has_events"] == True
            assert "warning" not in result


class TestAppendOnly:
    """Test 6: Events File Append-Only"""

    def test_events_append_only(self, temp_events_file):
        """Verify events are appended, not overwritten."""
        from governance_events import log_phase_transition, read_events

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            initial_count = len(read_events())
            assert initial_count == 0

            log_phase_transition("PLAN", "E2-108", "Hephaestus")
            assert len(read_events()) == 1

            log_phase_transition("DO", "E2-108", "Hephaestus")
            assert len(read_events()) == 2

            log_phase_transition("CHECK", "E2-108", "Hephaestus")
            assert len(read_events()) == 3
