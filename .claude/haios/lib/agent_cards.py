# generated: 2026-02-24
# Session 439: WORK-164 Agent Cards
"""Agent card discovery module (REQ-DISCOVER-003).

Provides programmatic access to agent capability cards by parsing
YAML frontmatter from .claude/agents/*.md files.

Public API:
    list_agents() -> list[AgentCard]
    get_agent(name) -> AgentCard | None
    filter_agents(category, requirement_level, model) -> list[AgentCard]
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path


# Anchored to this file's location, not cwd (critique A2/A9)
_LIB_DIR = Path(__file__).resolve().parent
_HAIOS_DIR = _LIB_DIR.parent
_CLAUDE_DIR = _HAIOS_DIR.parent
AGENTS_DIR = _CLAUDE_DIR / "agents"

# Controlled artifact vocabulary (critique A5)
ARTIFACT_VOCABULARY = frozenset({
    "critique-report",
    "assumptions-yaml",
    "test-results",
    "validation-report",
    "investigation-findings",
    "plan-document",
    "schema-info",
    "design-review",
    "anti-pattern-verdict",
    "learning-extraction",
    "work-item",
    "cycle-summary",
})


@dataclass
class AgentCard:
    """Structured representation of an agent's capability card.

    Required fields: name, description, tools, model.
    All other fields are optional with sensible defaults to support
    incremental frontmatter extension (critique A1).
    """

    # Required fields (always present in agent frontmatter)
    name: str
    description: str
    tools: list[str]
    model: str

    # Existing optional fields
    requirement_level: str = "optional"
    category: str = "utility"
    trigger_conditions: list[str] = field(default_factory=list)
    input_contract: str = ""
    output_contract: str = ""
    invoked_by: list[str] = field(default_factory=list)
    related_agents: list[str] = field(default_factory=list)

    # New fields (WORK-164, optional with defaults for TDD compatibility)
    id: str = ""
    role: str = ""
    capabilities: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    consumes: list[str] = field(default_factory=list)


def _parse_frontmatter(filepath: Path) -> dict | None:
    """Parse YAML frontmatter from an agent .md file.

    Returns None if parsing fails (defensive, critique A1).
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        return yaml.safe_load(parts[1])
    except Exception:
        return None


def _parse_tools(tools_value) -> list[str]:
    """Parse tools field which can be a string or list."""
    if isinstance(tools_value, list):
        return tools_value
    if isinstance(tools_value, str):
        return [t.strip() for t in tools_value.split(",") if t.strip()]
    return []


def _frontmatter_to_card(fm: dict) -> AgentCard | None:
    """Convert frontmatter dict to AgentCard, returning None if required fields missing."""
    name = fm.get("name")
    description = fm.get("description")
    tools_raw = fm.get("tools", [])
    model = fm.get("model")

    if not name or not description or not model:
        return None

    tools = _parse_tools(tools_raw)

    return AgentCard(
        name=name,
        description=description,
        tools=tools,
        model=model,
        requirement_level=fm.get("requirement_level", "optional"),
        category=fm.get("category", "utility"),
        trigger_conditions=fm.get("trigger_conditions") or [],
        input_contract=fm.get("input_contract") or "",
        output_contract=fm.get("output_contract") or "",
        invoked_by=fm.get("invoked_by") or [],
        related_agents=fm.get("related_agents") or [],
        id=fm.get("id") or "",
        role=fm.get("role") or "",
        capabilities=fm.get("capabilities") or [],
        produces=fm.get("produces") or [],
        consumes=fm.get("consumes") or [],
    )


def list_agents(agents_dir: Path | None = None) -> list[AgentCard]:
    """List all agents by parsing frontmatter from .md files.

    Args:
        agents_dir: Override agent directory (for testing). Defaults to AGENTS_DIR.

    Returns:
        List of AgentCard instances, sorted by name.
    """
    directory = agents_dir or AGENTS_DIR
    agents = []
    for filepath in sorted(directory.glob("*.md")):
        if filepath.name == "README.md":
            continue
        fm = _parse_frontmatter(filepath)
        if fm is None:
            continue
        card = _frontmatter_to_card(fm)
        if card is not None:
            agents.append(card)
    return agents


def get_agent(name: str, agents_dir: Path | None = None) -> AgentCard | None:
    """Get a single agent by name.

    Args:
        name: Agent name (e.g., "critique-agent").
        agents_dir: Override agent directory (for testing).

    Returns:
        AgentCard if found, None otherwise.
    """
    for agent in list_agents(agents_dir):
        if agent.name == name:
            return agent
    return None


def filter_agents(
    category: str | None = None,
    requirement_level: str | None = None,
    model: str | None = None,
    agents_dir: Path | None = None,
) -> list[AgentCard]:
    """Filter agents by frontmatter field values.

    All provided filters are ANDed together.

    Args:
        category: Filter by category (gate, verification, utility, cycle-delegation).
        requirement_level: Filter by requirement_level (required, recommended, optional).
        model: Filter by model (haiku, sonnet, opus).
        agents_dir: Override agent directory (for testing).

    Returns:
        List of matching AgentCard instances.
    """
    agents = list_agents(agents_dir)
    if category is not None:
        agents = [a for a in agents if a.category == category]
    if requirement_level is not None:
        agents = [a for a in agents if a.requirement_level == requirement_level]
    if model is not None:
        agents = [a for a in agents if a.model == model]
    return agents
