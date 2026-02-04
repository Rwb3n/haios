# generated: 2026-02-04
# System Auto: last updated on: 2026-02-04T23:01:33
# Tests for design lifecycle phase templates (WORK-089)
"""
TDD tests for design lifecycle templates.
Verifies: directory exists, files exist, contracts in frontmatter, size constraint.
"""

from pathlib import Path

import yaml


class TestDesignTemplates:
    """Tests for .claude/templates/design/ phase templates."""

    design_dir = Path(".claude/templates/design")
    phases = ["EXPLORE", "SPECIFY", "CRITIQUE", "COMPLETE"]

    def test_design_templates_directory_exists(self):
        """templates/design/ directory must exist."""
        assert self.design_dir.is_dir(), "templates/design/ directory does not exist"

    def test_design_phase_templates_exist(self):
        """All four design phase templates must exist."""
        for phase in self.phases:
            template = self.design_dir / f"{phase}.md"
            assert template.exists(), f"{phase}.md does not exist"

    def test_design_templates_have_contracts(self):
        """Each template must have input_contract and output_contract in frontmatter."""
        for phase in self.phases:
            template_path = self.design_dir / f"{phase}.md"
            content = template_path.read_text(encoding="utf-8")

            # Parse YAML frontmatter (between first two ---)
            parts = content.split("---")
            assert len(parts) >= 3, f"{phase}.md missing YAML frontmatter"

            frontmatter = yaml.safe_load(parts[1])
            assert frontmatter is not None, f"{phase}.md has empty frontmatter"

            assert "input_contract" in frontmatter, f"{phase}.md missing input_contract"
            assert "output_contract" in frontmatter, f"{phase}.md missing output_contract"
            assert frontmatter.get("phase") == phase, f"{phase}.md has wrong phase field"

    def test_design_templates_size_constraint(self):
        """Each template must be <=100 lines per REQ-TEMPLATE-002."""
        for phase in self.phases:
            template_path = self.design_dir / f"{phase}.md"
            content = template_path.read_text(encoding="utf-8")
            lines = len(content.splitlines())
            assert lines <= 100, f"{phase}.md has {lines} lines, exceeds 100"
