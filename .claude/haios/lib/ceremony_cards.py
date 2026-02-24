# generated: 2026-02-24
# Session 445: WORK-165 Ceremony Cards
"""Ceremony card discovery module (REQ-DISCOVER-003).

Provides programmatic access to ceremony capability cards by parsing
YAML frontmatter from .claude/skills/*/SKILL.md files where type == 'ceremony'.

Public API:
    list_ceremonies() -> list[CeremonyCard]
    get_ceremony(name) -> CeremonyCard | None
    filter_ceremonies(category) -> list[CeremonyCard]
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path


# Anchored to this file's location, not cwd (same pattern as agent_cards.py)
_LIB_DIR = Path(__file__).resolve().parent
_HAIOS_DIR = _LIB_DIR.parent
_CLAUDE_DIR = _HAIOS_DIR.parent
SKILLS_DIR = _CLAUDE_DIR / "skills"


@dataclass
class CeremonyCard:
    """Structured representation of a ceremony skill's capability card.

    Required fields: name, description, category.
    All other fields are optional with sensible defaults to support
    incremental frontmatter extension.

    Note: category stores the primary (first) category as a string for
    simple filtering. categories stores ALL categories as a list for
    multi-category ceremonies (e.g., close-work-cycle: [closure, queue]).
    filter_ceremonies checks membership in the full categories list.
    """

    # Required fields (always present in ceremony frontmatter)
    name: str
    description: str
    category: str  # Primary category (first element if list)

    # Multi-category support (critique A2: prevent silent data loss)
    categories: list[str] = field(default_factory=list)

    # Optional fields with defaults
    input_contract: list = field(default_factory=list)
    output_contract: list = field(default_factory=list)
    side_effects: list[str] = field(default_factory=list)


def _parse_frontmatter(filepath: Path) -> dict | None:
    """Parse YAML frontmatter from a SKILL.md file.

    Returns None if parsing fails (defensive, mirrors agent_cards.py pattern).
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        return yaml.safe_load(parts[1])
    except Exception:
        return None


def _frontmatter_to_card(fm: dict) -> CeremonyCard | None:
    """Convert frontmatter dict to CeremonyCard.

    Returns None if:
    - type != 'ceremony' (filters out non-ceremony skills)
    - required fields (name, description, category) are missing
    """
    if fm.get("type") != "ceremony":
        return None

    name = fm.get("name")
    description = fm.get("description")
    category = fm.get("category")

    if not name or not description or not category:
        return None

    # category may be a list (close-work-cycle has category: [closure, queue])
    # Preserve ALL categories in categories list; normalize primary to first element
    if isinstance(category, list):
        categories = [str(c) for c in category]
        primary_category = categories[0] if categories else ""
    else:
        categories = [str(category)]
        primary_category = str(category)

    return CeremonyCard(
        name=name,
        description=description,
        category=primary_category,
        categories=categories,
        input_contract=fm.get("input_contract") or [],
        output_contract=fm.get("output_contract") or [],
        side_effects=fm.get("side_effects") or [],
    )


def list_ceremonies(skills_dir: Path | None = None) -> list[CeremonyCard]:
    """List all ceremonies by parsing frontmatter from SKILL.md files.

    Scans all subdirectories of skills_dir for SKILL.md files.
    Only includes skills where type == 'ceremony'.

    Args:
        skills_dir: Override skills directory (for testing). Defaults to SKILLS_DIR.

    Returns:
        List of CeremonyCard instances, sorted by name.
    """
    directory = skills_dir or SKILLS_DIR
    ceremonies = []
    for skill_dir in sorted(directory.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        fm = _parse_frontmatter(skill_file)
        if fm is None:
            continue
        card = _frontmatter_to_card(fm)
        if card is not None:
            ceremonies.append(card)
    return ceremonies


def get_ceremony(name: str, skills_dir: Path | None = None) -> CeremonyCard | None:
    """Get a single ceremony by name.

    Args:
        name: Ceremony name (e.g., "open-epoch-ceremony").
        skills_dir: Override skills directory (for testing).

    Returns:
        CeremonyCard if found, None otherwise.
    """
    for ceremony in list_ceremonies(skills_dir):
        if ceremony.name == name:
            return ceremony
    return None


def filter_ceremonies(
    category: str | None = None,
    skills_dir: Path | None = None,
) -> list[CeremonyCard]:
    """Filter ceremonies by frontmatter field values.

    Checks against the full categories list, not just the primary category.
    This means filter_ceremonies(category="queue") will return close-work-cycle
    even though its primary category is "closure" (it has categories: [closure, queue]).

    Args:
        category: Filter by category (closure, queue, session, memory, feedback, spawn).
        skills_dir: Override skills directory (for testing).

    Returns:
        List of matching CeremonyCard instances.
    """
    ceremonies = list_ceremonies(skills_dir)
    if category is not None:
        ceremonies = [c for c in ceremonies if category in c.categories]
    return ceremonies
