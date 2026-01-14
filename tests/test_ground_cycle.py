# generated: 2026-01-06
# System Auto: last updated on: 2026-01-06T21:01:13
"""
Tests for ground-cycle skill.

E2-276: Design ground-cycle Skill
Tests written first per TDD requirements.
"""
from pathlib import Path


def test_ground_cycle_skill_has_required_sections():
    """Verify skill file has frontmatter and all 4 phases."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # Check frontmatter
    assert content.startswith("---")
    assert "name: ground-cycle" in content

    # Check phases exist
    assert "## 1. PROVENANCE Phase" in content or "### 1. PROVENANCE Phase" in content
    assert "ARCHITECTURE Phase" in content
    assert "MEMORY Phase" in content
    assert "CONTEXT MAP Phase" in content


def test_provenance_phase_documented():
    """Verify PROVENANCE phase specifies traversing spawned_by chain."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # PROVENANCE should mention spawned_by traversal
    assert "spawned_by" in content.lower() or "provenance" in content.lower()
    assert "Read work item" in content or "WORK.md" in content


def test_architecture_phase_loads_epoch():
    """Verify ARCHITECTURE phase specifies loading epoch architecture."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should reference epoch loading
    assert "epoch" in content.lower()
    assert "EPOCH.md" in content or "architecture" in content.lower()


def test_grounded_context_output_defined():
    """Verify the skill defines GroundedContext output structure."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should define output structure
    assert "GroundedContext" in content or "Output:" in content
    assert "provenance_chain" in content or "epoch" in content


def test_integration_points_documented():
    """Verify skill documents how other cycles call it."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should mention calling cycles
    assert "plan-authoring" in content or "investigation-cycle" in content or "implementation-cycle" in content
