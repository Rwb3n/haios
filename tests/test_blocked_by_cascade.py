# generated: 2026-02-19
# WORK-173: Tests for blocked_by cascade on work closure
"""
Tests for blocked_by_cascade.py — clears blocked_by references
in downstream WORK.md files when a work item closes.

Uses tmp_path for isolation. Tests both flow-style and block-style
YAML blocked_by formats found in production files.
"""
import json
import sys
import yaml
from pathlib import Path

import pytest

# Add lib/ to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from blocked_by_cascade import clear_blocked_by, _format_blocked_by, _replace_blocked_by_block


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_work_file(base: Path, work_id: str, blocked_by_yaml: str, extra: str = "") -> Path:
    """Create a minimal WORK.md with specified blocked_by content."""
    active = base / "docs" / "work" / "active" / work_id
    active.mkdir(parents=True, exist_ok=True)
    work_file = active / "WORK.md"
    content = f"""---
id: {work_id}
title: "Test item {work_id}"
status: active
{blocked_by_yaml}
blocks: []
enables: []
queue_position: backlog
{extra}---
# {work_id}
"""
    work_file.write_text(content, encoding="utf-8")
    return work_file


def _read_blocked_by(work_file: Path) -> list:
    """Read blocked_by from a WORK.md file via yaml.safe_load (round-trip verification)."""
    content = work_file.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1]) or {}
    return fm.get("blocked_by", []) or []


# ── Unit tests for helpers ───────────────────────────────────────────────────


class TestFormatBlockedBy:
    """Tests for _format_blocked_by() YAML flow sequence formatting."""

    def test_empty_list(self):
        assert _format_blocked_by([]) == "[]"

    def test_single_item(self):
        assert _format_blocked_by(["WORK-101"]) == "[WORK-101]"

    def test_multiple_items(self):
        assert _format_blocked_by(["WORK-A", "WORK-B"]) == "[WORK-A, WORK-B]"

    def test_no_python_quotes(self):
        """Verify output does NOT contain Python-style single quotes."""
        result = _format_blocked_by(["WORK-101"])
        assert "'" not in result  # A6: must not produce ['WORK-101']


class TestReplaceBlockedByBlock:
    """Tests for _replace_blocked_by_block() line-scanning replacement."""

    def test_flow_style_replacement(self):
        content = "blocked_by: [WORK-A, WORK-B]\nblocks: []"
        result = _replace_blocked_by_block(content, "[WORK-B]")
        assert "blocked_by: [WORK-B]" in result
        assert "WORK-A" not in result

    def test_block_style_replacement_no_indent(self):
        """Block style with no indent (production format from WORK-113)."""
        content = "blocked_by:\n- WORK-111\n- WORK-112\nblocks: []"
        result = _replace_blocked_by_block(content, "[WORK-112]")
        assert "blocked_by: [WORK-112]" in result
        assert "\n- WORK-111" not in result  # No orphaned list items
        assert "blocks: []" in result  # Next field preserved

    def test_block_style_replacement_with_indent(self):
        """Block style with 2-space indent (production format from WORK-169)."""
        content = "blocked_by:\n  - WORK-167\nblocks: []"
        result = _replace_blocked_by_block(content, "[]")
        assert "blocked_by: []" in result
        assert "WORK-167" not in result
        assert "blocks: []" in result

    def test_empty_flow_style(self):
        content = "blocked_by: []\nblocks: []"
        result = _replace_blocked_by_block(content, "[WORK-NEW]")
        assert "blocked_by: [WORK-NEW]" in result

    def test_no_blocked_by_field(self):
        content = "status: active\nblocks: []"
        result = _replace_blocked_by_block(content, "[]")
        assert result == content  # Unchanged


# ── Integration tests for clear_blocked_by ───────────────────────────────────


class TestClearBlockedBy:
    """Integration tests for clear_blocked_by() function."""

    def test_clears_single_reference(self, tmp_path):
        """Test 1: When WORK-A closes, WORK-B's blocked_by: [WORK-A] becomes []"""
        wf = _make_work_file(tmp_path, "WORK-B", "blocked_by: [WORK-A]")

        result = clear_blocked_by("WORK-A", base_path=tmp_path)

        assert result["cleared"] == ["WORK-B"]
        assert result["errors"] == []
        # Round-trip via yaml.safe_load to verify correct YAML
        bb = _read_blocked_by(wf)
        assert bb == []

    def test_preserves_other_blockers(self, tmp_path):
        """Test 2: When WORK-A closes, WORK-C's blocked_by: [WORK-A, WORK-B] becomes [WORK-B]"""
        wf = _make_work_file(tmp_path, "WORK-C", "blocked_by: [WORK-A, WORK-B]")

        result = clear_blocked_by("WORK-A", base_path=tmp_path)

        assert result["cleared"] == ["WORK-C"]
        bb = _read_blocked_by(wf)
        assert isinstance(bb, list), f"blocked_by should be list, got {type(bb)}"
        assert bb == ["WORK-B"]

    def test_noop_when_not_referenced(self, tmp_path):
        """Test 3: When WORK-X closes but nothing references it, returns empty"""
        _make_work_file(tmp_path, "WORK-D", "blocked_by: [WORK-Z]")

        result = clear_blocked_by("WORK-X", base_path=tmp_path)

        assert result["cleared"] == []
        assert result["errors"] == []

    def test_skips_corrupt_file(self, tmp_path):
        """Test 4: Corrupt WORK.md is skipped — fail-permissive"""
        # Valid file with blocked_by ref
        wf_valid = _make_work_file(tmp_path, "WORK-GOOD", "blocked_by: [WORK-A]")

        # Corrupt file — no frontmatter delimiters
        corrupt_dir = tmp_path / "docs" / "work" / "active" / "WORK-BAD"
        corrupt_dir.mkdir(parents=True, exist_ok=True)
        (corrupt_dir / "WORK.md").write_text("no frontmatter here", encoding="utf-8")

        result = clear_blocked_by("WORK-A", base_path=tmp_path)

        assert "WORK-GOOD" in result["cleared"]
        assert "WORK-BAD" in result["skipped"]
        # Valid file was still updated
        bb = _read_blocked_by(wf_valid)
        assert bb == []

    def test_logs_warning_on_write_error(self, tmp_path, monkeypatch):
        """Test 5: When cascade encounters error, logs warning event"""
        _make_work_file(tmp_path, "WORK-ERR", "blocked_by: [WORK-A]")
        events_file = tmp_path / "events.jsonl"

        # Monkeypatch Path.write_text to raise on the WORK.md write
        original_write = Path.write_text

        def failing_write(self, content, *args, **kwargs):
            if "WORK-ERR" in str(self) and "WORK.md" in str(self):
                raise OSError("Simulated write failure")
            return original_write(self, content, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", failing_write)

        result = clear_blocked_by("WORK-A", base_path=tmp_path, events_file=events_file)

        assert "WORK-ERR" in result["errors"]
        # Verify warning event was logged
        assert events_file.exists()
        event = json.loads(events_file.read_text(encoding="utf-8").strip())
        assert event["type"] == "BlockedByCascadeWarning"
        assert event["closed_id"] == "WORK-A"
        assert event["failed_id"] == "WORK-ERR"

    def test_handles_block_style_yaml(self, tmp_path):
        """Test 6: Block-style YAML (- WORK-A on separate lines) is handled correctly."""
        # Use block-style format (production format from WORK-113, WORK-169)
        blocked_by_block = "blocked_by:\n- WORK-A\n- WORK-B"
        wf = _make_work_file(tmp_path, "WORK-BLOCK", blocked_by_block)

        result = clear_blocked_by("WORK-A", base_path=tmp_path)

        assert result["cleared"] == ["WORK-BLOCK"]
        # MUST verify via yaml.safe_load round-trip (catches A1 orphan + A6 type bugs)
        bb = _read_blocked_by(wf)
        assert isinstance(bb, list), f"blocked_by should be list, got {type(bb)}: {bb!r}"
        assert bb == ["WORK-B"]

    def test_handles_indented_block_style(self, tmp_path):
        """Block-style with 2-space indent (WORK-169 format)."""
        blocked_by_block = "blocked_by:\n  - WORK-167"
        wf = _make_work_file(tmp_path, "WORK-INDENT", blocked_by_block)

        result = clear_blocked_by("WORK-167", base_path=tmp_path)

        assert result["cleared"] == ["WORK-INDENT"]
        bb = _read_blocked_by(wf)
        assert bb == []


class TestCmdClearBlockedBy:
    """Test 7: CLI entry point always returns 0 (fail-permissive)."""

    def test_returns_zero_on_missing_items(self, tmp_path, monkeypatch):
        """CLI returns 0 even when work item doesn't exist."""
        # Import cli module
        cli_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
        sys.path.insert(0, str(cli_path))
        import importlib
        cli_mod = importlib.import_module("cli")

        # Monkeypatch the default base path resolution
        monkeypatch.setattr(
            "blocked_by_cascade.Path.__file__",
            str(tmp_path / "fake"),
            raising=False,
        )

        # Call cmd_clear_blocked_by with nonexistent work item
        # It should return 0 (not raise, not return 1)
        ret = cli_mod.cmd_clear_blocked_by("WORK-NONEXISTENT")
        assert ret == 0

    def test_returns_zero_on_successful_clear(self, tmp_path, monkeypatch):
        """CLI returns 0 on successful cascade."""
        _make_work_file(tmp_path, "WORK-TARGET", "blocked_by: [WORK-CLOSED]")

        cli_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
        sys.path.insert(0, str(cli_path))
        import importlib
        cli_mod = importlib.import_module("cli")

        # We need to pass base_path — but cmd_clear_blocked_by calls clear_blocked_by
        # with default paths. Monkeypatch the lib function instead.
        import blocked_by_cascade
        monkeypatch.setattr(
            blocked_by_cascade,
            "clear_blocked_by",
            lambda closed_id, **kw: {"cleared": ["WORK-TARGET"], "errors": [], "skipped": []},
        )

        ret = cli_mod.cmd_clear_blocked_by("WORK-CLOSED")
        assert ret == 0
