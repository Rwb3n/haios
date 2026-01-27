# generated: 2025-12-29
# System Auto: last updated on: 2026-01-27T20:59:12
"""Tests for work file integrity validation (E2-163).

Tests validate_cycle_docs_consistency() and validate_node_history_integrity()
functions added to .claude/haios/lib/validate.py.
"""

import sys
from pathlib import Path

import pytest

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from validate import (
    validate_cycle_docs_consistency,
    validate_node_history_integrity,
    validate_template,
)


class TestCycleDocsConsistency:
    """Tests for validate_cycle_docs_consistency()."""

    def test_cycle_docs_missing_plan_id(self):
        """Detect cycle_docs without plan_id when documents.plans has entries."""
        metadata = {
            "documents": {"plans": ["PLAN.md"]},
            "cycle_docs": {},  # Missing plan_id
        }
        errors = validate_cycle_docs_consistency(metadata)
        assert len(errors) == 1
        assert "cycle_docs.plan_id missing" in errors[0]

    def test_cycle_docs_consistent(self):
        """Pass when cycle_docs matches documents."""
        metadata = {
            "documents": {"plans": ["PLAN.md"]},
            "cycle_docs": {"plan_id": "PLAN"},
        }
        errors = validate_cycle_docs_consistency(metadata)
        assert errors == []

    def test_cycle_docs_empty_documents_ok(self):
        """Pass when documents is empty (new work item)."""
        metadata = {
            "documents": {"plans": [], "investigations": []},
            "cycle_docs": {},
        }
        errors = validate_cycle_docs_consistency(metadata)
        assert errors == []


class TestNodeHistoryIntegrity:
    """Tests for validate_node_history_integrity()."""

    def test_node_history_missing_entered(self):
        """Detect node_history entry without entered field."""
        metadata = {
            "node_history": [{"node": "backlog"}],  # Missing entered
        }
        errors = validate_node_history_integrity(metadata)
        assert len(errors) == 1
        assert "missing 'entered' field" in errors[0]

    def test_node_history_out_of_order(self):
        """Detect timestamps that go backward."""
        metadata = {
            "node_history": [
                {"node": "backlog", "entered": "2025-12-29T10:00:00", "exited": "2025-12-29T11:00:00"},
                {"node": "plan", "entered": "2025-12-29T09:00:00"},  # Before previous!
            ],
        }
        errors = validate_node_history_integrity(metadata)
        assert len(errors) == 1
        assert "out-of-order timestamp" in errors[0]

    def test_node_history_consistent(self):
        """Pass when timestamps are in order."""
        metadata = {
            "node_history": [
                {"node": "backlog", "entered": "2025-12-29T09:00:00", "exited": "2025-12-29T10:00:00"},
                {"node": "plan", "entered": "2025-12-29T10:00:00", "exited": None},
            ],
        }
        errors = validate_node_history_integrity(metadata)
        assert errors == []

    def test_node_history_empty_ok(self):
        """Pass when node_history is empty (new work item)."""
        metadata = {"node_history": []}
        errors = validate_node_history_integrity(metadata)
        assert errors == []


class TestValidateTemplateIntegration:
    """Integration tests for work file validation."""

    def test_validate_template_includes_work_file_checks(self, tmp_path):
        """Work file validation includes integrity checks."""
        work_file = tmp_path / "WORK.md"
        work_file.write_text(
            """---
template: work_item
id: TEST-001
title: "Test Work"
status: active
current_node: backlog
documents:
  plans: ["PLAN.md"]
cycle_docs: {}
node_history: []
---
# WORK-TEST-001: Test Work

@docs/README.md
@docs/epistemic_state.md

## Context
Test context with sufficient content to pass placeholder detection.

## Current State
Test state with sufficient content to pass placeholder detection.

## Deliverables
- [ ] Test deliverable with sufficient content.
"""
        )
        result = validate_template(str(work_file))
        assert not result["is_valid"]
        assert any("cycle_docs" in e for e in result["errors"])
