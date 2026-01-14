# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T12:44:44
"""Tests for E2-233: Checkpoint Anti-Pattern Verification Integration.

Validates that checkpoint-cycle skill has VERIFY phase between FILL and CAPTURE.
"""

import re
from pathlib import Path

import pytest


def extract_section(content: str, section_name: str) -> str:
    """Extract content of a markdown section by name."""
    # Try ### first (subsections), then ## (main sections)
    # Handles "### VERIFY Phase", "### 3. VERIFY Phase", "## Composition Map"
    for level in (r"###", r"##"):
        pattern = rf"{level}\s+(?:\d+\.\s+)?{re.escape(section_name)}.*?\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


class TestVerifyPhaseDocumented:
    """Test that VERIFY phase exists in checkpoint-cycle skill documentation."""

    @pytest.fixture
    def skill_content(self) -> str:
        """Load checkpoint-cycle skill content."""
        skill_path = Path(".claude/skills/checkpoint-cycle/SKILL.md")
        assert skill_path.exists(), f"Skill file not found: {skill_path}"
        return skill_path.read_text(encoding="utf-8")

    def test_verify_phase_section_exists(self, skill_content: str):
        """VERIFY phase section exists in skill documentation."""
        # Check for VERIFY phase header (numbered or unnumbered)
        has_verify_section = (
            "### 3. VERIFY Phase" in skill_content
            or "### VERIFY Phase" in skill_content
        )
        assert has_verify_section, "VERIFY phase section not found in skill documentation"

    def test_verify_in_cycle_diagram(self, skill_content: str):
        """Diagram shows VERIFY between FILL and CAPTURE."""
        assert "FILL --> VERIFY --> CAPTURE" in skill_content, (
            "Cycle diagram should show VERIFY between FILL and CAPTURE"
        )


class TestVerifyPhaseInvokesAgent:
    """Test that VERIFY phase specifies anti-pattern-checker invocation."""

    @pytest.fixture
    def skill_content(self) -> str:
        """Load checkpoint-cycle skill content."""
        skill_path = Path(".claude/skills/checkpoint-cycle/SKILL.md")
        return skill_path.read_text(encoding="utf-8")

    def test_references_anti_pattern_checker(self, skill_content: str):
        """VERIFY phase references anti-pattern-checker agent."""
        verify_section = extract_section(skill_content, "VERIFY Phase")
        assert verify_section, "Could not extract VERIFY Phase section"
        assert "anti-pattern-checker" in verify_section, (
            "VERIFY phase should reference anti-pattern-checker agent"
        )

    def test_shows_task_invocation(self, skill_content: str):
        """VERIFY phase shows Task invocation pattern."""
        verify_section = extract_section(skill_content, "VERIFY Phase")
        assert "Task(subagent_type='anti-pattern-checker'" in verify_section, (
            "VERIFY phase should show Task invocation pattern for anti-pattern-checker"
        )


class TestCompositionMapUpdated:
    """Test that Composition Map includes VERIFY phase."""

    @pytest.fixture
    def skill_content(self) -> str:
        """Load checkpoint-cycle skill content."""
        skill_path = Path(".claude/skills/checkpoint-cycle/SKILL.md")
        return skill_path.read_text(encoding="utf-8")

    def test_verify_in_composition_map(self, skill_content: str):
        """Composition Map table includes VERIFY phase row."""
        comp_section = extract_section(skill_content, "Composition Map")
        assert comp_section, "Could not extract Composition Map section"
        assert "VERIFY" in comp_section, "Composition Map should include VERIFY phase"

    def test_composition_map_shows_task_tool(self, skill_content: str):
        """Composition Map shows Task tool for VERIFY phase."""
        comp_section = extract_section(skill_content, "Composition Map")
        # Should have Task in the VERIFY row
        assert "Task" in comp_section, "Composition Map should show Task tool"
