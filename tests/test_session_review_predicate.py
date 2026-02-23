# generated: 2026-02-23
"""
Tests for session_review_predicate module (WORK-209).

Tests the computable predicate that determines whether session-review-cycle
should run at session-end. Predicate is OR logic:
  - At least 1 close event in session-log.jsonl, OR
  - At least 2 RetroCycleCompleted events in governance-events.jsonl
"""
import json

import pytest


def test_should_run_when_close_event_exists(tmp_path):
    """Predicate passes when at least 1 close event exists in session log."""
    session_log = tmp_path / "session-log.jsonl"
    session_log.write_text(
        json.dumps({"t": "close", "v": "WORK-100", "w": "WORK-100", "ts": "15:00"}) + "\n",
        encoding="utf-8",
    )
    governance_events = tmp_path / "governance-events.jsonl"
    governance_events.write_text("", encoding="utf-8")

    from session_review_predicate import should_run_session_review

    assert should_run_session_review(
        session_log_path=session_log,
        governance_events_path=governance_events,
    ) is True


def test_should_run_when_two_retro_completed(tmp_path):
    """Predicate passes when at least 2 RetroCycleCompleted events exist."""
    session_log = tmp_path / "session-log.jsonl"
    session_log.write_text("", encoding="utf-8")

    governance_events = tmp_path / "governance-events.jsonl"
    events = [
        {"type": "RetroCycleCompleted", "work_id": "WORK-100", "timestamp": "2026-02-23T15:00:00"},
        {"type": "RetroCycleCompleted", "work_id": "WORK-101", "timestamp": "2026-02-23T16:00:00"},
    ]
    governance_events.write_text(
        "\n".join(json.dumps(e) for e in events) + "\n",
        encoding="utf-8",
    )

    from session_review_predicate import should_run_session_review

    assert should_run_session_review(
        session_log_path=session_log,
        governance_events_path=governance_events,
    ) is True


def test_should_not_run_when_no_qualifying_events(tmp_path):
    """Predicate fails when 0 close events and only 1 retro event (below threshold)."""
    session_log = tmp_path / "session-log.jsonl"
    session_log.write_text(
        json.dumps({"t": "phase", "v": "PLAN->DO", "w": "WORK-100", "ts": "14:00"}) + "\n",
        encoding="utf-8",
    )

    governance_events = tmp_path / "governance-events.jsonl"
    governance_events.write_text(
        json.dumps({"type": "RetroCycleCompleted", "work_id": "WORK-100", "timestamp": "2026-02-23T15:00:00"}) + "\n",
        encoding="utf-8",
    )

    from session_review_predicate import should_run_session_review

    assert should_run_session_review(
        session_log_path=session_log,
        governance_events_path=governance_events,
    ) is False


def test_should_not_run_when_files_missing(tmp_path):
    """Predicate returns False (not raises) when log files do not exist."""
    nonexistent_session = tmp_path / "nonexistent" / "session-log.jsonl"
    nonexistent_governance = tmp_path / "nonexistent" / "governance-events.jsonl"

    from session_review_predicate import should_run_session_review

    result = should_run_session_review(
        session_log_path=nonexistent_session,
        governance_events_path=nonexistent_governance,
    )
    assert result is False


def test_one_retro_does_not_pass_threshold(tmp_path):
    """Exactly 1 RetroCycleCompleted event does not meet the >= 2 threshold."""
    session_log = tmp_path / "session-log.jsonl"
    session_log.write_text("", encoding="utf-8")

    governance_events = tmp_path / "governance-events.jsonl"
    governance_events.write_text(
        json.dumps({"type": "RetroCycleCompleted", "work_id": "WORK-100", "timestamp": "2026-02-23T15:00:00"}) + "\n",
        encoding="utf-8",
    )

    from session_review_predicate import should_run_session_review

    assert should_run_session_review(
        session_log_path=session_log,
        governance_events_path=governance_events,
    ) is False
