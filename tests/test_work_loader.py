# generated: 2026-01-24
# System Auto: last updated on: 2026-01-24T19:44:51
"""
Tests for WorkLoader Module (CH-006)

TDD approach: Tests written before implementation.
"""
import sys
from pathlib import Path
from unittest.mock import Mock
import pytest

# Add lib path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestWorkLoaderConfig:
    """Tests for WorkLoader config loading."""

    def test_work_loader_loads_config(self):
        """WorkLoader reads work.yaml config file."""
        from work_loader import WorkLoader
        loader = WorkLoader()
        assert loader.config is not None
        assert "queue" in loader.config or "output" in loader.config


class TestWorkLoaderExtract:
    """Tests for WorkLoader extract method."""

    def test_extract_parses_queue_output(self):
        """extract() parses queue command output."""
        from work_loader import WorkLoader
        # Mock queue_fn returns list of work items
        mock_queue = lambda: [
            {"id": "E2-072", "title": "Critique Subagent", "priority": "medium"},
            {"id": "E2-236", "title": "Orphan Detection", "priority": "medium"},
        ]
        loader = WorkLoader(queue_fn=mock_queue)
        extracted = loader.extract()
        assert len(extracted["queue"]) == 2
        assert extracted["queue"][0]["id"] == "E2-072"

    def test_extract_gets_pending_from_checkpoint(self, tmp_path):
        """extract() gets pending items from checkpoint."""
        from work_loader import WorkLoader
        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "2026-01-24-checkpoint.md").write_text("""---
session: 230
pending:
  - CH-006 Work Loader
  - INV-068 Cycle Delegation
---""")
        # Use mock queue to avoid subprocess
        mock_queue = lambda: []
        loader = WorkLoader(checkpoint_dir=cp_dir, queue_fn=mock_queue)
        extracted = loader.extract()
        assert "CH-006" in str(extracted["pending"])


class TestWorkLoaderFormat:
    """Tests for WorkLoader format method."""

    def test_format_warns_on_epoch_mismatch(self):
        """format() warns when queue items are from prior epochs."""
        from work_loader import WorkLoader
        # Use mock queue to avoid subprocess
        mock_queue = lambda: []
        loader = WorkLoader(queue_fn=mock_queue)
        extracted = {
            "queue": [{"id": "E2-072", "title": "Old epoch item"}],
            "pending": [],
            "current_epoch": "E2.3",
            "legacy_count": 1,
            "queue_limit": 5,
        }
        formatted = loader.format(extracted)
        assert "WARNING" in formatted or "prior epoch" in formatted.lower()


# =============================================================================
# WORK-156: WorkLoader checkpoint sort bug fix
# =============================================================================


class TestWorkLoaderCheckpointSort:
    """WORK-156: _get_pending_from_checkpoint uses session-number sort."""

    def test_work_loader_find_latest_by_session_number(self, tmp_path):
        """T6: Picks checkpoint by highest session number, not lexicographic."""
        from work_loader import WorkLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "2026-02-11-SESSION-345-closure.md").write_text(
            "---\nsession: 345\npending:\n  - old\n---"
        )
        (cp_dir / "2026-02-11-07-SESSION-348-bug-fixes.md").write_text(
            "---\nsession: 348\npending:\n  - new\n---"
        )
        (cp_dir / "2026-02-11-01-SESSION-340-tiny.md").write_text(
            "---\nsession: 340\npending:\n  - oldest\n---"
        )

        loader = WorkLoader(checkpoint_dir=cp_dir, queue_fn=lambda: [])
        pending = loader._get_pending_from_checkpoint()
        assert pending == ["new"], f"Should pick SESSION-348 (highest), got {pending}"

    def test_work_loader_excludes_readme(self, tmp_path):
        """T7: README.md excluded from checkpoint discovery."""
        from work_loader import WorkLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "README.md").write_text("# Checkpoints")
        (cp_dir / "2026-02-11-SESSION-340-x.md").write_text(
            "---\nsession: 340\npending:\n  - item\n---"
        )

        loader = WorkLoader(checkpoint_dir=cp_dir, queue_fn=lambda: [])
        pending = loader._get_pending_from_checkpoint()
        assert pending == ["item"]


class TestWorkLoaderLoad:
    """Tests for WorkLoader load method."""

    def test_load_returns_formatted_string(self):
        """load() returns formatted string for context injection."""
        from work_loader import WorkLoader
        mock_queue = lambda: [{"id": "WORK-010", "title": "Test", "priority": "medium"}]
        loader = WorkLoader(queue_fn=mock_queue)
        result = loader.load()
        assert isinstance(result, str)
        assert "WORK" in result.upper()
