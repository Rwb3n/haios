# generated: 2026-02-14
# WORK-075: Tests for L4 requirement coverage audit script
"""Tests for scripts/audit_l4_coverage.py.

Validates parsing of traces_to from work items, building L4 coverage maps,
parsing epoch decisions, and gap analysis.
"""
import sys
from pathlib import Path

# Add scripts/ to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from audit_l4_coverage import (
    parse_traces_to,
    build_l4_coverage,
    parse_epoch_decisions,
    find_gaps,
)


class TestParseTracesTo:
    """Test extraction of traces_to from WORK.md frontmatter."""

    def test_extracts_requirement_ids(self):
        work_content = (
            "---\n"
            "id: WORK-075\n"
            "traces_to:\n"
            "- REQ-TRACE-005\n"
            "status: complete\n"
            "---\n"
            "# Title\n"
        )
        result = parse_traces_to(work_content)
        assert result == {
            "id": "WORK-075",
            "traces_to": ["REQ-TRACE-005"],
            "status": "complete",
        }

    def test_handles_multiple_traces(self):
        work_content = (
            "---\n"
            "id: WORK-015\n"
            "traces_to:\n"
            "- REQ-TRACE-001\n"
            "- REQ-TRACE-002\n"
            "status: active\n"
            "---\n"
        )
        result = parse_traces_to(work_content)
        assert result["traces_to"] == ["REQ-TRACE-001", "REQ-TRACE-002"]

    def test_handles_missing_traces_to_field(self):
        """Legacy work items (E2-xxx, INV-xxx) may lack traces_to entirely."""
        work_content = (
            "---\n"
            "id: E2-235\n"
            "status: complete\n"
            "category: feature\n"
            "---\n"
        )
        result = parse_traces_to(work_content)
        assert result["id"] == "E2-235"
        assert result["traces_to"] == []
        assert result["status"] == "complete"

    def test_handles_empty_traces_to_list(self):
        work_content = (
            "---\n"
            "id: WORK-080\n"
            "traces_to: []\n"
            "status: active\n"
            "---\n"
        )
        result = parse_traces_to(work_content)
        assert result["traces_to"] == []


class TestBuildL4Coverage:
    """Test building coverage map from work items."""

    def test_maps_requirements_to_work_items(self):
        work_items = [
            {"id": "WORK-001", "traces_to": ["REQ-TRACE-001", "REQ-TRACE-002"], "status": "complete"},
            {"id": "WORK-002", "traces_to": ["REQ-TRACE-001"], "status": "active"},
        ]
        all_req_ids = ["REQ-TRACE-001", "REQ-TRACE-002", "REQ-TRACE-003"]
        coverage = build_l4_coverage(work_items, all_req_ids)
        assert coverage["REQ-TRACE-001"] == [("WORK-001", "complete"), ("WORK-002", "active")]
        assert coverage["REQ-TRACE-002"] == [("WORK-001", "complete")]
        assert coverage["REQ-TRACE-003"] == []  # Gap

    def test_ignores_items_without_traces(self):
        work_items = [
            {"id": "E2-235", "traces_to": [], "status": "complete"},
        ]
        all_req_ids = ["REQ-TRACE-001"]
        coverage = build_l4_coverage(work_items, all_req_ids)
        assert coverage["REQ-TRACE-001"] == []


class TestParseEpochDecisions:
    """Test extraction of decisions from EPOCH.md."""

    def test_extracts_all_decisions(self):
        epoch_content = (
            "## Core Decisions (Session 265)\n\n"
            "### Decision 1: Five-Layer Hierarchy\n\n"
            "Some descriptive text about the decision.\n\n"
            "### Decision 2: Work Classification (Two-Axis)\n\n"
            "More text about classification.\n"
        )
        decisions = parse_epoch_decisions(epoch_content)
        assert len(decisions) == 2
        assert decisions["D1"]["title"] == "Five-Layer Hierarchy"
        assert decisions["D2"]["title"] == "Work Classification (Two-Axis)"

    def test_handles_session_additions_format(self):
        """Decisions added in later sessions use same header pattern."""
        epoch_content = (
            "## Session 276 Additions\n\n"
            "### Decision 7: Four-Dimensional Work Item State (WORK-065)\n\n"
            "Details here.\n"
        )
        decisions = parse_epoch_decisions(epoch_content)
        assert len(decisions) == 1
        assert decisions["D7"]["title"] == "Four-Dimensional Work Item State (WORK-065)"


class TestFindGaps:
    """Test gap analysis logic."""

    def test_finds_uncovered_requirements(self):
        coverage = {
            "REQ-TRACE-001": [("WORK-001", "complete")],
            "REQ-TRACE-002": [],
            "REQ-OBSERVE-001": [],
        }
        gaps = find_gaps(coverage)
        assert "REQ-TRACE-002" in gaps
        assert "REQ-OBSERVE-001" in gaps
        assert "REQ-TRACE-001" not in gaps

    def test_no_gaps_when_all_covered(self):
        coverage = {
            "REQ-TRACE-001": [("WORK-001", "complete")],
            "REQ-TRACE-002": [("WORK-002", "active")],
        }
        gaps = find_gaps(coverage)
        assert len(gaps) == 0

    def test_all_gaps_when_none_covered(self):
        coverage = {
            "REQ-TRACE-001": [],
            "REQ-TRACE-002": [],
        }
        gaps = find_gaps(coverage)
        assert len(gaps) == 2
