# generated: 2025-12-21
# System Auto: last updated on: 2026-01-27T20:58:31
"""Tests for .claude/haios/lib/scaffold.py - Template scaffolding module.

TDD tests for E2-120 Phase 2b.

Core functions:
1. generate_output_path() - Auto-generate path from template/backlog_id/title
2. load_template() - Read template file
3. substitute_variables() - Replace {{VAR}} placeholders
4. get_next_sequence_number() - Handle {{NN}} for same-day files
5. get_prev_session() - Read last session from haios-status.json
6. scaffold_template() - Main orchestrator
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest
import yaml

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestGenerateOutputPath:
    """Tests for generate_output_path() function."""

    def test_investigation_path(self, tmp_path):
        """Should generate correct path for investigation template (E2-212: inside work dir)."""
        import scaffold
        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Create work directory so E2-212 routing kicks in
        (tmp_path / "docs" / "work" / "active" / "INV-017").mkdir(parents=True)

        try:
            from scaffold import generate_output_path
            path = generate_output_path(
                template="investigation",
                backlog_id="INV-017",
                title="Observability Gap"
            )
            assert path == "docs/work/active/INV-017/investigations/001-observability-gap.md"
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_implementation_plan_path(self, tmp_path):
        """Should generate correct path for implementation_plan template (E2-212: inside work dir)."""
        import scaffold
        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Create work directory so E2-212 routing kicks in
        (tmp_path / "docs" / "work" / "active" / "E2-212").mkdir(parents=True)

        try:
            from scaffold import generate_output_path
            path = generate_output_path(
                template="implementation_plan",
                backlog_id="E2-212",
                title="Work Directory Migration"
            )
            assert path == "docs/work/active/E2-212/plans/PLAN.md"
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_checkpoint_path_has_date_and_session(self):
        """Checkpoint path should include date and session placeholder."""
        from scaffold import generate_output_path

        path = generate_output_path(
            template="checkpoint",
            backlog_id="93",
            title="Status Module"
        )

        today = datetime.now().strftime("%Y-%m-%d")
        assert path.startswith(f"docs/checkpoints/{today}-")
        assert "SESSION-93" in path
        assert "status-module" in path

    def test_adr_path(self):
        """Should generate correct path for ADR template."""
        from scaffold import generate_output_path

        path = generate_output_path(
            template="architecture_decision_record",
            backlog_id="038",
            title="Memory Schema"
        )

        assert path == "docs/ADR/ADR-038-memory-schema.md"

    def test_report_path_no_backlog_id(self):
        """Report should work without backlog_id."""
        from scaffold import generate_output_path

        path = generate_output_path(
            template="report",
            title="Session Summary"
        )

        today = datetime.now().strftime("%Y-%m-%d")
        assert path == f"docs/reports/{today}-REPORT-session-summary.md"

    def test_slug_removes_special_chars(self):
        """Slug should remove special characters."""
        from scaffold import generate_output_path

        path = generate_output_path(
            template="investigation",
            backlog_id="INV-001",
            title="What's the Bug? (Fix #123)"
        )

        assert "whats-the-bug-fix-123" in path

    def test_slug_collapses_multiple_hyphens(self):
        """Slug should collapse multiple hyphens."""
        from scaffold import generate_output_path

        path = generate_output_path(
            template="investigation",
            backlog_id="INV-001",
            title="One -- Two --- Three"
        )

        assert "--" not in path


class TestLoadTemplate:
    """Tests for load_template() function."""

    def test_loads_existing_template(self):
        """Should load template content from file."""
        from scaffold import load_template

        content = load_template("checkpoint")

        assert content is not None
        assert "{{SESSION}}" in content or "{{TITLE}}" in content

    def test_raises_on_missing_template(self):
        """Should raise error for non-existent template."""
        from scaffold import load_template

        with pytest.raises(FileNotFoundError):
            load_template("nonexistent_template")

    def test_known_templates_exist(self):
        """All known templates should be loadable."""
        from scaffold import load_template

        templates = [
            "checkpoint",
            "implementation_plan",
            "investigation",
            "report",
            "architecture_decision_record",
        ]

        for template in templates:
            content = load_template(template)
            assert content is not None


class TestSubstituteVariables:
    """Tests for substitute_variables() function."""

    def test_substitutes_single_variable(self):
        """Should substitute single {{VAR}} placeholder."""
        from scaffold import substitute_variables

        content = "Session {{SESSION}} started"
        result = substitute_variables(content, {"SESSION": "93"})

        assert result == "Session 93 started"

    def test_substitutes_multiple_variables(self):
        """Should substitute multiple placeholders."""
        from scaffold import substitute_variables

        content = "{{TITLE}} for Session {{SESSION}} on {{DATE}}"
        result = substitute_variables(content, {
            "TITLE": "Test",
            "SESSION": "93",
            "DATE": "2025-12-21"
        })

        assert result == "Test for Session 93 on 2025-12-21"

    def test_leaves_unmatched_placeholders(self):
        """Should leave unmatched placeholders as-is."""
        from scaffold import substitute_variables

        content = "{{KNOWN}} and {{UNKNOWN}}"
        result = substitute_variables(content, {"KNOWN": "value"})

        assert result == "value and {{UNKNOWN}}"

    def test_handles_empty_variables(self):
        """Should handle empty variables dict."""
        from scaffold import substitute_variables

        content = "No {{VARS}} here"
        result = substitute_variables(content, {})

        assert result == "No {{VARS}} here"


class TestGetNextSequenceNumber:
    """Tests for get_next_sequence_number() function."""

    def test_returns_01_for_empty_directory(self, tmp_path):
        """Should return '01' when no files exist."""
        from scaffold import get_next_sequence_number

        result = get_next_sequence_number(str(tmp_path), "2025-12-21")

        assert result == "01"

    def test_increments_existing_sequence(self, tmp_path):
        """Should return next number after existing files."""
        from scaffold import get_next_sequence_number

        # Create existing files
        (tmp_path / "2025-12-21-01-SESSION-92.md").touch()
        (tmp_path / "2025-12-21-02-SESSION-93.md").touch()

        result = get_next_sequence_number(str(tmp_path), "2025-12-21")

        assert result == "03"

    def test_ignores_other_dates(self, tmp_path):
        """Should only count files from specified date."""
        from scaffold import get_next_sequence_number

        # Create file from different date
        (tmp_path / "2025-12-20-05-SESSION-91.md").touch()

        result = get_next_sequence_number(str(tmp_path), "2025-12-21")

        assert result == "01"


class TestGetPrevSession:
    """Tests for get_prev_session() function."""

    def test_reads_from_status_file(self):
        """Should read last_session from haios-status.json."""
        from scaffold import get_prev_session

        result = get_prev_session()

        assert isinstance(result, int) or result == "??"

    def test_returns_fallback_on_error(self, tmp_path):
        """Should return '??' if status file unavailable."""
        from scaffold import get_prev_session
        import scaffold

        # Temporarily point to non-existent file
        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        try:
            result = get_prev_session()
            assert result == "??"
        finally:
            scaffold.PROJECT_ROOT = original_root


class TestScaffoldTemplate:
    """Tests for scaffold_template() main function."""

    def test_creates_file_with_substitutions(self, tmp_path):
        """Should create file with variables substituted."""
        from scaffold import scaffold_template

        output_path = tmp_path / "test-output.md"

        result = scaffold_template(
            template="checkpoint",
            output_path=str(output_path),
            variables={"SESSION": "99", "TITLE": "Test Checkpoint"}
        )

        assert output_path.exists()
        content = output_path.read_text()
        assert "99" in content or "Test Checkpoint" in content

    def test_auto_generates_path_when_not_provided(self, tmp_path):
        """Should auto-generate output path from backlog_id and title."""
        from scaffold import scaffold_template
        import scaffold

        # Point to tmp for output
        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Create required directories
        (tmp_path / "docs" / "investigations").mkdir(parents=True)
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create work file (E2-160 requirement)
        (tmp_path / "docs" / "work" / "active" / "WORK-INV-TEST-test.md").write_text(
            "---\nid: INV-TEST\n---"
        )

        # Create minimal template
        template_content = "---\ntemplate: investigation\n---\n# {{TITLE}}"
        (tmp_path / ".claude" / "templates" / "investigation.md").write_text(template_content)

        try:
            result = scaffold_template(
                template="investigation",
                backlog_id="INV-TEST",
                title="Test Investigation"
            )

            assert result is not None
            assert "INV-TEST" in result
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_adds_default_date_variable(self, tmp_path):
        """Should add DATE variable if not provided."""
        from scaffold import scaffold_template
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        template_content = "Date: {{DATE}}"
        (tmp_path / ".claude" / "templates" / "report.md").write_text(template_content)
        (tmp_path / "docs" / "reports").mkdir(parents=True)

        try:
            output_path = tmp_path / "docs" / "reports" / "test.md"
            result = scaffold_template(
                template="report",
                output_path=str(output_path),
                variables={}
            )

            content = output_path.read_text()
            today = datetime.now().strftime("%Y-%m-%d")
            assert today in content
        finally:
            scaffold.PROJECT_ROOT = original_root


class TestIntegration:
    """Integration tests for scaffold module."""

    def test_scaffold_checkpoint_flow(self, tmp_path):
        """Full flow: scaffold checkpoint with all features."""
        from scaffold import scaffold_template
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "checkpoints").mkdir(parents=True)

        # Create checkpoint template
        template = """---
template: checkpoint
session: {{SESSION}}
prior_session: {{PREV_SESSION}}
---
# Session {{SESSION}}: {{TITLE}}
Date: {{DATE}}
"""
        (tmp_path / ".claude" / "templates" / "checkpoint.md").write_text(template)

        # Create mock status file (E2-133: use session_delta schema)
        status = {"session_delta": {"prior_session": 92, "current_session": 93}}
        (tmp_path / ".claude").mkdir(exist_ok=True)
        (tmp_path / ".claude" / "haios-status.json").write_text(json.dumps(status))

        try:
            result = scaffold_template(
                template="checkpoint",
                backlog_id="93",
                title="Test Session"
            )

            assert result is not None
            assert Path(result).exists()

            content = Path(result).read_text()
            assert "session: 93" in content
            assert "prior_session: 92" in content
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_session_populated_for_investigation(self, tmp_path):
        """E2-133: SESSION should be auto-populated for non-checkpoint templates."""
        from scaffold import scaffold_template
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "investigations").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create work file (E2-160 requirement)
        (tmp_path / "docs" / "work" / "active" / "WORK-INV-TEST-test.md").write_text(
            "---\nid: INV-TEST\n---"
        )

        # Create investigation template with SESSION placeholder
        template = """---
template: investigation
session: {{SESSION}}
---
# Investigation: {{TITLE}}
"""
        (tmp_path / ".claude" / "templates" / "investigation.md").write_text(template)

        # Create mock status file with current_session
        status = {"session_delta": {"prior_session": 99, "current_session": 100}}
        (tmp_path / ".claude" / "haios-status.json").write_text(json.dumps(status))

        try:
            result = scaffold_template(
                template="investigation",
                backlog_id="INV-TEST",
                title="Test Investigation"
            )

            assert result is not None
            assert Path(result).exists()

            content = Path(result).read_text()
            # SESSION should be populated from current_session
            assert "session: 100" in content
        finally:
            scaffold.PROJECT_ROOT = original_root


class TestWorkFilePrerequisiteGate:
    """Tests for E2-160: Work file prerequisite gate."""

    def test_investigation_with_work_file_succeeds(self, tmp_path):
        """Investigation scaffold succeeds when work file exists."""
        from scaffold import scaffold_template
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "investigations").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create work file
        (tmp_path / "docs" / "work" / "active" / "WORK-E2-999-test.md").write_text(
            "---\nid: E2-999\n---"
        )

        # Create investigation template
        template = "---\ntemplate: investigation\n---\n# {{TITLE}}"
        (tmp_path / ".claude" / "templates" / "investigation.md").write_text(template)

        try:
            result = scaffold_template(
                template="investigation",
                backlog_id="E2-999",
                title="Test Investigation"
            )
            assert result is not None
            assert "INVESTIGATION-E2-999" in result
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_investigation_without_work_file_raises(self, tmp_path):
        """Investigation scaffold fails when no work file exists."""
        from scaffold import scaffold_template
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure (NO work file)
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "investigations").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create investigation template
        template = "---\ntemplate: investigation\n---\n# {{TITLE}}"
        (tmp_path / ".claude" / "templates" / "investigation.md").write_text(template)

        try:
            with pytest.raises(ValueError, match="Work file required"):
                scaffold_template(
                    template="investigation",
                    backlog_id="E2-999",
                    title="Test Investigation"
                )
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_work_item_template_not_gated(self, tmp_path):
        """Work item template should not require existing work file."""
        from scaffold import scaffold_template
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure (NO existing work file)
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create work_item template
        template = "---\ntemplate: work_item\nid: {{BACKLOG_ID}}\n---\n# {{TITLE}}"
        (tmp_path / ".claude" / "templates" / "work_item.md").write_text(template)

        try:
            result = scaffold_template(
                template="work_item",
                backlog_id="E2-999",
                title="Test Work Item"
            )
            assert result is not None
            # E2-212: Now creates directory structure, not flat file
            assert "E2-999" in result and "WORK.md" in result
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_checkpoint_not_gated(self, tmp_path):
        """Checkpoint template should not require work file."""
        from scaffold import scaffold_template
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure (NO work file)
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "checkpoints").mkdir(parents=True)

        # Create checkpoint template
        template = "---\ntemplate: checkpoint\nsession: {{SESSION}}\n---\n# {{TITLE}}"
        (tmp_path / ".claude" / "templates" / "checkpoint.md").write_text(template)

        # Create mock status file
        (tmp_path / ".claude" / "haios-status.json").write_text(
            '{"session_delta": {"prior_session": 109, "current_session": 110}}'
        )

        try:
            result = scaffold_template(
                template="checkpoint",
                backlog_id="110",
                title="Test Checkpoint"
            )
            assert result is not None
            assert "SESSION-110" in result
        finally:
            scaffold.PROJECT_ROOT = original_root


# =============================================================================
# WORK-001: Sequential Work ID Generation Tests
# =============================================================================

class TestGetNextWorkId:
    """Tests for get_next_work_id() function (WORK-001)."""

    def test_get_next_work_id_empty_directory(self, tmp_path):
        """Should return WORK-001 when no WORK items exist."""
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Create empty work directory
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        try:
            from scaffold import get_next_work_id
            result = get_next_work_id()
            assert result == "WORK-001"
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_get_next_work_id_sequential(self, tmp_path):
        """Should return next ID after highest existing."""
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Create work directories
        work_dir = tmp_path / "docs" / "work" / "active"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK-001").mkdir()
        (work_dir / "WORK-003").mkdir()  # Gap is OK

        try:
            from scaffold import get_next_work_id
            result = get_next_work_id()
            assert result == "WORK-004"  # Next after highest (003)
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_get_next_work_id_ignores_legacy_ids(self, tmp_path):
        """Should ignore E2-XXX and INV-XXX directories."""
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Create work directories with mixed IDs
        work_dir = tmp_path / "docs" / "work" / "active"
        work_dir.mkdir(parents=True)
        (work_dir / "E2-179").mkdir()  # Legacy - should be ignored
        (work_dir / "INV-041").mkdir()  # Legacy - should be ignored
        (work_dir / "WORK-002").mkdir()

        try:
            from scaffold import get_next_work_id
            result = get_next_work_id()
            assert result == "WORK-003"  # Based only on WORK-* items
        finally:
            scaffold.PROJECT_ROOT = original_root


# =============================================================================
# E2-179: Spawned_by Variable Tests
# =============================================================================

class TestSpawnedByVariable:
    """Tests for E2-179: spawned_by optional variable support."""

    def test_scaffold_work_item_without_spawned_by(self, tmp_path):
        """Scaffolding work item without spawned_by should default to null."""
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create work_item template with spawned_by placeholder
        template = """---
template: work_item
id: {{BACKLOG_ID}}
title: "{{TITLE}}"
spawned_by: {{SPAWNED_BY}}
priority: medium
---
# {{BACKLOG_ID}}: {{TITLE}}
"""
        (tmp_path / ".claude" / "templates" / "work_item.md").write_text(template)

        try:
            result = scaffold.scaffold_template(
                template="work_item",
                backlog_id="E2-999",
                title="Test Work Item"
            )

            assert result is not None
            content = Path(result).read_text()
            # Should default to null when not provided
            assert "spawned_by: null" in content
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_scaffold_work_item_with_spawned_by(self, tmp_path):
        """Scaffolding with variables dict should populate spawned_by."""
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create work_item template with spawned_by placeholder
        template = """---
template: work_item
id: {{BACKLOG_ID}}
title: "{{TITLE}}"
spawned_by: {{SPAWNED_BY}}
priority: medium
---
# {{BACKLOG_ID}}: {{TITLE}}
"""
        (tmp_path / ".claude" / "templates" / "work_item.md").write_text(template)

        try:
            result = scaffold.scaffold_template(
                template="work_item",
                backlog_id="E2-999",
                title="Test Work Item",
                variables={"SPAWNED_BY": "INV-033"}
            )

            assert result is not None
            content = Path(result).read_text()
            assert "spawned_by: INV-033" in content
        finally:
            scaffold.PROJECT_ROOT = original_root

    def test_scaffold_with_multiple_optional_variables(self, tmp_path):
        """Multiple optional variables should all be substituted."""
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Set up directory structure
        (tmp_path / ".claude" / "templates").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create work_item template with multiple optional placeholders
        template = """---
template: work_item
id: {{BACKLOG_ID}}
title: "{{TITLE}}"
spawned_by: {{SPAWNED_BY}}
priority: {{PRIORITY}}
milestone: {{MILESTONE}}
---
# {{BACKLOG_ID}}: {{TITLE}}
"""
        (tmp_path / ".claude" / "templates" / "work_item.md").write_text(template)

        try:
            result = scaffold.scaffold_template(
                template="work_item",
                backlog_id="E2-999",
                title="Test Work Item",
                variables={
                    "SPAWNED_BY": "INV-033",
                    "PRIORITY": "high",
                    "MILESTONE": "M8-Memory"
                }
            )

            assert result is not None
            content = Path(result).read_text()
            assert "spawned_by: INV-033" in content
            assert "priority: high" in content
            assert "milestone: M8-Memory" in content
        finally:
            scaffold.PROJECT_ROOT = original_root


# =============================================================================
# S340 B3: Scaffold Output Lint Tests
# =============================================================================

class TestScaffoldOutputLint:
    """Validate scaffold output produces valid YAML frontmatter and clean markdown.

    S340 tiny fix B3: ensures no broken frontmatter is produced by scaffolding.
    """

    TEMPLATE_CONFIGS = [
        ("checkpoint", "99", "Lint Test Session", {"SESSION": "99"}),
        ("report", None, "Lint Test Report", {}),
        ("architecture_decision_record", "099", "Lint Test ADR", {}),
    ]

    # Fields that are operator-fill (not auto-populated by scaffold)
    OPERATOR_FILL_FIELDS = {"SPAWNED_BY", "MILESTONE", "PRIORITY", "CHAPTER", "ARC", "AUTHOR", "ID", "WORK_ID", "PLAN_REF"}

    @pytest.fixture
    def scaffold_env(self, tmp_path):
        """Set up a scaffold environment with templates copied from real project."""
        import scaffold

        original_root = scaffold.PROJECT_ROOT
        scaffold.PROJECT_ROOT = tmp_path

        # Copy real templates to tmp
        real_templates = Path(__file__).parent.parent / ".claude" / "templates"
        tmp_templates = tmp_path / ".claude" / "templates"
        tmp_templates.mkdir(parents=True)

        for tmpl_file in real_templates.glob("*.md"):
            (tmp_templates / tmpl_file.name).write_text(
                tmpl_file.read_text(encoding="utf-8"), encoding="utf-8"
            )

        # Also copy _legacy/ if it exists
        legacy_dir = real_templates / "_legacy"
        if legacy_dir.exists():
            tmp_legacy = tmp_templates / "_legacy"
            tmp_legacy.mkdir(exist_ok=True)
            for tmpl_file in legacy_dir.glob("*.md"):
                (tmp_legacy / tmpl_file.name).write_text(
                    tmpl_file.read_text(encoding="utf-8"), encoding="utf-8"
                )

        # Create required output directories
        (tmp_path / "docs" / "checkpoints").mkdir(parents=True)
        (tmp_path / "docs" / "reports").mkdir(parents=True)
        (tmp_path / "docs" / "ADR").mkdir(parents=True)
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)

        # Create session file
        session_file = tmp_path / ".claude" / "session"
        session_file.write_text("# session\n99\n")

        # Create mock status file
        status = {"session_delta": {"prior_session": 98, "current_session": 99}}
        (tmp_path / ".claude" / "haios-status.json").write_text(json.dumps(status))

        yield tmp_path

        scaffold.PROJECT_ROOT = original_root

    @pytest.mark.parametrize("template,backlog_id,title,variables", TEMPLATE_CONFIGS)
    def test_scaffold_produces_valid_yaml_frontmatter(
        self, scaffold_env, template, backlog_id, title, variables
    ):
        """Scaffold output must have parseable YAML frontmatter."""
        from scaffold import scaffold_template

        result = scaffold_template(
            template=template,
            backlog_id=backlog_id,
            title=title,
            variables=variables,
        )

        assert result is not None
        content = Path(result).read_text(encoding="utf-8")

        # Extract frontmatter between --- markers
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        assert fm_match, f"No YAML frontmatter found in {template} output"

        # Replace unresolved {{VAR}} with placeholder strings so YAML can parse
        sanitized = re.sub(r"\{\{(\w+)\}\}", r"__PLACEHOLDER_\1__", fm_match.group(1))

        # Parse YAML - must not raise
        frontmatter = yaml.safe_load(sanitized)
        assert isinstance(frontmatter, dict), f"Frontmatter is not a dict in {template}"

    @pytest.mark.parametrize("template,backlog_id,title,variables", TEMPLATE_CONFIGS)
    def test_scaffold_no_unresolved_required_placeholders(
        self, scaffold_env, template, backlog_id, title, variables
    ):
        """Scaffold output must not have unresolved {{VAR}} in frontmatter for required fields."""
        from scaffold import scaffold_template

        result = scaffold_template(
            template=template,
            backlog_id=backlog_id,
            title=title,
            variables=variables,
        )

        content = Path(result).read_text(encoding="utf-8")

        # Extract frontmatter
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        assert fm_match

        frontmatter_text = fm_match.group(1)
        # Find any remaining {{...}} placeholders
        unresolved = re.findall(r"\{\{(\w+)\}\}", frontmatter_text)

        # Filter out operator-fill fields that are allowed to remain as placeholders
        required_unresolved = [f for f in unresolved if f not in self.OPERATOR_FILL_FIELDS]

        assert not required_unresolved, (
            f"Unresolved required placeholders in {template} frontmatter: {required_unresolved}"
        )


# =============================================================================
# WORK-138: CLI Scaffold Arg Parsing Tests
# =============================================================================

class TestCLIScaffoldArgParsing:
    """Tests for WORK-138: CLI scaffold command argument parsing.

    The CLI scaffold handler must parse --session and --title flags for checkpoint
    scaffolding, not treat them as positional args that mangle the filename.
    """

    def _parse_scaffold_args(self, argv_list):
        """Simulate the scaffold arg parsing logic from cli.py main().

        This extracts the parsing logic so we can test it in isolation.
        Returns (template, backlog_id, title, output_path, variables).
        """
        # Import the parsing logic - we test via cmd_scaffold indirectly,
        # but for unit testing the parsing we replicate the logic
        args = list(argv_list)

        output_path = None
        variables = {}

        # Extract --output flag
        if "--output" in args:
            output_idx = args.index("--output")
            output_path = args[output_idx + 1]
            args = [a for i, a in enumerate(args) if i not in (output_idx, output_idx + 1)]

        # Extract --spawned-by flag
        if "--spawned-by" in args:
            idx = args.index("--spawned-by")
            variables["SPAWNED_BY"] = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

        # Extract --type flag
        if "--type" in args:
            idx = args.index("--type")
            variables["TYPE"] = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

        # WORK-138: Extract --session flag (maps to backlog_id for checkpoints)
        session_override = None
        if "--session" in args:
            idx = args.index("--session")
            session_override = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

        # WORK-138: Extract --title flag (maps to title)
        title_override = None
        if "--title" in args:
            idx = args.index("--title")
            title_override = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

        template = args[2]

        # Remaining positional args after template (args[3:])
        positional = args[3:]

        if session_override and title_override:
            # Both flags provided — no positional consumption needed
            backlog_id = session_override
            title = title_override
        elif session_override:
            # --session provided: all remaining positional args are title
            backlog_id = session_override
            title = " ".join(positional) if positional else None
        elif title_override:
            # --title provided: first positional is backlog_id
            backlog_id = positional[0] if positional else None
            title = title_override
        else:
            # Pure positional: first is backlog_id, rest is title
            backlog_id = positional[0] if positional else None
            title = " ".join(positional[1:]) if len(positional) > 1 else None

        return template, backlog_id, title, output_path, variables

    def test_named_flags_session_and_title(self):
        """--session and --title flags should be parsed correctly."""
        argv = ["cli.py", "scaffold", "checkpoint", "--session", "358", "--title", "work-100-audit"]
        template, backlog_id, title, output_path, variables = self._parse_scaffold_args(argv)

        assert template == "checkpoint"
        assert backlog_id == "358"
        assert title == "work-100-audit"

    def test_positional_args_still_work(self):
        """Positional args (no flags) should still work: scaffold checkpoint 358 my title."""
        argv = ["cli.py", "scaffold", "checkpoint", "358", "my", "title"]
        template, backlog_id, title, output_path, variables = self._parse_scaffold_args(argv)

        assert template == "checkpoint"
        assert backlog_id == "358"
        assert title == "my title"

    def test_mixed_named_and_positional_flags(self):
        """--session flag mixed with positional title should work."""
        argv = ["cli.py", "scaffold", "checkpoint", "--session", "358", "my", "title"]
        template, backlog_id, title, output_path, variables = self._parse_scaffold_args(argv)

        assert template == "checkpoint"
        assert backlog_id == "358"
        assert title == "my title"

    def test_session_flag_with_spawned_by(self):
        """--session combined with --spawned-by should both parse."""
        argv = ["cli.py", "scaffold", "work_item", "--session", "99", "--spawned-by", "INV-033", "My", "Title"]
        template, backlog_id, title, output_path, variables = self._parse_scaffold_args(argv)

        assert template == "work_item"
        assert backlog_id == "99"
        assert title == "My Title"
        assert variables["SPAWNED_BY"] == "INV-033"


class TestPlanTemplateRouting:
    """Tests for WORK-152: Plan template fracturing by work type."""

    def test_get_plan_type_maps_feature_to_implementation(self):
        """Work item type 'feature' maps to plan template type 'implementation'."""
        from scaffold import get_plan_type

        assert get_plan_type("feature") == "implementation"

    def test_get_plan_type_maps_bug_to_cleanup(self):
        """Work item type 'bug' maps to plan template type 'cleanup'."""
        from scaffold import get_plan_type

        assert get_plan_type("bug") == "cleanup"

    def test_get_plan_type_maps_chore_to_cleanup(self):
        """Work item type 'chore' maps to plan template type 'cleanup'."""
        from scaffold import get_plan_type

        assert get_plan_type("chore") == "cleanup"

    def test_get_plan_type_maps_design_to_design(self):
        """Work item type 'design' maps to plan template type 'design'."""
        from scaffold import get_plan_type

        assert get_plan_type("design") == "design"

    def test_get_plan_type_maps_spike_to_implementation(self):
        """Work item type 'spike' maps to plan template type 'implementation'."""
        from scaffold import get_plan_type

        assert get_plan_type("spike") == "implementation"

    def test_get_plan_type_unknown_falls_back_to_implementation(self):
        """Unknown work item type defaults to 'implementation'."""
        from scaffold import get_plan_type

        assert get_plan_type("unknown_type") == "implementation"

    def test_load_plan_template_routes_by_type(self, tmp_path, monkeypatch):
        """load_plan_template('design') returns design-specific template."""
        import scaffold

        monkeypatch.setattr(scaffold, "PROJECT_ROOT", tmp_path)

        plans_dir = tmp_path / ".claude" / "templates" / "plans"
        plans_dir.mkdir(parents=True)
        (plans_dir / "design.md").write_text(
            "---\ntemplate: implementation_plan\nsubtype: design\n---\n# Design Plan\n",
            encoding="utf-8",
        )

        result = scaffold.load_plan_template("design")
        assert "Design Plan" in result

    def test_load_plan_template_fallback_to_legacy(self, tmp_path, monkeypatch):
        """load_plan_template('unknown_type') falls back to implementation_plan."""
        import scaffold

        monkeypatch.setattr(scaffold, "PROJECT_ROOT", tmp_path)

        # No plans/ directory exists, but legacy template does
        legacy_dir = tmp_path / ".claude" / "templates" / "_legacy"
        legacy_dir.mkdir(parents=True)
        (legacy_dir / "implementation_plan.md").write_text(
            "---\ntemplate: implementation_plan\n---\n# Implementation Plan: {{TITLE}}\n",
            encoding="utf-8",
        )

        result = scaffold.load_plan_template("unknown_type")
        assert "Implementation Plan" in result

    def test_load_plan_template_default_is_implementation(self, tmp_path, monkeypatch):
        """load_plan_template() with no arg loads implementation template."""
        import scaffold

        monkeypatch.setattr(scaffold, "PROJECT_ROOT", tmp_path)

        plans_dir = tmp_path / ".claude" / "templates" / "plans"
        plans_dir.mkdir(parents=True)
        (plans_dir / "implementation.md").write_text(
            "---\ntemplate: implementation_plan\n---\n# Implementation Plan\n## Tests First (TDD)\n",
            encoding="utf-8",
        )

        result = scaffold.load_plan_template()
        assert "Tests First" in result

    def test_scaffold_template_auto_extracts_type(self, tmp_path, monkeypatch):
        """scaffold_template reads work item type and routes to correct template."""
        import scaffold

        monkeypatch.setattr(scaffold, "PROJECT_ROOT", tmp_path)

        # Create work item with type: design
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-TEST"
        work_dir.mkdir(parents=True)
        (work_dir / "plans").mkdir()
        (work_dir / "WORK.md").write_text(
            "---\ntemplate: work_item\nid: WORK-TEST\ntitle: Test\ntype: design\nstatus: active\n---\n",
            encoding="utf-8",
        )

        # Create design plan template
        plans_dir = tmp_path / ".claude" / "templates" / "plans"
        plans_dir.mkdir(parents=True)
        (plans_dir / "design.md").write_text(
            "---\ntemplate: implementation_plan\nsubtype: design\nstatus: draft\ndate: {{DATE}}\nbacklog_id: {{BACKLOG_ID}}\ntitle: \"{{TITLE}}\"\nauthor: Hephaestus\nsession: {{SESSION}}\nversion: \"1.5\"\ngenerated: {{DATE}}\nlast_updated: {{TIMESTAMP}}\n---\n# Design Plan: {{TITLE}}\n## Goal\nDesign-specific content\n",
            encoding="utf-8",
        )

        result = scaffold.scaffold_template(
            "implementation_plan",
            output_path=str(work_dir / "plans" / "PLAN.md"),
            backlog_id="WORK-TEST",
            title="Test Design Plan",
        )

        # Read the output file and verify design template was used
        content = Path(result).read_text(encoding="utf-8")
        assert "Design-specific content" in content
