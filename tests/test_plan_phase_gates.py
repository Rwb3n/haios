# generated: 2026-03-07
"""
Tests for tier-aware gate skipping in PLAN phase skill (WORK-250).

Verifies that .claude/skills/implementation-cycle/phases/PLAN.md contains
tier-conditional gate instructions per REQ-LIFECYCLE-005 / REQ-CEREMONY-005.

These are skill TEXT verification tests — not logic unit tests.
The underlying tier detection logic is tested in test_tier_detector.py.

Pattern: read file as text, assert structural content per tier section.
"""
from pathlib import Path

import pytest

# Path to the PLAN.md skill file under test
PLAN_MD_PATH = (
    Path(__file__).parent.parent
    / ".claude"
    / "skills"
    / "implementation-cycle"
    / "phases"
    / "PLAN.md"
)


@pytest.fixture(scope="module")
def plan_md_text():
    """Read PLAN.md skill file once for all tests in this module."""
    return PLAN_MD_PATH.read_text(encoding="utf-8")


def _section_after(text: str, heading: str) -> str:
    """Extract text after a heading until the next 'If tier' heading."""
    idx = text.find(heading)
    if idx == -1:
        return ""
    after = text[idx + len(heading):]
    # Find the next section boundary (next "**If tier" heading)
    next_section = after.find("\n**If tier")
    if next_section != -1:
        return after[:next_section]
    return after


class TestTierGateMatrix:
    """Test 1: PLAN.md contains the tier gate matrix."""

    def test_plan_md_contains_tier_gate_matrix(self, plan_md_text):
        """Exit Gate section must include tier determination table."""
        assert "Tier-Aware" in plan_md_text, (
            "Exit Gate section must be labeled Tier-Aware"
        )
        assert "Step 1: Determine Tier" in plan_md_text, (
            "Must have Step 1: Determine Tier"
        )
        assert "Step 2: Apply Gate Set" in plan_md_text, (
            "Must have Step 2: Apply Gate Set"
        )
        # All four tiers must appear in the gate section
        gate_section_start = plan_md_text.find("Exit Gate (Tier-Aware")
        assert gate_section_start != -1, "Exit Gate (Tier-Aware) section not found"
        gate_section = plan_md_text[gate_section_start:]
        for tier in ("trivial", "small", "standard", "architectural"):
            assert tier in gate_section, f"Tier '{tier}' not found in gate section"


class TestTrivialTierGateSkip:
    """Test 2: Trivial tier skips all three gates."""

    def test_plan_md_trivial_all_gates_skipped(self, plan_md_text):
        """After 'If tier = trivial', all gates must be marked SKIPPED."""
        trivial_section = _section_after(plan_md_text, "If tier = trivial")
        assert trivial_section != "", "Trivial tier section not found"
        assert "SKIPPED" in trivial_section or "SKIP" in trivial_section, (
            "Trivial section must indicate gates are skipped"
        )
        # Must NOT invoke any subagent Task() for gates
        assert "Task(subagent_type='critique-agent'" not in trivial_section, (
            "Trivial tier must not invoke critique-agent subagent"
        )
        assert "Task(subagent_type='preflight-checker'" not in trivial_section, (
            "Trivial tier must not invoke preflight-checker subagent"
        )


class TestSmallTierInlineChecklist:
    """Test 3: Small tier has only inline checklist, no subagents."""

    def test_plan_md_small_tier_inline_checklist_only(self, plan_md_text):
        """After 'If tier = small', Gate 1 is inline checklist, Gates 2+3 skipped."""
        small_section = _section_after(plan_md_text, "If tier = small")
        assert small_section != "", "Small tier section not found"
        # Must have inline checklist items
        assert "acceptance criteria" in small_section.lower(), (
            "Small tier must include inline checklist with acceptance criteria check"
        )
        # Must NOT invoke critique-agent or preflight-checker subagents
        assert "Task(subagent_type='critique-agent'" not in small_section, (
            "Small tier must not invoke critique-agent as subagent"
        )
        assert "Task(subagent_type='preflight-checker'" not in small_section, (
            "Small tier must not invoke preflight-checker subagent"
        )
        # Gate 2 and 3 must be skipped
        assert "Gate 2" in small_section and "SKIP" in small_section, (
            "Small tier must explicitly skip Gate 2"
        )


class TestStandardTierThreeGates:
    """Test 4: Standard tier has all three gates."""

    def test_plan_md_standard_tier_has_three_gates(self, plan_md_text):
        """After 'If tier = standard', Gates 1, 2, and 3 must all be present."""
        standard_section = _section_after(plan_md_text, "If tier = standard")
        assert standard_section != "", "Standard tier section not found"
        assert "Gate 1" in standard_section, "Standard tier must have Gate 1 (Critique)"
        assert "Gate 2" in standard_section, "Standard tier must have Gate 2 (Plan-Validation)"
        assert "Gate 3" in standard_section, "Standard tier must have Gate 3 (Preflight)"
        assert "Task(subagent_type='critique-agent'" in standard_section, (
            "Standard tier must invoke critique-agent subagent"
        )
        assert "Task(subagent_type='preflight-checker'" in standard_section, (
            "Standard tier must invoke preflight-checker subagent for validation and preflight"
        )


class TestArchitecturalTierGate4:
    """Test 5: Architectural tier has Gate 4 operator approval."""

    def test_plan_md_architectural_tier_has_operator_approval(self, plan_md_text):
        """After 'If tier = architectural', Gate 4 with AskUserQuestion must be present."""
        arch_section = _section_after(plan_md_text, "If tier = architectural")
        assert arch_section != "", "Architectural tier section not found"
        assert "Gate 4" in arch_section, "Architectural tier must have Gate 4"
        assert "AskUserQuestion" in arch_section, (
            "Architectural tier must invoke AskUserQuestion for operator approval"
        )
        assert "Operator Approval" in arch_section or "operator" in arch_section.lower(), (
            "Architectural tier Gate 4 must require operator approval"
        )
