# generated: 2025-12-28
# System Auto: last updated on: 2025-12-28T21:35:12
"""
Dependency Integrity Validator (E2-024).

Validates that skill and agent references in HAIOS governance files exist.
Detects broken references before they cause runtime errors.

Usage:
    from dependencies import validate_dependencies

    result = validate_dependencies()
    if not result["valid"]:
        print(f"Broken refs: {result['broken_refs']}")
"""
import re
from pathlib import Path
from typing import Optional

# Paths relative to project root
# These are set as module-level for easy testing/mocking
SKILLS_PATH = Path(".claude/skills")
AGENTS_PATH = Path(".claude/agents")


def extract_skill_refs(content: str) -> list[str]:
    """
    Extract skill names from Skill(skill="...") patterns.

    Supports both single and double quotes.

    Args:
        content: Text content to search

    Returns:
        List of skill names referenced (may have duplicates)

    Example:
        >>> extract_skill_refs('Skill(skill="plan-validation-cycle")')
        ['plan-validation-cycle']
    """
    # Match Skill(skill="name") or Skill(skill='name')
    pattern = r'Skill\(skill=["\']([^"\']+)["\']\)'
    return re.findall(pattern, content)


def extract_agent_refs(content: str) -> list[str]:
    """
    Extract agent names from Task(subagent_type='...') patterns.

    Supports both single and double quotes, and handles other Task parameters.

    Args:
        content: Text content to search

    Returns:
        List of agent names referenced (may have duplicates)

    Example:
        >>> extract_agent_refs("Task(subagent_type='preflight-checker', prompt='...')")
        ['preflight-checker']
    """
    # Match Task(... subagent_type="name" ...) - subagent_type can appear anywhere in params
    pattern = r"Task\([^)]*subagent_type=['\"]([^'\"]+)['\"]"
    return re.findall(pattern, content)


def get_available_skills(skills_path: Optional[Path] = None) -> set[str]:
    """
    Get set of available skill names from .claude/skills/*/SKILL.md.

    Args:
        skills_path: Optional override path (for testing)

    Returns:
        Set of skill directory names that have a SKILL.md file
    """
    path = skills_path or SKILLS_PATH
    skills = set()

    if not path.exists():
        return skills

    for skill_file in path.glob("*/SKILL.md"):
        skills.add(skill_file.parent.name)

    return skills


def get_available_agents(agents_path: Optional[Path] = None) -> set[str]:
    """
    Get set of available agent names from .claude/agents/*.md.

    Excludes README.md from the list.

    Args:
        agents_path: Optional override path (for testing)

    Returns:
        Set of agent file stems (filenames without .md extension)
    """
    path = agents_path or AGENTS_PATH
    agents = set()

    if not path.exists():
        return agents

    for agent_file in path.glob("*.md"):
        # Exclude README files
        if agent_file.stem.lower() != "readme":
            agents.add(agent_file.stem)

    return agents


def validate_dependencies(
    skills_path: Optional[Path] = None,
    agents_path: Optional[Path] = None
) -> dict:
    """
    Validate all skill/agent references exist.

    Scans all skills for Skill() and Task() references, then checks
    that the referenced skills and agents actually exist.

    Args:
        skills_path: Optional override for skills directory (for testing)
        agents_path: Optional override for agents directory (for testing)

    Returns:
        dict with keys:
        - valid: bool - True if no broken refs
        - broken_refs: list[dict] - Each has source, target, type
        - summary: str - Human-readable summary
    """
    skills_dir = skills_path or SKILLS_PATH
    agents_dir = agents_path or AGENTS_PATH

    broken_refs = []
    total_refs = 0

    # Get available resources
    available_skills = get_available_skills(skills_dir)
    available_agents = get_available_agents(agents_dir)

    # Check each skill for references
    if skills_dir.exists():
        for skill_file in skills_dir.glob("*/SKILL.md"):
            skill_name = skill_file.parent.name

            try:
                content = skill_file.read_text(encoding="utf-8")
            except Exception:
                continue

            # Check skill references
            for ref in extract_skill_refs(content):
                total_refs += 1
                if ref not in available_skills:
                    broken_refs.append({
                        "source": f"skill:{skill_name}",
                        "target": f"skill:{ref}",
                        "type": "skill"
                    })

            # Check agent references
            for ref in extract_agent_refs(content):
                total_refs += 1
                if ref not in available_agents:
                    broken_refs.append({
                        "source": f"skill:{skill_name}",
                        "target": f"agent:{ref}",
                        "type": "agent"
                    })

    return {
        "valid": len(broken_refs) == 0,
        "broken_refs": broken_refs,
        "summary": f"{total_refs} refs checked, {len(broken_refs)} broken"
    }


if __name__ == "__main__":
    # Quick test when run directly
    result = validate_dependencies()
    print(f"Valid: {result['valid']}")
    print(f"Summary: {result['summary']}")
    if result['broken_refs']:
        print("Broken references:")
        for ref in result['broken_refs']:
            print(f"  {ref['source']} -> {ref['target']}")
