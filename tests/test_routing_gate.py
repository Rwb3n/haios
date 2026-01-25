# generated: 2025-12-28
# System Auto: last updated on: 2026-01-25T21:25:47
"""Tests for routing.py routing-gate logic (E2-221).

Tests the pure work-type routing logic. Threshold checks are in OBSERVE phase (E2-224).
"""

import pytest
import sys
from pathlib import Path

# Add .claude/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))

from routing import determine_route


class TestDetermineRoute:
    """Tests for determine_route() function."""

    def test_route_investigation_by_prefix(self):
        """INV-* IDs should route to investigation-cycle."""
        result = determine_route(next_work_id="INV-049", has_plan=False)

        assert result["action"] == "invoke_investigation"
        assert "INV-" in result["reason"]

    def test_route_implementation_when_has_plan(self):
        """Work items with plans should route to implementation-cycle."""
        result = determine_route(next_work_id="E2-221", has_plan=True)

        assert result["action"] == "invoke_implementation"
        assert "plan" in result["reason"].lower()

    def test_route_work_creation_when_no_plan(self):
        """Work items without plans should route to work-creation-cycle."""
        result = determine_route(next_work_id="E2-222", has_plan=False)

        assert result["action"] == "invoke_work_creation"
        assert "no plan" in result["reason"].lower() or "work-creation" in result["reason"].lower()

    def test_await_operator_when_no_work(self):
        """No work items should return await_operator."""
        result = determine_route(next_work_id=None, has_plan=False)

        assert result["action"] == "await_operator"
        assert "no" in result["reason"].lower() or "await" in result["reason"].lower()

    def test_returns_dict_with_required_keys(self):
        """Result should always have action and reason keys."""
        result = determine_route(next_work_id="E2-001", has_plan=True)

        assert "action" in result
        assert "reason" in result
        assert isinstance(result["action"], str)
        assert isinstance(result["reason"], str)

    # WORK-014: Type-based routing tests
    def test_route_investigation_by_type_field(self):
        """WORK-XXX with type: investigation routes to investigation-cycle."""
        result = determine_route(
            next_work_id="WORK-014",
            has_plan=False,
            work_type="investigation"
        )
        assert result["action"] == "invoke_investigation"

    def test_route_legacy_inv_prefix_without_type(self):
        """INV-XXX still routes to investigation-cycle (backward compat)."""
        result = determine_route(
            next_work_id="INV-017",
            has_plan=False,
            work_type=None  # Legacy items may not have type
        )
        assert result["action"] == "invoke_investigation"

    def test_route_feature_type_without_plan(self):
        """Feature type without plan goes to work-creation."""
        result = determine_route(
            next_work_id="WORK-015",
            has_plan=False,
            work_type="feature"
        )
        assert result["action"] == "invoke_work_creation"

    def test_route_work_type_none_fallback(self):
        """work_type=None with non-INV prefix falls back to plan check."""
        result = determine_route(
            next_work_id="WORK-016",
            has_plan=True,
            work_type=None
        )
        assert result["action"] == "invoke_implementation"
