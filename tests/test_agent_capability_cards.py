# generated: 2026-02-15
# Session 375: WORK-144 Agent Capability Cards
"""Tests for agent capability card frontmatter fields (REQ-DISCOVER-004)."""

import yaml
from pathlib import Path

AGENTS_DIR = Path(".claude/agents")


def _parse_frontmatter(agent_file: Path) -> dict:
    """Parse YAML frontmatter from agent .md file."""
    content = agent_file.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{agent_file.name}: missing frontmatter delimiters"
    return yaml.safe_load(parts[1])


def test_all_agents_have_capability_card_fields():
    """Every agent .md file must have the new capability card frontmatter fields."""
    required_fields = {
        "requirement_level", "category", "trigger_conditions",
        "input_contract", "output_contract", "invoked_by", "related_agents",
    }

    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        if agent_file.name == "README.md":
            continue
        fm = _parse_frontmatter(agent_file)
        for field in required_fields:
            assert field in fm, f"{agent_file.name}: missing field '{field}'"


def test_capability_card_field_values_valid():
    """Validate allowed values for enum-like fields."""
    valid_levels = {"required", "recommended", "optional"}
    valid_categories = {"gate", "verification", "utility", "cycle-delegation"}

    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        if agent_file.name == "README.md":
            continue
        fm = _parse_frontmatter(agent_file)
        assert fm["requirement_level"] in valid_levels, \
            f"{agent_file.name}: invalid requirement_level '{fm['requirement_level']}'"
        assert fm["category"] in valid_categories, \
            f"{agent_file.name}: invalid category '{fm['category']}'"
        assert isinstance(fm["trigger_conditions"], list), \
            f"{agent_file.name}: trigger_conditions must be a list"
        assert isinstance(fm["invoked_by"], list), \
            f"{agent_file.name}: invoked_by must be a list"
        assert isinstance(fm["related_agents"], list), \
            f"{agent_file.name}: related_agents must be a list"


def test_existing_frontmatter_fields_preserved():
    """Existing fields (name, description, tools, model) must still be present."""
    core_fields = {"name", "description", "tools", "model"}

    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        if agent_file.name == "README.md":
            continue
        fm = _parse_frontmatter(agent_file)
        for field in core_fields:
            assert field in fm, \
                f"{agent_file.name}: core field '{field}' missing after update"


def test_agent_count():
    """Verify exactly 11 agent files exist (excluding README)."""
    agent_files = [f for f in AGENTS_DIR.glob("*.md") if f.name != "README.md"]
    assert len(agent_files) == 11, \
        f"Expected 11 agents, found {len(agent_files)}: {[f.name for f in agent_files]}"


def test_contracts_are_nonempty():
    """input_contract and output_contract must be non-empty strings."""
    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        if agent_file.name == "README.md":
            continue
        fm = _parse_frontmatter(agent_file)
        assert isinstance(fm["input_contract"], str) and len(fm["input_contract"]) > 0, \
            f"{agent_file.name}: input_contract must be non-empty string"
        assert isinstance(fm["output_contract"], str) and len(fm["output_contract"]) > 0, \
            f"{agent_file.name}: output_contract must be non-empty string"
