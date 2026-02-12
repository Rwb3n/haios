# generated: 2026-02-12
"""
Tests for spawn ceremony execution and event logging (CH-017, WORK-137).

Tests the spawn_ceremonies module:
- execute_spawn(): Create child work item linked to parent with lineage
- log_spawn_ceremony(): Append SpawnWork events to JSONL
- _update_parent_children(): Maintain bidirectional parent-child links

Tests the WorkEngine.get_work_lineage() method.

Follows patterns from test_queue_ceremonies.py for module loading and fixtures.
"""
import json
import pytest
import yaml
from pathlib import Path

# WORK-117: Module loading handled by conftest.py (_load_module_once)
from governance_layer import GovernanceLayer
from work_engine import WorkEngine
import spawn_ceremonies
from ceremony_contracts import CeremonyContract, validate_ceremony_input


# =============================================================================
# Helpers
# =============================================================================


def _read_events(events_file: Path) -> list:
    """Read JSONL events file."""
    events = []
    if not events_file.exists():
        return events
    with open(events_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


def _read_frontmatter(path: Path) -> dict:
    """Read YAML frontmatter from a WORK.md file."""
    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def governance():
    """Create real GovernanceLayer for integration tests."""
    return GovernanceLayer()


@pytest.fixture
def engine(tmp_path, governance):
    """Create WorkEngine with real GovernanceLayer and tmp_path."""
    return WorkEngine(governance=governance, base_path=tmp_path)


@pytest.fixture(autouse=True)
def patch_events_file(tmp_path):
    """Redirect EVENTS_FILE to tmp_path for test isolation."""
    original = spawn_ceremonies.EVENTS_FILE
    spawn_ceremonies.EVENTS_FILE = tmp_path / "test-events.jsonl"
    yield
    spawn_ceremonies.EVENTS_FILE = original


@pytest.fixture
def parent_work(engine):
    """Create a parent work item for spawn tests."""
    engine.create_work("WORK-001", "Parent Investigation")
    return "WORK-001"


# =============================================================================
# Test 1: Spawn creates child with spawned_by linking
# =============================================================================


def test_spawn_creates_child_with_lineage(tmp_path, engine, parent_work):
    """execute_spawn() creates child WORK.md with spawned_by set to parent."""
    result = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id=parent_work,
        title="Child Implementation",
        work_type="implementation",
    )

    assert result["success"] is True
    new_work_id = result["new_work_id"]
    assert new_work_id.startswith("WORK-")

    # Verify child has spawned_by pointing to parent
    child_path = tmp_path / "docs" / "work" / "active" / new_work_id / "WORK.md"
    child_fm = _read_frontmatter(child_path)
    assert child_fm["spawned_by"] == parent_work


# =============================================================================
# Test 2: Spawn updates parent spawned_children
# =============================================================================


def test_spawn_updates_parent_children(tmp_path, engine, parent_work):
    """execute_spawn() adds child ID to parent's spawned_children field."""
    result = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id=parent_work,
        title="Child Task",
    )

    assert result["success"] is True
    new_work_id = result["new_work_id"]

    # Verify parent has child in spawned_children
    parent_path = tmp_path / "docs" / "work" / "active" / parent_work / "WORK.md"
    parent_fm = _read_frontmatter(parent_path)
    assert new_work_id in parent_fm.get("spawned_children", [])


# =============================================================================
# Test 3: Spawn logs SpawnWork event
# =============================================================================


def test_spawn_logs_event(tmp_path, engine, parent_work):
    """execute_spawn() logs SpawnWork event to governance-events.jsonl."""
    result = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id=parent_work,
        title="Follow-on task",
        rationale="Investigation revealed implementation need",
        agent="Hephaestus",
    )

    assert result["success"] is True
    new_work_id = result["new_work_id"]

    events = _read_events(spawn_ceremonies.EVENTS_FILE)
    spawn_events = [e for e in events if e["type"] == "SpawnWork"]
    assert len(spawn_events) == 1
    event = spawn_events[0]
    assert event["parent_work_id"] == parent_work
    assert event["new_work_id"] == new_work_id
    assert event["ceremony"] == "spawn-work"
    assert event["rationale"] == "Investigation revealed implementation need"
    assert event["agent"] == "Hephaestus"
    assert "timestamp" in event


# =============================================================================
# Test 4: Spawn validates parent exists
# =============================================================================


def test_spawn_fails_for_nonexistent_parent(tmp_path, engine):
    """execute_spawn() returns error when parent work item doesn't exist."""
    result = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id="WORK-999",
        title="Orphan task",
    )

    assert result["success"] is False
    assert "not found" in result["error"]
    assert result["parent_work_id"] == "WORK-999"


# =============================================================================
# Test 5: Spawn contract validation
# =============================================================================


def test_spawn_contract_validates_inputs():
    """Ceremony contract validates required inputs."""
    # Load contract from SKILL.md frontmatter
    skill_path = Path(".claude/skills/spawn-work-ceremony/SKILL.md")
    content = skill_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1]) or {}
    contract = CeremonyContract.from_frontmatter(fm)

    # Missing required field: parent_work_id
    result = validate_ceremony_input(contract, {"title": "Some task"})
    assert not result.valid
    assert any("parent_work_id" in e for e in result.errors)

    # Missing required field: title
    result = validate_ceremony_input(contract, {"parent_work_id": "WORK-001"})
    assert not result.valid
    assert any("title" in e for e in result.errors)

    # Valid inputs
    result = validate_ceremony_input(contract, {
        "parent_work_id": "WORK-001",
        "title": "Follow-on task",
    })
    assert result.valid


# =============================================================================
# Test 6: get_work_lineage returns parent and children
# =============================================================================


def test_get_work_lineage(tmp_path, engine, parent_work):
    """WorkEngine.get_work_lineage() returns parent and children."""
    result = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id=parent_work,
        title="Child for lineage test",
    )
    new_work_id = result["new_work_id"]

    # Check child lineage — has parent, no children
    child_lineage = engine.get_work_lineage(new_work_id)
    assert child_lineage["parent"] == parent_work
    assert child_lineage["children"] == []

    # Check parent lineage — no parent, has child
    parent_lineage = engine.get_work_lineage(parent_work)
    assert parent_lineage["parent"] is None
    assert new_work_id in parent_lineage["children"]


# =============================================================================
# Test 7: Multiple spawns accumulate in parent
# =============================================================================


def test_multiple_spawns_accumulate(tmp_path, engine, parent_work):
    """Multiple spawns from same parent accumulate in spawned_children."""
    result1 = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id=parent_work,
        title="First child",
        _override_work_id="WORK-CHILD-A",
    )
    result2 = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id=parent_work,
        title="Second child",
        _override_work_id="WORK-CHILD-B",
    )

    assert result1["success"] is True
    assert result2["success"] is True

    parent_path = tmp_path / "docs" / "work" / "active" / parent_work / "WORK.md"
    parent_fm = _read_frontmatter(parent_path)
    children = parent_fm.get("spawned_children", [])
    assert len(children) == 2
    assert result1["new_work_id"] in children
    assert result2["new_work_id"] in children


# =============================================================================
# Test 8: Spawn returns correct output contract
# =============================================================================


def test_spawn_output_contract(tmp_path, engine, parent_work):
    """execute_spawn() returns output matching ceremony contract."""
    result = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id=parent_work,
        title="Contract test child",
    )

    # Success case: has success, new_work_id, parent_work_id
    assert result["success"] is True
    assert result["new_work_id"].startswith("WORK-")
    assert result["parent_work_id"] == parent_work

    # Failure case: has success, error, parent_work_id
    fail_result = spawn_ceremonies.execute_spawn(
        work_engine=engine,
        parent_work_id="WORK-NOPE",
        title="Should fail",
    )
    assert fail_result["success"] is False
    assert "error" in fail_result
    assert fail_result["parent_work_id"] == "WORK-NOPE"
