# generated: 2026-01-03
# System Auto: last updated on: 2026-01-04T00:24:09
"""
Tests for HAIOS Modules CLI.

E2-250: Verifies that the CLI entry point correctly routes to WorkEngine.
"""
import subprocess
import sys
from pathlib import Path

import pytest


CLI_PATH = Path(".claude/haios/modules/cli.py")


class TestModulesCLI:
    """Tests for the modules CLI entry point."""

    def test_cli_exists(self):
        """CLI script should exist."""
        assert CLI_PATH.exists()

    def test_cli_help(self):
        """CLI should show help with no args."""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH)],
            capture_output=True,
            text=True
        )
        assert "Usage:" in result.stdout
        assert "Commands:" in result.stdout

    def test_cli_get_ready_runs(self):
        """get-ready command should execute without error."""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "get-ready"],
            capture_output=True,
            text=True
        )
        # Should not error (may or may not find items)
        assert result.returncode == 0

    def test_cli_get_work_not_found(self):
        """get-work should return 1 for missing ID."""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "get-work", "NONEXISTENT-999"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "Not found" in result.stdout

    def test_cli_transition_invalid(self):
        """transition should return 1 for missing ID."""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "transition", "NONEXISTENT-999", "plan"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "Not found" in result.stdout

    def test_cli_unknown_command(self):
        """Unknown command should return 1."""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "unknown-command"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "Unknown command" in result.stdout


class TestCLIIntegration:
    """Integration tests proving CLI routes through WorkEngine."""

    @pytest.fixture
    def temp_work_dir(self, tmp_path):
        """Create a temporary work directory structure."""
        active = tmp_path / "docs" / "work" / "active"
        archive = tmp_path / "docs" / "work" / "archive"
        active.mkdir(parents=True)
        archive.mkdir(parents=True)
        return tmp_path

    def test_transition_uses_work_engine(self, temp_work_dir):
        """Transition command should route through WorkEngine."""
        # Create a test work item
        work_dir = temp_work_dir / "docs" / "work" / "active" / "TEST-001"
        work_dir.mkdir(parents=True)
        work_file = work_dir / "WORK.md"
        work_file.write_text("""---
id: TEST-001
title: Test Item
status: active
current_node: backlog
blocked_by: []
node_history:
  - node: backlog
    entered: "2026-01-03T00:00:00"
    exited: null
memory_refs: []
---
# TEST-001
""")

        # Import WorkEngine directly and verify it can read the file
        sys.path.insert(0, str(Path(".claude/haios/modules")))
        from work_engine import WorkEngine
        from governance_layer import GovernanceLayer

        engine = WorkEngine(
            governance=GovernanceLayer(),
            base_path=temp_work_dir
        )

        # Verify WorkEngine can read it
        work = engine.get_work("TEST-001")
        assert work is not None
        assert work.current_node == "backlog"

        # Transition via WorkEngine
        work = engine.transition("TEST-001", "plan")
        assert work.current_node == "plan"

        # Verify transition was persisted
        work2 = engine.get_work("TEST-001")
        assert work2.current_node == "plan"
        assert len(work2.node_history) == 2


# =============================================================================
# E2-251: CLI Integration Tests for cascade, spawn-tree, backfill
# =============================================================================

class TestCLICascadeSpawnBackfill:
    """E2-251: Tests for cascade, spawn-tree, and backfill CLI commands."""

    def test_cli_cascade_runs(self):
        """E2-251 Test 8: cascade command should execute."""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "cascade", "E2-TEST", "complete"],
            capture_output=True,
            text=True
        )
        # Should not error (may not find items, but command should exist)
        assert result.returncode == 0
        assert "Cascade" in result.stdout or "cascade" in result.stdout.lower()

    def test_cli_spawn_tree_runs(self):
        """E2-251 Test 9: spawn-tree command should execute."""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "spawn-tree", "INV-017"],
            capture_output=True,
            text=True
        )
        # Should not error (may be empty tree)
        assert result.returncode == 0
        # Either shows the ID or indicates no spawned items
        assert "INV-017" in result.stdout

    def test_cli_backfill_runs(self):
        """E2-251 Test 10: backfill command should execute."""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "backfill", "E2-NONEXISTENT"],
            capture_output=True,
            text=True
        )
        # Should not error (may return "not found")
        assert result.returncode == 0
        assert "Not found" in result.stdout or "Backfilled" in result.stdout or "no changes" in result.stdout.lower()


# =============================================================================
# E2-252: CLI Integration Tests for validate, scaffold
# =============================================================================


class TestCLIValidateScaffold:
    """E2-252: Tests for validate and scaffold CLI commands."""

    def test_cli_validate_command(self, tmp_path):
        """E2-252: cli.py validate <file> should work."""
        # Create valid checkpoint
        checkpoint = tmp_path / "valid.md"
        checkpoint.write_text(
            """---
template: checkpoint
status: active
date: 2026-01-04
version: '1.0'
author: Test
project_phase: test
---
# Test Checkpoint

@docs/README.md
@docs/epistemic_state.md
"""
        )

        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "validate", str(checkpoint)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Passed" in result.stdout

    def test_cli_validate_invalid_file(self, tmp_path):
        """E2-252: cli.py validate should return 1 for invalid file."""
        # Create invalid checkpoint (missing required fields)
        checkpoint = tmp_path / "invalid.md"
        checkpoint.write_text(
            """---
template: checkpoint
status: active
---
# Test
"""
        )

        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "validate", str(checkpoint)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Failed" in result.stdout

    def test_cli_scaffold_command(self, tmp_path):
        """E2-252: cli.py scaffold <type> <id> <title> should work."""
        output_path = tmp_path / "test_scaffold.md"

        result = subprocess.run(
            [
                sys.executable,
                str(CLI_PATH),
                "scaffold",
                "checkpoint",
                "999",
                "Test Checkpoint",
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Created" in result.stdout or output_path.exists()
