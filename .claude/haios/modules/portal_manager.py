# generated: 2026-01-09
# System Auto: last updated on: 2026-01-25T21:28:00
"""
PortalManager Module (E2-279)

Portal (references/REFS.md) management for work items. Provides:
- create_portal(id, refs_path): Create REFS.md for new work item
- update_portal(id, updates): Add spawned_from, memory_refs, ADRs
- link_spawned_items(parent, children): Link multiple items

Extracted from WorkEngine as part of E2-279 decomposition per ADR-041 svelte criteria.

L4 Invariants:
- Owns REFS.md files (single writer)
- Works with WorkEngine for work item file access (link_spawned_items)

Usage:
    from portal_manager import PortalManager
    from work_engine import WorkEngine
    from governance_layer import GovernanceLayer

    manager = PortalManager(base_path=Path("."))
    manager.create_portal("E2-001", refs_path)
    manager.update_portal("E2-001", {"spawned_from": "INV-001"})
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import yaml

if TYPE_CHECKING:
    from work_engine import WorkEngine

# Constants
WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"


class PortalManager:
    """
    Portal (REFS.md) management for work items.

    Per S2C (Work Item Directory), each work item has a references/REFS.md
    portal that links to other work items, ADRs, and memory concepts.
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        work_engine: Optional["WorkEngine"] = None,
    ):
        """
        Initialize PortalManager.

        Args:
            base_path: Base path for file operations (default: cwd)
            work_engine: Optional WorkEngine for work file operations (needed for link_spawned_items)
        """
        self._base_path = base_path or Path(".")
        self._work_engine = work_engine

    @property
    def active_dir(self) -> Path:
        """Path to active work items directory."""
        return self._base_path / ACTIVE_DIR

    @property
    def archive_dir(self) -> Path:
        """Path to archived work items directory."""
        return self._base_path / ARCHIVE_DIR

    def create_portal(self, id: str, refs_path: Path) -> None:
        """
        Create initial REFS.md portal file.

        Per S2C (Work Item Directory), each work item has a references/REFS.md
        portal that links to other work items, ADRs, and memory concepts.

        Args:
            id: Work item ID
            refs_path: Path to REFS.md
        """
        now = datetime.now()
        content = f"""---
type: portal-index
work_id: {id}
generated: {now.strftime("%Y-%m-%d")}
last_updated: {now.isoformat()}
---
# References: {id}

## Provenance
(no parent)

## Dependencies
(none)

## ADRs
(none)

## Memory Concepts
(none)
"""
        refs_path.write_text(content, encoding="utf-8")

    def update_portal(self, id: str, updates: Dict[str, Any]) -> None:
        """
        Update REFS.md portal file with new data.

        Args:
            id: Work item ID
            updates: Dict with keys: spawned_from, blocks, related, adrs, memory_refs
        """
        refs_path = self.active_dir / id / "references" / "REFS.md"
        if not refs_path.exists():
            return

        # Read current content
        content = refs_path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        fm = yaml.safe_load(parts[1]) or {}
        fm["last_updated"] = datetime.now().isoformat()

        # Build sections
        sections = []
        sections.append(f"# References: {id}")
        sections.append("")

        # Provenance
        sections.append("## Provenance")
        spawned_from = updates.get("spawned_from") or fm.get("spawned_from")
        if spawned_from:
            sections.append(f"- **Spawned from:** [[{spawned_from}]]")
            fm["spawned_from"] = spawned_from
        else:
            sections.append("(no parent)")
        sections.append("")

        # Dependencies
        sections.append("## Dependencies")
        blocks = updates.get("blocks", [])
        related = updates.get("related", [])
        if blocks:
            sections.append("### Blocks")
            for b in blocks:
                sections.append(f"- [[{b}]]")
        if related:
            sections.append("### Related")
            for r in related:
                sections.append(f"- [[{r}]]")
        if not blocks and not related:
            sections.append("(none)")
        sections.append("")

        # ADRs
        sections.append("## ADRs")
        adrs = updates.get("adrs", [])
        if adrs:
            for a in adrs:
                sections.append(f"- [[{a}]]")
        else:
            sections.append("(none)")
        sections.append("")

        # Memory Concepts
        sections.append("## Memory Concepts")
        memory_refs = updates.get("memory_refs", [])
        if memory_refs:
            for m in memory_refs:
                sections.append(f"- [[concept:{m}]]")
        else:
            sections.append("(none)")

        # Write back
        new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_fm}---\n" + "\n".join(sections) + "\n"
        refs_path.write_text(new_content, encoding="utf-8")

    def link_spawned_items(
        self, spawned_by: str, ids: List[str], milestone: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Link multiple work items to a spawning investigation/work item.

        Args:
            spawned_by: ID of spawning item (e.g., "INV-035")
            ids: List of spawned work item IDs
            milestone: Optional milestone to assign

        Returns:
            Dict with 'updated' and 'failed' lists
        """
        if self._work_engine is None:
            # Lazy import to avoid circular dependency
            from governance_layer import GovernanceLayer
            from work_engine import WorkEngine

            governance = GovernanceLayer()
            self._work_engine = WorkEngine(
                governance=governance, base_path=self._base_path
            )

        updated = []
        failed = []

        for work_id in ids:
            path = self._find_work_file(work_id)
            if path is None:
                failed.append(work_id)
                continue

            try:
                content = path.read_text(encoding="utf-8")
                parts = content.split("---", 2)
                if len(parts) < 3:
                    failed.append(work_id)
                    continue

                fm = yaml.safe_load(parts[1]) or {}
                fm["spawned_by"] = spawned_by
                # WORK-014: spawned_by_investigation is DEPRECATED per TRD-WORK-ITEM-UNIVERSAL
                # Legacy field preserved for existing items but not set for new items
                # if spawned_by.startswith("INV-"):
                #     fm["spawned_by_investigation"] = spawned_by
                if milestone:
                    fm["milestone"] = milestone

                new_fm = yaml.dump(
                    fm, default_flow_style=False, sort_keys=False, allow_unicode=True
                )
                path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")

                # Update portal with spawned_from
                self.update_portal(work_id, {"spawned_from": spawned_by})

                updated.append(work_id)
            except Exception:
                failed.append(work_id)

        return {"updated": updated, "failed": failed}

    def _find_work_file(self, id: str) -> Optional[Path]:
        """Find WORK.md for given ID."""
        # Directory structure (primary)
        dir_path = self.active_dir / id / "WORK.md"
        if dir_path.exists():
            return dir_path

        # Check archive
        archive_path = self.archive_dir / id / "WORK.md"
        if archive_path.exists():
            return archive_path

        return None
