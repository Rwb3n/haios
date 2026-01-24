# generated: 2026-01-24
# System Auto: last updated on: 2026-01-24T18:37:13
"""
Tests for SessionLoader Module (CH-005)

TDD approach: Tests written before implementation.
"""
import sys
from pathlib import Path
from unittest.mock import Mock
import pytest

# Add lib path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestSessionLoaderConfig:
    """Tests for SessionLoader config loading."""

    def test_session_loader_loads_config(self):
        """SessionLoader reads session.yaml config file."""
        from session_loader import SessionLoader

        loader = SessionLoader()
        assert loader.config is not None
        # Config should have checkpoint_dir or output section
        assert "checkpoint_dir" in loader.config or "output" in loader.config


class TestSessionLoaderExtract:
    """Tests for SessionLoader extract method."""

    def test_extract_finds_latest_checkpoint(self, tmp_path):
        """extract() finds and parses latest checkpoint file."""
        from session_loader import SessionLoader

        # Setup: create two checkpoint files
        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "2026-01-22-session-228.md").write_text("---\nsession: 228\n---")
        (cp_dir / "2026-01-24-session-229.md").write_text("---\nsession: 229\npending: []\n---")

        loader = SessionLoader(checkpoint_dir=cp_dir)
        extracted = loader.extract()

        assert extracted["prior_session"] == 229  # Latest by name sort

    def test_extract_parses_memory_refs(self, tmp_path):
        """extract() gets load_memory_refs from checkpoint frontmatter."""
        from session_loader import SessionLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "2026-01-24-checkpoint.md").write_text("""---
session: 229
load_memory_refs:
  - 82302
  - 82303
---""")

        loader = SessionLoader(checkpoint_dir=cp_dir)
        extracted = loader.extract()

        assert extracted["memory_refs"] == [82302, 82303]


class TestSessionLoaderFormat:
    """Tests for SessionLoader format method."""

    def test_format_drift_prominent(self, tmp_path):
        """format() makes drift warnings visually prominent."""
        from session_loader import SessionLoader

        # Create minimal checkpoint for config loading
        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "2026-01-24-checkpoint.md").write_text("---\nsession: 229\n---")

        loader = SessionLoader(checkpoint_dir=cp_dir)
        extracted = {
            "prior_session": 228,
            "completed": ["WORK-009"],
            "pending": ["Next task"],
            "drift_observed": ["Stale work item"],
            "memory_refs": [],
            "memory_content": "Prior reasoning...",
        }

        formatted = loader.format(extracted)

        # Drift warnings should be prominent (e.g., with === or WARNING markers)
        assert "DRIFT" in formatted.upper() or "WARNING" in formatted.upper()
        assert "Stale work item" in formatted


class TestSessionLoaderLoad:
    """Tests for SessionLoader load method."""

    def test_load_returns_string(self, tmp_path):
        """load() returns formatted string for context injection."""
        from session_loader import SessionLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "2026-01-24-checkpoint.md").write_text("""---
session: 229
completed: [WORK-009]
pending: [Pick next work]
drift_observed: []
load_memory_refs: []
---""")

        loader = SessionLoader(checkpoint_dir=cp_dir)
        result = loader.load()

        assert isinstance(result, str)
        assert "SESSION" in result.upper()
        assert "229" in result
