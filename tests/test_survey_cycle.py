# generated: 2026-01-08
# System Auto: last updated on: 2026-01-08T21:56:45
"""
Tests for survey-cycle skill (E2-280).

Verifies:
1. SKILL.md has required 5 phases (GATHER, ASSESS, OPTIONS, CHOOSE, ROUTE)
2. Pressure annotations present per S20 ([volumous], [tight])
3. Skill registered in haios manifest for discovery
"""

from pathlib import Path

import pytest


class TestSurveyCycleSkill:
    """Test suite for survey-cycle skill structure."""

    def test_survey_cycle_has_five_phases(self):
        """Verify SURVEY skill has GATHER, ASSESS, OPTIONS, CHOOSE, ROUTE phases."""
        skill_path = Path(".claude/skills/survey-cycle/SKILL.md")
        assert skill_path.exists(), "SKILL.md must exist"
        content = skill_path.read_text()
        assert "GATHER" in content, "Must have GATHER phase"
        assert "ASSESS" in content, "Must have ASSESS phase"
        assert "OPTIONS" in content, "Must have OPTIONS phase"
        assert "CHOOSE" in content, "Must have CHOOSE phase"
        assert "ROUTE" in content, "Must have ROUTE phase"

    def test_survey_cycle_has_pressure_annotations(self):
        """Verify SURVEY skill has [volumous] and [tight] pressure annotations per S20."""
        skill_path = Path(".claude/skills/survey-cycle/SKILL.md")
        assert skill_path.exists(), "SKILL.md must exist"
        content = skill_path.read_text()
        # GATHER, ASSESS, OPTIONS should be volumous
        assert "[volumous]" in content, "Must have volumous phases"
        # CHOOSE, ROUTE should be tight
        assert "[tight]" in content, "Must have tight phases"

    def test_survey_cycle_in_manifest(self):
        """Verify survey-cycle appears in haios manifest for discovery."""
        manifest_path = Path(".claude/haios/manifest.yaml")
        assert manifest_path.exists(), "manifest.yaml must exist"
        content = manifest_path.read_text()
        assert "survey-cycle" in content, "Must be registered in manifest"
