# generated: 2026-01-08
# System Auto: last updated on: 2026-01-09T21:53:40
"""
Tests for E2-279 WorkEngine Decomposition.

Phase 1: CascadeEngine extraction tests.
Additional phases will add tests for PortalManager, SpawnTree, BackfillEngine.
"""
import sys
from pathlib import Path
import pytest

# Add modules to path for testing
modules_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
if str(modules_path) not in sys.path:
    sys.path.insert(0, str(modules_path))


# =============================================================================
# Phase 1: CascadeEngine Tests
# =============================================================================

class TestCascadeEngineImports:
    """Test 1: CascadeEngine can be imported from modules package."""

    def test_cascade_engine_imports(self):
        """CascadeEngine can be imported."""
        from cascade_engine import CascadeEngine
        assert CascadeEngine is not None

    def test_cascade_result_imports(self):
        """CascadeResult can be imported."""
        from cascade_engine import CascadeResult
        assert CascadeResult is not None


class TestCascadeEngineBasicFunction:
    """Test 1b: CascadeEngine.cascade returns CascadeResult."""

    def test_cascade_returns_result(self, tmp_path):
        """CascadeEngine.cascade returns CascadeResult."""
        from cascade_engine import CascadeEngine, CascadeResult
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        work_engine = WorkEngine(governance=governance, base_path=tmp_path)
        cascade_engine = CascadeEngine(work_engine=work_engine, base_path=tmp_path)

        # Non-trigger status should return result with message
        result = cascade_engine.cascade("E2-TEST", "in_progress")
        assert isinstance(result, CascadeResult)
        assert "does not trigger" in result.message

    def test_cascade_with_complete_status(self, tmp_path):
        """CascadeEngine.cascade with 'complete' status runs full cascade."""
        from cascade_engine import CascadeEngine, CascadeResult
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        work_engine = WorkEngine(governance=governance, base_path=tmp_path)
        cascade_engine = CascadeEngine(work_engine=work_engine, base_path=tmp_path)

        # Create a work item to cascade
        work_engine.create_work("E2-TEST", "Test Item")

        result = cascade_engine.cascade("E2-TEST", "complete", dry_run=True)
        assert isinstance(result, CascadeResult)
        assert result.message  # Should have cascade report


class TestWorkEngineBackwardCompatibility:
    """Test 5: Existing WorkEngine.cascade() still works via delegation."""

    def test_work_engine_cascade_delegates(self, tmp_path):
        """WorkEngine.cascade() delegates to CascadeEngine."""
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        engine = WorkEngine(governance=governance, base_path=tmp_path)

        # Create a work item
        engine.create_work("E2-COMPAT", "Compat Test")

        # Call cascade on WorkEngine - should delegate
        result = engine.cascade("E2-COMPAT", "complete", dry_run=True)

        # Should return CascadeResult (verify backward compat)
        assert hasattr(result, 'unblocked')
        assert hasattr(result, 'message')


# =============================================================================
# Phase 2: PortalManager Tests
# =============================================================================

class TestPortalManagerImports:
    """Test 2a: PortalManager can be imported from modules package."""

    def test_portal_manager_imports(self):
        """PortalManager can be imported."""
        from portal_manager import PortalManager
        assert PortalManager is not None


class TestPortalManagerBasicFunction:
    """Test 2b: PortalManager.create_portal creates REFS.md."""

    def test_create_portal_creates_file(self, tmp_path):
        """PortalManager.create_portal creates REFS.md file."""
        from portal_manager import PortalManager

        manager = PortalManager(base_path=tmp_path)

        # Create refs directory
        refs_path = tmp_path / "docs" / "work" / "active" / "E2-TEST" / "references" / "REFS.md"
        refs_path.parent.mkdir(parents=True, exist_ok=True)

        manager.create_portal("E2-TEST", refs_path)

        assert refs_path.exists()
        content = refs_path.read_text()
        assert "work_id: E2-TEST" in content
        assert "## Provenance" in content

    def test_update_portal_updates_content(self, tmp_path):
        """PortalManager.update_portal updates existing REFS.md."""
        from portal_manager import PortalManager

        manager = PortalManager(base_path=tmp_path)

        # Create work dir structure
        work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
        refs_path = work_dir / "references" / "REFS.md"
        refs_path.parent.mkdir(parents=True, exist_ok=True)

        # Create initial portal
        manager.create_portal("E2-TEST", refs_path)

        # Update with spawned_from
        manager.update_portal("E2-TEST", {"spawned_from": "INV-001"})

        content = refs_path.read_text()
        assert "spawned_from: INV-001" in content or "Spawned from" in content

    def test_link_spawned_items_updates_work_files(self, tmp_path):
        """PortalManager.link_spawned_items updates work files and portals."""
        from portal_manager import PortalManager
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        work_engine = WorkEngine(governance=governance, base_path=tmp_path)
        manager = PortalManager(base_path=tmp_path, work_engine=work_engine)

        # Create work items
        work_engine.create_work("E2-001", "Work 1")
        work_engine.create_work("E2-002", "Work 2")

        # Link them to a parent
        result = manager.link_spawned_items("INV-001", ["E2-001", "E2-002"])

        assert "E2-001" in result.get("updated", [])
        assert "E2-002" in result.get("updated", [])


class TestWorkEnginePortalBackwardCompatibility:
    """Test 5b: Existing WorkEngine portal methods still work via delegation."""

    def test_work_engine_link_spawned_items_delegates(self, tmp_path):
        """WorkEngine.link_spawned_items() delegates to PortalManager."""
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        engine = WorkEngine(governance=governance, base_path=tmp_path)

        # Create work items
        engine.create_work("E2-001", "Work 1")
        engine.create_work("E2-002", "Work 2")

        # Call link_spawned_items on WorkEngine - should still work
        result = engine.link_spawned_items("INV-001", ["E2-001", "E2-002"])

        # Should return dict with 'updated' and 'failed' lists
        assert isinstance(result, dict)
        assert "updated" in result
        assert "failed" in result


# =============================================================================
# Phase 3: SpawnTree Tests
# =============================================================================

class TestSpawnTreeImports:
    """Test 3a: SpawnTree can be imported from modules package."""

    def test_spawn_tree_imports(self):
        """SpawnTree can be imported."""
        from spawn_tree import SpawnTree
        assert SpawnTree is not None


class TestSpawnTreeBasicFunction:
    """Test 3b: SpawnTree.spawn_tree returns nested dict."""

    def test_spawn_tree_returns_tree(self, tmp_path):
        """SpawnTree.spawn_tree returns nested dict."""
        from spawn_tree import SpawnTree

        tree = SpawnTree(base_path=tmp_path)
        result = tree.spawn_tree("E2-001")

        # Should return dict with root_id as key
        assert isinstance(result, dict)
        assert "E2-001" in result

    def test_spawn_tree_finds_children(self, tmp_path):
        """SpawnTree finds spawned_by children."""
        from spawn_tree import SpawnTree
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine
        import yaml

        governance = GovernanceLayer()
        work_engine = WorkEngine(governance=governance, base_path=tmp_path)

        # Create parent and child
        work_engine.create_work("INV-001", "Investigation")
        work_engine.create_work("E2-001", "Work 1")

        # Manually set spawned_by by parsing and re-writing the frontmatter
        work_path = tmp_path / "docs" / "work" / "active" / "E2-001" / "WORK.md"
        content = work_path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        fm = yaml.safe_load(parts[1]) or {}
        fm["spawned_by"] = "INV-001"
        new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
        work_path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")

        tree = SpawnTree(base_path=tmp_path)
        result = tree.spawn_tree("INV-001")

        # Should find E2-001 as child
        assert "INV-001" in result
        assert "E2-001" in result.get("INV-001", {})

    def test_format_tree_produces_output(self):
        """SpawnTree.format_tree formats tree as text."""
        from spawn_tree import SpawnTree

        tree = {"INV-001": {"E2-001": {}, "E2-002": {}}}
        result = SpawnTree.format_tree(tree, use_ascii=True)

        assert "INV-001" in result
        assert "E2-001" in result


class TestWorkEngineSpawnTreeBackwardCompatibility:
    """Test 5c: Existing WorkEngine.spawn_tree() still works."""

    def test_work_engine_spawn_tree_still_works(self, tmp_path):
        """WorkEngine.spawn_tree() still works."""
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        engine = WorkEngine(governance=governance, base_path=tmp_path)

        # Create work item
        engine.create_work("INV-001", "Investigation")

        # Call spawn_tree on WorkEngine - should still work
        result = engine.spawn_tree("INV-001")

        # Should return dict
        assert isinstance(result, dict)
        assert "INV-001" in result


# =============================================================================
# Phase 4: BackfillEngine Tests
# =============================================================================

class TestBackfillEngineImports:
    """Test 4a: BackfillEngine can be imported from modules package."""

    def test_backfill_engine_imports(self):
        """BackfillEngine can be imported."""
        from backfill_engine import BackfillEngine
        assert BackfillEngine is not None


class TestBackfillEngineBasicFunction:
    """Test 4b: BackfillEngine.backfill updates work file from backlog."""

    def test_backfill_returns_bool(self, tmp_path):
        """BackfillEngine.backfill returns boolean."""
        from backfill_engine import BackfillEngine
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        work_engine = WorkEngine(governance=governance, base_path=tmp_path)
        backfill_engine = BackfillEngine(work_engine=work_engine, base_path=tmp_path)

        # Create work item
        work_engine.create_work("E2-001", "Test Item")

        # Backfill should return False (no backlog entry)
        result = backfill_engine.backfill("E2-001")
        assert isinstance(result, bool)
        assert result is False  # No backlog source

    def test_backfill_all_returns_dict(self, tmp_path):
        """BackfillEngine.backfill_all returns dict with result lists."""
        from backfill_engine import BackfillEngine
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        work_engine = WorkEngine(governance=governance, base_path=tmp_path)
        backfill_engine = BackfillEngine(work_engine=work_engine, base_path=tmp_path)

        result = backfill_engine.backfill_all()

        assert isinstance(result, dict)
        assert "success" in result
        assert "not_found" in result
        assert "no_changes" in result

    def test_parse_backlog_entry_extracts_fields(self, tmp_path):
        """BackfillEngine._parse_backlog_entry extracts fields from backlog entry."""
        from backfill_engine import BackfillEngine
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        work_engine = WorkEngine(governance=governance, base_path=tmp_path)
        backfill_engine = BackfillEngine(work_engine=work_engine, base_path=tmp_path)

        # Sample backlog entry content
        content = """### [READY] E2-001: Test Item

**Context:** This is a test problem statement.
**Milestone:** M8

- [ ] Deliverable one
- [ ] Deliverable two

### [READY] E2-002: Another Item
"""
        result = backfill_engine._parse_backlog_entry("E2-001", content)

        assert result is not None
        assert "This is a test problem statement" in result.get("context", "")
        assert result.get("milestone") == "M8"
        assert len(result.get("deliverables", [])) == 2


class TestWorkEngineBackfillBackwardCompatibility:
    """Test 5d: Existing WorkEngine.backfill() still works."""

    def test_work_engine_backfill_still_works(self, tmp_path):
        """WorkEngine.backfill() still works."""
        from governance_layer import GovernanceLayer
        from work_engine import WorkEngine

        governance = GovernanceLayer()
        engine = WorkEngine(governance=governance, base_path=tmp_path)

        # Create work item
        engine.create_work("E2-001", "Test Item")

        # Call backfill on WorkEngine - should still work (returns False, no source)
        result = engine.backfill("E2-001")

        assert isinstance(result, bool)
