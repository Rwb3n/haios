# generated: 2026-02-13
"""
Tests for retro-cycle ceremony skill (WORK-142).

Validates:
1. Skill exists with valid ceremony contract frontmatter
2. 4 phases present (REFLECT, DERIVE, EXTRACT, COMMIT)
3. Computable predicate for trivial/substantial threshold
4. Evidence anchoring rule documented
5. Escape hatch (skip_retro) documented
6. 3 provenance tags (retro-reflect, retro-kss, retro-extract)
7. /close command invokes retro-cycle
8. close-work-cycle references retro-cycle before VALIDATE
9. observation-capture-cycle is deprecated
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from ceremony_contracts import CeremonyContract
from helpers import load_frontmatter


class TestRetroCycleSkillExists:
    """Verify retro-cycle skill exists with valid ceremony contract."""

    def test_retro_cycle_skill_exists(self):
        """retro-cycle SKILL.md exists at expected path."""
        skill_path = Path(".claude/skills/retro-cycle/SKILL.md")
        assert skill_path.exists(), "retro-cycle/SKILL.md must exist"

    def test_retro_cycle_has_ceremony_contract(self):
        """retro-cycle has name, type: ceremony, input/output contracts."""
        fm = load_frontmatter(".claude/skills/retro-cycle/SKILL.md")
        assert fm["name"] == "retro-cycle"
        assert fm["type"] == "ceremony"
        assert "input_contract" in fm
        assert "output_contract" in fm
        contract = CeremonyContract.from_frontmatter(fm)
        assert len(contract.input_contract) >= 1
        assert len(contract.output_contract) >= 1
        assert len(contract.side_effects) >= 1


class TestRetroCyclePhases:
    """Verify retro-cycle has all 4 phases documented."""

    def test_retro_cycle_has_four_phases(self):
        """retro-cycle documents REFLECT, DERIVE, EXTRACT, COMMIT phases."""
        content = Path(".claude/skills/retro-cycle/SKILL.md").read_text(encoding="utf-8")
        for phase in ["REFLECT", "DERIVE", "EXTRACT", "COMMIT"]:
            assert phase in content, f"Phase {phase} must be documented"

    def test_retro_cycle_has_computable_predicate(self):
        """retro-cycle documents a computable trivial/substantial predicate."""
        content = Path(".claude/skills/retro-cycle/SKILL.md").read_text(encoding="utf-8")
        assert "files_changed" in content, "Predicate must reference files_changed"
        assert "trivial" in content, "Predicate must define trivial threshold"

    def test_retro_cycle_has_evidence_anchoring(self):
        """retro-cycle requires evidence anchoring for REFLECT observations."""
        content = Path(".claude/skills/retro-cycle/SKILL.md").read_text(encoding="utf-8")
        content_lower = content.lower()
        assert "evidence" in content_lower, "Must mention evidence"
        assert "anchor" in content_lower, "Must mention anchoring"

    def test_retro_cycle_has_escape_hatch(self):
        """retro-cycle documents skip_retro escape hatch."""
        content = Path(".claude/skills/retro-cycle/SKILL.md").read_text(encoding="utf-8")
        assert "skip_retro" in content or "skip-retro" in content, \
            "Must document skip_retro escape hatch"

    def test_retro_cycle_has_provenance_tags(self):
        """retro-cycle documents 3 typed provenance tags."""
        content = Path(".claude/skills/retro-cycle/SKILL.md").read_text(encoding="utf-8")
        for tag in ["retro-reflect", "retro-kss", "retro-extract"]:
            assert tag in content, f"Provenance tag {tag} must be documented"


class TestRetroCycleConsumerIntegration:
    """Verify retro-cycle is properly integrated into close pipeline."""

    def test_close_command_invokes_retro_cycle(self):
        """/close command invokes retro-cycle before close-work-cycle."""
        content = Path(".claude/commands/close.md").read_text(encoding="utf-8")
        assert "retro-cycle" in content, "close.md must reference retro-cycle"
        retro_pos = content.find("retro-cycle")
        close_pos = content.find("close-work-cycle")
        assert retro_pos < close_pos, \
            "retro-cycle must be invoked before close-work-cycle"

    def test_close_work_cycle_references_retro_cycle(self):
        """close-work-cycle references retro-cycle before VALIDATE."""
        content = Path(".claude/skills/close-work-cycle/SKILL.md").read_text(encoding="utf-8")
        assert "retro-cycle" in content, "close-work-cycle must reference retro-cycle"
        retro_pos = content.find("retro-cycle")
        validate_pos = content.find("VALIDATE")
        assert retro_pos < validate_pos, \
            "retro-cycle must be referenced before VALIDATE phase"

    def test_observation_capture_cycle_deprecated(self):
        """observation-capture-cycle has deprecated: true in frontmatter."""
        fm = load_frontmatter(".claude/skills/observation-capture-cycle/SKILL.md")
        assert fm.get("deprecated") is True, \
            "observation-capture-cycle must have deprecated: true"
