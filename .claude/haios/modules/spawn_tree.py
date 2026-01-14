# generated: 2026-01-09
# System Auto: last updated on: 2026-01-09T21:48:11
"""
SpawnTree Module (E2-279)

Spawn tree traversal and formatting. Provides:
- spawn_tree(root_id): Build nested spawn tree
- format_tree(tree): Format as ASCII art

Extracted from WorkEngine as part of E2-279 decomposition per ADR-041 svelte criteria.

Stateless utility - no persistent state.

Usage:
    from spawn_tree import SpawnTree

    tree = SpawnTree(base_path=Path("."))
    result = tree.spawn_tree("INV-001")
    print(SpawnTree.format_tree(result))
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

# Constants
WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"


class SpawnTree:
    """
    Spawn tree traversal and formatting.

    Traverses spawned_by relationships across work files to build
    hierarchical trees showing work item lineage.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize SpawnTree.

        Args:
            base_path: Base path for file operations (default: cwd)
        """
        self._base_path = base_path or Path(".")

    @property
    def active_dir(self) -> Path:
        """Path to active work items directory."""
        return self._base_path / ACTIVE_DIR

    @property
    def archive_dir(self) -> Path:
        """Path to archived work items directory."""
        return self._base_path / ARCHIVE_DIR

    def spawn_tree(self, root_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Build spawn tree from root_id.

        Traverses spawned_by relationships across work files.

        Args:
            root_id: ID to start tree from
            max_depth: Maximum recursion depth

        Returns:
            Nested dict: {root_id: {child_id: {grandchild_id: {}}}}
        """
        if max_depth <= 0:
            return {root_id: {}}

        children = self._find_children(root_id)
        subtree = {}

        for child_id in children:
            child_tree = self.spawn_tree(child_id, max_depth - 1)
            subtree[child_id] = child_tree.get(child_id, {})

        return {root_id: subtree}

    def _find_children(self, parent_id: str) -> List[str]:
        """Find all items with spawned_by: parent_id."""
        children = []

        # Scan active work items
        if self.active_dir.exists():
            for work_dir in self.active_dir.iterdir():
                if not work_dir.is_dir():
                    continue
                work_file = work_dir / "WORK.md"
                if not work_file.exists():
                    continue

                try:
                    content = work_file.read_text(encoding="utf-8")
                    parts = content.split("---", 2)
                    if len(parts) < 3:
                        continue
                    fm = yaml.safe_load(parts[1]) or {}
                    spawned_by = fm.get("spawned_by", "")
                    if spawned_by == parent_id:
                        item_id = fm.get("id", work_dir.name)
                        children.append(item_id)
                except Exception:
                    continue

        # Also scan archive
        if self.archive_dir.exists():
            for work_dir in self.archive_dir.iterdir():
                if not work_dir.is_dir():
                    continue
                work_file = work_dir / "WORK.md"
                if not work_file.exists():
                    continue

                try:
                    content = work_file.read_text(encoding="utf-8")
                    parts = content.split("---", 2)
                    if len(parts) < 3:
                        continue
                    fm = yaml.safe_load(parts[1]) or {}
                    spawned_by = fm.get("spawned_by", "")
                    if spawned_by == parent_id:
                        item_id = fm.get("id", work_dir.name)
                        if item_id not in children:
                            children.append(item_id)
                except Exception:
                    continue

        return children

    @staticmethod
    def format_tree(tree: Dict[str, Any], use_ascii: bool = False) -> str:
        """Format spawn tree as ASCII art."""
        if use_ascii:
            LAST = "+-- "
            MID = "+-- "
            LAST_PRE = "    "
            MID_PRE = "|   "
        else:
            LAST = "\u2514\u2500\u2500 "
            MID = "\u251c\u2500\u2500 "
            LAST_PRE = "    "
            MID_PRE = "\u2502   "

        def _format(subtree: Dict[str, Any], prefix: str = "") -> List[str]:
            lines = []
            items = list(subtree.items())
            for i, (child_id, grandchildren) in enumerate(items):
                is_last = i == len(items) - 1
                conn = LAST if is_last else MID
                child_pre = LAST_PRE if is_last else MID_PRE
                lines.append(f"{prefix}{conn}{child_id}")
                if grandchildren:
                    lines.extend(_format(grandchildren, prefix + child_pre))
            return lines

        result = []
        for root_id, children in tree.items():
            result.append(root_id)
            if children:
                result.extend(_format(children))
            elif not children:
                pass  # Just show root

        if len(result) == 1:
            return f"{result[0]} (no spawned items found)"
        return "\n".join(result)
