# generated: 2025-12-22
# System Auto: last updated on: 2026-01-27T20:56:52
"""Tests for spawn tree query module.

Tests the spawn.py module that visualizes spawn relationships
(what work items were spawned by a given investigation/session).
"""

import pytest
from pathlib import Path


class TestParseYamlFrontmatter:
    """Tests for parse_yaml_frontmatter function."""

    def test_parse_spawned_by_field(self):
        """Test extraction of spawned_by from frontmatter."""
        # Import here to test module exists
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import parse_yaml_frontmatter

        content = "---\nspawned_by: INV-017\ntitle: Test\n---\n# Content"
        result = parse_yaml_frontmatter(content)
        assert result.get('spawned_by') == 'INV-017'

    def test_parse_multiple_fields(self):
        """Test extraction of multiple frontmatter fields."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import parse_yaml_frontmatter

        content = "---\nspawned_by: Session-84\nbacklog_id: E2-099\ntitle: Test Item\n---"
        result = parse_yaml_frontmatter(content)
        assert result.get('spawned_by') == 'Session-84'
        assert result.get('backlog_id') == 'E2-099'
        assert result.get('title') == 'Test Item'

    def test_no_frontmatter(self):
        """Test handling of content without frontmatter."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import parse_yaml_frontmatter

        content = "# Just a header\n\nSome content."
        result = parse_yaml_frontmatter(content)
        assert result == {}


class TestFindChildren:
    """Tests for find_children function."""

    def test_find_children_of_parent(self, tmp_path):
        """Test finding children by spawned_by field."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import find_children

        # Create test directory structure
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()

        # Create files with spawned_by: INV-017
        (plans_dir / "PLAN-E2-099.md").write_text(
            "---\nspawned_by: INV-017\nbacklog_id: E2-099\ntitle: Bug Fix\n---\n# Content"
        )
        (plans_dir / "PLAN-E2-102.md").write_text(
            "---\nspawned_by: INV-017\nbacklog_id: E2-102\ntitle: Setup\n---\n# Content"
        )
        # Create file with different parent
        (plans_dir / "PLAN-E2-103.md").write_text(
            "---\nspawned_by: INV-018\nbacklog_id: E2-103\ntitle: Other\n---\n# Content"
        )

        children = find_children("INV-017", docs_path=tmp_path)
        child_ids = {c['id'] for c in children}
        assert child_ids == {"E2-099", "E2-102"}

    def test_find_no_children(self, tmp_path):
        """Test when no children exist."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import find_children

        children = find_children("NONEXISTENT", docs_path=tmp_path)
        assert children == []


class TestBuildSpawnTree:
    """Tests for build_spawn_tree function."""

    def test_build_spawn_tree_single_level(self, tmp_path):
        """Test building tree with single level of children."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import build_spawn_tree

        # Create test file
        (tmp_path / "PLAN-E2-099.md").write_text(
            "---\nspawned_by: INV-017\nbacklog_id: E2-099\n---"
        )

        tree = build_spawn_tree("INV-017", docs_path=tmp_path)
        assert "INV-017" in tree
        assert "E2-099" in tree["INV-017"]

    def test_build_spawn_tree_multi_level(self, tmp_path):
        """Test building tree with multiple levels."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import build_spawn_tree

        # INV-017 spawns E2-099, E2-099 spawns E2-100
        (tmp_path / "PLAN-E2-099.md").write_text(
            "---\nspawned_by: INV-017\nbacklog_id: E2-099\n---"
        )
        (tmp_path / "PLAN-E2-100.md").write_text(
            "---\nspawned_by: E2-099\nbacklog_id: E2-100\n---"
        )

        tree = build_spawn_tree("INV-017", docs_path=tmp_path)
        assert "INV-017" in tree
        assert "E2-099" in tree["INV-017"]
        assert "E2-100" in tree["INV-017"]["E2-099"]

    def test_no_spawns_returns_root_only(self, tmp_path):
        """Test that no spawns returns tree with just root."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import build_spawn_tree

        tree = build_spawn_tree("NONEXISTENT", docs_path=tmp_path)
        assert tree == {"NONEXISTENT": {}}


class TestFormatTree:
    """Tests for format_tree function."""

    def test_format_tree_output(self):
        """Test ASCII tree formatting."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import format_tree

        tree = {"INV-017": {"E2-099": {}, "E2-102": {}}}
        output = format_tree(tree)

        assert "INV-017" in output
        assert "E2-099" in output
        assert "E2-102" in output
        # Check tree structure characters
        assert "├──" in output or "└──" in output

    def test_format_empty_tree(self):
        """Test formatting tree with no children."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
        from spawn import format_tree

        tree = {"NONEXISTENT": {}}
        output = format_tree(tree)
        assert "NONEXISTENT" in output
