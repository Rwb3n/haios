# generated: 2025-12-29
# System Auto: last updated on: 2026-01-27T20:58:00
"""
Tests for governance event logging and threshold monitoring.

E2-108: Gate Observability for Implementation Cycle
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
import sys

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
# Add .claude/haios/lib for scan_incomplete_work (WORK-023)
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


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


class TestScanIncompleteWorkStatusFiltering:
    """Tests for scan_incomplete_work status filtering (WORK-023)."""

    def test_scan_incomplete_work_excludes_complete_status(self, tmp_path):
        """Work items with status: complete should not appear in results."""
        from governance_events import scan_incomplete_work

        work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text("""---
id: E2-TEST
status: complete
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-01
  exited: null
---
""")
        result = scan_incomplete_work(tmp_path)
        assert len(result) == 0, "Complete items should be excluded"

    def test_scan_incomplete_work_excludes_archived_status(self, tmp_path):
        """Work items with status: archived should not appear in results."""
        from governance_events import scan_incomplete_work

        work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text("""---
id: E2-TEST
status: archived
current_node: complete
node_history:
- node: complete
  entered: 2026-01-01
  exited: null
---
""")
        result = scan_incomplete_work(tmp_path)
        assert len(result) == 0, "Archived items should be excluded"

    def test_scan_incomplete_work_includes_active_status(self, tmp_path):
        """Work items with status: active and exited: null should appear."""
        from governance_events import scan_incomplete_work

        work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text("""---
id: E2-TEST
status: active
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-01
  exited: null
---
""")
        result = scan_incomplete_work(tmp_path)
        assert len(result) == 1, "Active items should be included"
        assert result[0]["id"] == "E2-TEST"


# =============================================================================
# WORK-129: scan_incomplete_work accepts string input
# =============================================================================


class TestScanIncompleteWorkStringInput:
    """WORK-129: scan_incomplete_work should accept string project_root."""

    def test_scan_incomplete_work_accepts_string(self, tmp_path):
        """WORK-129 T1: Passing a string instead of Path should not raise TypeError."""
        from governance_events import scan_incomplete_work

        work_dir = tmp_path / "docs" / "work" / "active" / "E2-STR"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text("""---
id: E2-STR
status: active
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-01
  exited: null
---
""")
        # Pass string instead of Path - should not raise TypeError
        result = scan_incomplete_work(str(tmp_path))
        assert len(result) == 1
        assert result[0]["id"] == "E2-STR"

    def test_scan_incomplete_work_dot_string(self, tmp_path):
        """WORK-129 T2: Passing '.' as string should work (session-end-ceremony use case)."""
        from governance_events import scan_incomplete_work

        # '.' with no work dirs should return empty, not TypeError
        result = scan_incomplete_work(".")
        # Should not raise; result depends on actual project state
        assert isinstance(result, list)


# =============================================================================
# WORK-146: Gate Violation Logging
# =============================================================================


class TestGateViolationLogging:
    """Tests for gate violation event logging (WORK-146, REQ-OBSERVE-005)."""

    def test_log_gate_violation_creates_event(self, temp_events_file):
        """Verify gate violation creates structured event with all fields."""
        from governance_events import log_gate_violation, read_events

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            log_gate_violation(
                gate_id="ceremony_contract",
                work_id="WORK-146",
                violation_type="warn",
                context="Missing input contract field",
            )

            events = read_events()
            violations = [e for e in events if e["type"] == "GateViolation"]
            assert len(violations) == 1
            v = violations[0]
            assert v["gate_id"] == "ceremony_contract"
            assert v["work_id"] == "WORK-146"
            assert v["violation_type"] == "warn"
            assert v["context"] == "Missing input contract field"
            assert "timestamp" in v

    def test_log_gate_violation_returns_event(self, temp_events_file):
        """Verify log_gate_violation returns the event dict."""
        from governance_events import log_gate_violation

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            result = log_gate_violation("sql_block", "WORK-100", "block", "Direct SQL")
            assert result["type"] == "GateViolation"
            assert result["gate_id"] == "sql_block"

    def test_get_gate_violations_filters_by_work_id(self, temp_events_file):
        """Verify get_gate_violations returns only violations for given work_id."""
        from governance_events import log_gate_violation, get_gate_violations

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            log_gate_violation("sql", "WORK-100", "block", "SQL detected")
            log_gate_violation("ceremony", "WORK-146", "warn", "Contract missing")
            log_gate_violation("powershell", "WORK-100", "block", "PS detected")

            violations = get_gate_violations("WORK-100")
            assert len(violations) == 2
            assert all(v["work_id"] == "WORK-100" for v in violations)

    def test_get_gate_violations_empty_when_none(self, temp_events_file):
        """Verify get_gate_violations returns [] when no violations exist."""
        from governance_events import get_gate_violations

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            violations = get_gate_violations("WORK-999")
            assert violations == []

    def test_existing_log_functions_unaffected(self, temp_events_file):
        """Verify existing log_phase_transition and log_validation_outcome still work."""
        from governance_events import (
            log_phase_transition,
            log_validation_outcome,
            log_gate_violation,
            read_events,
        )

        with patch("governance_events.EVENTS_FILE", temp_events_file):
            log_phase_transition("PLAN", "WORK-146", "Hephaestus")
            log_validation_outcome("preflight", "WORK-146", "pass", "OK")
            log_gate_violation("sql", "WORK-146", "block", "SQL")

            events = read_events()
            types = [e["type"] for e in events]
            assert "CyclePhaseEntered" in types
            assert "ValidationOutcome" in types
            assert "GateViolation" in types
