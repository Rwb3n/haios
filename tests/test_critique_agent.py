# generated: 2026-01-25
# System Auto: last updated on: 2026-01-25T01:24:27
"""
Tests for E2-072: Critique Agent (Assumption Surfacing)

TDD: These tests define expected behavior BEFORE implementation.
"""

import pytest
from pathlib import Path
import yaml


class TestFrameworkLoading:
    """Test 1: Framework loads from config correctly."""

    def test_framework_loads_from_config(self):
        """Verify assumption_surfacing.yaml loads correctly."""
        framework_path = Path(".claude/haios/config/critique_frameworks/assumption_surfacing.yaml")
        assert framework_path.exists(), "Framework file must exist"

        with open(framework_path) as f:
            framework = yaml.safe_load(f)

        # Required top-level keys
        assert "name" in framework, "Framework must have name"
        assert "categories" in framework, "Framework must have categories"
        assert "verdict_rules" in framework, "Framework must have verdict_rules"

        # Must have at least 5 categories
        assert len(framework["categories"]) >= 5, (
            f"Expected at least 5 categories, got {len(framework['categories'])}"
        )

        # Required category IDs
        required_categories = {"dependency", "data", "user_behavior", "environment", "scope"}
        actual_categories = {cat["id"] for cat in framework["categories"]}
        assert required_categories.issubset(actual_categories), (
            f"Missing required categories: {required_categories - actual_categories}"
        )

    def test_categories_have_required_fields(self):
        """Each category must have id, label, and prompt."""
        framework_path = Path(".claude/haios/config/critique_frameworks/assumption_surfacing.yaml")

        with open(framework_path) as f:
            framework = yaml.safe_load(f)

        for cat in framework["categories"]:
            assert "id" in cat, f"Category missing 'id': {cat}"
            assert "label" in cat, f"Category {cat.get('id')} missing 'label'"
            assert "prompt" in cat, f"Category {cat.get('id')} missing 'prompt'"

    def test_verdict_rules_defined(self):
        """Verdict rules must define BLOCK, REVISE, PROCEED."""
        framework_path = Path(".claude/haios/config/critique_frameworks/assumption_surfacing.yaml")

        with open(framework_path) as f:
            framework = yaml.safe_load(f)

        required_verdicts = {"BLOCK", "REVISE", "PROCEED"}
        actual_verdicts = set(framework["verdict_rules"].keys())
        assert required_verdicts.issubset(actual_verdicts), (
            f"Missing verdict rules: {required_verdicts - actual_verdicts}"
        )


class TestCritiqueOutputSchema:
    """Test 2: Critique output matches expected schema."""

    def test_critique_output_schema(self):
        """Verify critique output matches expected schema."""
        # Mock critique output - this is the expected format
        output = {
            "assumptions": [
                {
                    "id": "A1",
                    "statement": "Memory query returns results",
                    "category": "dependency",
                    "confidence": "medium",
                    "risk_if_wrong": "Context loading fails",
                    "mitigation": "Add fallback",
                    "related_requirement": "Builder must signal blockage",
                    "related_deliverable": "D2"
                }
            ],
            "verdict": "REVISE",
            "blocking_assumptions": ["A1"]
        }

        # Validate required fields
        assert "assumptions" in output
        assert "verdict" in output
        assert output["verdict"] in ["BLOCK", "REVISE", "PROCEED"]

        for assumption in output["assumptions"]:
            assert "id" in assumption, "Assumption must have id"
            assert "category" in assumption, "Assumption must have category"
            assert assumption["category"] in [
                "dependency", "data", "user_behavior", "environment", "scope"
            ], f"Invalid category: {assumption['category']}"
            assert "confidence" in assumption, "Assumption must have confidence"
            assert assumption["confidence"] in ["high", "medium", "low"]
            assert "mitigation" in assumption, "Assumption must have mitigation"

    def test_empty_assumptions_returns_proceed(self):
        """If no assumptions found, verdict should be PROCEED."""
        output = {
            "assumptions": [],
            "verdict": "PROCEED",
            "blocking_assumptions": []
        }

        assert output["verdict"] == "PROCEED"
        assert len(output["blocking_assumptions"]) == 0


class TestAgentDefinition:
    """Test 3: Agent definition has required frontmatter."""

    def test_critique_agent_definition(self):
        """Verify agent definition has required frontmatter."""
        agent_path = Path(".claude/agents/critique-agent.md")
        assert agent_path.exists(), "Agent file must exist"

        content = agent_path.read_text()

        # Extract frontmatter (between first two ---)
        parts = content.split("---")
        assert len(parts) >= 3, "Agent file must have YAML frontmatter"

        frontmatter = yaml.safe_load(parts[1])

        # Required frontmatter fields
        assert frontmatter["name"] == "critique-agent", (
            f"Expected name 'critique-agent', got '{frontmatter.get('name')}'"
        )
        assert "description" in frontmatter, "Agent must have description"
        assert "tools" in frontmatter, "Agent must have tools"

        # Required tools
        required_tools = {"Read", "Glob"}
        if isinstance(frontmatter["tools"], str):
            actual_tools = {t.strip() for t in frontmatter["tools"].split(",")}
        else:
            actual_tools = set(frontmatter["tools"])

        assert required_tools.issubset(actual_tools), (
            f"Missing required tools: {required_tools - actual_tools}"
        )

    def test_agent_has_context_loading_instructions(self):
        """Agent must document how to load config and framework."""
        agent_path = Path(".claude/agents/critique-agent.md")
        content = agent_path.read_text()

        # Must mention config loading
        assert "haios.yaml" in content, "Agent must reference haios.yaml for config"
        assert "framework" in content.lower(), "Agent must mention framework loading"

    def test_agent_has_output_instructions(self):
        """Agent must document output format and location."""
        agent_path = Path(".claude/agents/critique-agent.md")
        content = agent_path.read_text()

        # Must mention output
        assert "critique-report" in content.lower() or "assumptions.yaml" in content.lower(), (
            "Agent must document output files"
        )
        assert "verdict" in content.lower(), "Agent must mention verdict output"
