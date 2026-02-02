# generated: 2026-02-02
# System Auto: last updated on: 2026-02-02T15:41:55
# Tests for WORK-070: Multi-Level DoD Cascade Design
# TDD: These tests written BEFORE implementation

from pathlib import Path
import pytest


class TestL4Requirements:
    """Test REQ-DOD-001 and REQ-DOD-002 exist in functional_requirements.md"""

    @pytest.fixture
    def requirements_content(self):
        path = Path(".claude/haios/manifesto/L4/functional_requirements.md")
        assert path.exists(), f"Requirements file not found: {path}"
        return path.read_text()

    def test_req_dod_001_exists(self, requirements_content):
        """REQ-DOD-001 should exist in functional_requirements.md"""
        assert "REQ-DOD-001" in requirements_content
        assert "chapter closure" in requirements_content.lower()

    def test_req_dod_002_exists(self, requirements_content):
        """REQ-DOD-002 should exist in functional_requirements.md"""
        assert "REQ-DOD-002" in requirements_content
        assert "arc closure" in requirements_content.lower()

    def test_req_dod_in_registry(self, requirements_content):
        """REQ-DOD requirements should be in the registry table"""
        # Registry table has format: | ID | Domain | Description | Derives From | Implemented By |
        assert "| REQ-DOD-001 |" in requirements_content or "| **REQ-DOD-001** |" in requirements_content
        assert "| REQ-DOD-002 |" in requirements_content or "| **REQ-DOD-002** |" in requirements_content


class TestCH010ChapterFile:
    """Test CH-010 chapter file exists with required fields"""

    @pytest.fixture
    def chapter_path(self):
        return Path(".claude/haios/epochs/E2_4/arcs/flow/CH-010-MultiLevelDoD.md")

    def test_ch010_chapter_file_exists(self, chapter_path):
        """CH-010 chapter file should exist"""
        assert chapter_path.exists(), f"Chapter file not found: {chapter_path}"

    def test_ch010_has_implements_decisions(self, chapter_path):
        """CH-010 should have implements_decisions field"""
        content = chapter_path.read_text()
        assert "implements_decisions" in content
        # Should implement D8 (Multi-Level Governance from EPOCH.md)
        assert "D8" in content

    def test_ch010_has_required_sections(self, chapter_path):
        """CH-010 should have Definition, Problem, Solution, Exit Criteria sections"""
        content = chapter_path.read_text()
        assert "## Definition" in content
        assert "**Chapter ID:** CH-010" in content
        assert "**Arc:** flow" in content
        assert "## Problem" in content
        assert "## Solution" in content or "## Solution:" in content
        assert "## Exit Criteria" in content


class TestCloseChapterCeremony:
    """Test close-chapter-ceremony skill exists with required structure (WORK-076)"""

    @pytest.fixture
    def skill_path(self):
        return Path(".claude/skills/close-chapter-ceremony/SKILL.md")

    def test_close_chapter_ceremony_exists(self, skill_path):
        """close-chapter-ceremony skill should exist"""
        assert skill_path.exists(), f"Skill file not found: {skill_path}"

    def test_close_chapter_ceremony_has_cycle(self, skill_path):
        """Skill should have VALIDATE->MARK->REPORT cycle"""
        content = skill_path.read_text()
        assert "## The Cycle" in content
        assert "VALIDATE" in content
        assert "MARK" in content
        assert "REPORT" in content

    def test_close_chapter_ceremony_references_req_dod_001(self, skill_path):
        """Skill should reference REQ-DOD-001"""
        content = skill_path.read_text()
        assert "REQ-DOD-001" in content

    def test_close_chapter_ceremony_has_implements_decisions_check(self, skill_path):
        """Skill should check implements_decisions field"""
        content = skill_path.read_text()
        assert "implements_decisions" in content

    def test_close_chapter_ceremony_has_frontmatter(self, skill_path):
        """Skill should have proper frontmatter with name and description"""
        content = skill_path.read_text()
        assert content.startswith("---")
        assert "name: close-chapter-ceremony" in content
        assert "description:" in content


class TestCloseArcCeremony:
    """Test close-arc-ceremony skill exists with required structure (WORK-077)"""

    @pytest.fixture
    def skill_path(self):
        return Path(".claude/skills/close-arc-ceremony/SKILL.md")

    def test_close_arc_ceremony_exists(self, skill_path):
        """close-arc-ceremony skill should exist"""
        assert skill_path.exists(), f"Skill file not found: {skill_path}"

    def test_close_arc_ceremony_has_cycle(self, skill_path):
        """Skill should have VALIDATE->MARK->REPORT cycle"""
        content = skill_path.read_text()
        assert "## The Cycle" in content
        assert "VALIDATE" in content
        assert "MARK" in content
        assert "REPORT" in content

    def test_close_arc_ceremony_references_req_dod_002(self, skill_path):
        """Skill should reference REQ-DOD-002"""
        content = skill_path.read_text()
        assert "REQ-DOD-002" in content

    def test_close_arc_ceremony_has_orphan_decision_check(self, skill_path):
        """Skill should check for orphan decisions (unassigned epoch decisions)"""
        content = skill_path.read_text()
        assert "orphan" in content.lower() or "unassigned" in content.lower()

    def test_close_arc_ceremony_has_frontmatter(self, skill_path):
        """Skill should have proper frontmatter with name and description"""
        content = skill_path.read_text()
        assert content.startswith("---")
        assert "name: close-arc-ceremony" in content
        assert "description:" in content


class TestCloseEpochCeremony:
    """Test close-epoch-ceremony skill exists with required structure (WORK-078)"""

    @pytest.fixture
    def skill_path(self):
        return Path(".claude/skills/close-epoch-ceremony/SKILL.md")

    def test_close_epoch_ceremony_exists(self, skill_path):
        """close-epoch-ceremony skill should exist"""
        assert skill_path.exists(), f"Skill file not found: {skill_path}"

    def test_close_epoch_ceremony_has_cycle(self, skill_path):
        """Skill should have VALIDATE->ARCHIVE->TRANSITION cycle"""
        content = skill_path.read_text()
        assert "## The Cycle" in content
        assert "VALIDATE" in content
        assert "ARCHIVE" in content
        assert "TRANSITION" in content

    def test_close_epoch_ceremony_has_archive_work_items(self, skill_path):
        """Skill should document archiving work items at epoch boundary"""
        content = skill_path.read_text()
        assert "archive" in content.lower()
        assert "work item" in content.lower() or "work items" in content.lower()

    def test_close_epoch_ceremony_has_haios_yaml_update(self, skill_path):
        """Skill should document haios.yaml update for epoch transition"""
        content = skill_path.read_text()
        assert "haios.yaml" in content

    def test_close_epoch_ceremony_has_frontmatter(self, skill_path):
        """Skill should have proper frontmatter with name and description"""
        content = skill_path.read_text()
        assert content.startswith("---")
        assert "name: close-epoch-ceremony" in content
        assert "description:" in content
