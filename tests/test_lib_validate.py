# generated: 2025-12-21
# System Auto: last updated on: 2026-01-05T23:15:18
"""Tests for .claude/lib/validate.py - Template validation module.

TDD tests for E2-120 Phase 2c.

Core functions:
1. get_template_registry() - Return template type definitions
2. extract_yaml_header() - Parse YAML frontmatter from content
3. parse_yaml() - Convert YAML text to dict
4. count_references() - Count @ references in content
5. validate_template() - Main validation function
"""

import sys
from pathlib import Path

import pytest

# Add .claude/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


class TestGetTemplateRegistry:
    """Tests for get_template_registry() function."""

    def test_returns_dict(self):
        """Should return a dictionary of template types."""
        from validate import get_template_registry

        registry = get_template_registry()

        assert isinstance(registry, dict)
        assert len(registry) > 0

    def test_contains_core_templates(self):
        """Should contain all core template types."""
        from validate import get_template_registry

        registry = get_template_registry()

        core_types = [
            "checkpoint",
            "implementation_plan",
            "architecture_decision_record",
            "investigation",
            "report",
            "readme",
            "backlog_item",
        ]

        for template_type in core_types:
            assert template_type in registry

    def test_template_has_required_fields(self):
        """Each template should define required_fields."""
        from validate import get_template_registry

        registry = get_template_registry()

        for name, config in registry.items():
            assert "required_fields" in config, f"{name} missing required_fields"
            assert isinstance(config["required_fields"], list)

    def test_template_has_allowed_status(self):
        """Each template should define allowed_status."""
        from validate import get_template_registry

        registry = get_template_registry()

        for name, config in registry.items():
            assert "allowed_status" in config, f"{name} missing allowed_status"
            assert isinstance(config["allowed_status"], list)

    def test_work_item_registry_includes_operator_decisions(self):
        """Work item template should list operator_decisions as optional field.

        E2-272: First gate of ambiguity gating - adds structured field for
        operator decisions that agents can machine-check.
        """
        from validate import get_template_registry

        registry = get_template_registry()
        work_item_config = registry["work_item"]

        assert "operator_decisions" in work_item_config["optional_fields"]


class TestWorkItemTemplate:
    """Tests for work_item.md template structure (E2-272)."""

    def test_work_item_template_has_operator_decisions_field(self):
        """Work item template file should have operator_decisions in frontmatter."""
        template_path = Path(__file__).parent.parent / ".claude" / "templates" / "work_item.md"
        content = template_path.read_text()

        assert "operator_decisions:" in content

    def test_operator_decisions_defaults_to_empty_list(self):
        """New work items should have operator_decisions: [] by default."""
        template_path = Path(__file__).parent.parent / ".claude" / "templates" / "work_item.md"
        content = template_path.read_text()

        # Template should have empty list as default
        assert "operator_decisions: []" in content


class TestImplementationPlanTemplate:
    """Tests for implementation_plan.md template structure (E2-273)."""

    def test_implementation_plan_template_has_open_decisions_section(self):
        """Implementation plan template should have Open Decisions section."""
        template_path = Path(__file__).parent.parent / ".claude" / "templates" / "implementation_plan.md"
        content = template_path.read_text()

        assert "## Open Decisions" in content

    def test_open_decisions_section_has_table(self):
        """Open Decisions section should have Decision/Options/Chosen/Rationale table."""
        template_path = Path(__file__).parent.parent / ".claude" / "templates" / "implementation_plan.md"
        content = template_path.read_text()

        assert "| Decision | Options | Chosen | Rationale |" in content

    def test_open_decisions_section_has_block_comment(self):
        """Open Decisions section should document BLOCK behavior."""
        template_path = Path(__file__).parent.parent / ".claude" / "templates" / "implementation_plan.md"
        content = template_path.read_text()

        assert "plan-validation-cycle will BLOCK" in content


class TestExtractYamlHeader:
    """Tests for extract_yaml_header() function."""

    def test_extracts_yaml_between_dashes(self):
        """Should extract content between --- markers."""
        from validate import extract_yaml_header

        content = """---
template: checkpoint
status: active
---
# Body content
"""
        yaml = extract_yaml_header(content)

        assert yaml is not None
        assert "template: checkpoint" in yaml
        assert "status: active" in yaml

    def test_returns_none_for_missing_yaml(self):
        """Should return None if no YAML header found."""
        from validate import extract_yaml_header

        content = "# No YAML header here"
        yaml = extract_yaml_header(content)

        assert yaml is None

    def test_skips_timestamp_lines(self):
        """Should skip # generated: and # System Auto: lines."""
        from validate import extract_yaml_header

        content = """---
# generated: 2025-12-21
# System Auto: last updated on: 2025-12-21 12:00:00
template: checkpoint
status: active
---
"""
        yaml = extract_yaml_header(content)

        assert yaml is not None
        assert "generated:" not in yaml
        assert "System Auto:" not in yaml
        assert "template: checkpoint" in yaml


class TestParseYaml:
    """Tests for parse_yaml() function."""

    def test_parses_simple_fields(self):
        """Should parse key: value pairs."""
        from validate import parse_yaml

        yaml_text = """template: checkpoint
status: active
date: 2025-12-21"""

        result = parse_yaml(yaml_text)

        assert result["template"] == "checkpoint"
        assert result["status"] == "active"
        assert result["date"] == "2025-12-21"

    def test_handles_quoted_values(self):
        """Should strip quotes from values."""
        from validate import parse_yaml

        yaml_text = '''title: "Session 93: Status Module"
author: 'Hephaestus' '''

        result = parse_yaml(yaml_text)

        assert result["title"] == "Session 93: Status Module"
        assert result["author"] == "Hephaestus"

    def test_handles_empty_values(self):
        """Should handle empty values."""
        from validate import parse_yaml

        yaml_text = """template: checkpoint
title: """

        result = parse_yaml(yaml_text)

        assert result["template"] == "checkpoint"
        assert result["title"] == ""


class TestCountReferences:
    """Tests for count_references() function."""

    def test_counts_at_references(self):
        """Should count @ references in content."""
        from validate import count_references

        content = """
@docs/README.md
@docs/epistemic_state.md
Some text @inline/reference.md here
"""
        count = count_references(content)

        assert count == 3

    def test_returns_zero_for_no_references(self):
        """Should return 0 if no @ references."""
        from validate import count_references

        content = "No references here"
        count = count_references(content)

        assert count == 0


class TestValidateTemplate:
    """Tests for validate_template() main function."""

    def test_valid_checkpoint(self, tmp_path):
        """Should pass validation for valid checkpoint."""
        from validate import validate_template

        content = """---
template: checkpoint
status: active
date: 2025-12-21
version: "1.0"
author: Hephaestus
project_phase: Epoch 2
---
# Checkpoint

@docs/README.md
@docs/epistemic_state.md
"""
        file_path = tmp_path / "test-checkpoint.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        assert result["is_valid"] is True
        assert result["template_type"] == "checkpoint"
        assert len(result["errors"]) == 0

    def test_missing_required_field(self, tmp_path):
        """Should fail if required field is missing."""
        from validate import validate_template

        content = """---
template: checkpoint
status: active
---
# Missing required fields

@ref1
@ref2
"""
        file_path = tmp_path / "test-invalid.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        assert result["is_valid"] is False
        assert any("Missing required" in e for e in result["errors"])

    def test_invalid_status(self, tmp_path):
        """Should fail if status is not in allowed list."""
        from validate import validate_template

        content = """---
template: checkpoint
status: invalid_status
date: 2025-12-21
version: "1.0"
author: Hephaestus
project_phase: Epoch 2
---
# Invalid status

@ref1
@ref2
"""
        file_path = tmp_path / "test-invalid.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        assert result["is_valid"] is False
        assert any("Invalid status" in e for e in result["errors"])

    def test_insufficient_references(self, tmp_path):
        """Should fail if fewer than 2 @ references."""
        from validate import validate_template

        content = """---
template: checkpoint
status: active
date: 2025-12-21
version: "1.0"
author: Hephaestus
project_phase: Epoch 2
---
# Only one reference

@docs/README.md
"""
        file_path = tmp_path / "test-invalid.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        assert result["is_valid"] is False
        assert any("reference" in e.lower() for e in result["errors"])

    def test_unknown_template_type(self, tmp_path):
        """Should fail for unknown template type."""
        from validate import validate_template

        content = """---
template: unknown_type
status: active
---
# Unknown type

@ref1
@ref2
"""
        file_path = tmp_path / "test-invalid.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        assert result["is_valid"] is False
        assert any("Unknown template type" in e for e in result["errors"])

    def test_missing_yaml_header(self, tmp_path):
        """Should fail if no YAML header present."""
        from validate import validate_template

        content = """# No YAML header

Just content here.
"""
        file_path = tmp_path / "test-invalid.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        assert result["is_valid"] is False
        assert any("YAML header" in e for e in result["errors"])

    def test_unknown_fields_generate_warnings(self, tmp_path):
        """Unknown fields should generate warnings, not errors."""
        from validate import validate_template

        content = """---
template: checkpoint
status: active
date: 2025-12-21
version: "1.0"
author: Hephaestus
project_phase: Epoch 2
unknown_field: some_value
---
# With unknown field

@ref1
@ref2
"""
        file_path = tmp_path / "test-warning.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        assert result["is_valid"] is True  # Should still pass
        assert len(result["warnings"]) > 0
        assert any("unknown_field" in w for w in result["warnings"])

    def test_file_not_found(self):
        """Should fail gracefully for non-existent file."""
        from validate import validate_template

        result = validate_template("/nonexistent/file.md")

        assert result["is_valid"] is False
        assert any("not found" in e.lower() for e in result["errors"])


class TestValidateRealFiles:
    """Integration tests with real template files."""

    # E2-126 COMPLETE: Legacy timestamps migrated to YAML frontmatter (Session 94)
    def test_validate_existing_checkpoint(self):
        """Should validate an existing checkpoint file."""
        from validate import validate_template

        # Use the checkpoint we created this session
        checkpoint_path = "docs/checkpoints/2025-12-21-02-SESSION-93-e2-120-phase-2a-status-module-core.md"

        if Path(checkpoint_path).exists():
            result = validate_template(checkpoint_path)
            # May have warnings but should be structurally valid
            assert result["template_type"] == "checkpoint"

    def test_validate_existing_plan(self):
        """Should validate an existing plan file."""
        from validate import validate_template

        plan_path = "docs/plans/PLAN-E2-120-complete-powershell-to-python-migration.md"

        if Path(plan_path).exists():
            result = validate_template(plan_path)
            assert result["template_type"] == "implementation_plan"


class TestSectionSkipValidation:
    """Tests for E2-129: Section skip validation (v1.4 governance)."""

    def test_get_expected_sections_returns_list(self):
        """Should return expected sections for template type."""
        from validate import get_expected_sections

        sections = get_expected_sections("implementation_plan")

        assert isinstance(sections, list)
        assert len(sections) > 0
        assert "Goal" in sections
        assert "Tests First (TDD)" in sections

    def test_get_expected_sections_unknown_template(self):
        """Should return empty list for unknown template."""
        from validate import get_expected_sections

        sections = get_expected_sections("unknown_type")

        assert sections == []

    def test_extract_sections_finds_h2_headings(self):
        """Should extract ## headings from content."""
        from validate import extract_sections

        content = """
## Goal

Some content

## Tests First (TDD)

More content

## Implementation Steps
"""
        sections = extract_sections(content)

        assert "Goal" in sections
        assert "Tests First (TDD)" in sections
        assert "Implementation Steps" in sections

    def test_check_section_coverage_all_present(self, tmp_path):
        """Should pass when all sections are present."""
        from validate import check_section_coverage

        content = """---
template: implementation_plan
status: draft
date: 2025-12-21
directive_id: E2-129
---
# Implementation Plan

## Goal

This section describes the goal in sufficient detail.

## Effort Estimation (Ground Truth)

Effort estimation with real analysis content.

## Current State vs Desired State

Current and desired state comparison content.

## Tests First (TDD)

Test first content with sufficient length.

## Detailed Design

Detailed design documentation goes here.

## Implementation Steps

Implementation steps are documented here.

## Verification

Verification procedures for this plan.

## Risks & Mitigations

Risk analysis and mitigation strategies here.

## Progress Tracker

Progress tracking information goes here.

## Ground Truth Verification (Before Closing)

Ground truth verification content here.

@ref1
@ref2
"""
        result = check_section_coverage("implementation_plan", content)

        assert result["all_covered"] is True
        assert len(result["missing_sections"]) == 0

    def test_check_section_coverage_missing_without_skip(self, tmp_path):
        """Should fail when section is missing without SKIPPED marker."""
        from validate import check_section_coverage

        content = """---
template: implementation_plan
status: draft
date: 2025-12-21
directive_id: E2-129
---
# Implementation Plan

## Goal

Content

## Tests First (TDD)

Content

@ref1
@ref2
"""
        result = check_section_coverage("implementation_plan", content)

        assert result["all_covered"] is False
        assert len(result["missing_sections"]) > 0
        # Should be missing Effort Estimation, Current/Desired State, etc.

    def test_check_section_coverage_skipped_with_rationale(self, tmp_path):
        """Should pass when section has SKIPPED marker with rationale."""
        from validate import check_section_coverage

        content = """---
template: implementation_plan
status: draft
date: 2025-12-21
directive_id: E2-129
---
# Implementation Plan

## Goal

This section describes the goal in detail.

## Effort Estimation (Ground Truth)

**SKIPPED:** Trivial single-line fix, no estimation needed

## Current State vs Desired State

Current and desired state comparison content.

## Tests First (TDD)

Test first content with sufficient length.

## Detailed Design

**SKIPPED:** Pure documentation task, no code design needed

## Implementation Steps

Implementation steps are documented here.

## Verification

Verification procedures for this plan.

## Risks & Mitigations

Risk analysis and mitigation strategies.

## Progress Tracker

Progress tracking information goes here.

## Ground Truth Verification (Before Closing)

Ground truth verification content here.

@ref1
@ref2
"""
        result = check_section_coverage("implementation_plan", content)

        assert result["all_covered"] is True
        assert "Effort Estimation (Ground Truth)" in result["skipped_sections"]
        assert "Detailed Design" in result["skipped_sections"]

    def test_validate_template_includes_section_check(self, tmp_path):
        """validate_template should include section coverage errors."""
        from validate import validate_template

        content = """---
template: implementation_plan
status: draft
date: 2025-12-21
directive_id: E2-129
---
# Implementation Plan

## Goal

Only goal section, missing everything else

@ref1
@ref2
"""
        file_path = tmp_path / "test-plan.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        # Should have section coverage errors
        assert any("section" in e.lower() or "missing" in e.lower() for e in result["errors"])


class TestInvestigationSections:
    """Tests for E2-145: Investigation template section enforcement."""

    def test_investigation_has_expected_sections(self):
        """Investigation template should have expected_sections defined."""
        from validate import get_template_registry

        registry = get_template_registry()
        sections = registry["investigation"]["expected_sections"]

        assert len(sections) > 0
        assert "Findings" in sections
        assert "Hypotheses" in sections
        assert "Spawned Work Items" in sections


class TestPlaceholderDetection:
    """Tests for E2-145: Placeholder content detection."""

    def test_is_placeholder_content_detects_brackets(self):
        """Should detect [placeholder] patterns as placeholder content."""
        from validate import is_placeholder_content

        assert is_placeholder_content("[Document findings here]") is True
        assert is_placeholder_content("[TODO: fill in]") is True
        assert is_placeholder_content("Actual content without brackets that is sufficiently long") is False

    def test_is_placeholder_content_detects_todo(self):
        """Should detect TODO and TBD markers."""
        from validate import is_placeholder_content

        assert is_placeholder_content("TODO: implement this section later") is True
        assert is_placeholder_content("TBD - need more info") is True
        assert is_placeholder_content("This is done and complete") is False

    def test_section_with_only_placeholder_fails(self):
        """Section with only placeholder content should fail validation."""
        from validate import check_section_coverage

        content = """---
template: implementation_plan
status: draft
date: 2025-12-23
backlog_id: E2-TEST
---
# Test Plan

## Goal

[One sentence: What capability will exist?]

## Effort Estimation (Ground Truth)

Actual content here with metrics that is long enough.

## Current State vs Desired State

Proper content describing state.

## Tests First (TDD)

Test content goes here.

## Detailed Design

Design content here.

## Implementation Steps

Steps content.

## Verification

Verify content.

## Risks & Mitigations

Risk content.

## Progress Tracker

Progress content.

## Ground Truth Verification (Before Closing)

Verify content.

@ref1
@ref2
"""
        result = check_section_coverage("implementation_plan", content)

        assert result["all_covered"] is False
        assert "Goal" in result["placeholder_sections"]

    def test_skip_rationale_bypasses_placeholder_check(self):
        """SKIPPED rationale should bypass placeholder check."""
        from validate import check_section_coverage

        content = """---
template: implementation_plan
status: draft
date: 2025-12-23
backlog_id: E2-TEST
---
# Test Plan

## Goal

**SKIPPED:** Trivial fix, no formal goal needed

## Effort Estimation (Ground Truth)

Content.

## Current State vs Desired State

Content.

## Tests First (TDD)

Content.

## Detailed Design

Content.

## Implementation Steps

Content.

## Verification

Content.

## Risks & Mitigations

Content.

## Progress Tracker

Content.

## Ground Truth Verification (Before Closing)

Content.

@ref1
@ref2
"""
        result = check_section_coverage("implementation_plan", content)

        assert "Goal" in result["skipped_sections"]
        assert "Goal" not in result.get("placeholder_sections", [])

    def test_error_message_includes_placeholder_sections(self, tmp_path):
        """E2-146: Error message should include placeholder_sections when validation fails."""
        from validate import validate_template

        content = """---
template: implementation_plan
status: draft
date: 2025-12-23
backlog_id: E2-TEST
---
# Test Plan

## Goal

[One sentence placeholder]

## Effort Estimation (Ground Truth)

Real content here that is sufficiently long.

## Current State vs Desired State

Real content here that is sufficiently long.

## Tests First (TDD)

Real content here that is sufficiently long.

## Detailed Design

Real content here that is sufficiently long.

## Implementation Steps

Real content here that is sufficiently long.

## Verification

Real content here that is sufficiently long.

## Risks & Mitigations

Real content here that is sufficiently long.

## Progress Tracker

Real content here that is sufficiently long.

## Ground Truth Verification (Before Closing)

Real content here that is sufficiently long.

@ref1
@ref2
"""
        file_path = tmp_path / "test-plan.md"
        file_path.write_text(content)

        result = validate_template(str(file_path))

        assert result["is_valid"] is False
        # Error should mention placeholder sections, not just "Missing sections: ."
        error_text = " ".join(result["errors"])
        assert "Goal" in error_text
        assert "laceholder" in error_text.lower()  # "Placeholder" appears


class TestPlanAuthoringCycleSkill:
    """Tests for plan-authoring-cycle skill structure (E2-274: Gate 3).

    Gate 3 of the Ambiguity Gating defense-in-depth strategy (INV-058).
    Verifies the skill has AMBIGUITY phase that:
    - Reads work item before proceeding
    - Checks operator_decisions field
    - Blocks with AskUserQuestion on unresolved decisions
    """

    def test_skill_has_ambiguity_phase(self):
        """SKILL.md should contain AMBIGUITY phase section."""
        skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-authoring-cycle" / "SKILL.md"
        content = skill_path.read_text()

        # Phase section exists (numbered 0 or just named AMBIGUITY)
        assert "AMBIGUITY Phase" in content, "Missing AMBIGUITY phase section"
        # Phase is in cycle diagram
        assert "AMBIGUITY" in content.upper(), "AMBIGUITY not in cycle diagram"

    def test_ambiguity_phase_reads_work_item(self):
        """AMBIGUITY phase instructions must read WORK.md before proceeding."""
        skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-authoring-cycle" / "SKILL.md"
        content = skill_path.read_text()

        # Must mention reading work item
        assert "WORK.md" in content, "Must instruct to read WORK.md"
        # Must mention operator_decisions field
        assert "operator_decisions" in content, "Must reference operator_decisions field"

    def test_ambiguity_phase_blocks_on_unresolved(self):
        """AMBIGUITY phase must BLOCK when unresolved decisions exist."""
        skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-authoring-cycle" / "SKILL.md"
        content = skill_path.read_text()

        # Must mention blocking behavior (case insensitive)
        assert "BLOCK" in content, "Must use BLOCK keyword for gating behavior"
        # Must mention AskUserQuestion for surfacing decisions
        assert "AskUserQuestion" in content, "Must reference AskUserQuestion for operator decisions"


class TestPlanValidationCycleSkill:
    """Tests for plan-validation-cycle skill structure (E2-275: Gate 4).

    Gate 4 of the Ambiguity Gating defense-in-depth strategy (INV-058).
    Verifies the skill checks for unresolved Open Decisions in plans.
    """

    def test_skill_has_decision_check(self):
        """SKILL.md should mention checking Open Decisions section."""
        skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-validation-cycle" / "SKILL.md"
        content = skill_path.read_text()

        # Must mention Open Decisions check
        assert "Open Decisions" in content, "Must check Open Decisions section"
        # Must mention BLOCKED detection
        assert "BLOCKED" in content, "Must detect [BLOCKED] entries"

    def test_decision_check_is_gate_4(self):
        """Decision check should be labeled as Gate 4 of INV-058."""
        skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-validation-cycle" / "SKILL.md"
        content = skill_path.read_text()

        # Should reference Gate 4
        assert "Gate 4" in content, "Must be labeled as Gate 4"
