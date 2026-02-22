# generated: 2026-02-22
# WORK-187: Fracture Implementation-Cycle SKILL.md into Phase Files
"""
Tests for WORK-187: Phase-per-file fracturing of implementation-cycle SKILL.md.

Verifies:
1. Slim router line count <= 100
2. All 5 phase files exist under phases/
3. Both reference files exist under reference/
4. PLAN phase file contains critique contract (moved from SKILL.md)
5. PLAN phase file contains plan-authoring-agent delegation
6. Phase files are self-contained (no cross-phase references)
7. Slim router retains cycle diagram and phase table
"""

from pathlib import Path

SKILL_DIR = Path(".claude/skills/implementation-cycle")


class TestSlimRouter:
    """Verify the slim SKILL.md router meets size and content constraints."""

    def test_slim_router_line_count(self):
        """Slim router must be <= 100 lines (target ~80)."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        line_count = len(content.splitlines())
        assert line_count <= 100, (
            f"Slim router is {line_count} lines — must be <= 100. "
            "Phase content should be in phases/ files."
        )

    def test_slim_router_has_cycle_diagram(self):
        """Slim router must retain the PLAN->DO->CHECK->DONE->CHAIN cycle diagram."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        assert "PLAN --> DO --> CHECK --> DONE --> CHAIN" in content, (
            "Slim router must contain the cycle diagram"
        )

    def test_slim_router_has_phase_table(self):
        """Slim router must contain a phase table referencing phase files."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        for phase in ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]:
            assert phase in content, f"Slim router must reference {phase} phase"
        assert "phases/" in content, "Slim router must reference phases/ directory"


class TestPhaseFilesExist:
    """Verify all required phase files exist."""

    def test_plan_phase_exists(self):
        assert (SKILL_DIR / "phases" / "PLAN.md").exists()

    def test_do_phase_exists(self):
        assert (SKILL_DIR / "phases" / "DO.md").exists()

    def test_check_phase_exists(self):
        assert (SKILL_DIR / "phases" / "CHECK.md").exists()

    def test_done_phase_exists(self):
        assert (SKILL_DIR / "phases" / "DONE.md").exists()

    def test_chain_phase_exists(self):
        assert (SKILL_DIR / "phases" / "CHAIN.md").exists()


class TestReferenceFilesExist:
    """Verify all required reference files exist."""

    def test_decisions_reference_exists(self):
        assert (SKILL_DIR / "reference" / "decisions.md").exists()

    def test_composition_reference_exists(self):
        assert (SKILL_DIR / "reference" / "composition.md").exists()


class TestPlanPhaseContent:
    """Verify PLAN phase file contains required content (moved from SKILL.md)."""

    def test_plan_phase_contains_critique_contract(self):
        """PLAN phase must contain critique-agent reference."""
        content = (SKILL_DIR / "phases" / "PLAN.md").read_text(encoding="utf-8")
        assert "critique-agent" in content, (
            "phases/PLAN.md must reference critique-agent"
        )

    def test_plan_phase_contains_critique_verdicts(self):
        """PLAN phase must describe all three critique verdicts."""
        content = (SKILL_DIR / "phases" / "PLAN.md").read_text(encoding="utf-8")
        assert "revise" in content.lower(), "PLAN phase must describe critique-revise loop"
        assert "PROCEED" in content, "Must describe PROCEED verdict"
        assert "REVISE" in content, "Must describe REVISE verdict"
        assert "BLOCK" in content, "Must describe BLOCK verdict"

    def test_plan_phase_contains_authoring_agent(self):
        """PLAN phase must contain plan-authoring-agent delegation."""
        content = (SKILL_DIR / "phases" / "PLAN.md").read_text(encoding="utf-8")
        assert "plan-authoring-agent" in content, (
            "phases/PLAN.md must reference plan-authoring-agent"
        )
        assert "Task(subagent_type='plan-authoring-agent'" in content, (
            "phases/PLAN.md must contain Task invocation pattern"
        )


class TestSelfContainment:
    """Verify phase files have no cross-phase references (ADR-048 self-containment rule)."""

    CROSS_PHASE_PATTERNS = [
        "see PLAN phase",
        "see DO phase",
        "see CHECK phase",
        "see DONE phase",
        "see CHAIN phase",
    ]

    def _check_phase(self, phase_name: str):
        content = (SKILL_DIR / "phases" / f"{phase_name}.md").read_text(encoding="utf-8")
        for pattern in self.CROSS_PHASE_PATTERNS:
            assert pattern.lower() not in content.lower(), (
                f"phases/{phase_name}.md contains cross-phase reference: '{pattern}'. "
                "Phase files must be self-contained (ADR-048)."
            )

    def test_plan_self_contained(self):
        self._check_phase("PLAN")

    def test_do_self_contained(self):
        self._check_phase("DO")

    def test_check_self_contained(self):
        self._check_phase("CHECK")

    def test_done_self_contained(self):
        self._check_phase("DONE")

    def test_chain_self_contained(self):
        self._check_phase("CHAIN")
