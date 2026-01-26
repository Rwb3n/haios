# generated: 2026-01-26
# System Auto: last updated on: 2026-01-26T20:12:20
"""
Tests for orphan session detection (E2-236).

Tests:
1. detect_orphan_session_finds_orphan - Detect when SessionStarted without SessionEnded
2. detect_orphan_session_no_orphan - No orphan when all sessions ended
3. scan_incomplete_work_finds_exited_null - Find WORK.md with exited: null
4. log_session_start - Log SessionStarted event
5. log_session_end - Log SessionEnded event
6. existing_log_phase_transition_unchanged - Backward compatibility
"""
import json
import sys
from pathlib import Path

import pytest

# Add the lib path for imports (haios/lib is canonical, .claude/lib is deprecated)
LIB_PATH = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
# Remove deprecated path if present to avoid import confusion
DEPRECATED_LIB_PATH = str(Path(__file__).parent.parent / ".claude" / "lib")
if DEPRECATED_LIB_PATH in sys.path:
    sys.path.remove(DEPRECATED_LIB_PATH)
if str(LIB_PATH) not in sys.path:
    sys.path.insert(0, str(LIB_PATH))


class TestDetectOrphanSession:
    """Tests for detect_orphan_session function."""

    def test_detect_orphan_session_finds_orphan(self, tmp_path: Path):
        """Detect orphan when SessionStarted exists without SessionEnded."""
        from governance_events import detect_orphan_session

        events_file = tmp_path / "events.jsonl"
        events_file.write_text(
            '{"type": "SessionStarted", "session": 100, "timestamp": "2026-01-26T10:00:00"}\n'
            '{"type": "SessionStarted", "session": 101, "timestamp": "2026-01-26T11:00:00"}\n'
        )

        result = detect_orphan_session(events_file)

        assert result is not None
        assert result["orphan_session"] == 100
        assert result["current_session"] == 101

    def test_detect_orphan_session_no_orphan(self, tmp_path: Path):
        """No orphan when all SessionStarted have matching SessionEnded."""
        from governance_events import detect_orphan_session

        events_file = tmp_path / "events.jsonl"
        events_file.write_text(
            '{"type": "SessionStarted", "session": 100, "timestamp": "2026-01-26T10:00:00"}\n'
            '{"type": "SessionEnded", "session": 100, "timestamp": "2026-01-26T10:30:00"}\n'
            '{"type": "SessionStarted", "session": 101, "timestamp": "2026-01-26T11:00:00"}\n'
        )

        result = detect_orphan_session(events_file)

        # Session 101 is current (not ended yet), not orphan
        assert result is None

    def test_detect_orphan_empty_file(self, tmp_path: Path):
        """No orphan when events file is empty."""
        from governance_events import detect_orphan_session

        events_file = tmp_path / "events.jsonl"
        events_file.write_text("")

        result = detect_orphan_session(events_file)

        assert result is None

    def test_detect_orphan_file_not_exists(self, tmp_path: Path):
        """No orphan when events file doesn't exist."""
        from governance_events import detect_orphan_session

        events_file = tmp_path / "nonexistent.jsonl"

        result = detect_orphan_session(events_file)

        assert result is None


class TestScanIncompleteWork:
    """Tests for scan_incomplete_work function."""

    def test_scan_incomplete_work_finds_exited_null(self, tmp_path: Path):
        """Find work items with exited: null in node_history."""
        from governance_events import scan_incomplete_work

        # Create work directory structure
        work_dir = tmp_path / "docs" / "work" / "active" / "E2-999"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text(
            """---
id: E2-999
title: Test Work Item
node_history:
- node: doing
  entered: 2026-01-26 10:00:00
  exited: null
---
# Test Work Item
"""
        )

        result = scan_incomplete_work(tmp_path)

        assert len(result) == 1
        assert result[0]["id"] == "E2-999"
        assert result[0]["incomplete_node"] == "doing"

    def test_scan_incomplete_work_no_incomplete(self, tmp_path: Path):
        """No incomplete work when all transitions are complete."""
        from governance_events import scan_incomplete_work

        work_dir = tmp_path / "docs" / "work" / "active" / "E2-888"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text(
            """---
id: E2-888
title: Complete Work Item
node_history:
- node: doing
  entered: 2026-01-26 10:00:00
  exited: 2026-01-26 11:00:00
---
"""
        )

        result = scan_incomplete_work(tmp_path)

        assert len(result) == 0

    def test_scan_incomplete_work_empty_dir(self, tmp_path: Path):
        """No incomplete work when work directory is empty."""
        from governance_events import scan_incomplete_work

        # Create empty work directories
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "blocked").mkdir(parents=True)

        result = scan_incomplete_work(tmp_path)

        assert len(result) == 0


class TestSessionEventLogging:
    """Tests for session event logging functions."""

    def test_log_session_start(self, tmp_path: Path, monkeypatch):
        """Log SessionStarted event to events file."""
        from governance_events import log_session_start, EVENTS_FILE

        events_file = tmp_path / "events.jsonl"
        monkeypatch.setattr("governance_events.EVENTS_FILE", events_file)

        event = log_session_start(session_number=245, agent="Hephaestus")

        assert event["type"] == "SessionStarted"
        assert event["session"] == 245
        assert event["agent"] == "Hephaestus"
        assert "timestamp" in event

        # Verify written to file
        content = events_file.read_text()
        assert "SessionStarted" in content
        assert "245" in content

    def test_log_session_end(self, tmp_path: Path, monkeypatch):
        """Log SessionEnded event to events file."""
        from governance_events import log_session_end

        events_file = tmp_path / "events.jsonl"
        monkeypatch.setattr("governance_events.EVENTS_FILE", events_file)

        event = log_session_end(session_number=245, agent="Hephaestus")

        assert event["type"] == "SessionEnded"
        assert event["session"] == 245
        assert event["agent"] == "Hephaestus"
        assert "timestamp" in event

        # Verify written to file
        content = events_file.read_text()
        assert "SessionEnded" in content


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing functions."""

    def test_existing_log_phase_transition_unchanged(self, tmp_path: Path, monkeypatch):
        """Verify log_phase_transition still works as before."""
        from governance_events import log_phase_transition

        events_file = tmp_path / "events.jsonl"
        monkeypatch.setattr("governance_events.EVENTS_FILE", events_file)

        event = log_phase_transition("PLAN", "E2-236", "Hephaestus")

        assert event["type"] == "CyclePhaseEntered"
        assert event["phase"] == "PLAN"
        assert event["work_id"] == "E2-236"
        assert event["agent"] == "Hephaestus"

    def test_existing_log_validation_outcome_unchanged(self, tmp_path: Path, monkeypatch):
        """Verify log_validation_outcome still works as before."""
        from governance_events import log_validation_outcome

        events_file = tmp_path / "events.jsonl"
        monkeypatch.setattr("governance_events.EVENTS_FILE", events_file)

        event = log_validation_outcome("preflight", "E2-236", "pass", "All checks passed")

        assert event["type"] == "ValidationOutcome"
        assert event["gate"] == "preflight"
        assert event["result"] == "pass"
