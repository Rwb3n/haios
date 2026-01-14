# generated: 2025-12-28
# System Auto: last updated on: 2025-12-28T21:32:33
"""
Tests for dependency validation module (E2-024).

Tests extraction of skill/agent references and validation that they exist.
"""
import pytest
import sys
from pathlib import Path

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


class TestExtractSkillRefs:
    """Test extraction of Skill(skill="...") patterns."""

    def test_extract_skill_refs_single(self):
        """Test extraction of single skill reference."""
        from dependencies import extract_skill_refs

        content = 'Skill(skill="plan-validation-cycle")'
        refs = extract_skill_refs(content)
        assert refs == ["plan-validation-cycle"]

    def test_extract_skill_refs_single_quotes(self):
        """Test extraction with single quotes."""
        from dependencies import extract_skill_refs

        content = "Skill(skill='close-work-cycle')"
        refs = extract_skill_refs(content)
        assert refs == ["close-work-cycle"]

    def test_extract_skill_refs_multiple(self):
        """Test extraction of multiple skill references."""
        from dependencies import extract_skill_refs

        content = 'Skill(skill="a") then Skill(skill="b")'
        refs = extract_skill_refs(content)
        assert refs == ["a", "b"]

    def test_extract_skill_refs_none(self):
        """Test extraction when no refs present."""
        from dependencies import extract_skill_refs

        content = "No skill references here"
        refs = extract_skill_refs(content)
        assert refs == []


class TestExtractAgentRefs:
    """Test extraction of Task(subagent_type='...') patterns."""

    def test_extract_agent_refs_single(self):
        """Test extraction of single agent reference."""
        from dependencies import extract_agent_refs

        content = "Task(subagent_type='preflight-checker', prompt='...')"
        refs = extract_agent_refs(content)
        assert refs == ["preflight-checker"]

    def test_extract_agent_refs_double_quotes(self):
        """Test extraction with double quotes."""
        from dependencies import extract_agent_refs

        content = 'Task(subagent_type="schema-verifier")'
        refs = extract_agent_refs(content)
        assert refs == ["schema-verifier"]

    def test_extract_agent_refs_none(self):
        """Test extraction when no refs present."""
        from dependencies import extract_agent_refs

        content = "No agent references here"
        refs = extract_agent_refs(content)
        assert refs == []


class TestGetAvailableSkills:
    """Test discovery of available skills."""

    def test_get_available_skills_includes_known(self):
        """Test that known skills are discovered."""
        from dependencies import get_available_skills

        skills = get_available_skills()
        # These skills should exist in the system
        assert "implementation-cycle" in skills
        assert "close-work-cycle" in skills

    def test_get_available_skills_returns_set(self):
        """Test that return type is set."""
        from dependencies import get_available_skills

        skills = get_available_skills()
        assert isinstance(skills, set)


class TestGetAvailableAgents:
    """Test discovery of available agents."""

    def test_get_available_agents_includes_known(self):
        """Test that known agents are discovered."""
        from dependencies import get_available_agents

        agents = get_available_agents()
        # These agents should exist in the system
        assert "preflight-checker" in agents
        assert "schema-verifier" in agents

    def test_get_available_agents_excludes_readme(self):
        """Test that README.md is not included as an agent."""
        from dependencies import get_available_agents

        agents = get_available_agents()
        assert "README" not in agents

    def test_get_available_agents_returns_set(self):
        """Test that return type is set."""
        from dependencies import get_available_agents

        agents = get_available_agents()
        assert isinstance(agents, set)


class TestValidateDependencies:
    """Test the main validation function."""

    def test_validate_dependencies_returns_dict(self):
        """Test that validation returns expected structure."""
        from dependencies import validate_dependencies

        result = validate_dependencies()
        assert isinstance(result, dict)
        assert "valid" in result
        assert "broken_refs" in result
        assert "summary" in result

    def test_validate_dependencies_valid_system(self):
        """Test validation on current (hopefully healthy) system."""
        from dependencies import validate_dependencies

        result = validate_dependencies()
        # In a healthy system, should have no broken refs
        # (or at least the function should run without error)
        assert isinstance(result["valid"], bool)
        assert isinstance(result["broken_refs"], list)

    def test_validate_dependencies_summary_format(self):
        """Test that summary has expected format."""
        from dependencies import validate_dependencies

        result = validate_dependencies()
        # Summary should mention refs and broken count
        assert "refs" in result["summary"].lower() or "reference" in result["summary"].lower()
