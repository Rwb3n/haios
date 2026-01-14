# generated: 2025-12-23
# System Auto: last updated on: 2025-12-23T19:53:02
"""Tests for node_cycle.py - Scaffold-on-Entry (E2-154)."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import will fail until we create the module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


class TestLoadNodeCycleBindings:
    """Test loading node-cycle bindings from config."""

    def test_load_bindings_returns_dict(self):
        """Config file loads and returns node bindings."""
        from node_cycle import load_node_cycle_bindings

        bindings = load_node_cycle_bindings()
        assert isinstance(bindings, dict)
        assert "plan" in bindings
        assert "discovery" in bindings


class TestGetNodeBinding:
    """Test getting binding for specific node."""

    def test_get_binding_for_plan_node(self):
        """Plan node has correct scaffold config."""
        from node_cycle import get_node_binding

        binding = get_node_binding("plan")
        assert binding is not None
        assert binding["scaffold"][0]["type"] == "plan"
        assert binding["scaffold"][0]["command"].startswith("/new-plan")

    def test_get_binding_for_missing_node(self):
        """Missing node returns None."""
        from node_cycle import get_node_binding

        binding = get_node_binding("nonexistent_node_xyz")
        assert binding is None


class TestDetectNodeChange:
    """Test detecting current_node field changes."""

    def test_detect_node_change_returns_new_node(self):
        """Detects current_node field changed in work file."""
        from node_cycle import detect_node_change

        old_content = "---\ncurrent_node: backlog\ntitle: Test\n---"
        new_content = "---\ncurrent_node: plan\ntitle: Test\n---"

        result = detect_node_change(old_content, new_content)
        assert result == "plan"

    def test_detect_node_change_returns_none_if_same(self):
        """Returns None if node unchanged."""
        from node_cycle import detect_node_change

        content = "---\ncurrent_node: backlog\ntitle: Test\n---"

        result = detect_node_change(content, content)
        assert result is None

    def test_detect_node_change_with_no_current_node(self):
        """Returns None if no current_node in new content."""
        from node_cycle import detect_node_change

        old_content = "---\ncurrent_node: backlog\n---"
        new_content = "---\ntitle: Test\n---"

        result = detect_node_change(old_content, new_content)
        assert result is None


class TestCheckDocExists:
    """Test checking if document exists matching pattern."""

    def test_check_doc_exists_returns_path(self, tmp_path):
        """Returns path if doc exists matching pattern."""
        plan_dir = tmp_path / "docs" / "plans"
        plan_dir.mkdir(parents=True)
        plan = plan_dir / "PLAN-E2-154-test.md"
        plan.write_text("test")

        from node_cycle import check_doc_exists

        result = check_doc_exists("docs/plans/PLAN-E2-154-*.md", tmp_path)
        assert result is not None
        assert result.exists()

    def test_check_doc_exists_returns_none_if_missing(self, tmp_path):
        """Returns None if no doc matches pattern."""
        from node_cycle import check_doc_exists

        result = check_doc_exists("docs/plans/PLAN-E2-999-*.md", tmp_path)
        assert result is None


class TestBuildScaffoldCommand:
    """Test building scaffold commands from templates."""

    def test_build_scaffold_command(self):
        """Builds correct /new-plan command."""
        from node_cycle import build_scaffold_command

        cmd = build_scaffold_command('/new-plan {id} "{title}"', "E2-154", "Test Title")
        assert cmd == '/new-plan E2-154 "Test Title"'

    def test_build_scaffold_command_with_complex_title(self):
        """Handles titles with special characters."""
        from node_cycle import build_scaffold_command

        cmd = build_scaffold_command('/new-plan {id} "{title}"', "E2-154", "Hook: Scaffold-on-Entry")
        assert cmd == '/new-plan E2-154 "Hook: Scaffold-on-Entry"'


class TestExtractWorkId:
    """Test extracting work ID from file path."""

    def test_extract_work_id_e2(self):
        """Extracts E2 work ID."""
        from node_cycle import extract_work_id

        result = extract_work_id(Path("docs/work/active/WORK-E2-154-scaffold.md"))
        assert result == "E2-154"

    def test_extract_work_id_inv(self):
        """Extracts INV work ID."""
        from node_cycle import extract_work_id

        result = extract_work_id(Path("docs/work/active/WORK-INV-022-arch.md"))
        assert result == "INV-022"

    def test_extract_work_id_none(self):
        """Returns None for non-work files."""
        from node_cycle import extract_work_id

        result = extract_work_id(Path("docs/plans/PLAN-E2-154.md"))
        assert result is None


class TestExtractTitle:
    """Test extracting title from frontmatter."""

    def test_extract_title(self):
        """Extracts title from frontmatter."""
        from node_cycle import extract_title

        content = '---\ntitle: "Scaffold-on-Entry Hook"\ncurrent_node: plan\n---'
        result = extract_title(content)
        assert result == "Scaffold-on-Entry Hook"

    def test_extract_title_unquoted(self):
        """Extracts unquoted title."""
        from node_cycle import extract_title

        content = '---\ntitle: Simple Title\ncurrent_node: plan\n---'
        result = extract_title(content)
        assert result == "Simple Title"

    def test_extract_title_missing(self):
        """Returns Untitled if missing."""
        from node_cycle import extract_title

        content = "---\ncurrent_node: plan\n---"
        result = extract_title(content)
        assert result == "Untitled"


class TestUpdateCycleDocs:
    """Test updating cycle_docs field in work file."""

    def test_update_cycle_docs_empty(self, tmp_path):
        """Updates empty cycle_docs field."""
        from node_cycle import update_cycle_docs

        work_file = tmp_path / "WORK-E2-154.md"
        work_file.write_text("---\ncycle_docs: {}\n---\n# Test")

        update_cycle_docs(work_file, "plan", "docs/plans/PLAN-E2-154-test.md")

        content = work_file.read_text()
        assert "plan: docs/plans/PLAN-E2-154-test.md" in content
        assert "cycle_docs: {}" not in content

    def test_update_cycle_docs_append(self, tmp_path):
        """Appends to existing cycle_docs field."""
        from node_cycle import update_cycle_docs

        work_file = tmp_path / "WORK-E2-154.md"
        work_file.write_text("---\ncycle_docs:\n  investigation: docs/investigations/INV-022.md\n---\n# Test")

        update_cycle_docs(work_file, "plan", "docs/plans/PLAN-E2-154-test.md")

        content = work_file.read_text()
        assert "investigation: docs/investigations/INV-022.md" in content
        assert "plan: docs/plans/PLAN-E2-154-test.md" in content
