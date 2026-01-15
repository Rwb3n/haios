# generated: 2026-01-15
# System Auto: last updated on: 2026-01-15T21:22:13
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
