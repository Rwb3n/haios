# generated: 2026-02-05
# System Auto: last updated on: 2026-02-05T20:25:33
# Tests for WORK-091: Fracture Validation Lifecycle Templates
# Tests for WORK-092: Fracture Triage Lifecycle Templates (added later)

from pathlib import Path

import pytest

from helpers import load_frontmatter


# =============================================================================
# WORK-091: Validation Templates
# =============================================================================

VALIDATION_DIR = Path(".claude/templates/validation")
VALIDATION_PHASES = ["VERIFY", "JUDGE", "REPORT"]


class TestValidationTemplatesExist:
    """Validation lifecycle templates must exist with correct structure."""

    def test_validation_templates_directory_exists(self):
        """templates/validation/ directory must exist."""
        assert VALIDATION_DIR.is_dir(), "templates/validation/ directory does not exist"

    @pytest.mark.parametrize("phase", VALIDATION_PHASES)
    def test_validation_phase_template_exists(self, phase):
        """Each validation phase template must exist."""
        template = VALIDATION_DIR / f"{phase}.md"
        assert template.exists(), f"{phase}.md does not exist"

    def test_validation_readme_exists(self):
        """README.md must exist in validation directory."""
        readme = VALIDATION_DIR / "README.md"
        assert readme.exists(), "README.md does not exist in validation/"


class TestValidationTemplateContracts:
    """Validation templates must have machine-readable contracts in frontmatter."""

    @pytest.mark.parametrize("phase", VALIDATION_PHASES)
    def test_validation_template_has_contracts(self, phase):
        """Each template must have input_contract and output_contract."""
        frontmatter = load_frontmatter(VALIDATION_DIR / f"{phase}.md")
        assert "input_contract" in frontmatter, f"{phase}.md missing input_contract"
        assert "output_contract" in frontmatter, f"{phase}.md missing output_contract"

    @pytest.mark.parametrize("phase", VALIDATION_PHASES)
    def test_validation_template_phase_field(self, phase):
        """Each template must have correct phase field."""
        frontmatter = load_frontmatter(VALIDATION_DIR / f"{phase}.md")
        assert frontmatter["phase"] == phase, f"Expected phase={phase}, got {frontmatter['phase']}"

    @pytest.mark.parametrize("phase", VALIDATION_PHASES)
    def test_validation_template_type_field(self, phase):
        """Each template must have template: validation_phase."""
        frontmatter = load_frontmatter(VALIDATION_DIR / f"{phase}.md")
        assert frontmatter["template"] == "validation_phase"


class TestValidationTemplateSizeConstraint:
    """Templates must be ≤100 lines per REQ-TEMPLATE-002."""

    @pytest.mark.parametrize("phase", VALIDATION_PHASES)
    def test_validation_template_under_100_lines(self, phase):
        """Each template must be ≤100 lines."""
        lines = len((VALIDATION_DIR / f"{phase}.md").read_text().splitlines())
        assert lines <= 100, f"{phase}.md has {lines} lines, exceeds 100"


# =============================================================================
# WORK-092: Triage Templates (placeholder - tests added when implementing)
# =============================================================================

TRIAGE_DIR = Path(".claude/templates/triage")
TRIAGE_PHASES = ["SCAN", "ASSESS", "RANK", "COMMIT"]


class TestTriageTemplatesExist:
    """Triage lifecycle templates must exist with correct structure."""

    def test_triage_templates_directory_exists(self):
        """templates/triage/ directory must exist."""
        assert TRIAGE_DIR.is_dir(), "templates/triage/ directory does not exist"

    @pytest.mark.parametrize("phase", TRIAGE_PHASES)
    def test_triage_phase_template_exists(self, phase):
        """Each triage phase template must exist."""
        template = TRIAGE_DIR / f"{phase}.md"
        assert template.exists(), f"{phase}.md does not exist"

    def test_triage_readme_exists(self):
        """README.md must exist in triage directory."""
        readme = TRIAGE_DIR / "README.md"
        assert readme.exists(), "README.md does not exist in triage/"


class TestTriageTemplateContracts:
    """Triage templates must have machine-readable contracts in frontmatter."""

    @pytest.mark.parametrize("phase", TRIAGE_PHASES)
    def test_triage_template_has_contracts(self, phase):
        """Each template must have input_contract and output_contract."""
        frontmatter = load_frontmatter(TRIAGE_DIR / f"{phase}.md")
        assert "input_contract" in frontmatter, f"{phase}.md missing input_contract"
        assert "output_contract" in frontmatter, f"{phase}.md missing output_contract"

    @pytest.mark.parametrize("phase", TRIAGE_PHASES)
    def test_triage_template_phase_field(self, phase):
        """Each template must have correct phase field."""
        frontmatter = load_frontmatter(TRIAGE_DIR / f"{phase}.md")
        assert frontmatter["phase"] == phase

    @pytest.mark.parametrize("phase", TRIAGE_PHASES)
    def test_triage_template_type_field(self, phase):
        """Each template must have template: triage_phase."""
        frontmatter = load_frontmatter(TRIAGE_DIR / f"{phase}.md")
        assert frontmatter["template"] == "triage_phase"


class TestTriageTemplateSizeConstraint:
    """Templates must be ≤100 lines per REQ-TEMPLATE-002."""

    @pytest.mark.parametrize("phase", TRIAGE_PHASES)
    def test_triage_template_under_100_lines(self, phase):
        """Each template must be ≤100 lines."""
        lines = len((TRIAGE_DIR / f"{phase}.md").read_text().splitlines())
        assert lines <= 100, f"{phase}.md has {lines} lines, exceeds 100"
