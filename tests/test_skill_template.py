"""
Tests for skill template structure (E2-285)

Verifies:
- Template file exists
- Required sections present
- Single-phase default structure
- S20 principle alignment
"""
from pathlib import Path


def test_skill_template_exists():
    """Verify skill template file can be read"""
    template_path = Path(".claude/templates/skill.md")
    assert template_path.exists(), "skill.md template must exist"
    assert template_path.is_file(), "skill.md must be a file"


def test_template_has_required_sections():
    """Verify template contains all required sections per E2-285"""
    template = Path(".claude/templates/skill.md").read_text()

    # MUST have single-phase default structure
    assert "## When to Use" in template, "Missing: When to Use section"
    assert "## Instructions" in template or "## Logic" in template, "Missing: Instructions/Logic section"
    assert "## Output" in template or "## Gate" in template, "Missing: Output/Gate section"

    # MUST have multi-phase justification section
    assert "Multi-Phase" in template or "multi-phase" in template, "Missing: Multi-phase justification section"
    assert "When Multi-Phase is Justified" in template, "Missing: explicit multi-phase rationale section"

    # MUST have principle alignment section
    assert "Principle Alignment" in template, "Missing: Principle Alignment section"
    assert "S20" in template or "pressure dynamics" in template, "Missing: S20 reference"

    # MUST NOT have default exit criteria checklists
    assert "Exit Criteria:" not in template, "Template should not have default Exit Criteria checklists"


def test_template_discourages_multi_phase():
    """Verify template structure nudges toward single-phase"""
    template = Path(".claude/templates/skill.md").read_text()

    # Should NOT have "## The Cycle" as primary section
    lines = template.split('\n')
    cycle_section_line = next((i for i, line in enumerate(lines) if "## The Cycle" in line), None)

    # If "The Cycle" exists, it should be in the multi-phase justification section
    # with warning text, not as the primary structure
    if cycle_section_line:
        # Check surrounding context for justification/warning
        context = '\n'.join(lines[max(0, cycle_section_line-5):cycle_section_line+10])
        assert any(word in context.lower() for word in ["justification", "rationale", "only if", "must"]), \
            "If The Cycle section exists, it must be accompanied by justification requirement"


def test_template_aligns_with_s20_principle():
    """Verify template enforces 'each skill does ONE thing'"""
    template = Path(".claude/templates/skill.md").read_text()

    # Should reference S20 or the principle
    assert any(phrase in template for phrase in [
        "each skill does ONE thing",
        "smaller containers",
        "UNIX philosophy",
        "single responsibility"
    ]), "Template must reference S20 'each skill does ONE thing' principle"
