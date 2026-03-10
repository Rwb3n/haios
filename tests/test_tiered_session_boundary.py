# generated: 2026-03-10
"""
Tests for WORK-289: Tiered Session Architecture — Plan/Build Session Boundary.

Verifies skill file content matches the tiered session architecture specification:
1. PLAN phase documents session yield for standard+ tiers
2. PLAN phase preserves single-session behavior for trivial/small (regression guard)
3. Survey-cycle documents approved-plan fast-path routing with three-condition check
4. Implementation-cycle slim router documents direct DO-phase entry
5. Existing plan-authoring-agent references preserved (regression guard)
"""

from pathlib import Path


class TestTieredSessionBoundary:
    """Test suite for tiered session architecture skill content."""

    def test_plan_phase_documents_session_yield_for_standard(self):
        """Verify PLAN phase has session yield block for standard tier."""
        plan_path = Path(".claude/skills/implementation-cycle/phases/PLAN.md")
        assert plan_path.exists(), "phases/PLAN.md must exist"
        content = plan_path.read_text()
        assert "Session Yield" in content, "Must document Session Yield"
        assert "standard" in content, "Must reference standard tier"
        assert "checkpoint-cycle" in content, "Must invoke checkpoint-cycle"
        assert "Do NOT proceed to DO phase" in content, "Must have hard stop instruction"

    def test_plan_phase_single_session_guard_present(self):
        """Verify PLAN phase has regression guard for trivial/small tiers."""
        plan_path = Path(".claude/skills/implementation-cycle/phases/PLAN.md")
        assert plan_path.exists(), "phases/PLAN.md must exist"
        content = plan_path.read_text()
        assert "trivial and small tiers are NOT affected" in content, (
            "Must have explicit regression guard for trivial/small"
        )

    def test_survey_cycle_documents_approved_plan_fast_path(self):
        """Verify survey-cycle has approved-plan fast-path routing with three-condition check."""
        skill_path = Path(".claude/skills/survey-cycle/SKILL.md")
        assert skill_path.exists(), "survey-cycle/SKILL.md must exist"
        content = skill_path.read_text()
        assert "status: approved" in content, "Must check plan status: approved"
        assert "cycle_phase: PLAN" in content, "Must check cycle_phase: PLAN"
        assert "DO phase" in content, "Must route to DO phase"
        assert "skip PLAN" in content, "Must document PLAN phase skip"
        assert "pending" in content, "Must check pending field (third condition)"

    def test_implementation_cycle_documents_direct_do_entry(self):
        """Verify implementation-cycle slim router documents direct DO-phase entry."""
        skill_path = Path(".claude/skills/implementation-cycle/SKILL.md")
        assert skill_path.exists(), "implementation-cycle/SKILL.md must exist"
        content = skill_path.read_text()
        line_count = len(content.splitlines())
        assert line_count <= 100, f"SKILL.md must be <= 100 lines, got {line_count}"
        assert "Direct DO-Phase Entry" in content, "Must document direct DO entry"
        assert "Build-Session" in content, "Must reference build-session context"
        assert "skip PLAN phase" in content, "Must document PLAN phase skip"

    def test_plan_phase_still_references_authoring_agent(self):
        """Regression guard: plan-authoring-agent still referenced in PLAN phase."""
        plan_path = Path(".claude/skills/implementation-cycle/phases/PLAN.md")
        assert plan_path.exists(), "phases/PLAN.md must exist"
        content = plan_path.read_text()
        assert "plan-authoring-agent" in content, "Must still reference plan-authoring-agent"
        assert "Task(subagent_type='plan-authoring-agent'" in content, (
            "Must still have Task invocation for plan-authoring-agent"
        )
