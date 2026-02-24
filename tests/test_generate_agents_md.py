# generated: 2026-02-24
# Session 439: WORK-164 Agent Cards
"""Tests for generate_agents_md.py — AGENTS.md auto-generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
from agent_cards import list_agents
from generate_agents_md import generate_agents_md


class TestGenerateAgentsMd:
    """Test AGENTS.md generation."""

    def test_returns_string(self):
        """generate_agents_md() returns a string."""
        result = generate_agents_md()
        assert isinstance(result, str)

    def test_contains_header(self):
        """Generated markdown contains a top-level header."""
        result = generate_agents_md()
        assert "# AGENTS" in result or "# Agents" in result

    def test_contains_all_agents(self):
        """Generated markdown mentions all agents by name."""
        result = generate_agents_md()
        agents = list_agents()
        for agent in agents:
            assert agent.name in result, \
                f"Agent '{agent.name}' not found in generated AGENTS.md"

    def test_contains_table(self):
        """Generated markdown contains a markdown table."""
        result = generate_agents_md()
        assert "| Agent |" in result or "| Name |" in result

    def test_table_row_count(self):
        """Summary table (Agent Registry) has one row per agent."""
        result = generate_agents_md()
        agents = list_agents()
        # Extract only the Agent Registry table — rows with bold agent names
        # Format: | **agent-name** | model | ...
        registry_rows = [
            line for line in result.splitlines()
            if line.startswith("| **") and "| " in line
        ]
        assert len(registry_rows) == len(agents), \
            f"Expected {len(agents)} registry rows, got {len(registry_rows)}"

    def test_contains_invocation_pattern(self):
        """Generated markdown contains invocation example."""
        result = generate_agents_md()
        assert "Task(" in result or "subagent_type" in result

    def test_no_readme_in_output(self):
        """README.md should not appear as an agent entry."""
        result = generate_agents_md()
        # Should not have a table row for README
        lines = result.splitlines()
        for line in lines:
            if line.startswith("|") and "README" in line:
                assert False, "README.md appeared as agent entry in generated output"
