# generated: 2026-02-12
# System Auto: last updated on: 2026-02-12
"""
Shared test utilities for HAIOS test suite.

Session 355: Promoted load_skill_frontmatter() from test_memory_ceremonies.py.
Session 356: Renamed to load_frontmatter() for general-purpose use.
"""

from pathlib import Path

import yaml


def load_frontmatter(file_path: str) -> dict:
    """Parse YAML frontmatter from a markdown file.

    Reads the content between the first two '---' delimiters
    and returns the parsed YAML dict. Works with any markdown
    file that uses YAML frontmatter (skills, templates, work items, etc.).

    Args:
        file_path: Relative or absolute path to a markdown file.
            Accepts str or Path objects.

    Returns:
        Parsed YAML frontmatter as a dict.

    Raises:
        ValueError: If no YAML frontmatter delimiters found.
    """
    content = Path(file_path).read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No YAML frontmatter found in {file_path}")
    return yaml.safe_load(parts[1])


# Backward-compatible alias
load_skill_frontmatter = load_frontmatter
