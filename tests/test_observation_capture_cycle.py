# generated: 2026-01-08
# System Auto: last updated on: 2026-01-10T16:30:17
"""
Tests for observation-capture-cycle skill (E2-284 simplification).

Validates:
1. Skill has 3 questions (not 3 phases) - S20 compliance
2. Skill is minimal (<50 lines) - "smaller containers"
3. Skill has hard gate for non-empty responses
4. /close command still invokes observation-capture-cycle (backward compat)
"""
from pathlib import Path

import pytest


def test_skill_has_three_questions():
    """Verify skill defines 3 questions, not 3 phases (E2-284)."""
    skill_path = Path(".claude/skills/observation-capture-cycle/SKILL.md")
    assert skill_path.exists(), "Skill file must exist"

    content = skill_path.read_text(encoding="utf-8")

    # Should have questions section
    assert "## Questions" in content or "1. **What surprised" in content, \
        "Must have Questions section or numbered questions"

    # Should NOT have phase headers (old structure)
    assert "### 1. RECALL Phase" not in content, "RECALL Phase should be removed"
    assert "### 2. NOTICE Phase" not in content, "NOTICE Phase should be removed"
    assert "### 3. COMMIT Phase" not in content, "COMMIT Phase should be removed"


def test_skill_is_minimal():
    """Verify skill follows S20 'smaller containers' principle (<50 lines)."""
    skill_path = Path(".claude/skills/observation-capture-cycle/SKILL.md")
    content = skill_path.read_text(encoding="utf-8")
    line_count = len(content.split('\n'))

    assert line_count < 50, f"Skill should be <50 lines per S20, got {line_count}"


def test_gate_requires_content():
    """Verify skill has hard gate for non-empty responses."""
    skill_path = Path(".claude/skills/observation-capture-cycle/SKILL.md")
    content = skill_path.read_text(encoding="utf-8")

    # Should mention gate/block for empty
    content_lower = content.lower()
    assert "gate" in content_lower or "block" in content_lower, \
        "Must mention gate or block"
    assert "none observed" in content_lower or "explicit" in content_lower, \
        "Must mention 'none observed' or explicit acknowledgment"


def test_close_command_invokes_skill():
    """Verify /close command still invokes observation-capture-cycle (backward compat)."""
    close_path = Path(".claude/commands/close.md")
    content = close_path.read_text(encoding="utf-8")

    assert "observation-capture-cycle" in content, \
        "observation-capture-cycle must be mentioned in close command"

    # Should still come before close-work-cycle
    obs_pos = content.find("observation-capture-cycle")
    close_pos = content.find("close-work-cycle")
    assert obs_pos < close_pos, \
        "observation-capture-cycle must be invoked before close-work-cycle"


def test_close_work_cycle_references_skill():
    """Verify close-work-cycle still references observation-capture-cycle."""
    skill_path = Path(".claude/skills/close-work-cycle/SKILL.md")
    content = skill_path.read_text(encoding="utf-8")

    # Should reference observation-capture-cycle as entry gate
    assert "observation-capture-cycle" in content, \
        "close-work-cycle must reference observation-capture-cycle"
