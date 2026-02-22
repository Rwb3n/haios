# generated: 2026-02-11
# Session: 344
# WORK-121: Enforce Critique Gate Before DO Phase
"""
Tests for WORK-121: Critique gate enforcement in implementation-cycle.

Verifies:
1. implementation-cycle PLAN phase references critique-agent
2. PLAN phase exit criteria includes critique with revise loop and verdicts
3. plan-validation-cycle no longer has CRITIQUE phase (moved to implementation-cycle)
4. plan-validation-cycle phase numbering is consistent after CRITIQUE removal
"""

from pathlib import Path


class TestImplementationCycleCritiqueGate:
    """Tests for critique-agent presence in implementation-cycle PLAN phase."""

    def test_implementation_cycle_plan_phase_references_critique(self):
        """PLAN phase exit gate must reference critique-agent."""
        # After fracturing (WORK-187), critique content lives in phases/PLAN.md
        plan_phase_path = Path(".claude/skills/implementation-cycle/phases/PLAN.md")
        content = plan_phase_path.read_text()

        assert "critique-agent" in content, (
            "implementation-cycle phases/PLAN.md must reference critique-agent"
        )

    def test_plan_phase_exit_criteria_includes_critique(self):
        """PLAN phase exit criteria must include critique with verdicts."""
        # After fracturing (WORK-187), critique content lives in phases/PLAN.md
        plan_phase_path = Path(".claude/skills/implementation-cycle/phases/PLAN.md")
        content = plan_phase_path.read_text()

        # Exit criteria must mention critique
        assert "critique" in content.lower(), (
            "PLAN phase must mention critique"
        )

        # Must describe the revise loop
        assert "revise" in content.lower(), (
            "PLAN phase must describe critique-revise loop"
        )

        # Must describe the three verdicts
        assert "PROCEED" in content, "Must describe PROCEED verdict"
        assert "REVISE" in content, "Must describe REVISE verdict"
        assert "BLOCK" in content, "Must describe BLOCK verdict"


class TestPlanValidationCycleCritiqueRemoval:
    """Tests for CRITIQUE phase removal from plan-validation-cycle."""

    def test_plan_validation_cycle_no_critique_phase(self):
        """plan-validation-cycle should not have a CRITIQUE phase."""
        skill_path = Path(".claude/skills/plan-validation-cycle/SKILL.md")
        content = skill_path.read_text()

        # Should NOT have a CRITIQUE phase header
        assert "### 3. CRITIQUE Phase" not in content, (
            "plan-validation-cycle should not have CRITIQUE phase "
            "(moved to implementation-cycle)"
        )

        # The cycle diagram should be 4-phase
        assert "CHECK --> SPEC_ALIGN --> VALIDATE --> APPROVE" in content, (
            "plan-validation-cycle should be 4-phase: "
            "CHECK->SPEC_ALIGN->VALIDATE->APPROVE"
        )

    def test_plan_validation_cycle_phase_numbering(self):
        """After CRITIQUE removal, phases should be numbered 1-4."""
        skill_path = Path(".claude/skills/plan-validation-cycle/SKILL.md")
        content = skill_path.read_text()

        assert "### 1. CHECK Phase" in content
        assert "### 2. SPEC_ALIGN Phase" in content
        assert "### 3. VALIDATE Phase" in content
        assert "### 4. APPROVE Phase" in content
