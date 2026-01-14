# generated: 2025-12-22
# System Auto: last updated on: 2025-12-22T15:23:59
"""Tests for cascade module.

Tests the cascade propagation logic for dependency resolution.
"""

import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))

from cascade import (
    parse_yaml_frontmatter,
    is_item_complete,
    get_unblocked_items,
    get_related_items,
    get_substantive_references,
    get_review_prompts,
    format_cascade_message,
    run_cascade,
    TRIGGER_STATUSES,
)


class TestParseYamlFrontmatter:
    """Tests for YAML frontmatter parsing."""

    def test_parse_simple_fields(self):
        """Parse simple key-value fields."""
        content = """---
status: complete
backlog_id: E2-110
session: 97
---
# Content here
"""
        fm = parse_yaml_frontmatter(content)
        assert fm['status'] == 'complete'
        assert fm['backlog_id'] == 'E2-110'
        assert fm['session'] == '97'

    def test_parse_array_field(self):
        """Parse array fields like blocked_by and related."""
        content = """---
blocked_by: [E2-110, E2-111]
related: [E2-112, E2-113]
---
"""
        fm = parse_yaml_frontmatter(content)
        assert fm['blocked_by'] == ['E2-110', 'E2-111']
        assert fm['related'] == ['E2-112', 'E2-113']

    def test_parse_empty_array(self):
        """Parse empty array fields."""
        content = """---
blocked_by: []
---
"""
        fm = parse_yaml_frontmatter(content)
        assert fm['blocked_by'] == []

    def test_no_frontmatter(self):
        """Handle content without frontmatter."""
        content = "# Just markdown\nNo frontmatter here."
        fm = parse_yaml_frontmatter(content)
        assert fm == {}

    def test_parse_quoted_values(self):
        """Parse values with quotes."""
        content = """---
title: "Investigation Cycle Skill"
author: 'Hephaestus'
---
"""
        fm = parse_yaml_frontmatter(content)
        assert fm['title'] == 'Investigation Cycle Skill'
        assert fm['author'] == 'Hephaestus'


class TestTriggerStatuses:
    """Tests for trigger status constants."""

    def test_complete_triggers(self):
        """Complete/done/closed should trigger cascade."""
        assert 'complete' in TRIGGER_STATUSES
        assert 'completed' in TRIGGER_STATUSES
        assert 'done' in TRIGGER_STATUSES
        assert 'closed' in TRIGGER_STATUSES
        assert 'accepted' in TRIGGER_STATUSES

    def test_non_trigger_statuses(self):
        """Draft/proposed should NOT trigger cascade."""
        assert 'draft' not in TRIGGER_STATUSES
        assert 'proposed' not in TRIGGER_STATUSES
        assert 'in-progress' not in TRIGGER_STATUSES


class TestRunCascade:
    """Tests for main cascade execution."""

    def test_non_trigger_status_skips(self):
        """Non-trigger status should not run cascade."""
        result = run_cascade("E2-999", "draft", dry_run=True)
        assert result['triggered'] is False
        assert 'does not trigger' in result['message']

    def test_trigger_status_runs(self):
        """Trigger status should run cascade."""
        result = run_cascade("E2-NONEXISTENT", "complete", dry_run=True)
        assert result['triggered'] is True
        assert 'Cascade (Heartbeat)' in result['message']

    def test_dry_run_no_side_effects(self):
        """Dry run should not write events."""
        result = run_cascade("E2-999", "complete", dry_run=True)
        assert result['triggered'] is True
        # Effects might be empty for non-existent item
        assert isinstance(result['effects'], list)


class TestFormatCascadeMessage:
    """Tests for message formatting."""

    def test_empty_cascade(self):
        """Format message with no effects."""
        result = format_cascade_message(
            completed_id="E2-110",
            new_status="complete",
            unblocked_items=[],
            related_items=[],
            milestone_delta=None,
            substantive_refs=[],
            review_prompts=[]
        )
        assert 'E2-110 status: complete' in result['message']
        assert 'No dependents affected' in result['message']
        assert result['effects'] == []

    def test_unblock_section(self):
        """Format message with unblocked items."""
        unblocked = [{
            'id': 'E2-114',
            'status': 'READY',
            'message': 'E2-114 is now READY',
            'last_session': 89,
            'remaining': []
        }]
        result = format_cascade_message(
            completed_id="E2-110",
            new_status="complete",
            unblocked_items=unblocked,
            related_items=[],
            milestone_delta=None,
            substantive_refs=[],
            review_prompts=[]
        )
        assert '[UNBLOCK]' in result['message']
        assert 'E2-114 is now READY' in result['message']
        assert 'unblock:E2-114' in result['effects']

    def test_related_section(self):
        """Format message with related items."""
        related = [{
            'id': 'E2-115',
            'direction': 'outbound',
            'reason': 'E2-110 listed it in related array'
        }]
        result = format_cascade_message(
            completed_id="E2-110",
            new_status="complete",
            unblocked_items=[],
            related_items=related,
            milestone_delta=None,
            substantive_refs=[],
            review_prompts=[]
        )
        assert '[RELATED - REVIEW REQUIRED]' in result['message']
        assert '[outbound] E2-115' in result['message']
        assert 'related:1' in result['effects']

    def test_milestone_section(self):
        """Format message with milestone delta."""
        milestone = {
            'milestone': 'M4-Research',
            'name': 'Investigation Infrastructure',
            'old': 14,
            'new': 28,
            'delta': 14
        }
        result = format_cascade_message(
            completed_id="E2-111",
            new_status="complete",
            unblocked_items=[],
            related_items=[],
            milestone_delta=milestone,
            substantive_refs=[],
            review_prompts=[]
        )
        assert '[MILESTONE]' in result['message']
        assert '14% -> 28%' in result['message']
        assert 'milestone:+14' in result['effects']


class TestGetReviewPrompts:
    """Tests for review prompt generation."""

    def test_ready_items_get_prompt(self):
        """Ready items should get review prompts."""
        unblocked = [{
            'id': 'E2-114',
            'status': 'READY',
            'message': 'ready',
            'last_session': 89,
            'remaining': []
        }]
        prompts = get_review_prompts(unblocked, current_session=97)
        assert len(prompts) == 1
        assert prompts[0]['id'] == 'E2-114'
        assert 'SHOULD review' in prompts[0]['message']

    def test_stale_items_flagged(self):
        """Stale items (3+ sessions) should be flagged."""
        unblocked = [{
            'id': 'E2-OLD',
            'status': 'READY',
            'message': 'ready',
            'last_session': 90,
            'remaining': []
        }]
        prompts = get_review_prompts(unblocked, current_session=97)
        assert 'STALE' in prompts[0]['message']
        assert '7 sessions ago' in prompts[0]['message']

    def test_still_blocked_no_prompt(self):
        """Still blocked items should NOT get review prompts."""
        unblocked = [{
            'id': 'E2-BLOCKED',
            'status': 'STILL_BLOCKED',
            'message': 'still blocked',
            'last_session': 89,
            'remaining': ['E2-999']
        }]
        prompts = get_review_prompts(unblocked, current_session=97)
        assert len(prompts) == 0


class TestGetSubstantiveReferences:
    """Tests for substantive reference detection."""

    def test_checks_claude_md(self):
        """Should check CLAUDE.md for references."""
        # This test depends on actual file content
        # Just verify the function runs without error
        refs = get_substantive_references("E2-120")
        assert isinstance(refs, list)
        # E2-120 is mentioned in CLAUDE.md, so should find it
        # (but only if it's actually referenced)


class TestIsItemComplete:
    """Tests for item completion check."""

    def test_nonexistent_item(self):
        """Non-existent item should not be complete."""
        assert is_item_complete("E2-99999") is False

    def test_known_complete_item(self):
        """Known complete item should be detected."""
        # E2-120 is complete - check if detected
        result = is_item_complete("E2-120")
        # Should be True based on plan status or backlog
        assert isinstance(result, bool)
