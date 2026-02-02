# generated: 2026-02-02
# System Auto: last updated on: 2026-02-02T08:56:42
"""Tests for decision traceability validation.

Validates bidirectional traceability between epoch decisions and chapter files:
- Decisions in EPOCH.md should have assigned_to fields
- Chapter files should have implements_decisions fields
- Both directions should be consistent
"""
import pytest
from pathlib import Path
import sys

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from audit_decision_coverage import (
    parse_epoch_decisions,
    parse_chapter_refs,
    validate_decision_coverage,
    validate_chapter_traceability,
    validate_bidirectional,
    ValidationResult,
)


class TestDecisionWithoutAssignedTo:
    """Test 1: Decision without assigned_to triggers warning."""

    def test_decision_without_assigned_to_warns(self):
        """Validation warns when decision lacks assigned_to field."""
        epoch_content = """
## Core Decisions

### Decision 1: Test Decision

This is a prose-only decision with no assigned_to field.
The validation should warn about this.

### Decision 2: Another Decision

More prose without traceability.
"""
        result = validate_decision_coverage(epoch_content)
        assert "D1 has no assigned_to field" in result.warnings
        assert "D2 has no assigned_to field" in result.warnings

    def test_decision_with_assigned_to_no_warning(self):
        """Decision with assigned_to should not trigger warning."""
        epoch_content = """
## Core Decisions

### Decision 1: Test Decision

assigned_to:
  - arc: flow
    chapters: [CH-009]

This decision has proper traceability.
"""
        result = validate_decision_coverage(epoch_content)
        assert "D1 has no assigned_to field" not in result.warnings


class TestChapterMissingImplementsDecisions:
    """Test 2: Chapter without implements_decisions field detected."""

    def test_chapter_missing_implements_decisions(self):
        """Validation detects chapters without implements_decisions."""
        chapter_content = """
# Chapter: TestChapter

## Definition

**Chapter ID:** CH-001
**Arc:** activities
**Status:** Draft
**Depends:** None

This chapter has no implements_decisions field.
"""
        result = validate_chapter_traceability(chapter_content, "CH-001")
        assert "CH-001 missing implements_decisions field" in result.warnings

    def test_chapter_with_implements_decisions_no_warning(self):
        """Chapter with implements_decisions should not trigger warning."""
        chapter_content = """
# Chapter: TestChapter

## Definition

**Chapter ID:** CH-009
**Arc:** flow
**Status:** Draft
**implements_decisions:** [D8]
**Depends:** None
"""
        result = validate_chapter_traceability(chapter_content, "CH-009")
        assert "CH-009 missing implements_decisions field" not in result.warnings


class TestBidirectionalTraceability:
    """Test 3: Bidirectional consistency check."""

    def test_bidirectional_traceability_consistent(self):
        """Decision assigned_to matches chapter implements_decisions."""
        epoch_decisions = {
            "D1": {"assigned_to": [{"arc": "flow", "chapters": ["CH-009"]}]}
        }
        chapter_refs = {
            "flow/CH-009": {"implements_decisions": ["D1"]}
        }
        result = validate_bidirectional(epoch_decisions, chapter_refs)
        assert result.is_consistent
        assert result.orphan_decisions == []
        assert result.orphan_chapters == []

    def test_orphan_decision_detected(self):
        """Decision not claimed by any chapter is orphan."""
        epoch_decisions = {
            "D1": {"assigned_to": [{"arc": "flow", "chapters": ["CH-009"]}]},
            "D2": {"assigned_to": [{"arc": "flow", "chapters": ["CH-010"]}]}
        }
        chapter_refs = {
            "flow/CH-009": {"implements_decisions": ["D1"]}
            # CH-010 doesn't exist or doesn't claim D2
        }
        result = validate_bidirectional(epoch_decisions, chapter_refs)
        assert not result.is_consistent
        assert "D2" in result.orphan_decisions

    def test_orphan_chapter_claim_detected(self):
        """Chapter claiming non-existent decision is error."""
        epoch_decisions = {
            "D1": {"assigned_to": [{"arc": "flow", "chapters": ["CH-009"]}]}
        }
        chapter_refs = {
            "flow/CH-009": {"implements_decisions": ["D1", "D99"]}  # D99 doesn't exist
        }
        result = validate_bidirectional(epoch_decisions, chapter_refs)
        assert not result.is_consistent
        assert "flow/CH-009 claims D99 which doesn't exist" in result.errors
