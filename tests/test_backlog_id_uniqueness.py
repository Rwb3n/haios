# generated: 2025-12-23
# System Auto: last updated on: 2025-12-23T12:33:15
"""
Tests for Backlog ID Uniqueness Gate (E2-141).

Tests the PreToolUse hook check that prevents duplicate backlog_id values
across documents in docs/.
"""
import sys
from pathlib import Path

import pytest

# Add hook handlers to path for importing
hooks_dir = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"
if str(hooks_dir) not in sys.path:
    sys.path.insert(0, str(hooks_dir))


class TestBacklogIdUniqueness:
    """Test backlog_id uniqueness enforcement."""

    def test_blocks_duplicate_backlog_id(self, tmp_path, monkeypatch):
        """When backlog_id already exists in another file, block creation."""
        from pre_tool_use import _check_backlog_id_uniqueness

        # Setup: Create existing file with backlog_id
        docs_dir = tmp_path / "docs" / "plans"
        docs_dir.mkdir(parents=True)
        existing = docs_dir / "PLAN-E2-141-existing.md"
        existing.write_text("---\nbacklog_id: E2-141\n---\n# Content")

        # Mock cwd to tmp_path
        monkeypatch.chdir(tmp_path)

        # Try to create new file with same ID
        new_file = str(docs_dir / "PLAN-E2-141-new.md")
        content = "---\nbacklog_id: E2-141\n---\n# New Content"

        result = _check_backlog_id_uniqueness(new_file, content)

        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "E2-141" in result["hookSpecificOutput"]["permissionDecisionReason"]

    def test_allows_unique_backlog_id(self, tmp_path, monkeypatch):
        """When backlog_id is new, allow creation."""
        from pre_tool_use import _check_backlog_id_uniqueness

        docs_dir = tmp_path / "docs" / "plans"
        docs_dir.mkdir(parents=True)

        monkeypatch.chdir(tmp_path)

        new_file = str(docs_dir / "PLAN-E2-999-new.md")
        content = "---\nbacklog_id: E2-999\n---\n# Content"

        result = _check_backlog_id_uniqueness(new_file, content)

        assert result is None  # Allow

    def test_skips_files_without_backlog_id(self, tmp_path, monkeypatch):
        """Files without backlog_id field should pass through."""
        from pre_tool_use import _check_backlog_id_uniqueness

        monkeypatch.chdir(tmp_path)

        result = _check_backlog_id_uniqueness(
            "docs/random.md",
            "# Just some content\nNo frontmatter here"
        )

        assert result is None  # Allow

    def test_allows_edits_to_same_file(self, tmp_path, monkeypatch):
        """Editing an existing file with its own ID should be allowed."""
        from pre_tool_use import _check_backlog_id_uniqueness

        docs_dir = tmp_path / "docs" / "plans"
        docs_dir.mkdir(parents=True)
        existing = docs_dir / "PLAN-E2-141-existing.md"
        existing.write_text("---\nbacklog_id: E2-141\n---\n# Content")

        monkeypatch.chdir(tmp_path)

        # Edit the SAME file (not a new file)
        result = _check_backlog_id_uniqueness(
            str(existing),  # Same file path
            "---\nbacklog_id: E2-141\n---\n# Updated Content"
        )

        assert result is None  # Allow - editing same file

    def test_ignores_backlog_id_in_body_text(self, tmp_path, monkeypatch):
        """WORK-190: backlog_id in body text must NOT trigger false positive.

        When frontmatter has backlog_id: WORK-190 but body text references
        backlog_id: E2-141 (e.g., in code examples or references), the gate
        should extract WORK-190 from frontmatter, not E2-141 from body.
        """
        from pre_tool_use import _check_backlog_id_uniqueness

        docs_dir = tmp_path / "docs" / "plans"
        docs_dir.mkdir(parents=True)

        # Existing legacy plan with E2-141
        existing = docs_dir / "PLAN-E2-141-existing.md"
        existing.write_text("---\nbacklog_id: E2-141\n---\n# Legacy Content")

        monkeypatch.chdir(tmp_path)

        # New file with WORK-190 in frontmatter, but E2-141 mentioned in body
        new_file = str(tmp_path / "docs" / "work" / "active" / "WORK-190" / "plans" / "PLAN.md")
        content = (
            "---\nbacklog_id: WORK-190\n---\n"
            "# Implementation Plan\n\n"
            "This fixes the backlog_id: E2-141 gate that was created in Session 103.\n"
        )

        result = _check_backlog_id_uniqueness(new_file, content)

        # Should allow — WORK-190 is unique, body text E2-141 reference is irrelevant
        assert result is None

    def test_extracts_from_frontmatter_not_body(self, tmp_path, monkeypatch):
        """WORK-190: Gate must extract backlog_id from frontmatter only.

        File with no frontmatter backlog_id but body text containing
        backlog_id: E2-141 should NOT trigger the gate.
        """
        from pre_tool_use import _check_backlog_id_uniqueness

        docs_dir = tmp_path / "docs" / "plans"
        docs_dir.mkdir(parents=True)

        existing = docs_dir / "PLAN-E2-141-existing.md"
        existing.write_text("---\nbacklog_id: E2-141\n---\n# Content")

        monkeypatch.chdir(tmp_path)

        # File without backlog_id in frontmatter, only in body
        new_file = str(docs_dir / "some-doc.md")
        content = (
            "---\ntitle: Some Doc\n---\n"
            "# Body\n\n"
            "Example: backlog_id: E2-141\n"
        )

        result = _check_backlog_id_uniqueness(new_file, content)

        # Should allow — no backlog_id in frontmatter
        assert result is None

    def test_frontmatter_duplicate_still_blocked(self, tmp_path, monkeypatch):
        """WORK-190: Actual frontmatter duplicates are still correctly blocked."""
        from pre_tool_use import _check_backlog_id_uniqueness

        docs_dir = tmp_path / "docs" / "plans"
        docs_dir.mkdir(parents=True)

        existing = docs_dir / "PLAN-WORK-190-existing.md"
        existing.write_text("---\nbacklog_id: WORK-190\n---\n# Content")

        monkeypatch.chdir(tmp_path)

        new_file = str(docs_dir / "PLAN-WORK-190-new.md")
        content = "---\nbacklog_id: WORK-190\n---\n# New Content"

        result = _check_backlog_id_uniqueness(new_file, content)

        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "WORK-190" in result["hookSpecificOutput"]["permissionDecisionReason"]
