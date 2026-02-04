# generated: 2026-01-03
# System Auto: last updated on: 2026-02-04T21:09:04
"""
Tests for WorkEngine module (E2-242).

Tests the 5 L4 functions and 4 invariants:
- get_work(id): Returns parsed WORK.md
- create_work(id, title, ...): Creates directory + WORK.md
- transition(id, to_node): Validates and updates node_history
- get_ready(): Returns unblocked items
- archive(id): Moves to archive directory
- add_memory_refs(id, refs): Links concepts and calls MemoryBridge

Invariants:
- MUST be the ONLY writer to WORK.md files
- MUST validate transitions via GovernanceLayer
- MUST update node_history with timestamps on every transition
- MUST call MemoryBridge.auto_link after memory operations
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add parent paths for module imports
import sys
_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(_root / ".claude" / "lib"))

# Import modules directly (avoiding relative import issues)
# These are standalone modules, not part of a package when run from tests
import importlib.util

def _load_module(name: str, path: Path):
    """Load a module from a specific path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load governance_layer first (dependency)
_gov_path = _root / ".claude" / "haios" / "modules" / "governance_layer.py"
governance_layer = _load_module("governance_layer", _gov_path)
GovernanceLayer = governance_layer.GovernanceLayer

# Load work_engine with governance_layer already in sys.modules
_work_path = _root / ".claude" / "haios" / "modules" / "work_engine.py"
work_engine = _load_module("work_engine", _work_path)
WorkEngine = work_engine.WorkEngine
WorkState = work_engine.WorkState
InvalidTransitionError = work_engine.InvalidTransitionError
WorkNotFoundError = work_engine.WorkNotFoundError
# E2-304: Import new exception for ID validation tests
# Note: Will fail until work_engine.py is updated
try:
    WorkIDUnavailableError = work_engine.WorkIDUnavailableError
except AttributeError:
    # Define stub for TDD - tests will fail until implementation
    class WorkIDUnavailableError(Exception):
        pass


# Sample WORK.md content for testing
SAMPLE_WORK_MD = """---
template: work_item
id: E2-TEST
title: Test Work Item
status: active
owner: Hephaestus
created: 2026-01-03
closed: null
milestone: M7b-WorkInfra
priority: medium
category: implementation
blocked_by: []
blocks: []
current_node: backlog
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
documents:
  plans: []
  investigations: []
  checkpoints: []
---
# WORK-E2-TEST: Test Work Item
"""

SAMPLE_BLOCKED_WORK_MD = """---
template: work_item
id: E2-BLOCKED
title: Blocked Work Item
status: active
owner: Hephaestus
created: 2026-01-03
closed: null
milestone: M7b-WorkInfra
priority: medium
category: implementation
blocked_by:
- E2-240
- E2-241
blocks: []
current_node: backlog
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
documents:
  plans: []
  investigations: []
  checkpoints: []
---
# WORK-E2-BLOCKED: Blocked Work Item
"""

# E2-304: Sample content for complete status work item
SAMPLE_COMPLETE_WORK_MD = """---
template: work_item
id: E2-COMPLETE
title: Complete Work Item
status: complete
owner: Hephaestus
created: 2026-01-03
closed: 2026-01-05
milestone: M7b-WorkInfra
priority: medium
category: implementation
blocked_by: []
blocks: []
current_node: complete
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: '2026-01-05T10:00:00'
- node: complete
  entered: '2026-01-05T10:00:00'
  exited: null
memory_refs: []
documents:
  plans: []
  investigations: []
  checkpoints: []
---
# WORK-E2-COMPLETE: Complete Work Item
"""

# E2-304: Sample content for archived status work item
SAMPLE_ARCHIVED_WORK_MD = """---
template: work_item
id: E2-ARCHIVED
title: Archived Work Item
status: archived
owner: Hephaestus
created: 2026-01-03
closed: 2026-01-05
milestone: M7b-WorkInfra
priority: medium
category: implementation
blocked_by: []
blocks: []
current_node: complete
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: '2026-01-05T10:00:00'
- node: complete
  entered: '2026-01-05T10:00:00'
  exited: null
memory_refs: []
documents:
  plans: []
  investigations: []
  checkpoints: []
---
# WORK-E2-ARCHIVED: Archived Work Item
"""


@pytest.fixture
def governance():
    """Create real GovernanceLayer for integration tests."""
    return GovernanceLayer()


@pytest.fixture
def mock_governance():
    """Create mock GovernanceLayer for isolation tests."""
    mock = Mock(spec=GovernanceLayer)
    mock.validate_transition.return_value = True
    return mock


@pytest.fixture
def mock_memory():
    """Create mock MemoryBridge for testing auto_link calls."""
    mock = Mock()
    mock.auto_link = Mock()
    return mock


@pytest.fixture
def engine(tmp_path, governance):
    """Create WorkEngine with real GovernanceLayer and tmp_path."""
    return WorkEngine(governance=governance, base_path=tmp_path)


@pytest.fixture
def setup_work_item(tmp_path):
    """Helper to create a work item in tmp_path."""
    def _create(work_id: str, content: str = SAMPLE_WORK_MD):
        work_dir = tmp_path / "docs" / "work" / "active" / work_id
        work_dir.mkdir(parents=True)
        work_file = work_dir / "WORK.md"
        # Replace E2-TEST with actual work_id in content
        actual_content = content.replace("E2-TEST", work_id).replace("E2-BLOCKED", work_id)
        work_file.write_text(actual_content, encoding="utf-8")
        return work_file
    return _create


# =============================================================================
# Test 1: get_work returns WorkState for existing item
# =============================================================================
def test_get_work_returns_work_state(tmp_path, engine, setup_work_item):
    """Test that get_work returns a WorkState for an existing work item."""
    setup_work_item("E2-TEST")

    result = engine.get_work("E2-TEST")

    assert result is not None
    assert isinstance(result, WorkState)
    assert result.id == "E2-TEST"
    assert result.title == "Test Work Item"
    assert result.current_node == "backlog"
    assert isinstance(result.blocked_by, list)
    assert result.blocked_by == []


# =============================================================================
# Test 2: get_work returns None for missing item
# =============================================================================
def test_get_work_returns_none_for_missing(engine):
    """Test that get_work returns None when work item doesn't exist."""
    result = engine.get_work("NONEXISTENT-123")
    assert result is None


# =============================================================================
# Test 3: transition validates via GovernanceLayer
# =============================================================================
def test_transition_validates_via_governance(tmp_path, setup_work_item, mock_governance):
    """Test that transition calls GovernanceLayer.validate_transition."""
    setup_work_item("E2-TEST")
    mock_governance.validate_transition.return_value = False
    engine = WorkEngine(governance=mock_governance, base_path=tmp_path)

    with pytest.raises(InvalidTransitionError):
        engine.transition("E2-TEST", "complete")

    mock_governance.validate_transition.assert_called_once()


# =============================================================================
# Test 4: transition updates node_history with timestamp
# =============================================================================
def test_transition_updates_node_history(tmp_path, engine, setup_work_item):
    """Test that transition updates node_history with timestamps."""
    setup_work_item("E2-TEST")

    result = engine.transition("E2-TEST", "plan")

    assert result.current_node == "plan"
    assert len(result.node_history) == 2  # backlog + plan
    assert result.node_history[-1]["node"] == "plan"
    assert result.node_history[-1]["entered"] is not None
    assert result.node_history[-1]["exited"] is None
    # Previous node should have exited timestamp
    assert result.node_history[-2]["exited"] is not None


# =============================================================================
# Test 5: get_ready returns unblocked items only
# =============================================================================
def test_get_ready_returns_unblocked_only(tmp_path, engine, setup_work_item):
    """Test that get_ready returns only unblocked items."""
    # Create 1 unblocked and 1 blocked item
    setup_work_item("E2-UNBLOCKED", SAMPLE_WORK_MD)
    setup_work_item("E2-BLOCKED", SAMPLE_BLOCKED_WORK_MD)

    result = engine.get_ready()

    assert len(result) == 1
    assert result[0].id == "E2-UNBLOCKED"
    assert result[0].blocked_by == []


# =============================================================================
# Test 6: create_work creates directory and WORK.md
# =============================================================================
def test_create_work_creates_directory_structure(tmp_path, engine):
    """Test that create_work creates directory structure and WORK.md."""
    result = engine.create_work(
        id="E2-NEW",
        title="New Work Item",
        milestone="M7b-WorkInfra"
    )

    assert result.exists()
    assert result.name == "WORK.md"
    assert result.parent.name == "E2-NEW"
    # Verify plans/ subdirectory also created
    assert (result.parent / "plans").exists()


# =============================================================================
# Test 7: archive moves to archive directory
# =============================================================================
def test_archive_moves_to_archive_dir(tmp_path, engine, setup_work_item):
    """Test that archive moves work item to archive directory."""
    setup_work_item("E2-TEST")

    result = engine.archive("E2-TEST")

    assert "archive" in str(result)
    assert not (tmp_path / "docs" / "work" / "active" / "E2-TEST").exists()
    assert (tmp_path / "docs" / "work" / "archive" / "E2-TEST" / "WORK.md").exists()


# =============================================================================
# Test 8: add_memory_refs calls MemoryBridge auto_link
# =============================================================================
def test_add_memory_refs_calls_memory_bridge(tmp_path, setup_work_item, mock_memory):
    """Test that add_memory_refs calls MemoryBridge.auto_link."""
    setup_work_item("E2-TEST")
    engine = WorkEngine(
        governance=GovernanceLayer(),
        memory=mock_memory,
        base_path=tmp_path
    )

    engine.add_memory_refs("E2-TEST", [80534, 80535])

    mock_memory.auto_link.assert_called_once_with("E2-TEST", [80534, 80535])


# =============================================================================
# Test 9: L4 Invariant - WorkEngine is only writer to WORK.md
# =============================================================================
def test_work_engine_is_only_writer(tmp_path, engine, setup_work_item):
    """Verify WorkEngine owns WORK.md writes (transition modifies file)."""
    work_file = setup_work_item("E2-TEST")
    original_content = work_file.read_text(encoding="utf-8")

    # Transition should modify file
    engine.transition("E2-TEST", "plan")
    new_content = work_file.read_text(encoding="utf-8")

    assert original_content != new_content
    assert "current_node: plan" in new_content


# =============================================================================
# Test 10: transition blocks invalid DAG transitions
# =============================================================================
def test_transition_blocks_invalid_dag_path(tmp_path, engine, setup_work_item):
    """Test that transition blocks invalid DAG transitions."""
    setup_work_item("E2-TEST")

    # Try to skip from backlog directly to complete (invalid)
    with pytest.raises(InvalidTransitionError, match="Invalid transition"):
        engine.transition("E2-TEST", "complete")


# =============================================================================
# Test 11: archive preserves directory structure
# =============================================================================
def test_archive_preserves_subdirectories(tmp_path, engine, setup_work_item):
    """Test that archive preserves subdirectories like plans/."""
    work_file = setup_work_item("E2-TEST")
    # Create plans/ subdirectory with a file
    plans_dir = work_file.parent / "plans"
    plans_dir.mkdir(exist_ok=True)
    (plans_dir / "PLAN.md").write_text("# Plan", encoding="utf-8")

    engine.archive("E2-TEST")

    archive_path = tmp_path / "docs" / "work" / "archive" / "E2-TEST"
    assert (archive_path / "WORK.md").exists()
    assert (archive_path / "plans").exists()
    assert (archive_path / "plans" / "PLAN.md").exists()


# =============================================================================
# Test 12: get_ready excludes archived items
# =============================================================================
def test_get_ready_excludes_archived(tmp_path, engine, setup_work_item):
    """Test that get_ready only returns active items, not archived."""
    # Create active unblocked item
    setup_work_item("E2-ACTIVE", SAMPLE_WORK_MD)

    # Create archived unblocked item manually
    archive_dir = tmp_path / "docs" / "work" / "archive" / "E2-ARCHIVED"
    archive_dir.mkdir(parents=True)
    (archive_dir / "WORK.md").write_text(
        SAMPLE_WORK_MD.replace("E2-TEST", "E2-ARCHIVED"),
        encoding="utf-8"
    )

    result = engine.get_ready()

    assert len(result) == 1
    assert result[0].id == "E2-ACTIVE"
    assert all("archive" not in str(w.path) for w in result)


# =============================================================================
# INV-070: get_ready excludes complete items
# =============================================================================

SAMPLE_COMPLETE_WORK_MD = """---
template: work_item
id: E2-COMPLETE
title: Already Complete Item
status: complete
owner: Hephaestus
created: 2026-01-03
closed: '2026-01-18'
milestone: null
priority: high
category: implementation
blocked_by: []
blocks: []
current_node: backlog
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
---
# E2-COMPLETE
"""

def test_get_ready_excludes_complete_items(tmp_path, engine, setup_work_item):
    """Test that get_ready excludes items with status: complete (INV-070 fix)."""
    # Create active unblocked item
    setup_work_item("E2-ACTIVE", SAMPLE_WORK_MD)

    # Create complete item (should be excluded)
    setup_work_item("E2-COMPLETE", SAMPLE_COMPLETE_WORK_MD)

    result = engine.get_ready()

    # Should only return active items, not complete ones
    assert len(result) == 1
    assert result[0].id == "E2-ACTIVE"
    assert result[0].status == "active"
    # Verify the complete item was excluded
    assert not any(w.id == "E2-COMPLETE" for w in result)


# =============================================================================
# E2-251: Cascade Tests
# =============================================================================

# Sample work file with blocked_by for cascade tests
SAMPLE_BLOCKED_BY_100 = """---
template: work_item
id: E2-101
title: Blocked by E2-100
status: active
current_node: backlog
blocked_by:
- E2-100
blocks: []
related: []
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
---
# E2-101
"""

SAMPLE_BLOCKED_BY_TWO = """---
template: work_item
id: E2-101
title: Blocked by Two
status: active
current_node: backlog
blocked_by:
- E2-100
- E2-102
blocks: []
related: []
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
---
# E2-101
"""

SAMPLE_WITH_RELATED = """---
template: work_item
id: E2-101
title: Related to E2-100
status: active
current_node: backlog
blocked_by: []
blocks: []
related:
- E2-100
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
---
# E2-101
"""

SAMPLE_E2_100_RELATED = """---
template: work_item
id: E2-100
title: Relates to E2-102
status: active
current_node: backlog
blocked_by: []
blocks: []
related:
- E2-102
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
---
# E2-100
"""


def test_cascade_unblocks_items(tmp_path, governance):
    """E2-251 Test 1: When E2-100 completes, E2-101 (blocked_by: [E2-100]) becomes READY."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create E2-100 (the blocker) and E2-101 (blocked by E2-100)
    work_100_dir = tmp_path / "docs" / "work" / "active" / "E2-100"
    work_100_dir.mkdir(parents=True)
    (work_100_dir / "WORK.md").write_text(SAMPLE_WORK_MD.replace("E2-TEST", "E2-100"))

    work_101_dir = tmp_path / "docs" / "work" / "active" / "E2-101"
    work_101_dir.mkdir(parents=True)
    (work_101_dir / "WORK.md").write_text(SAMPLE_BLOCKED_BY_100)

    # Action: Cascade from E2-100 completion
    result = engine.cascade("E2-100", "complete")

    # Assert: E2-101 should be unblocked
    assert "E2-101" in result.unblocked
    assert len(result.still_blocked) == 0


def test_cascade_partial_unblock(tmp_path, governance):
    """E2-251 Test 2: E2-101 blocked_by [E2-100, E2-102] - completing E2-100 leaves still blocked."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: E2-100 (will complete), E2-102 (not complete), E2-101 (blocked by both)
    work_100_dir = tmp_path / "docs" / "work" / "active" / "E2-100"
    work_100_dir.mkdir(parents=True)
    (work_100_dir / "WORK.md").write_text(SAMPLE_WORK_MD.replace("E2-TEST", "E2-100"))

    work_102_dir = tmp_path / "docs" / "work" / "active" / "E2-102"
    work_102_dir.mkdir(parents=True)
    (work_102_dir / "WORK.md").write_text(SAMPLE_WORK_MD.replace("E2-TEST", "E2-102"))

    work_101_dir = tmp_path / "docs" / "work" / "active" / "E2-101"
    work_101_dir.mkdir(parents=True)
    (work_101_dir / "WORK.md").write_text(SAMPLE_BLOCKED_BY_TWO)

    # Action: Cascade from E2-100 completion
    result = engine.cascade("E2-100", "complete")

    # Assert: E2-101 should still be blocked (E2-102 not complete)
    assert len(result.unblocked) == 0
    assert "E2-101" in result.still_blocked


def test_cascade_finds_related(tmp_path, governance):
    """E2-251 Test 3: Both inbound and outbound related items are discovered."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: E2-100 related: [E2-102], E2-101 related: [E2-100]
    work_100_dir = tmp_path / "docs" / "work" / "active" / "E2-100"
    work_100_dir.mkdir(parents=True)
    (work_100_dir / "WORK.md").write_text(SAMPLE_E2_100_RELATED)

    work_101_dir = tmp_path / "docs" / "work" / "active" / "E2-101"
    work_101_dir.mkdir(parents=True)
    (work_101_dir / "WORK.md").write_text(SAMPLE_WITH_RELATED)

    work_102_dir = tmp_path / "docs" / "work" / "active" / "E2-102"
    work_102_dir.mkdir(parents=True)
    (work_102_dir / "WORK.md").write_text(SAMPLE_WORK_MD.replace("E2-TEST", "E2-102"))

    # Action: Cascade from E2-100 completion
    result = engine.cascade("E2-100", "complete")

    # Assert: Both E2-101 (inbound - references E2-100) and E2-102 (outbound - E2-100 references it)
    assert "E2-101" in result.related  # inbound: E2-101's related includes E2-100
    assert "E2-102" in result.related  # outbound: E2-100's related includes E2-102


# =============================================================================
# E2-251: Spawn Tree Tests
# =============================================================================

SAMPLE_SPAWNED_BY_INV = """---
template: work_item
id: E2-A
title: Spawned by INV-017
status: active
current_node: backlog
blocked_by: []
spawned_by: INV-017
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
---
# E2-A
"""


def test_spawn_tree_simple(tmp_path, governance):
    """E2-251 Test 4: INV-X spawns E2-A, E2-B -> tree shows both as children."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: E2-A and E2-B both spawned_by INV-017
    work_a_dir = tmp_path / "docs" / "work" / "active" / "E2-A"
    work_a_dir.mkdir(parents=True)
    (work_a_dir / "WORK.md").write_text(SAMPLE_SPAWNED_BY_INV)

    work_b_dir = tmp_path / "docs" / "work" / "active" / "E2-B"
    work_b_dir.mkdir(parents=True)
    (work_b_dir / "WORK.md").write_text(
        SAMPLE_SPAWNED_BY_INV.replace("E2-A", "E2-B")
    )

    # Action: Build spawn tree from INV-017
    tree = engine.spawn_tree("INV-017")

    # Assert: Both E2-A and E2-B are children of INV-017
    assert "INV-017" in tree
    assert "E2-A" in tree["INV-017"]
    assert "E2-B" in tree["INV-017"]


def test_spawn_tree_nested(tmp_path, governance):
    """E2-251 Test 5: INV-X spawns E2-A, E2-A spawns E2-B -> nested tree."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: E2-A spawned by INV-017, E2-B spawned by E2-A
    work_a_dir = tmp_path / "docs" / "work" / "active" / "E2-A"
    work_a_dir.mkdir(parents=True)
    (work_a_dir / "WORK.md").write_text(SAMPLE_SPAWNED_BY_INV)

    work_b_dir = tmp_path / "docs" / "work" / "active" / "E2-B"
    work_b_dir.mkdir(parents=True)
    (work_b_dir / "WORK.md").write_text(
        SAMPLE_SPAWNED_BY_INV.replace("E2-A", "E2-B").replace("INV-017", "E2-A")
    )

    # Action: Build spawn tree from INV-017
    tree = engine.spawn_tree("INV-017")

    # Assert: E2-A is child of INV-017, E2-B is child of E2-A
    assert "INV-017" in tree
    assert "E2-A" in tree["INV-017"]
    assert "E2-B" in tree["INV-017"]["E2-A"]


# =============================================================================
# E2-251: Backfill Tests
# =============================================================================

SAMPLE_WORK_WITH_PLACEHOLDER = """---
template: work_item
id: E2-021
title: Test Backfill Item
status: active
current_node: backlog
blocked_by: []
milestone: null
spawned_by: null
memory_refs: []
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
---
# E2-021

## Context

[Problem and root cause]

## Deliverables

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
"""

SAMPLE_BACKLOG_CONTENT = """
## Epoch 2 - Governance Suite

### [PENDING] E2-021: Memory Reference Governance
- **Context:** Memory refs should be linked to work items for traceability
- **Milestone:** M7b-WorkInfra
- **Spawned By:** ADR-032
- **Memory:** Concepts 64641-64652
- [ ] Add memory_refs field to work file schema
- [ ] Link memory operations to work items
"""


def test_backfill_updates_context(tmp_path, governance):
    """E2-251 Test 6: Placeholder [Problem and root cause] is replaced with backlog context."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Work file with placeholder, backlog with context
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-021"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_WITH_PLACEHOLDER)

    pm_dir = tmp_path / "docs" / "pm"
    pm_dir.mkdir(parents=True)
    (pm_dir / "backlog.md").write_text(SAMPLE_BACKLOG_CONTENT)

    # Action: Backfill E2-021
    success = engine.backfill("E2-021")

    # Assert: Context was updated
    assert success
    work_content = (work_dir / "WORK.md").read_text()
    assert "[Problem and root cause]" not in work_content
    assert "Memory refs should be linked" in work_content


def test_backfill_updates_deliverables(tmp_path, governance):
    """E2-251 Test 7: Placeholder deliverables are replaced with backlog checklist."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Work file with placeholder deliverables
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-021"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_WITH_PLACEHOLDER)

    pm_dir = tmp_path / "docs" / "pm"
    pm_dir.mkdir(parents=True)
    (pm_dir / "backlog.md").write_text(SAMPLE_BACKLOG_CONTENT)

    # Action: Backfill E2-021
    success = engine.backfill("E2-021")

    # Assert: Deliverables were updated
    assert success
    work_content = (work_dir / "WORK.md").read_text()
    assert "[Deliverable 1]" not in work_content
    assert "Add memory_refs field" in work_content


# =============================================================================
# E2-277: Portal System Tests
# =============================================================================

def test_create_work_creates_references_directory(tmp_path, governance):
    """E2-277 Test 1: WorkEngine.create_work creates references/ directory."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    engine.create_work("E2-TEST", "Test Work Item")

    refs_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST" / "references"
    assert refs_dir.exists()
    assert refs_dir.is_dir()


def test_create_work_creates_refs_md(tmp_path, governance):
    """E2-277 Test 2: WorkEngine.create_work creates REFS.md with frontmatter."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    engine.create_work("E2-TEST", "Test Work Item")

    refs_file = tmp_path / "docs" / "work" / "active" / "E2-TEST" / "references" / "REFS.md"
    assert refs_file.exists()
    content = refs_file.read_text()
    assert "type: portal-index" in content
    assert "work_id: E2-TEST" in content


def test_link_spawned_items_updates_portal(tmp_path, governance):
    """E2-277 Test 3: link_spawned_items updates REFS.md with spawned_from."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Create work item
    engine.create_work("E2-TEST", "Test Work Item")

    # Link to parent
    engine.link_spawned_items("INV-050", ["E2-TEST"])

    refs_file = tmp_path / "docs" / "work" / "active" / "E2-TEST" / "references" / "REFS.md"
    content = refs_file.read_text()
    assert "INV-050" in content
    assert "Spawned from" in content


def test_add_memory_refs_updates_portal(tmp_path, governance):
    """E2-277 Test 4: add_memory_refs updates REFS.md with memory concepts."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Create work item
    engine.create_work("E2-TEST", "Test Work Item")

    # Add memory refs
    engine.add_memory_refs("E2-TEST", [80910, 80911])

    refs_file = tmp_path / "docs" / "work" / "active" / "E2-TEST" / "references" / "REFS.md"
    content = refs_file.read_text()
    assert "80910" in content
    assert "Memory" in content


# =============================================================================
# WORK-001: Universal Work Item Structure Tests
# =============================================================================

# Sample WORK.md with universal structure (new fields)
SAMPLE_UNIVERSAL_WORK_MD = """---
template: work_item
id: WORK-001
title: Universal Work Item
type: feature
status: active
owner: Hephaestus
created: 2026-01-18
closed: null
priority: high
effort: medium
requirement_refs:
- REQ-001
- REQ-002
source_files:
- docs/specs/TRD-WORK-ITEM-UNIVERSAL.md
acceptance_criteria:
- AC1: Work items use sequential IDs
- AC2: Type is a field not prefix
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: '2026-01-18T16:00:00'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  custom_field: custom_value
version: "2.0"
---
# WORK-001: Universal Work Item
"""


def test_workstate_parses_universal_fields(tmp_path, governance):
    """WORK-001 Test 1: WorkState should parse type, requirement_refs, source_files, artifacts, extensions."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup work item with universal structure
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-001"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_UNIVERSAL_WORK_MD, encoding="utf-8")

    work = engine.get_work("WORK-001")

    assert work is not None
    assert work.id == "WORK-001"
    assert work.type == "feature"
    assert work.requirement_refs == ["REQ-001", "REQ-002"]
    assert work.source_files == ["docs/specs/TRD-WORK-ITEM-UNIVERSAL.md"]
    assert len(work.acceptance_criteria) == 2
    assert work.artifacts == []
    assert work.extensions == {"custom_field": "custom_value"}


def test_workstate_type_fallback_to_category(tmp_path, governance):
    """WORK-001 Test 4: Existing E2-XXX work items should still parse via category fallback."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup legacy work item with category field (no type field)
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-179"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_MD.replace("E2-TEST", "E2-179"), encoding="utf-8")

    work = engine.get_work("E2-179")

    assert work is not None
    assert work.id == "E2-179"
    assert work.status == "active"
    # Type should fall back to category value or default
    assert work.type in ["implementation", "feature"]  # Either fallback to category or default


def test_workstate_defaults_for_missing_universal_fields(tmp_path, governance):
    """WORK-001: Missing universal fields should have sensible defaults."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup legacy work item without new fields
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-LEGACY"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_MD.replace("E2-TEST", "E2-LEGACY"), encoding="utf-8")

    work = engine.get_work("E2-LEGACY")

    assert work is not None
    # All new fields should have empty list/dict defaults
    assert work.requirement_refs == []
    assert work.source_files == []
    assert work.acceptance_criteria == []
    assert work.artifacts == []
    assert work.extensions == {}


# =============================================================================
# E2-304: ID Validation Tests (REQ-VALID-001)
# Tests for status-aware ID validation in create_work()
# =============================================================================

def test_create_work_rejects_complete_status(tmp_path, governance):
    """E2-304: create_work should reject IDs with status=complete."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create work item with status=complete
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-COMPLETE"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_COMPLETE_WORK_MD, encoding="utf-8")

    # Action + Assert: Should raise WorkIDUnavailableError
    with pytest.raises(WorkIDUnavailableError) as exc:
        engine.create_work("E2-COMPLETE", "New Title")
    assert "already exists with status 'complete'" in str(exc.value)


def test_create_work_rejects_archived_status(tmp_path, governance):
    """E2-304: create_work should reject IDs with status=archived."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create work item with status=archived
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-ARCHIVED"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_ARCHIVED_WORK_MD, encoding="utf-8")

    # Action + Assert: Should raise WorkIDUnavailableError
    with pytest.raises(WorkIDUnavailableError) as exc:
        engine.create_work("E2-ARCHIVED", "New Title")
    assert "already exists with status 'archived'" in str(exc.value)


def test_create_work_allows_active_status(tmp_path, governance):
    """E2-304: create_work should allow overwriting active items (backward compat)."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create work item with status=active
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-ACTIVE"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_MD.replace("E2-TEST", "E2-ACTIVE"), encoding="utf-8")

    # Should succeed - overwriting active items is intentional (backward compat)
    result = engine.create_work("E2-ACTIVE", "Updated Title")
    assert result.exists()


def test_create_work_new_id_succeeds(tmp_path, governance):
    """E2-304: create_work should succeed for new IDs."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # No setup - ID doesn't exist
    result = engine.create_work("E2-NEW", "New Work Item")

    assert result.exists()
    assert "WORK.md" in str(result)


# =============================================================================
# WORK-085: Pause Point Recognition (REQ-LIFECYCLE-002, S27 Breath Model)
# =============================================================================

# Sample work item at CONCLUDE phase (investigation pause point)
SAMPLE_INV_AT_CONCLUDE = """---
template: work_item
id: INV-TEST
title: Test Investigation
type: investigation
status: active
owner: Hephaestus
created: 2026-02-03
closed: null
priority: high
blocked_by: []
blocks: []
current_node: CONCLUDE
node_history:
- node: backlog
  entered: '2026-02-03T10:00:00'
  exited: '2026-02-03T11:00:00'
- node: CONCLUDE
  entered: '2026-02-03T11:00:00'
  exited: null
memory_refs: []
---
# INV-TEST: Test Investigation
"""

# Sample work item at EXPLORE phase (not a pause point)
SAMPLE_INV_AT_EXPLORE = """---
template: work_item
id: INV-TEST
title: Test Investigation
type: investigation
status: active
owner: Hephaestus
created: 2026-02-03
closed: null
priority: high
blocked_by: []
blocks: []
current_node: EXPLORE
node_history:
- node: backlog
  entered: '2026-02-03T10:00:00'
  exited: '2026-02-03T11:00:00'
- node: EXPLORE
  entered: '2026-02-03T11:00:00'
  exited: null
memory_refs: []
---
# INV-TEST: Test Investigation
"""

# Sample feature at DONE phase (implementation pause point)
SAMPLE_FEATURE_AT_DONE = """---
template: work_item
id: WORK-TEST
title: Test Feature
type: feature
status: active
owner: Hephaestus
created: 2026-02-03
closed: null
priority: high
blocked_by: []
blocks: []
current_node: DONE
node_history:
- node: backlog
  entered: '2026-02-03T10:00:00'
  exited: '2026-02-03T11:00:00'
- node: DONE
  entered: '2026-02-03T11:00:00'
  exited: null
memory_refs: []
---
# WORK-TEST: Test Feature
"""


def test_is_at_pause_point_true_at_conclude(tmp_path, governance):
    """WORK-085: is_at_pause_point returns True when investigation is at CONCLUDE phase."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create investigation at CONCLUDE phase
    work_dir = tmp_path / "docs" / "work" / "active" / "INV-001"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(
        SAMPLE_INV_AT_CONCLUDE.replace("INV-TEST", "INV-001"),
        encoding="utf-8"
    )

    result = engine.is_at_pause_point("INV-001")
    assert result is True


def test_is_at_pause_point_false_at_explore(tmp_path, governance):
    """WORK-085: is_at_pause_point returns False when investigation is at EXPLORE phase (inhale, not pause)."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create investigation at EXPLORE phase
    work_dir = tmp_path / "docs" / "work" / "active" / "INV-002"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(
        SAMPLE_INV_AT_EXPLORE.replace("INV-TEST", "INV-002"),
        encoding="utf-8"
    )

    result = engine.is_at_pause_point("INV-002")
    assert result is False


def test_is_at_pause_point_false_for_unknown_work(tmp_path, governance):
    """WORK-085: is_at_pause_point returns False when work item doesn't exist."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    result = engine.is_at_pause_point("NONEXISTENT-001")
    assert result is False


def test_is_at_pause_point_feature_at_done(tmp_path, governance):
    """WORK-085: is_at_pause_point returns True when feature is at DONE phase."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create feature at DONE phase
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-001"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(
        SAMPLE_FEATURE_AT_DONE.replace("WORK-TEST", "WORK-001"),
        encoding="utf-8"
    )

    result = engine.is_at_pause_point("WORK-001")
    assert result is True


# =============================================================================
# WORK-066: Queue Position Field and Cycle Phase (Four-Dimensional Model)
# =============================================================================

# Sample work item with queue_position field
SAMPLE_WORK_WITH_QUEUE_POSITION = """---
template: work_item
id: WORK-QP
title: Work Item with Queue Position
type: feature
status: active
owner: Hephaestus
created: 2026-02-04
closed: null
priority: high
queue_position: in_progress
cycle_phase: plan
current_node: plan
blocked_by: []
blocks: []
node_history:
- node: backlog
  entered: '2026-02-04T10:00:00'
  exited: '2026-02-04T11:00:00'
- node: plan
  entered: '2026-02-04T11:00:00'
  exited: null
memory_refs: []
---
# WORK-QP: Work Item with Queue Position
"""

# Sample work item without queue_position (legacy format)
SAMPLE_WORK_LEGACY_NO_QUEUE = """---
template: work_item
id: WORK-LEGACY
title: Legacy Work Item
type: feature
status: active
owner: Hephaestus
created: 2026-02-04
closed: null
priority: high
current_node: implement
blocked_by: []
blocks: []
node_history:
- node: backlog
  entered: '2026-02-04T10:00:00'
  exited: null
memory_refs: []
---
# WORK-LEGACY: Legacy Work Item
"""


def test_parse_queue_position(tmp_path, governance):
    """WORK-066 Test 1: WorkEngine._parse_work_file reads queue_position field."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create work item with queue_position: in_progress
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-QP"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_WITH_QUEUE_POSITION, encoding="utf-8")

    work = engine.get_work("WORK-QP")

    assert work is not None
    assert work.queue_position == "in_progress"


def test_queue_position_defaults_to_backlog(tmp_path, governance):
    """WORK-066 Test 2: Work items without queue_position field default to 'backlog'."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create work item WITHOUT queue_position field (legacy format)
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-LEGACY"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_LEGACY_NO_QUEUE, encoding="utf-8")

    work = engine.get_work("WORK-LEGACY")

    assert work is not None
    assert work.queue_position == "backlog"


def test_set_queue_position(tmp_path, governance):
    """WORK-066 Test 3: WorkEngine.set_queue_position updates field in file."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create work item
    engine.create_work("WORK-SET", "Test Set Queue Position")

    # Action: Set queue_position to in_progress
    result = engine.set_queue_position("WORK-SET", "in_progress")

    # Assert: Result reflects update
    assert result is not None
    assert result.queue_position == "in_progress"

    # Assert: Re-read shows queue_position: in_progress
    work = engine.get_work("WORK-SET")
    assert work.queue_position == "in_progress"


def test_get_in_progress_items(tmp_path, governance):
    """WORK-066 Test 4: WorkEngine.get_in_progress returns items with queue_position: in_progress."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create 3 items
    engine.create_work("WORK-A", "Item A")
    engine.create_work("WORK-B", "Item B")
    engine.create_work("WORK-C", "Item C")

    # Set one to in_progress
    engine.set_queue_position("WORK-B", "in_progress")

    # Action
    in_progress = engine.get_in_progress()

    # Assert
    assert len(in_progress) == 1
    assert in_progress[0].id == "WORK-B"
    assert in_progress[0].queue_position == "in_progress"


def test_cycle_phase_falls_back_to_current_node(tmp_path, governance):
    """WORK-066 Test 5: cycle_phase falls back to current_node for legacy items."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create work item with current_node but NO cycle_phase
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-FALLBACK"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_LEGACY_NO_QUEUE, encoding="utf-8")

    work = engine.get_work("WORK-FALLBACK")

    assert work is not None
    # cycle_phase should fall back to current_node value
    assert work.cycle_phase == "implement"


def test_invalid_queue_position_raises(tmp_path, governance):
    """WORK-066 Test 6: set_queue_position rejects invalid values."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Setup: Create work item
    engine.create_work("WORK-INVALID", "Test Invalid Queue Position")

    # Action + Assert: Invalid value should raise ValueError
    with pytest.raises(ValueError) as exc:
        engine.set_queue_position("WORK-INVALID", "invalid_value")

    assert "invalid_value" in str(exc.value)
    assert "backlog" in str(exc.value) or "in_progress" in str(exc.value) or "done" in str(exc.value)
