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


# =============================================================================
# WORK-215: Session ID Injection on Governance Events
# =============================================================================


class TestSessionIdInjection:
    """WORK-215: Every governance event includes session_id integer field."""

    def test_log_phase_transition_includes_session_id(self, tmp_path):
        """session_id from .claude/session appears in CyclePhaseEntered event."""
        from governance_events import log_phase_transition

        session_file = tmp_path / "session"
        session_file.write_text("# generated: 2026-02-24\n442\n")
        events_file = tmp_path / "governance-events.jsonl"

        with patch("governance_events.EVENTS_FILE", events_file), \
             patch("governance_events.SESSION_FILE", session_file):
            event = log_phase_transition("DO", "WORK-215", "Hephaestus")
            assert event["session_id"] == 442

    def test_log_session_start_includes_session_id(self, tmp_path):
        """session_id from .claude/session appears in SessionStarted event."""
        from governance_events import log_session_start

        session_file = tmp_path / "session"
        session_file.write_text("442\n")
        events_file = tmp_path / "governance-events.jsonl"

        with patch("governance_events.EVENTS_FILE", events_file), \
             patch("governance_events.SESSION_FILE", session_file):
            event = log_session_start(442, "Hephaestus")
            assert event["session_id"] == 442

    def test_log_session_end_includes_session_id(self, tmp_path):
        """session_id from .claude/session appears in SessionEnded event."""
        from governance_events import log_session_end

        session_file = tmp_path / "session"
        session_file.write_text("442\n")
        events_file = tmp_path / "governance-events.jsonl"

        with patch("governance_events.EVENTS_FILE", events_file), \
             patch("governance_events.SESSION_FILE", session_file):
            event = log_session_end(442, "Hephaestus")
            assert event["session_id"] == 442

    def test_session_id_defaults_to_zero_when_file_missing(self, tmp_path):
        """session_id defaults to 0 when .claude/session does not exist."""
        from governance_events import log_phase_transition

        session_file = tmp_path / "nonexistent" / "session"  # Does not exist
        events_file = tmp_path / "governance-events.jsonl"

        with patch("governance_events.EVENTS_FILE", events_file), \
             patch("governance_events.SESSION_FILE", session_file):
            event = log_phase_transition("PLAN", "WORK-215", "Hephaestus")
            assert event["session_id"] == 0

    def test_session_id_defaults_to_zero_when_malformed(self, tmp_path):
        """session_id defaults to 0 when file contains non-integer content."""
        from governance_events import log_phase_transition

        session_file = tmp_path / "session"
        session_file.write_text("not-an-integer\n")
        events_file = tmp_path / "governance-events.jsonl"

        with patch("governance_events.EVENTS_FILE", events_file), \
             patch("governance_events.SESSION_FILE", session_file):
            event = log_phase_transition("PLAN", "WORK-215", "Hephaestus")
            assert event["session_id"] == 0


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


# =============================================================================
# WORK-214: Governance Event Log Rotation Per Epoch
# =============================================================================


class TestArchiveGovernanceEvents:
    """WORK-214: Archive governance-events.jsonl to epoch directory on transition."""

    def _make_events_content(self, n_lines=3):
        """Helper: create n JSON lines of event content."""
        lines = []
        for i in range(n_lines):
            lines.append(json.dumps({"type": "TestEvent", "seq": i}) + "\n")
        return "".join(lines)

    def test_archive_governance_events_copies_to_epoch_dir(self, tmp_path, monkeypatch):
        """Test 1: Archive copies file content to epoch directory."""
        import governance_events
        from governance_events import archive_governance_events

        events_file = tmp_path / "governance-events.jsonl"
        content = self._make_events_content(3)
        events_file.write_text(content, encoding="utf-8")

        epoch_dir = tmp_path / "epochs" / "E2_8"
        epoch_dir.mkdir(parents=True)

        monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

        result = archive_governance_events(epoch_dir)

        archive_path = epoch_dir / "governance-events.jsonl"
        assert archive_path.exists()
        assert archive_path.read_text(encoding="utf-8") == content
        assert result["archived"] is True
        assert result["lines_archived"] == 3

    def test_archive_governance_events_truncates_live_file(self, tmp_path, monkeypatch):
        """Test 2: Archive truncates live file to empty after copying."""
        import governance_events
        from governance_events import archive_governance_events

        events_file = tmp_path / "governance-events.jsonl"
        content = self._make_events_content(3)
        events_file.write_text(content, encoding="utf-8")

        epoch_dir = tmp_path / "epochs" / "E2_8"
        epoch_dir.mkdir(parents=True)

        monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

        archive_governance_events(epoch_dir)

        assert events_file.exists()
        assert events_file.stat().st_size == 0

    def test_archive_governance_events_skips_when_source_missing(self, tmp_path, monkeypatch):
        """Test 3: Returns skipped when source events file does not exist."""
        import governance_events
        from governance_events import archive_governance_events

        events_file = tmp_path / "governance-events.jsonl"
        # Do NOT create the file

        epoch_dir = tmp_path / "epochs" / "E2_8"
        epoch_dir.mkdir(parents=True)

        monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

        result = archive_governance_events(epoch_dir)

        assert result["skipped"] is True
        assert result["archived"] is False
        assert result["lines_archived"] == 0
        assert not (epoch_dir / "governance-events.jsonl").exists()

    def test_archive_governance_events_raises_for_missing_epoch_dir(self, tmp_path, monkeypatch):
        """Test 4: Raises NotADirectoryError when epoch dir does not exist."""
        import governance_events
        from governance_events import archive_governance_events

        events_file = tmp_path / "governance-events.jsonl"
        events_file.write_text(json.dumps({"type": "TestEvent"}) + "\n", encoding="utf-8")

        monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

        with pytest.raises(NotADirectoryError, match="prior_epoch_dir does not exist"):
            archive_governance_events(tmp_path / "nonexistent_epoch")

    def test_archive_governance_events_idempotency_guard(self, tmp_path, monkeypatch):
        """Test 5: Second call with empty source does not overwrite non-empty archive."""
        import governance_events
        from governance_events import archive_governance_events

        events_file = tmp_path / "governance-events.jsonl"
        content = self._make_events_content(3)
        events_file.write_text(content, encoding="utf-8")

        epoch_dir = tmp_path / "epochs" / "E2_8"
        epoch_dir.mkdir(parents=True)

        monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

        # First call: archives and truncates
        first_result = archive_governance_events(epoch_dir)
        assert first_result["archived"] is True

        # Second call: source is now empty, archive has content
        second_result = archive_governance_events(epoch_dir)
        assert second_result["skipped"] is True
        assert second_result["archived"] is False

        # Archive still contains original content (not overwritten with empty)
        archive_path = epoch_dir / "governance-events.jsonl"
        assert archive_path.read_text(encoding="utf-8") == content

    def test_archive_governance_events_empty_source_archives(self, tmp_path, monkeypatch):
        """Test 6: Zero-byte source file archives empty file (guard does NOT fire)."""
        import governance_events
        from governance_events import archive_governance_events

        events_file = tmp_path / "governance-events.jsonl"
        events_file.write_text("", encoding="utf-8")  # 0-byte file

        epoch_dir = tmp_path / "epochs" / "E2_8"
        epoch_dir.mkdir(parents=True)

        monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

        result = archive_governance_events(epoch_dir)

        # Idempotency guard does NOT fire: no pre-existing archive with content
        assert result["archived"] is True
        assert result["lines_archived"] == 0
        archive_path = epoch_dir / "governance-events.jsonl"
        assert archive_path.exists()
        assert archive_path.stat().st_size == 0
