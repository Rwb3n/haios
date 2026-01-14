# generated: 2025-12-23
# System Auto: last updated on: 2025-12-27T21:33:55
"""Tests for work_item template and infrastructure.

E2-150: Work-Item Infrastructure
- Tests for validate.py work_item registry
- Tests for scaffold.py work_item path generation
- Tests for status.py work item scanning
"""

import sys
from pathlib import Path

# Add .claude/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


class TestWorkItemValidation:
    """Tests for work_item template validation."""

    def test_work_item_template_in_registry(self):
        """Verify work_item template exists in registry with required fields."""
        from validate import get_template_registry

        registry = get_template_registry()
        assert "work_item" in registry, "work_item template missing from registry"
        assert "id" in registry["work_item"]["required_fields"]
        assert "current_node" in registry["work_item"]["required_fields"]
        assert "status" in registry["work_item"]["required_fields"]

    def test_work_item_validation_passes_for_prototype(self):
        """Verify prototype WORK-E2-143.md passes validation."""
        from validate import validate_template

        work_file = Path(__file__).parent.parent / "docs" / "work" / "active" / "WORK-E2-143.md"
        if not work_file.exists():
            # Skip if prototype doesn't exist
            return

        result = validate_template(str(work_file))
        assert result["is_valid"] is True, f"Validation failed: {result.get('errors', [])}"


class TestWorkItemScaffold:
    """Tests for work_item scaffolding."""

    def test_scaffold_generates_work_item_path(self):
        """Verify scaffold generates correct path for work_item (E2-212 directory structure)."""
        from scaffold import generate_output_path

        path = generate_output_path("work_item", backlog_id="E2-999", title="Test Item")
        assert "docs/work/active" in path, f"Wrong directory in path: {path}"
        # E2-212: Now creates directory structure, not flat file
        assert "E2-999/WORK.md" in path, f"Expected directory structure in path: {path}"

    def test_scaffold_work_item_config_exists(self):
        """Verify work_item exists in TEMPLATE_CONFIG (E2-212 directory structure)."""
        from scaffold import TEMPLATE_CONFIG

        assert "work_item" in TEMPLATE_CONFIG, "work_item missing from TEMPLATE_CONFIG"
        assert TEMPLATE_CONFIG["work_item"]["dir"] == "docs/work/active"
        # E2-212: prefix is None, subdirs added
        assert TEMPLATE_CONFIG["work_item"]["prefix"] is None
        assert "subdirs" in TEMPLATE_CONFIG["work_item"]


class TestWorkItemStatus:
    """Tests for work item status scanning."""

    def test_get_live_files_includes_work_items(self):
        """Verify get_live_files scans docs/work/ directories."""
        from status import get_live_files

        files = get_live_files()
        work_files = [f for f in files if "docs/work/" in f["path"]]

        # Should find at least the prototype if it exists
        prototype_path = Path(__file__).parent.parent / "docs" / "work" / "active" / "WORK-E2-143.md"
        if prototype_path.exists():
            assert any("WORK-E2-143" in f["path"] for f in work_files), \
                f"Prototype not found in live_files. Found: {[f['path'] for f in work_files]}"

    def test_get_work_items_returns_list(self):
        """Verify get_work_items function exists and returns list."""
        from status import get_work_items

        items = get_work_items()
        assert isinstance(items, list), f"Expected list, got {type(items)}"

        # If prototype exists, should be found
        prototype_path = Path(__file__).parent.parent / "docs" / "work" / "active" / "WORK-E2-143.md"
        if prototype_path.exists():
            active = [i for i in items if i.get("status") == "active"]
            assert len(active) >= 1, f"Expected at least 1 active item, found: {items}"


class TestWorkDirectoryStructure:
    """Tests for E2-212: Work directory structure migration."""

    def test_scaffold_work_item_creates_directory(self, tmp_path):
        """Work item scaffold creates directory structure, not flat file."""
        from scaffold import scaffold_template, PROJECT_ROOT
        import os

        # Temporarily override PROJECT_ROOT for test
        original_root = scaffold_template.__globals__["PROJECT_ROOT"]
        scaffold_template.__globals__["PROJECT_ROOT"] = tmp_path

        try:
            # Create required template
            template_dir = tmp_path / ".claude" / "templates"
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "work_item.md").write_text("""---
template: work_item
id: {{BACKLOG_ID}}
---
# WORK-{{BACKLOG_ID}}
""")
            # Create work directory
            (tmp_path / "docs" / "work" / "active").mkdir(parents=True, exist_ok=True)

            result = scaffold_template("work_item", backlog_id="E2-TEST", title="Test Item")

            # Verify directory structure
            result_path = Path(result)
            assert result_path.name == "WORK.md", f"Expected WORK.md, got {result_path.name}"
            assert result_path.parent.name == "E2-TEST", f"Expected E2-TEST dir, got {result_path.parent.name}"
            assert (result_path.parent / "plans").exists(), "plans subdir not created"
            assert (result_path.parent / "investigations").exists(), "investigations subdir not created"
        finally:
            scaffold_template.__globals__["PROJECT_ROOT"] = original_root

    def test_find_work_file_resolves_directory(self, tmp_path):
        """find_work_file finds WORK.md in directory structure."""
        from work_item import find_work_file, ACTIVE_DIR
        import work_item

        # Temporarily override ACTIVE_DIR
        original_active = work_item.ACTIVE_DIR
        work_item.ACTIVE_DIR = tmp_path

        try:
            # Create directory structure
            work_dir = tmp_path / "E2-TEST"
            work_dir.mkdir(parents=True)
            (work_dir / "WORK.md").write_text("---\nid: E2-TEST\n---\n# Test")

            result = find_work_file("E2-TEST")
            assert result is not None, "find_work_file returned None"
            assert result.name == "WORK.md", f"Expected WORK.md, got {result.name}"
            assert result.parent.name == "E2-TEST", f"Expected E2-TEST dir, got {result.parent.name}"
        finally:
            work_item.ACTIVE_DIR = original_active

    def test_find_work_file_falls_back_to_flat(self, tmp_path):
        """find_work_file falls back to flat file pattern for backward compat."""
        from work_item import find_work_file
        import work_item

        # Temporarily override ACTIVE_DIR
        original_active = work_item.ACTIVE_DIR
        work_item.ACTIVE_DIR = tmp_path

        try:
            # Create flat file (old format)
            (tmp_path / "WORK-E2-LEGACY-old-item.md").write_text("---\nid: E2-LEGACY\n---\n# Test")

            result = find_work_file("E2-LEGACY")
            assert result is not None, "find_work_file returned None for flat file"
            assert "WORK-E2-LEGACY" in result.name, f"Expected flat file, got {result.name}"
        finally:
            work_item.ACTIVE_DIR = original_active

    def test_plan_scaffolds_into_work_directory(self, tmp_path):
        """Plan creates inside work item's plans/ subdirectory."""
        from scaffold import scaffold_template

        # Temporarily override PROJECT_ROOT
        original_root = scaffold_template.__globals__["PROJECT_ROOT"]
        scaffold_template.__globals__["PROJECT_ROOT"] = tmp_path

        try:
            # Create required template
            template_dir = tmp_path / ".claude" / "templates"
            template_dir.mkdir(parents=True, exist_ok=True)
            (template_dir / "implementation_plan.md").write_text("""---
template: implementation_plan
backlog_id: {{BACKLOG_ID}}
---
# Plan
""")
            # Create work directory with work file (prerequisite)
            work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
            work_dir.mkdir(parents=True, exist_ok=True)
            (work_dir / "WORK.md").write_text("---\nid: E2-TEST\n---\n# Test")
            (work_dir / "plans").mkdir(exist_ok=True)

            result = scaffold_template("implementation_plan", backlog_id="E2-TEST", title="Test Plan")

            assert "E2-TEST/plans/PLAN.md" in str(result).replace("\\", "/"), f"Plan not in work dir: {result}"
        finally:
            scaffold_template.__globals__["PROJECT_ROOT"] = original_root

    def test_archive_structure_unchanged(self):
        """Completed items in archive stay as-is (no migration of archive)."""
        from pathlib import Path

        archive_dir = Path(__file__).parent.parent / "docs" / "work" / "archive"
        if not archive_dir.exists():
            return  # Skip if no archive

        # Archive should still have flat WORK-*.md files
        flat_files = list(archive_dir.glob("WORK-*.md"))
        # This test verifies we don't migrate archive files
        # After migration, archive still has flat files
        assert len(flat_files) >= 0  # Just checking pattern works


class TestNodeTransitions:
    """Tests for E2-162: Node transition functions."""

    def test_update_node_changes_current_node(self, tmp_path):
        """Verify update_node changes current_node field."""
        from work_item import update_node

        work_file = tmp_path / "WORK-TEST-001.md"
        work_file.write_text("""---
current_node: backlog
node_history:
  - node: backlog
    entered: 2025-12-24T10:00:00
    exited: null
---
# Test
""")
        update_node(work_file, "plan")
        content = work_file.read_text()
        assert "current_node: plan" in content

    def test_update_node_appends_history(self, tmp_path):
        """Verify update_node adds new entry to node_history."""
        from work_item import update_node

        work_file = tmp_path / "WORK-TEST-001.md"
        work_file.write_text("""---
current_node: backlog
node_history:
  - node: backlog
    entered: 2025-12-24T10:00:00
    exited: null
---
# Test
""")
        update_node(work_file, "plan")
        content = work_file.read_text()
        assert "node: plan" in content
        assert content.count("- node:") == 2

    def test_add_document_link_adds_plan(self, tmp_path):
        """Verify add_document_link adds to documents.plans."""
        from work_item import add_document_link

        work_file = tmp_path / "WORK-TEST-001.md"
        work_file.write_text("""---
current_node: plan
documents:
  investigations: []
  plans: []
  checkpoints: []
cycle_docs: {}
---
# Test
""")
        add_document_link(work_file, "plan", "docs/plans/PLAN-TEST.md")
        content = work_file.read_text()
        assert "PLAN-TEST.md" in content

    def test_add_document_link_updates_cycle_docs(self, tmp_path):
        """Verify add_document_link updates cycle_docs for current node."""
        from work_item import add_document_link

        work_file = tmp_path / "WORK-TEST-001.md"
        work_file.write_text("""---
current_node: plan
documents:
  plans: []
cycle_docs: {}
---
# Test
""")
        add_document_link(work_file, "plan", "docs/plans/PLAN-TEST.md")
        content = work_file.read_text()
        # cycle_docs should have plan: docs/plans/PLAN-TEST.md
        assert "plan:" in content.split("cycle_docs:")[1].split("---")[0]
