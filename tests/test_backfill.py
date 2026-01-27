# generated: 2025-12-24
# System Auto: last updated on: 2026-01-27T20:57:55
"""Tests for backfill.py - Work file backfill from backlog entries."""

import sys
from pathlib import Path

import pytest

# Add .claude/haios/lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


# Sample backlog content for testing
SAMPLE_BACKLOG = """
## Priority: High

### [HIGH] E2-021: Memory Reference Governance + Rhythm
- **Status:** pending
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Session:** 50, 65
- **Milestone:** M4-Research
- **Spawned By:** Session 50
- **Context:** Backlog items inconsistently link to memory concepts. No closed learning loop.
- **Vision:** APIP Memory Linkage Pattern
  - [ ] Add memory-specific MUST/SHOULD rules to CLAUDE.md
  - [ ] Add `memory_refs` field to backlog_item template
  - [ ] PreToolUse hook validates memory_refs on backlog.md edits

### [SMALL] E2-999: Fake Entry
- **Status:** proposed
- **Context:** This is a test entry.
"""

SAMPLE_ARCHIVE = """
# Backlog Archive

### [CLOSED] E2-010: Staleness Awareness Command
- **Status:** superseded
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Closed:** 2025-12-10 (Session 58)
- **Session:** 41
- **Context:** Auto-detect stale documentation using System Auto timestamps.
- **Resolution (Session 58):** Achieved via different mechanisms.
- **Memory:** Concept 62544
"""

SAMPLE_WORK_FILE = """---
template: work_item
id: E2-021
title: "Memory Reference Governance + Rhythm"
status: active
milestone: null
spawned_by: null
---
# WORK-E2-021: Memory Reference Governance + Rhythm

## Context

[Problem and root cause]

---

## Deliverables

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
"""


class TestParseBacklogEntry:
    """Test parse_backlog_entry function."""

    def test_parse_backlog_entry_extracts_fields(self):
        """Parse a backlog entry and extract key fields."""
        from backfill import parse_backlog_entry

        entry = parse_backlog_entry("E2-021", SAMPLE_BACKLOG)

        assert entry is not None
        assert entry["context"] is not None
        assert "memory" in entry["context"].lower()
        assert entry["milestone"] == "M4-Research"
        assert len(entry["deliverables"]) > 0
        assert entry["spawned_by"] == "Session 50"

    def test_parse_backlog_entry_not_found(self):
        """Return None if ID not found."""
        from backfill import parse_backlog_entry

        entry = parse_backlog_entry("E2-NONEXISTENT", SAMPLE_BACKLOG)
        assert entry is None

    def test_parse_archive_entry(self):
        """Parse archive entry with different format (has Closed, Resolution)."""
        from backfill import parse_backlog_entry

        entry = parse_backlog_entry("E2-010", SAMPLE_ARCHIVE)

        assert entry is not None
        assert entry["status"] == "closed"
        assert entry["closed_date"] is not None
        assert "2025-12-10" in entry["closed_date"]


class TestUpdateWorkFile:
    """Test update_work_file function."""

    def test_update_work_file_content(self, tmp_path):
        """Update work file Context and Deliverables sections."""
        from backfill import parse_backlog_entry, update_work_file

        # Create temp work file
        work_path = tmp_path / "WORK-E2-021-test.md"
        work_path.write_text(SAMPLE_WORK_FILE)

        # Parse backlog entry
        parsed = parse_backlog_entry("E2-021", SAMPLE_BACKLOG)

        # Update work file
        result = update_work_file(work_path, parsed)

        assert "[Problem and root cause]" not in result
        assert "inconsistently link" in result.lower()

    def test_update_work_file_frontmatter(self, tmp_path):
        """Update milestone, spawned_by in frontmatter."""
        from backfill import parse_backlog_entry, update_work_file

        # Create temp work file
        work_path = tmp_path / "WORK-E2-021-test.md"
        work_path.write_text(SAMPLE_WORK_FILE)

        # Parse backlog entry
        parsed = parse_backlog_entry("E2-021", SAMPLE_BACKLOG)

        # Update work file
        result = update_work_file(work_path, parsed)

        assert "milestone: M4-Research" in result
        assert 'spawned_by: "Session 50"' in result
