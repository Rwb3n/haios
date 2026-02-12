# generated: 2026-02-12
"""
Shared test utilities for HAIOS test suite.

Session 355: Promoted load_skill_frontmatter() from test_memory_ceremonies.py
to shared utility (checkpoint pending item from S353).
"""

from pathlib import Path

import yaml


def load_skill_frontmatter(skill_path: str) -> dict:
    """Parse YAML frontmatter from a skill markdown file.

    Reads the content between the first two '---' delimiters
    and returns the parsed YAML dict.

    Args:
        skill_path: Relative or absolute path to a SKILL.md file.
            Accepts str or Path objects.

    Returns:
        Parsed YAML frontmatter as a dict.

    Raises:
        ValueError: If no YAML frontmatter delimiters found.
    """
    content = Path(skill_path).read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No YAML frontmatter found in {skill_path}")
    return yaml.safe_load(parts[1])
