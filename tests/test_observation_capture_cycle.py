# generated: 2026-01-08
# System Auto: last updated on: 2026-02-15T22:30:00
"""
Tests for observation-capture-cycle migration to retro-cycle (WORK-142).

WORK-145: observation-capture-cycle skill deleted (deprecated).
Remaining tests verify close/retro integration.
"""
from pathlib import Path


def test_close_command_invokes_retro_cycle():
    """Verify /close command invokes retro-cycle (WORK-142 migration)."""
    close_path = Path(".claude/commands/close.md")
    content = close_path.read_text(encoding="utf-8")

    assert "retro-cycle" in content, \
        "retro-cycle must be mentioned in close command"

    # Should still come before close-work-cycle
    retro_pos = content.find("retro-cycle")
    close_pos = content.find("close-work-cycle")
    assert retro_pos < close_pos, \
        "retro-cycle must be invoked before close-work-cycle"


def test_close_work_cycle_references_retro_cycle():
    """Verify close-work-cycle references retro-cycle (WORK-142 migration)."""
    skill_path = Path(".claude/skills/close-work-cycle/SKILL.md")
    content = skill_path.read_text(encoding="utf-8")

    # Should reference retro-cycle as predecessor
    assert "retro-cycle" in content, \
        "close-work-cycle must reference retro-cycle"
