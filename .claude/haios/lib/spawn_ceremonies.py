# generated: 2026-02-12
"""
Spawn ceremony execution and event logging (CH-017, WORK-137).

Events stored in .claude/haios/governance-events.jsonl (append-only).

Event Types:
- SpawnWork: Logged when spawn ceremony creates a child work item

Ceremonies:
- Spawn: Create child work item linked to parent with bidirectional lineage

Usage:
    from spawn_ceremonies import execute_spawn
    result = execute_spawn(engine, "WORK-001", "Follow-on task")
"""
import json
import sys
import yaml
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

# Module-level sys.path for sibling imports
_lib_dir = str(Path(__file__).parent)
if _lib_dir not in sys.path:
    sys.path.insert(0, _lib_dir)

EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"


def log_spawn_ceremony(
    parent_work_id: str,
    new_work_id: str,
    title: str,
    work_type: str = "implementation",
    rationale: Optional[str] = None,
    agent: Optional[str] = None,
) -> dict:
    """Log spawn ceremony event to governance-events.jsonl.

    Args:
        parent_work_id: ID of parent work item
        new_work_id: ID of newly created child work item
        title: Title of the new work item
        work_type: Type of the new work item
        rationale: Optional reason for the spawn
        agent: Optional agent name performing the ceremony

    Returns:
        The logged event dict
    """
    event = {
        "type": "SpawnWork",
        "ceremony": "spawn-work",
        "parent_work_id": parent_work_id,
        "new_work_id": new_work_id,
        "title": title,
        "work_type": work_type,
        "timestamp": datetime.now().isoformat(),
    }
    if rationale:
        event["rationale"] = rationale
    if agent:
        event["agent"] = agent
    _append_event(event)
    return event


def execute_spawn(
    work_engine: Any,
    parent_work_id: str,
    title: str,
    work_type: str = "implementation",
    traces_to: Optional[List[str]] = None,
    rationale: Optional[str] = None,
    agent: Optional[str] = None,
    _override_work_id: Optional[str] = None,
) -> dict:
    """Execute spawn ceremony: create child work item linked to parent.

    Steps:
    1. Validate parent exists
    2. Get next work ID
    3. Scaffold child via scaffold_template (with spawned_by=parent)
    4. Create REFS.md portal for child (structural parity with WorkEngine.create_work)
    5. Update parent frontmatter with spawned_children
    6. Log SpawnWork event with side effects on ceremony context

    Args:
        work_engine: WorkEngine instance
        parent_work_id: ID of parent work item to spawn from
        title: Title for the new work item
        work_type: Type of the new work item (default: implementation)
        traces_to: Optional L4 requirement IDs
        rationale: Optional reason for the spawn
        agent: Optional agent name performing the ceremony

    Returns:
        {success: True, new_work_id, parent_work_id} on success,
        or {success: False, error, parent_work_id} on failure.
    """
    from scaffold import get_next_work_id, scaffold_template

    # 1. Validate parent
    parent = work_engine.get_work(parent_work_id)
    if parent is None:
        return {
            "success": False,
            "error": f"Parent {parent_work_id} not found",
            "parent_work_id": parent_work_id,
        }

    # 2. Get next ID (override for test isolation, else scaffold's global counter)
    new_work_id = _override_work_id or get_next_work_id()

    try:
        with _ceremony_context_safe("spawn-work") as ctx:
            # 3. Scaffold child — use absolute path via engine's base_path
            abs_output = (
                work_engine._base_path / "docs" / "work" / "active"
                / new_work_id / "WORK.md"
            )
            scaffold_template(
                "work_item",
                output_path=str(abs_output),
                backlog_id=new_work_id,
                title=title,
                variables={"SPAWNED_BY": parent_work_id, "TYPE": work_type},
            )
            if ctx:
                ctx.log_side_effect("scaffold_child", {
                    "new_work_id": new_work_id,
                    "parent": parent_work_id,
                })

            # 4. Create REFS.md portal for child (A8: structural parity)
            refs_dir = (
                work_engine._base_path / "docs" / "work" / "active"
                / new_work_id / "references"
            )
            refs_dir.mkdir(parents=True, exist_ok=True)
            work_engine._create_portal(new_work_id, refs_dir / "REFS.md")

            # 5. Update parent spawned_children
            _update_parent_children(work_engine, parent_work_id, new_work_id)
            if ctx:
                ctx.log_side_effect("update_parent_children", {
                    "parent": parent_work_id,
                    "child": new_work_id,
                })

            # 6. Log event
            log_spawn_ceremony(
                parent_work_id=parent_work_id,
                new_work_id=new_work_id,
                title=title,
                work_type=work_type,
                rationale=rationale,
                agent=agent,
            )
            if ctx:
                ctx.log_side_effect("spawn_event_logged", {
                    "event_type": "SpawnWork",
                })

        return {
            "success": True,
            "new_work_id": new_work_id,
            "parent_work_id": parent_work_id,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "parent_work_id": parent_work_id,
        }


def _update_parent_children(
    work_engine: Any, parent_id: str, child_id: str
) -> None:
    """Append child_id to parent's spawned_children field in frontmatter.

    Note: Writes directly to WORK.md (bypasses WorkEngine._write_work_file).
    This follows the precedent set by PortalManager.link_spawned_items() and
    WorkEngine._set_closed_date() for field-specific updates. The spawned_children
    field survives subsequent _write_work_file calls because that method reads
    existing frontmatter and only overwrites specific keys.
    """
    parent = work_engine.get_work(parent_id)
    path = parent.path
    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {parent_id}")
    fm = yaml.safe_load(parts[1]) or {}
    children = fm.get("spawned_children", []) or []
    if child_id not in children:
        children.append(child_id)
    fm["spawned_children"] = children
    fm["last_updated"] = datetime.now().isoformat()
    new_fm = yaml.dump(
        fm, default_flow_style=False, sort_keys=False, allow_unicode=True
    )
    path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")


@contextmanager
def _ceremony_context_safe(name: str):
    """Ceremony context wrapper matching queue_ceremonies.py pattern.

    Handles: ImportError (no governance module), already-inside-context
    (reuse outer context to avoid CeremonyNestingError).
    """
    try:
        from governance_layer import ceremony_context, in_ceremony_context

        if in_ceremony_context():
            yield None  # Already inside ceremony — no-op (avoid nesting)
        else:
            with ceremony_context(name) as ctx:
                yield ctx
    except ImportError:
        yield None


def _append_event(event: dict) -> None:
    """Append event to JSONL file."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
