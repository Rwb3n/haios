# generated: 2025-12-23
# System Auto: last updated on: 2025-12-23T19:21:10
"""Tests for work item closure functions (E2-152).

Tests the .claude/lib/work_item.py helper functions used by /close command.
"""
import pytest
from pathlib import Path
import tempfile
import shutil


class TestFindWorkFile:
    """Tests for find_work_file function."""

    def test_find_work_file_exists(self, tmp_path: Path):
        """Test that find_work_file returns path when work file exists."""
        # Setup: Create temp work directory structure
        active_dir = tmp_path / "docs" / "work" / "active"
        active_dir.mkdir(parents=True)
        work_file = active_dir / "WORK-E2-152-test-item.md"
        work_file.write_text("---\nstatus: active\n---\n# Test")

        # Import and patch
        import sys
        sys.path.insert(0, str(Path(".claude/lib").resolve()))
        from work_item import find_work_file, ACTIVE_DIR

        # Temporarily override ACTIVE_DIR for testing
        import work_item
        original_active = work_item.ACTIVE_DIR
        work_item.ACTIVE_DIR = active_dir

        try:
            # Action
            result = find_work_file("E2-152")

            # Assert
            assert result is not None
            assert result.exists()
            assert "WORK-E2-152" in result.name
        finally:
            work_item.ACTIVE_DIR = original_active

    def test_find_work_file_not_found_returns_none(self, tmp_path: Path):
        """Test that find_work_file returns None when no work file exists."""
        # Setup: Create empty temp work directory
        active_dir = tmp_path / "docs" / "work" / "active"
        active_dir.mkdir(parents=True)

        # Import and patch
        import sys
        sys.path.insert(0, str(Path(".claude/lib").resolve()))
        from work_item import find_work_file

        import work_item
        original_active = work_item.ACTIVE_DIR
        work_item.ACTIVE_DIR = active_dir

        try:
            # Action
            result = find_work_file("E2-999")  # non-existent

            # Assert
            assert result is None
        finally:
            work_item.ACTIVE_DIR = original_active


class TestUpdateWorkFileStatus:
    """Tests for update_work_file_status function."""

    def test_update_work_file_status(self, tmp_path: Path):
        """Test that work file status field is updated correctly."""
        # Setup: Create temp work file with status: active
        work_file = tmp_path / "WORK-E2-TEST.md"
        work_file.write_text(
            "---\ntemplate: work_item\nstatus: active\nclosed: null\n---\n# Test"
        )

        # Import
        import sys
        sys.path.insert(0, str(Path(".claude/lib").resolve()))
        from work_item import update_work_file_status

        # Action
        update_work_file_status(work_file, "complete")

        # Assert
        content = work_file.read_text()
        assert "status: complete" in content
        assert "status: active" not in content


class TestMoveWorkFileToArchive:
    """Tests for move_work_file_to_archive function."""

    def test_move_work_file_to_archive(self, tmp_path: Path):
        """Test that work file is moved from active/ to archive/."""
        # Setup: Create temp work directories and file
        active_dir = tmp_path / "docs" / "work" / "active"
        archive_dir = tmp_path / "docs" / "work" / "archive"
        active_dir.mkdir(parents=True)
        # Don't create archive_dir - function should create it

        work_file = active_dir / "WORK-E2-TEST.md"
        work_file.write_text("---\nstatus: complete\n---\n# Test")

        # Import and patch
        import sys
        sys.path.insert(0, str(Path(".claude/lib").resolve()))
        from work_item import move_work_file_to_archive

        import work_item
        original_archive = work_item.ARCHIVE_DIR
        work_item.ARCHIVE_DIR = archive_dir

        try:
            # Action
            new_path = move_work_file_to_archive(work_file)

            # Assert
            assert not work_file.exists(), "Original file should be moved"
            assert new_path.exists(), "File should exist in archive"
            assert new_path.parent == archive_dir
        finally:
            work_item.ARCHIVE_DIR = original_archive
