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
