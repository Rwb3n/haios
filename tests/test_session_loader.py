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


# =============================================================================
# WORK-156: Checkpoint pending item staleness detection
# =============================================================================


class TestValidatePendingItems:
    """WORK-156: validate_pending_items annotates stale pending items."""

    def test_validate_pending_resolves_terminal_work_id(self, tmp_path):
        """T1: WORK-ID with terminal status gets [RESOLVED] prefix."""
        from session_loader import SessionLoader

        loader = SessionLoader(checkpoint_dir=tmp_path, work_status_fn=lambda wid: "complete")
        result = loader.validate_pending_items(["WORK-100: Do something"], checkpoint_session=385)
        assert result == ["[RESOLVED] WORK-100: Do something"]

    def test_validate_pending_keeps_active_work_id(self, tmp_path):
        """T2: WORK-ID with active status passes through unchanged."""
        from session_loader import SessionLoader

        loader = SessionLoader(checkpoint_dir=tmp_path, work_status_fn=lambda wid: "active")
        result = loader.validate_pending_items(["WORK-101: Still working"], checkpoint_session=385)
        assert result == ["WORK-101: Still working"]

    def test_validate_pending_age_marker_free_text(self, tmp_path):
        """T3: Free-text items get age marker with session number."""
        from session_loader import SessionLoader

        loader = SessionLoader(checkpoint_dir=tmp_path)
        result = loader.validate_pending_items(["Fix the bug in checkout"], checkpoint_session=385)
        assert result == ["(pending since session 385) Fix the bug in checkout"]

    def test_validate_pending_mixed_items(self, tmp_path):
        """T4: Mixed WORK-ID and free-text items annotated correctly."""
        from session_loader import SessionLoader

        def mock_status(wid):
            return {"WORK-100": "complete", "WORK-101": "active"}.get(wid)

        loader = SessionLoader(checkpoint_dir=tmp_path, work_status_fn=mock_status)
        result = loader.validate_pending_items(
            ["WORK-100: Done", "Fix bug", "WORK-101: Active"], checkpoint_session=385
        )
        assert result == [
            "[RESOLVED] WORK-100: Done",
            "(pending since session 385) Fix bug",
            "WORK-101: Active",
        ]

    def test_validate_pending_no_status_fn_passthrough(self, tmp_path):
        """T5: Without work_status_fn, WORK-ID items pass through unchanged."""
        from session_loader import SessionLoader

        loader = SessionLoader(checkpoint_dir=tmp_path)
        result = loader.validate_pending_items(["WORK-100: Something"], checkpoint_session=385)
        assert result == ["WORK-100: Something"]


class TestExtractIntegration:
    """WORK-156: extract() integrates validate_pending_items."""

    def test_extract_annotates_pending_items(self, tmp_path):
        """T8: extract() calls validate_pending_items on pending items."""
        from session_loader import SessionLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "2026-02-16-SESSION-387-checkpoint.md").write_text(
            '---\nsession: 387\npending:\n  - "WORK-100: Resolved task"\n  - "Free text item"\n---'
        )

        loader = SessionLoader(
            checkpoint_dir=cp_dir,
            work_status_fn=lambda wid: "complete" if wid == "WORK-100" else None,
        )
        extracted = loader.extract()

        assert "[RESOLVED]" in extracted["pending"][0]
        assert "pending since session 387" in extracted["pending"][1]


# =============================================================================
# WORK-130: Checkpoint discovery sorts by session number, not filename
# =============================================================================


class TestCheckpointDiscoveryOrder:
    """WORK-130: _find_latest_checkpoint must pick highest session number."""

    def test_find_latest_checkpoint_mixed_sequence_numbers(self, tmp_path):
        """WORK-130 T1: Checkpoint without sequence number should not outrank higher-session checkpoint."""
        from session_loader import SessionLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)

        # S345 has no sequence number (sorts lexically AFTER 07-SESSION-348)
        (cp_dir / "2026-02-11-SESSION-345-closure.md").write_text(
            "---\nsession: 345\n---"
        )
        # S348 has sequence number 07
        (cp_dir / "2026-02-11-07-SESSION-348-bug-fixes.md").write_text(
            "---\nsession: 348\npending: [CH-016]\n---"
        )
        # S340 has sequence number 01
        (cp_dir / "2026-02-11-01-SESSION-340-tiny-fixes.md").write_text(
            "---\nsession: 340\n---"
        )

        loader = SessionLoader(checkpoint_dir=cp_dir)
        extracted = loader.extract()

        assert extracted["prior_session"] == 348, \
            f"Should find session 348 (highest), got {extracted['prior_session']}"

    def test_find_latest_checkpoint_consistent_sequence(self, tmp_path):
        """WORK-130 T2: When all checkpoints have sequence numbers, highest wins."""
        from session_loader import SessionLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)

        (cp_dir / "2026-02-11-01-SESSION-340-x.md").write_text("---\nsession: 340\n---")
        (cp_dir / "2026-02-11-02-SESSION-341-x.md").write_text("---\nsession: 341\n---")
        (cp_dir / "2026-02-11-03-SESSION-343-x.md").write_text("---\nsession: 343\n---")

        loader = SessionLoader(checkpoint_dir=cp_dir)
        extracted = loader.extract()

        assert extracted["prior_session"] == 343


# =============================================================================
# WORK-166: Checkpoint same-session sort tie-breaking
# =============================================================================


class TestCheckpointSortTieBreaking:
    """WORK-166: _find_latest_checkpoint breaks ties by date prefix when session numbers match."""

    def test_find_latest_checkpoint_tiebreak(self, tmp_path):
        """WORK-166 T1: Same session number, different date prefix — pick latest prefix."""
        from session_loader import SessionLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "2025-12-21-04-SESSION-94-early.md").write_text("---\nsession: 94\n---\n")
        (cp_dir / "2025-12-21-05-SESSION-94-late.md").write_text("---\nsession: 94\n---\n")

        loader = SessionLoader(checkpoint_dir=cp_dir)
        result = loader._find_latest_checkpoint()

        assert result is not None
        assert "05-SESSION-94-late" in result.name, \
            f"Should pick -05- prefix (latest), got {result.name}"

    def test_find_latest_checkpoint_no_date_prefix_backward_compat(self, tmp_path):
        """WORK-166 T5: Checkpoints without date prefix still sort by session number."""
        from session_loader import SessionLoader

        cp_dir = tmp_path / "docs" / "checkpoints"
        cp_dir.mkdir(parents=True)
        (cp_dir / "SESSION-100-foo.md").write_text("---\nsession: 100\n---\n")
        (cp_dir / "SESSION-99-bar.md").write_text("---\nsession: 99\n---\n")

        loader = SessionLoader(checkpoint_dir=cp_dir)
        result = loader._find_latest_checkpoint()

        assert result is not None
        assert "SESSION-100" in result.name
