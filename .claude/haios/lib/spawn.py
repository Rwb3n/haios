# generated: 2025-12-22
# System Auto: last updated on: 2026-01-21T22:19:33
# DEPRECATED: E2-251 migrated this functionality to WorkEngine
# Use: python .claude/haios/modules/cli.py spawn-tree <id>
# This file remains for reference only - will be removed in E2-255
"""DEPRECATED: Spawn tree - migrated to WorkEngine.spawn_tree() in E2-251.

Spawn tree query - visualizes what work items spawned from a source.

Traverses spawned_by relationships across plans, investigations, checkpoints.

Usage:
    from spawn import build_spawn_tree, format_tree
    tree = build_spawn_tree("INV-017")
    print(format_tree(tree))

Or via justfile:
    just spawns INV-017
"""

from pathlib import Path
import re
from typing import Any

# Project root detection (4 levels up from .claude/haios/lib/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOCS_PATH = PROJECT_ROOT / "docs"


def parse_yaml_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Full markdown file content

    Returns:
        Dict of frontmatter fields, or empty dict if no frontmatter
    """
    match = re.match(r'^---\s*\n([\s\S]*?)\n---', content)
    if not match:
        return {}

    yaml_str = match.group(1)
    result = {}

    # Parse simple YAML fields
    for line in yaml_str.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            result[key.strip()] = value.strip().strip('"\'')

    return result


def find_children(parent_id: str, docs_path: Path = None) -> list[dict]:
    """Find all items that have spawned_by: parent_id.

    Args:
        parent_id: The ID to search for in spawned_by fields
        docs_path: Path to docs directory (for testing)

    Returns:
        List of dicts with id, title, file keys
    """
    docs_path = docs_path or DOCS_PATH
    children = []

    # Scan all markdown files in docs/
    for md_file in docs_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue

        fm = parse_yaml_frontmatter(content)
        spawned_by = fm.get('spawned_by', '')

        if spawned_by == parent_id:
            # Get ID from backlog_id, investigation_id, or filename
            item_id = (
                fm.get('backlog_id') or
                fm.get('investigation_id') or
                md_file.stem
            )
            title = fm.get('title', '')
            children.append({
                'id': item_id,
                'title': title,
                'file': str(md_file)
            })

    return children


def build_spawn_tree(
    root_id: str,
    docs_path: Path = None,
    max_depth: int = 5
) -> dict:
    """Build recursive spawn tree from root_id.

    Args:
        root_id: The ID to start the tree from
        docs_path: Path to docs directory (for testing)
        max_depth: Maximum recursion depth (prevents infinite loops)

    Returns:
        Nested dict representing the tree: {root_id: {child_id: {...}}}
    """
    if max_depth <= 0:
        return {root_id: {}}

    children = find_children(root_id, docs_path)
    subtree = {}

    for child in children:
        child_tree = build_spawn_tree(
            child['id'],
            docs_path,
            max_depth - 1
        )
        # Merge child tree into subtree
        subtree[child['id']] = child_tree.get(child['id'], {})

    return {root_id: subtree}


def format_tree(tree: dict, prefix: str = "", use_ascii: bool = False) -> str:
    """Format tree as ASCII art.

    Args:
        tree: Nested dict from build_spawn_tree
        prefix: Current line prefix (for recursion)
        use_ascii: Use ASCII-only characters for Windows compatibility

    Returns:
        ASCII tree string
    """
    # Use ASCII-only on Windows to avoid encoding issues
    if use_ascii:
        LAST_CONNECTOR = "+-- "
        MID_CONNECTOR = "+-- "
        LAST_PREFIX = "    "
        MID_PREFIX = "|   "
    else:
        LAST_CONNECTOR = "└── "
        MID_CONNECTOR = "├── "
        LAST_PREFIX = "    "
        MID_PREFIX = "│   "

    lines = []

    for root_id, children in tree.items():
        lines.append(f"{root_id}")

        child_items = list(children.items())
        for i, (child_id, grandchildren) in enumerate(child_items):
            is_last_child = (i == len(child_items) - 1)
            connector = LAST_CONNECTOR if is_last_child else MID_CONNECTOR
            child_prefix = LAST_PREFIX if is_last_child else MID_PREFIX

            lines.append(f"{prefix}{connector}{child_id}")

            if grandchildren:
                # Recursively format grandchildren
                subtree = {child_id: grandchildren}
                sublines = format_tree(subtree, prefix + child_prefix, use_ascii)
                # Skip first line (already printed child_id)
                for subline in sublines.split('\n')[1:]:
                    if subline:
                        lines.append(subline)

    return '\n'.join(lines)


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python spawn.py <id>")
        print("Example: python spawn.py INV-017")
        sys.exit(1)

    root_id = sys.argv[1]
    tree = build_spawn_tree(root_id)
    output = format_tree(tree)

    if output.strip() == root_id:
        print(f"{root_id} (no spawned items found)")
    else:
        print(output)
