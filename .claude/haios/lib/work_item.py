# generated: 2025-12-23
# System Auto: last updated on: 2026-01-17T15:57:51
"""
DEPRECATED: This module is deprecated as of E2-298 (Session 201).
Use WorkEngine from .claude/haios/modules/work_engine.py instead.

Migration guide:
- find_work_file(id) -> engine.get_work(id).path
- update_work_file_status(path, status) -> engine.close(id) or engine.transition()
- update_work_file_closed_date(path, date) -> handled by engine.close(id)
- move_work_file_to_archive(path) -> engine.archive(id)
- update_node(path, node) -> engine.transition(id, node)
- add_document_link(path, type, path) -> engine.add_document_link(id, type, path)

This module remains for backward compatibility with hooks that may reference it.
Do not add new functionality here - use WorkEngine instead.

---
Original docstring (E2-152):
Work item file operations for /close command.
Provides helper functions for closing work items stored as files
in docs/work/active/, moving them to docs/work/archive/ on closure.
"""
from pathlib import Path
from typing import Optional
import re

WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"


def find_work_file(backlog_id: str) -> Optional[Path]:
    """
    Find work file for a backlog ID.

    E2-212: Supports both directory structure (new) and flat file (legacy).

    Args:
        backlog_id: Work item ID (e.g., "E2-152")

    Returns:
        Path to work file if found, None otherwise
    """
    # E2-212: Try directory structure first (new)
    dir_path = ACTIVE_DIR / backlog_id / "WORK.md"
    if dir_path.exists():
        return dir_path

    # Fall back to flat file pattern (legacy/archive)
    pattern = f"WORK-{backlog_id}-*.md"
    matches = list(ACTIVE_DIR.glob(pattern))
    return matches[0] if matches else None


def update_work_file_status(path: Path, new_status: str) -> None:
    """
    Update status field in work file frontmatter.

    Args:
        path: Path to work file
        new_status: New status value (e.g., "complete")
    """
    content = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'^status: .*$',
        f'status: {new_status}',
        content,
        flags=re.MULTILINE
    )
    path.write_text(updated, encoding="utf-8")


def update_work_file_closed_date(path: Path, date: str) -> None:
    """
    Update closed field in work file frontmatter.

    Args:
        path: Path to work file
        date: Date string (e.g., "2025-12-23")
    """
    content = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'^closed: .*$',
        f'closed: {date}',
        content,
        flags=re.MULTILINE
    )
    path.write_text(updated, encoding="utf-8")


def move_work_file_to_archive(path: Path) -> Path:
    """
    Move work file from active/ to archive/.

    Args:
        path: Path to work file in active/

    Returns:
        New path in archive/
    """
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    new_path = ARCHIVE_DIR / path.name
    path.rename(new_path)
    return new_path


def update_node(path: Path, new_node: str) -> None:
    """
    Update work file to new DAG node with history tracking.

    Updates current_node field and appends new entry to node_history,
    marking the previous entry's exited timestamp.

    Args:
        path: Path to work file
        new_node: Target node (backlog, plan, implement, check, done)
    """
    import yaml
    from datetime import datetime

    content = path.read_text(encoding="utf-8")
    # Split frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {path}")

    fm = yaml.safe_load(parts[1])
    now = datetime.now().isoformat()

    # Mark previous node as exited
    if fm.get("node_history"):
        fm["node_history"][-1]["exited"] = now

    # Update current node
    fm["current_node"] = new_node

    # Append new history entry
    fm.setdefault("node_history", []).append({
        "node": new_node,
        "entered": now,
        "exited": None
    })

    # Rebuild content
    new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
    path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")


def add_document_link(path: Path, doc_type: str, doc_path: str) -> None:
    """
    Link a document to the work file.

    Updates both cycle_docs (current node's doc) and documents section.

    Args:
        path: Path to work file
        doc_type: Document type (plan, investigation, checkpoint)
        doc_path: Path to the document being linked
    """
    import yaml

    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {path}")

    fm = yaml.safe_load(parts[1])

    # Map doc_type to documents key (plural)
    type_map = {"plan": "plans", "investigation": "investigations", "checkpoint": "checkpoints"}
    docs_key = type_map.get(doc_type, f"{doc_type}s")

    # Update documents section
    fm.setdefault("documents", {}).setdefault(docs_key, [])
    if doc_path not in fm["documents"][docs_key]:
        fm["documents"][docs_key].append(doc_path)

    # Update cycle_docs for current node
    current_node = fm.get("current_node", "unknown")
    fm.setdefault("cycle_docs", {})[current_node] = doc_path

    new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
    path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")


def batch_update_fields(ids: list, **kwargs) -> dict:
    """
    Batch update frontmatter fields on multiple work items.

    Args:
        ids: List of work item IDs (e.g., ["E2-180", "E2-181"])
        **kwargs: Fields to update (e.g., spawned_by="INV-035", milestone="M8-SkillArch")

    Returns:
        Dict with 'updated' and 'failed' lists
    """
    import yaml

    results = {"updated": [], "failed": []}

    for work_id in ids:
        path = find_work_file(work_id)
        if not path:
            results["failed"].append((work_id, "not found"))
            continue

        try:
            content = path.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                results["failed"].append((work_id, "invalid frontmatter"))
                continue

            fm = yaml.safe_load(parts[1])

            # Update each field
            for key, value in kwargs.items():
                fm[key] = value

            new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
            path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")
            results["updated"].append(work_id)

        except Exception as e:
            results["failed"].append((work_id, str(e)))

    return results


def link_spawned_items(spawned_by: str, ids: list, milestone: str = None) -> dict:
    """
    Link multiple work items to a spawning investigation/work item.

    Convenience wrapper around batch_update_fields for common spawn-linking pattern.

    Args:
        spawned_by: ID of spawning item (e.g., "INV-035")
        ids: List of spawned work item IDs
        milestone: Optional milestone to assign

    Returns:
        Dict with 'updated' and 'failed' lists
    """
    fields = {
        "spawned_by": spawned_by,
        "spawned_by_investigation": spawned_by if spawned_by.startswith("INV-") else None
    }
    if milestone:
        fields["milestone"] = milestone

    return batch_update_fields(ids, **fields)
