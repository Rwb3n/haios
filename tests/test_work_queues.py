# generated: 2026-01-15
# System Auto: last updated on: 2026-01-19T18:00:29
"""
Tests for Work Queue functionality (E2-290).

Tests queue loading, ordering, cycle-locking, and backward compatibility.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add modules to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))

from work_engine import WorkEngine, WorkState
from governance_layer import GovernanceLayer


@pytest.fixture
def engine():
    """Create WorkEngine with mocked governance."""
    governance = MagicMock(spec=GovernanceLayer)
    return WorkEngine(governance=governance)


class TestWorkQueues:
    """Test suite for work queue functionality."""

    def test_load_queues_from_yaml(self, tmp_path, engine):
        """Verify work_queues.yaml loads correctly."""
        # Create temp config
        config_content = """
version: "1.0"
queues:
  default:
    type: priority
    items: auto
    allowed_cycles: [implementation-cycle]
"""
        config_file = tmp_path / "work_queues.yaml"
        config_file.write_text(config_content)

        with patch.object(engine, '_get_queue_config_path', return_value=config_file):
            queues = engine.load_queues()

        assert "default" in queues
        assert queues["default"].type == "priority"

    def test_priority_queue_ordering(self, engine):
        """High priority items come first."""
        # Create mock work items with different priorities
        high = WorkState(id="E2-001", title="High", status="active", current_node="backlog", priority="high")
        medium = WorkState(id="E2-002", title="Medium", status="active", current_node="backlog", priority="medium")
        low = WorkState(id="E2-003", title="Low", status="active", current_node="backlog", priority="low")

        # Mock get_ready to return items in wrong order
        with patch.object(engine, 'get_ready', return_value=[low, high, medium]):
            with patch.object(engine, 'load_queues', return_value={
                "default": MagicMock(type="priority", items="auto", allowed_cycles=[])
            }):
                items = engine.get_queue("default")

        # High should be first
        assert items[0].priority == "high"

    def test_cycle_locking_blocks_wrong_cycle(self, engine):
        """Queue with allowed_cycles blocks other cycles."""
        # Mock load_queues to return planning-only queue
        with patch.object(engine, 'load_queues', return_value={
            "planning-queue": MagicMock(
                type="priority",
                items="auto",
                allowed_cycles=["plan-authoring-cycle"]
            )
        }):
            assert engine.is_cycle_allowed("planning-queue", "plan-authoring-cycle") == True
            assert engine.is_cycle_allowed("planning-queue", "implementation-cycle") == False

    def test_get_next_returns_queue_head(self, engine):
        """get_next() returns first item from queue."""
        first = WorkState(id="E2-001", title="First", status="active", current_node="backlog")
        second = WorkState(id="E2-002", title="Second", status="active", current_node="backlog")

        with patch.object(engine, 'get_queue', return_value=[first, second]):
            next_item = engine.get_next("default")

        assert next_item == first

    def test_get_ready_unchanged(self, engine):
        """Existing get_ready() still works (backward compatibility)."""
        # This should not raise - get_ready() exists and returns list
        ready = engine.get_ready()
        assert isinstance(ready, list)

    def test_empty_queue_returns_none(self, engine):
        """get_next() returns None for empty queue."""
        with patch.object(engine, 'get_queue', return_value=[]):
            next_item = engine.get_next("default")

        assert next_item is None

    def test_unknown_queue_fallback(self, engine):
        """Unknown queue name falls back to get_ready()."""
        item = WorkState(id="E2-001", title="Item", status="active", current_node="backlog")

        with patch.object(engine, 'load_queues', return_value={}):
            with patch.object(engine, 'get_ready', return_value=[item]):
                items = engine.get_queue("nonexistent")

        assert items == [item]

    def test_governance_queue_cycle_enforcement(self, engine):
        """E2-291: Governance queue allows implementation and investigation, blocks work-creation."""
        # Mock governance queue matching work_queues.yaml config
        with patch.object(engine, 'load_queues', return_value={
            "governance": MagicMock(
                type="priority",
                items=["E2-291", "INV-054", "INV-041", "E2-164"],
                allowed_cycles=["implementation-cycle", "investigation-cycle"]
            )
        }):
            # These should be allowed
            assert engine.is_cycle_allowed("governance", "implementation-cycle") == True
            assert engine.is_cycle_allowed("governance", "investigation-cycle") == True
            # This should be blocked
            assert engine.is_cycle_allowed("governance", "work-creation-cycle") == False

    def test_explicit_list_filters_completed_items(self, engine):
        """Session 211 Bug 1: Explicit item lists filter out completed items."""
        # Create mock work items - one active, one complete
        active_item = WorkState(
            id="E2-179", title="Active", status="active", current_node="backlog", priority="medium"
        )
        complete_item = WorkState(
            id="WORK-001", title="Complete", status="complete", current_node="backlog", priority="critical"
        )

        # Mock the work existence and get_work for explicit list
        with patch.object(engine, 'load_queues', return_value={
            "test-queue": MagicMock(type="fifo", items=["WORK-001", "E2-179"], allowed_cycles=[])
        }):
            with patch.object(engine, '_work_exists', return_value=True):
                with patch.object(engine, 'get_work', side_effect=lambda id: complete_item if id == "WORK-001" else active_item):
                    items = engine.get_queue("test-queue")

        # Complete item should be filtered out
        assert len(items) == 1
        assert items[0].id == "E2-179"

    def test_fifo_explicit_list_preserves_yaml_order(self, engine):
        """Session 211 Bug 2: FIFO with explicit items preserves YAML order."""
        # Create items with different creation dates
        first = WorkState(
            id="E2-001", title="First in YAML", status="active", current_node="backlog",
            node_history=[{"entered": "2026-01-19T10:00:00", "exited": None}]  # Later date
        )
        second = WorkState(
            id="E2-002", title="Second in YAML", status="active", current_node="backlog",
            node_history=[{"entered": "2026-01-18T10:00:00", "exited": None}]  # Earlier date
        )

        # Mock FIFO queue with explicit order [E2-001, E2-002]
        with patch.object(engine, 'load_queues', return_value={
            "fifo-queue": MagicMock(type="fifo", items=["E2-001", "E2-002"], allowed_cycles=[])
        }):
            with patch.object(engine, '_work_exists', return_value=True):
                # Return items in YAML order when called
                def mock_get_work(id):
                    return first if id == "E2-001" else second
                with patch.object(engine, 'get_work', side_effect=mock_get_work):
                    items = engine.get_queue("fifo-queue")

        # Should preserve YAML order, not sort by creation date
        assert len(items) == 2
        assert items[0].id == "E2-001"  # First in YAML, despite later creation date
        assert items[1].id == "E2-002"  # Second in YAML, despite earlier creation date

    def test_fifo_auto_list_sorts_by_creation_date(self, engine):
        """FIFO with auto items still sorts by creation date."""
        # Create items with different creation dates
        earlier = WorkState(
            id="E2-002", title="Earlier", status="active", current_node="backlog",
            node_history=[{"entered": "2026-01-18T10:00:00", "exited": None}]
        )
        later = WorkState(
            id="E2-001", title="Later", status="active", current_node="backlog",
            node_history=[{"entered": "2026-01-19T10:00:00", "exited": None}]
        )

        # Mock get_ready to return items in wrong order
        with patch.object(engine, 'get_ready', return_value=[later, earlier]):
            with patch.object(engine, 'load_queues', return_value={
                "fifo-queue": MagicMock(type="fifo", items="auto", allowed_cycles=[])
            }):
                items = engine.get_queue("fifo-queue")

        # Should sort by creation date - earlier first
        assert items[0].id == "E2-002"  # Earlier creation date
        assert items[1].id == "E2-001"  # Later creation date
