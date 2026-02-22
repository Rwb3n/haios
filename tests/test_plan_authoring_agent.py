# generated: 2026-02-21
# Tests for WORK-176: Plan-Authoring-Cycle Subagent Delegation
"""
Tests verifying the plan-authoring-agent card and its integration
with implementation-cycle SKILL.md.
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end])


def _read_body(path: Path) -> str:
    """Read markdown body (after frontmatter) from a file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return text
    end = text.index("---", 3)
    return text[end + 3 :]


class TestPlanAuthoringAgent:
    """Tests for .claude/agents/plan-authoring-agent.md"""

    AGENT_PATH = ROOT / ".claude" / "agents" / "plan-authoring-agent.md"

    def test_agent_card_has_required_frontmatter(self):
        """Agent card must have all required capability card fields."""
        assert self.AGENT_PATH.exists(), f"Agent card not found: {self.AGENT_PATH}"
        fm = _parse_frontmatter(self.AGENT_PATH)

        required_fields = [
            "name",
            "description",
            "tools",
            "model",
            "context",
            "requirement_level",
            "category",
            "trigger_conditions",
            "input_contract",
            "output_contract",
            "invoked_by",
            "related_agents",
        ]
        for field in required_fields:
            assert field in fm, f"Missing required field: {field}"

        # Verify specific values
        assert fm["name"] == "plan-authoring-agent"
        assert fm["model"] == "sonnet"
        assert fm["context"] == "fork"
        assert fm["category"] == "cycle-delegation"
        assert fm["requirement_level"] == "optional"

    def test_agent_card_references_plan_authoring_skill(self):
        """Agent card body must reference the plan-authoring-cycle SKILL.md as source of truth."""
        assert self.AGENT_PATH.exists(), f"Agent card not found: {self.AGENT_PATH}"
        body = _read_body(self.AGENT_PATH)

        assert (
            ".claude/skills/plan-authoring-cycle/SKILL.md" in body
        ), "Agent card must reference plan-authoring-cycle SKILL.md"

    def test_implementation_cycle_delegates_to_subagent(self):
        """implementation-cycle phases/PLAN.md must contain subagent invocation pattern."""
        # After fracturing (WORK-187), plan-authoring delegation lives in phases/PLAN.md
        plan_phase_path = ROOT / ".claude" / "skills" / "implementation-cycle" / "phases" / "PLAN.md"
        assert plan_phase_path.exists(), f"Phase file not found: {plan_phase_path}"
        content = plan_phase_path.read_text(encoding="utf-8")

        assert (
            "plan-authoring-agent" in content
        ), "implementation-cycle phases/PLAN.md must reference plan-authoring-agent"
        assert (
            "Task(subagent_type='plan-authoring-agent'" in content
        ), "implementation-cycle phases/PLAN.md must contain Task invocation pattern"

    def test_agent_listed_in_readme(self):
        """plan-authoring-agent must appear in the agents README table."""
        readme_path = ROOT / ".claude" / "agents" / "README.md"
        assert readme_path.exists(), f"README not found: {readme_path}"
        content = readme_path.read_text(encoding="utf-8")

        assert (
            "plan-authoring-agent" in content
        ), "plan-authoring-agent must be listed in agents README"
