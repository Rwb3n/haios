# generated: 2026-02-23
"""
Tests for PreToolUse ProcessReviewApproved gate (WORK-209).

Tests that writes to manifesto/L3/ and manifesto/L4/ are blocked
unless a ProcessReviewApproved governance event exists.
"""
import importlib
import json
import sys
from pathlib import Path


def _load_pre_tool_use():
    """Load pre_tool_use module from hooks directory."""
    hooks_dir = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"
    if str(hooks_dir) not in sys.path:
        sys.path.insert(0, str(hooks_dir))
    # Use importlib to avoid name collision with any cached module
    spec = importlib.util.spec_from_file_location(
        "pre_tool_use_hooks", hooks_dir / "pre_tool_use.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_governance_events():
    """Load governance_events module from lib directory."""
    lib_dir = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
    if str(lib_dir) not in sys.path:
        sys.path.insert(0, str(lib_dir))
    import governance_events
    return governance_events


def test_l3_write_blocked_without_process_review_approved(tmp_path, monkeypatch):
    """Write to manifesto/L3/ is blocked when no ProcessReviewApproved event exists."""
    governance_events = _load_governance_events()
    events_file = tmp_path / "governance-events.jsonl"
    events_file.write_text("", encoding="utf-8")
    monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

    pre_tool_use = _load_pre_tool_use()
    result = pre_tool_use._check_process_review_gate(
        ".claude/haios/manifesto/L3/principles.md"
    )

    assert result is not None
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "ProcessReviewApproved" in result["hookSpecificOutput"]["permissionDecisionReason"]


def test_l3_write_allowed_with_process_review_approved(tmp_path, monkeypatch):
    """Write to manifesto/L3/ is allowed when ProcessReviewApproved event exists."""
    governance_events = _load_governance_events()
    events_file = tmp_path / "governance-events.jsonl"
    events_file.write_text(
        json.dumps({
            "type": "ProcessReviewApproved",
            "proposal_id": "P1",
            "target": ".claude/haios/manifesto/L3/principles.md",
            "scope": "l3_principle",
            "session": 435,
            "timestamp": "2026-02-23T17:00:00",
        }) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

    pre_tool_use = _load_pre_tool_use()
    result = pre_tool_use._check_process_review_gate(
        ".claude/haios/manifesto/L3/principles.md"
    )

    assert result is None


def test_non_manifesto_path_not_affected():
    """Non-manifesto paths are not affected by the ProcessReview gate."""
    pre_tool_use = _load_pre_tool_use()
    result = pre_tool_use._check_process_review_gate(
        "docs/work/active/WORK-100/WORK.md"
    )

    assert result is None
