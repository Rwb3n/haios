# generated: 2025-12-21
# System Auto: last updated on: 2026-01-25T21:27:48
"""Core status module for HAIOS plugin.

E2-120 Phase 2a: Core functions for haios-status-slim.json generation.
E2-125: Full status functions for haios-status.json generation.

Core functions (9) - for slim status:
1. get_agents() - Discover agents from .claude/agents/
2. get_commands() - Discover commands from .claude/commands/
3. get_skills() - Discover skills from .claude/skills/
4. get_memory_stats() - Get concept/entity counts from database
5. get_backlog_stats() - Parse backlog.md for active counts
6. get_session_delta() - Compare last 2 checkpoints for momentum
7. get_milestone_progress() - Calculate milestone completion %
8. get_blocked_items() - Detect blocked_by dependencies
9. generate_slim_status() - Main orchestrator for slim status

Full status functions (8) - E2-125 complete:
10. get_valid_templates() - Template definitions from validate.py registry
11. get_live_files() - Scan governed paths for files
12. get_outstanding_items() - Items with status != complete/closed
13. get_stale_items() - Files not updated within threshold
14. get_workspace_summary() - Aggregate counts by template/status
15. check_alignment() - Match files to backlog items
16. get_spawn_map() - Track spawned_by relationships
17. generate_full_status() - Complete haios-status.json
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Project root is 2 levels up from .claude/lib/
PROJECT_ROOT = Path(__file__).parent.parent.parent


def _iter_work_files(directory: Path):
    """Iterate over work files in a directory (E2-212 dual pattern support).

    Yields work file paths from both:
    - Directory structure: {id}/WORK.md (new)
    - Flat files: WORK-{id}-*.md (legacy)

    Args:
        directory: Directory to scan (e.g., docs/work/active/)

    Yields:
        Path objects for each work file found.
    """
    if not directory.exists():
        return

    # E2-212: Check for directory structure first
    for subdir in directory.iterdir():
        if subdir.is_dir():
            work_md = subdir / "WORK.md"
            if work_md.exists():
                yield work_md

    # Fall back to flat file pattern (legacy)
    for file_path in directory.glob("WORK-*.md"):
        yield file_path


def get_agents() -> list[str]:
    """Discover agents from .claude/agents/ directory.

    Returns:
        Sorted list of agent names (from YAML frontmatter 'name' field).
    """
    agents_dir = PROJECT_ROOT / ".claude" / "agents"
    agents = []

    if not agents_dir.exists():
        return agents

    for file in agents_dir.glob("*.md"):
        # Skip README
        if file.name.lower() == "readme.md":
            continue

        content = file.read_text(encoding="utf-8", errors="ignore")

        # Parse YAML frontmatter for name field
        match = re.search(r"^---\s*\n.*?name:\s*([^\n]+)", content, re.DOTALL)
        if match:
            agent_name = match.group(1).strip()
            if agent_name:
                agents.append(agent_name)

    return sorted(agents)


def get_commands() -> list[str]:
    """Discover commands from .claude/commands/ directory.

    Returns:
        Sorted list of command names (prefixed with /).
    """
    commands_dir = PROJECT_ROOT / ".claude" / "commands"
    commands = []

    if not commands_dir.exists():
        return commands

    for file in commands_dir.glob("*.md"):
        # Skip README
        if file.name.lower() == "readme.md":
            continue

        # Command name is filename without extension, prefixed with /
        cmd_name = "/" + file.stem
        commands.append(cmd_name)

    return sorted(commands)


def get_skills() -> list[str]:
    """Discover skills from .claude/skills/ directory.

    Skills are directories containing SKILL.md with name in frontmatter.

    Returns:
        Sorted list of skill names.
    """
    skills_dir = PROJECT_ROOT / ".claude" / "skills"
    skills = []

    if not skills_dir.exists():
        return skills

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8", errors="ignore")

        # Parse YAML frontmatter for name field
        match = re.search(r"^---\s*\n.*?name:\s*([^\n]+)", content, re.DOTALL)
        if match:
            skill_name = match.group(1).strip()
            if skill_name:
                skills.append(skill_name)

    return sorted(skills)


def get_memory_stats() -> Optional[dict[str, int]]:
    """Get memory statistics from database.

    Returns:
        Dict with 'concepts', 'entities' counts, or None if unavailable.
    """
    try:
        from database import DatabaseManager

        db_path = PROJECT_ROOT / "haios_memory.db"
        if not db_path.exists():
            return None

        db = DatabaseManager(str(db_path))
        stats = db.get_stats()
        return {
            "concepts": stats.get("concepts", 0),
            "entities": stats.get("entities", 0),
        }
    except Exception:
        return None


def get_backlog_stats() -> dict[str, Any]:
    """Parse backlog.md for active item statistics.

    Returns:
        Dict with active_count, by_priority, last_session.
    """
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"
    stats = {
        "active_count": 0,
        "last_session": 0,
        "by_priority": {"urgent": 0, "high": 0, "medium": 0, "low": 0},
    }

    if not backlog_path.exists():
        return stats

    content = backlog_path.read_text(encoding="utf-8", errors="ignore")

    # Count by priority
    stats["by_priority"]["urgent"] = len(re.findall(r"\[URGENT\]", content))
    stats["by_priority"]["high"] = len(re.findall(r"\[HIGH\]", content))
    stats["by_priority"]["medium"] = len(re.findall(r"\[MEDIUM\]", content))
    stats["by_priority"]["low"] = len(re.findall(r"\[LOW\]", content))

    # Total active (non-closed)
    closed_count = len(re.findall(r"\[CLOSED\]", content))
    total_items = sum(stats["by_priority"].values())
    stats["active_count"] = total_items - closed_count

    # Extract session numbers
    session_matches = re.findall(r"Session[:\s]*(\d+)", content)
    if session_matches:
        sessions = [int(s) for s in session_matches]
        stats["last_session"] = max(sessions)

    return stats


def _parse_checkpoint_yaml(filepath: Path) -> Optional[dict]:
    """Parse YAML frontmatter from checkpoint file.

    Returns:
        Dict with session, date, backlog_ids or None.
    """
    if not filepath.exists():
        return None

    content = filepath.read_text(encoding="utf-8", errors="ignore")

    # Extract YAML frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    yaml_content = match.group(1)

    data = {
        "session": None,
        "date": None,
        "backlog_ids": [],
    }

    # Extract session number
    session_match = re.search(r"session:\s*(\d+)", yaml_content)
    if session_match:
        data["session"] = int(session_match.group(1))

    # Extract date
    date_match = re.search(r"date:\s*(\d{4}-\d{2}-\d{2})", yaml_content)
    if date_match:
        data["date"] = date_match.group(1)

    # Extract backlog_ids array
    ids_match = re.search(r"backlog_ids:\s*\[([^\]]*)\]", yaml_content)
    if ids_match:
        ids_str = ids_match.group(1)
        ids = [s.strip().strip("\"'") for s in ids_str.split(",") if s.strip()]
        data["backlog_ids"] = ids

    return data


def get_session_delta() -> dict[str, Any]:
    """Compare last 2 checkpoints to calculate momentum delta.

    Returns:
        Dict with prior_session, current_session, completed, added, etc.
    """
    checkpoints_dir = PROJECT_ROOT / "docs" / "checkpoints"
    delta = {
        "prior_session": None,
        "current_session": None,
        "prior_date": None,
        "completed": [],
        "completed_count": 0,
        "added": [],
        "added_count": 0,
        "milestone_delta": None,
    }

    if not checkpoints_dir.exists():
        return delta

    # Get checkpoint files sorted by name (includes date and session)
    checkpoint_files = [
        f
        for f in sorted(checkpoints_dir.glob("*.md"), reverse=True)
        if f.name.lower() != "readme.md" and "SESSION-" in f.name.upper()
    ]

    if len(checkpoint_files) < 2:
        return delta

    current_file = checkpoint_files[0]
    prior_file = checkpoint_files[1]

    current_data = _parse_checkpoint_yaml(current_file)
    prior_data = _parse_checkpoint_yaml(prior_file)

    if not current_data or not prior_data:
        return delta

    delta["current_session"] = current_data.get("session")
    delta["prior_session"] = prior_data.get("session")
    delta["prior_date"] = prior_data.get("date")

    # Calculate added items: in current but not in prior
    current_ids = set(current_data.get("backlog_ids", []))
    prior_ids = set(prior_data.get("backlog_ids", []))

    added = list(current_ids - prior_ids)
    delta["added"] = added
    delta["added_count"] = len(added)

    # Calculate completed items (items that were in prior and now complete)
    completed = _find_completed_items(prior_ids)
    delta["completed"] = completed
    delta["completed_count"] = len(completed)

    return delta


def _find_completed_items(item_ids: set[str]) -> list[str]:
    """Find items from set that are now complete.

    Checks plan status and backlog [CLOSED] markers.
    """
    completed = []
    plans_dir = PROJECT_ROOT / "docs" / "plans"
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"

    backlog_content = ""
    if backlog_path.exists():
        backlog_content = backlog_path.read_text(encoding="utf-8", errors="ignore")

    for item_id in item_ids:
        if not item_id:
            continue

        is_complete = False

        # Check plan status
        for plan_file in plans_dir.glob(f"PLAN-{item_id}*.md"):
            content = plan_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"status:\s*(complete|completed|done)", content, re.IGNORECASE):
                is_complete = True
                break

        # Check backlog status
        if not is_complete and backlog_content:
            pattern = rf"{re.escape(item_id)}[^\[]*\[(COMPLETE|CLOSED)\]"
            if re.search(pattern, backlog_content, re.IGNORECASE):
                is_complete = True

        if is_complete and item_id not in completed:
            completed.append(item_id)

    return completed


def get_milestone_progress(existing_milestones: dict) -> dict[str, Any]:
    """Calculate milestone progress from backlog and plan statuses.

    Args:
        existing_milestones: Dict of milestone data from status file.

    Returns:
        Updated milestone dict with progress percentages.
    """
    if not existing_milestones:
        return {}

    result = {}
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"
    plans_dir = PROJECT_ROOT / "docs" / "plans"

    backlog_content = ""
    if backlog_path.exists():
        backlog_content = backlog_path.read_text(encoding="utf-8", errors="ignore")

    for key, milestone in existing_milestones.items():
        items = list(milestone.get("items", []))
        # Start with complete items from work file discovery (E2-173)
        complete_items = list(milestone.get("complete", []))

        for item in items:
            if item in complete_items:
                continue  # Already marked complete from work file

            # Check if item is closed in backlog
            if re.search(rf"{re.escape(item)}.*\[CLOSED\]", backlog_content):
                complete_items.append(item)
                continue

            # Check plan status
            for plan_file in plans_dir.glob(f"PLAN-{item}*.md"):
                content = plan_file.read_text(encoding="utf-8", errors="ignore")
                if re.search(r"status:\s*(complete|completed|done)", content, re.IGNORECASE):
                    if item not in complete_items:
                        complete_items.append(item)
                    break

        total = len(items)
        completed_count = len(complete_items)
        progress = round((completed_count / total) * 100) if total > 0 else 0

        prior_progress = milestone.get("progress", 0)
        prior_complete = list(milestone.get("complete", []))

        # Find delta source (newly completed item)
        delta_source = None
        if progress > prior_progress:
            for c in complete_items:
                if c not in prior_complete:
                    delta_source = c
                    break

        result[key] = {
            "name": milestone.get("name", key),
            "items": items,
            "complete": complete_items,
            "progress": progress,
            "prior_progress": prior_progress,
            "delta_source": delta_source,
        }

    return result


def get_blocked_items() -> list[dict[str, Any]]:
    """Detect items with unresolved blocked_by dependencies.

    Scans plans for blocked_by field and checks if blockers are complete.

    Returns:
        List of dicts with 'id' and 'blocked_by' keys.
    """
    blocked = []
    plans_dir = PROJECT_ROOT / "docs" / "plans"

    if not plans_dir.exists():
        return blocked

    for plan_file in plans_dir.glob("*.md"):
        content = plan_file.read_text(encoding="utf-8", errors="ignore")

        # Parse YAML frontmatter
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            continue

        yaml_content = match.group(1)

        # Check if has blocked_by field
        blocked_by_match = re.search(r"blocked_by:\s*\[([^\]]+)\]", yaml_content)
        if not blocked_by_match:
            continue

        blockers_str = blocked_by_match.group(1)
        blockers = [s.strip().strip("\"'") for s in blockers_str.split(",") if s.strip()]

        # Get this item's ID
        backlog_id_match = re.search(r"backlog_id:\s*(\S+)", yaml_content)
        backlog_id = backlog_id_match.group(1).strip() if backlog_id_match else None

        status_match = re.search(r"status:\s*(\S+)", yaml_content)
        file_status = status_match.group(1).strip() if status_match else "unknown"

        # Skip if already complete
        if file_status.lower() in ("complete", "completed", "done", "closed"):
            continue

        # Check if any blockers are still incomplete
        unresolved_blockers = []
        for blocker in blockers:
            if not blocker:
                continue

            blocker_complete = False
            for blocker_plan in plans_dir.glob(f"PLAN-{blocker}*.md"):
                bp_content = blocker_plan.read_text(encoding="utf-8", errors="ignore")
                if re.search(r"status:\s*(complete|completed|done)", bp_content, re.IGNORECASE):
                    blocker_complete = True
                    break

            if not blocker_complete:
                unresolved_blockers.append(blocker)

        if unresolved_blockers and backlog_id:
            blocked.append({
                "id": backlog_id,
                "blocked_by": unresolved_blockers,
            })

    return blocked


# =============================================================================
# E2-125: Full Status Functions (8 new functions)
# =============================================================================


def get_valid_templates() -> list[dict[str, Any]]:
    """Get template definitions by wrapping validate.py's registry.

    Reuses get_template_registry() from validate.py (E2-129 overlap fix).

    Returns:
        List of template dicts with name, required_fields, allowed_status, etc.
    """
    try:
        from validate import get_template_registry

        registry = get_template_registry()
        templates = []
        for name, rules in registry.items():
            templates.append({
                "name": name,
                "required_fields": rules.get("required_fields", []),
                "optional_fields": rules.get("optional_fields", []),
                "allowed_status": rules.get("allowed_status", []),
                "expected_sections": rules.get("expected_sections", []),
            })
        return templates
    except ImportError:
        return []


def get_live_files() -> list[dict[str, Any]]:
    """Scan governed paths for files with YAML frontmatter.

    Governed paths: docs/checkpoints/, docs/plans/, docs/investigations/, docs/ADR/

    Returns:
        List of file dicts with path, template, status, date, etc.
    """
    governed_paths = [
        PROJECT_ROOT / "docs" / "checkpoints",
        PROJECT_ROOT / "docs" / "plans",
        PROJECT_ROOT / "docs" / "investigations",
        PROJECT_ROOT / "docs" / "ADR",
        PROJECT_ROOT / "docs" / "reports",
        PROJECT_ROOT / "docs" / "work" / "active",
        PROJECT_ROOT / "docs" / "work" / "blocked",
        PROJECT_ROOT / "docs" / "work" / "archive",
    ]

    files = []
    for dir_path in governed_paths:
        if not dir_path.exists():
            continue

        for file_path in dir_path.glob("*.md"):
            if file_path.name.lower() == "readme.md":
                continue

            try:
                content = file_path.read_text(encoding="utf-8-sig")
                metadata = _parse_yaml_frontmatter(content)

                rel_path = str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
                files.append({
                    "path": rel_path,
                    "template": metadata.get("template"),
                    "status": metadata.get("status"),
                    "date": metadata.get("date"),
                    "last_updated": metadata.get("last_updated"),
                    "backlog_id": metadata.get("backlog_id"),
                    "spawned_by": metadata.get("spawned_by"),
                })
            except Exception:
                continue

    return files


def _parse_yaml_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter from content."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    yaml_content = match.group(1)
    result = {}

    for line in yaml_content.split("\n"):
        m = re.match(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()
            # Remove quotes
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            result[key] = value

    return result


def get_outstanding_items() -> list[dict[str, Any]]:
    """Find items with status != complete/closed.

    Returns:
        List of item dicts with id/path, status, priority.
    """
    live_files = get_live_files()
    complete_statuses = {"complete", "completed", "closed", "done", "archived"}

    outstanding = []
    for f in live_files:
        status = (f.get("status") or "").lower()
        if status and status not in complete_statuses:
            outstanding.append({
                "path": f["path"],
                "id": f.get("backlog_id"),
                "status": f.get("status"),
                "template": f.get("template"),
            })

    return outstanding


def get_stale_items(days: int = 30) -> list[dict[str, Any]]:
    """Find files not updated within threshold days.

    Args:
        days: Staleness threshold in days.

    Returns:
        List of stale items with path, last_updated, days_stale.
    """
    from datetime import datetime, timedelta

    live_files = get_live_files()
    threshold = datetime.now() - timedelta(days=days)
    stale = []

    for f in live_files:
        last_updated = f.get("last_updated") or f.get("date")
        if not last_updated:
            continue

        try:
            # Parse date (handle various formats)
            if "T" in str(last_updated):
                dt = datetime.fromisoformat(str(last_updated).replace("Z", ""))
            else:
                dt = datetime.strptime(str(last_updated)[:10], "%Y-%m-%d")

            if dt < threshold:
                days_stale = (datetime.now() - dt).days
                stale.append({
                    "path": f["path"],
                    "last_updated": str(last_updated),
                    "days_stale": days_stale,
                })
        except Exception:
            continue

    return stale


def get_workspace_summary() -> dict[str, Any]:
    """Aggregate counts by template type, status, staleness.

    Returns:
        Dict with total_files, by_template, by_status, stale_count.
    """
    live_files = get_live_files()
    stale_items = get_stale_items()

    by_template = {}
    by_status = {}

    for f in live_files:
        template = f.get("template") or "unknown"
        status = f.get("status") or "unknown"

        by_template[template] = by_template.get(template, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

    return {
        "total_files": len(live_files),
        "by_template": by_template,
        "by_status": by_status,
        "stale_count": len(stale_items),
    }


def check_alignment() -> dict[str, Any]:
    """Match files to backlog items, detect orphans.

    Returns:
        Dict with aligned, orphan_files, missing_files.
    """
    live_files = get_live_files()

    aligned = []
    orphan_files = []

    for f in live_files:
        backlog_id = f.get("backlog_id")
        if backlog_id:
            aligned.append({
                "path": f["path"],
                "backlog_id": backlog_id,
            })
        else:
            # Plans without backlog_id are orphans
            if f.get("template") == "implementation_plan":
                orphan_files.append(f["path"])

    return {
        "aligned": aligned,
        "orphan_files": orphan_files,
    }


def get_spawn_map() -> dict[str, list[str]]:
    """Track spawned_by relationships from frontmatter.

    Returns:
        Dict mapping parent IDs to list of spawned child IDs.
    """
    live_files = get_live_files()
    spawn_map = {}

    for f in live_files:
        spawned_by = f.get("spawned_by")
        backlog_id = f.get("backlog_id")

        if spawned_by and backlog_id:
            parent = str(spawned_by).strip()
            if parent not in spawn_map:
                spawn_map[parent] = []
            if backlog_id not in spawn_map[parent]:
                spawn_map[parent].append(backlog_id)

    return spawn_map


def get_work_items() -> list[dict[str, Any]]:
    """Scan docs/work/ for work item files.

    Returns:
        List of work item dicts with id, title, status, current_node, priority.
    """
    work_dirs = [
        PROJECT_ROOT / "docs" / "work" / "active",
        PROJECT_ROOT / "docs" / "work" / "blocked",
        PROJECT_ROOT / "docs" / "work" / "archive",
    ]

    items = []
    for dir_path in work_dirs:
        # E2-212: Use dual-pattern iterator
        for file_path in _iter_work_files(dir_path):
            try:
                content = file_path.read_text(encoding="utf-8-sig")
                metadata = _parse_yaml_frontmatter(content)

                items.append({
                    "id": metadata.get("id"),
                    "title": metadata.get("title"),
                    "status": metadata.get("status"),
                    "current_node": metadata.get("current_node"),
                    "priority": metadata.get("priority"),
                    "path": str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                })
            except Exception:
                continue

    return items


def get_active_work_cycle() -> Optional[dict[str, Any]]:
    """Find the currently active work item and its cycle state.

    Scans docs/work/active/ for work items with current_node != 'backlog'.
    Also checks associated plan/investigation for lifecycle_phase.

    Returns:
        Dict with id, title, current_node, cycle_type, lifecycle_phase, or None.
    """
    active_dir = PROJECT_ROOT / "docs" / "work" / "active"
    plans_dir = PROJECT_ROOT / "docs" / "plans"
    inv_dir = PROJECT_ROOT / "docs" / "investigations"

    if not active_dir.exists():
        return None

    # Find work items that are actively being worked (not in backlog)
    # E2-212: Use dual-pattern iterator
    for file_path in _iter_work_files(active_dir):
        try:
            content = file_path.read_text(encoding="utf-8-sig")
            metadata = _parse_yaml_frontmatter(content)

            current_node = metadata.get("current_node", "backlog")

            # Skip items still in backlog - not actively being worked
            if current_node == "backlog":
                continue

            item_id = metadata.get("id")
            if not item_id:
                continue

            # Determine cycle type from ID prefix or associated documents
            cycle_type = "implementation"  # default
            lifecycle_phase = None

            # Check for associated plan
            for plan_file in plans_dir.glob(f"PLAN-{item_id}*.md"):
                plan_content = plan_file.read_text(encoding="utf-8-sig")
                plan_meta = _parse_yaml_frontmatter(plan_content)
                lifecycle_phase = plan_meta.get("lifecycle_phase")
                cycle_type = "implementation"
                break

            # Check for investigation type (type field OR legacy INV-* prefix)
            # WORK-014: Type field takes precedence over ID prefix
            work_type = metadata.get("type", "")
            if work_type == "investigation" or item_id.startswith("INV-"):
                cycle_type = "investigation"
                for inv_file in inv_dir.glob(f"INVESTIGATION-{item_id}*.md"):
                    inv_content = inv_file.read_text(encoding="utf-8-sig")
                    inv_meta = _parse_yaml_frontmatter(inv_content)
                    lifecycle_phase = inv_meta.get("lifecycle_phase")
                    break

            return {
                "id": item_id,
                "title": metadata.get("title"),
                "current_node": current_node,
                "cycle_type": cycle_type,
                "lifecycle_phase": lifecycle_phase,
            }

        except Exception:
            continue

    return None


def generate_full_status() -> dict[str, Any]:
    """Orchestrate all functions into complete haios-status.json.

    Returns:
        Full status dict with all sections.
    """
    # Get slim status as base
    slim = generate_slim_status()

    # Add full status sections
    templates = get_valid_templates()
    live_files = get_live_files()
    outstanding = get_outstanding_items()
    stale = get_stale_items()
    workspace = get_workspace_summary()
    alignment = check_alignment()
    spawn_map = get_spawn_map()

    # Add full milestones structure for plan_tree.py compatibility
    existing_milestones = _load_existing_milestones()
    milestones = get_milestone_progress(existing_milestones)

    full = {
        **slim,
        "milestones": milestones,  # Full milestone breakdown for plan_tree.py
        "templates": templates,
        "live_files": live_files,
        "outstanding_items": outstanding,
        "stale_items": stale,
        "workspace": workspace,
        "alignment": alignment,
        "spawn_map": spawn_map,
    }

    return full


def generate_slim_status() -> dict[str, Any]:
    """Generate slim status structure for haios-status-slim.json.

    This is the main orchestrator that calls all core functions.

    Returns:
        Dict matching haios-status-slim.json structure.
    """
    # Gather data from all sources
    agents = get_agents()
    commands = get_commands()
    skills = get_skills()
    memory_stats = get_memory_stats() or {"concepts": 0, "entities": 0}
    backlog_stats = get_backlog_stats()
    session_delta = get_session_delta()
    blocked_items = get_blocked_items()

    # Get active work items (HIGH and URGENT from backlog)
    active_work = _get_active_work()

    # Get active work cycle context (E2-118)
    work_cycle = get_active_work_cycle()

    # Load existing milestones from status file
    existing_milestones = _load_existing_milestones()
    milestones = get_milestone_progress(existing_milestones)

    # Select current milestone (highest progress non-complete)
    milestone_data = _select_current_milestone(milestones)

    # Calculate milestone delta string
    milestone_delta_str = None
    if milestone_data and session_delta.get("prior_session"):
        prior_prog = milestone_data.get("prior_progress", 0)
        curr_prog = milestone_data.get("progress", 0)
        if curr_prog != prior_prog:
            mdelta = curr_prog - prior_prog
            sign = "+" if mdelta > 0 else ""
            milestone_delta_str = f"{sign}{mdelta}%"

    # Build session_delta for slim
    session_delta_slim = None
    if session_delta.get("prior_session"):
        session_delta_slim = {
            "prior_session": session_delta["prior_session"],
            "current_session": session_delta["current_session"],
            "prior_date": session_delta["prior_date"],
            "completed": session_delta["completed"],
            "completed_count": session_delta["completed_count"],
            "added": session_delta["added"],
            "added_count": session_delta["added_count"],
            "milestone_delta": milestone_delta_str,
        }

    # Build blocked_items dict (keyed by ID for JSON)
    blocked_dict = {item["id"]: item["blocked_by"] for item in blocked_items} if blocked_items else {}

    slim = {
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "milestone": milestone_data,
        "session_delta": session_delta_slim,
        "work_cycle": work_cycle,  # E2-118: Active work cycle context
        "session_state": {  # E2-286: Session-level cycle tracking
            "active_cycle": None,       # e.g., "implementation-cycle"
            "current_phase": None,      # e.g., "DO", "CHECK"
            "work_id": None,            # e.g., "E2-286"
            "entered_at": None,         # ISO8601 timestamp
            "active_queue": None,       # E2-293: e.g., "default", "governance"
            "phase_history": [],        # E2-293: Recent phase transitions
        },
        "active_work": active_work,
        "blocked_items": blocked_dict,
        "counts": {
            "concepts": memory_stats.get("concepts", 0),
            "entities": memory_stats.get("entities", 0),
            "backlog_pending": backlog_stats.get("active_count", 0),
        },
        "infrastructure": {
            "commands": commands,
            "skills": skills,
            "agents": agents,
            "mcps": [
                {"name": "haios-memory", "tools": 13},
                {"name": "context7", "tools": 2},
            ],
        },
    }

    return slim


def _get_active_work() -> list[str]:
    """Get active work items (HIGH and URGENT priority)."""
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"
    active_work = []

    if not backlog_path.exists():
        return active_work

    content = backlog_path.read_text(encoding="utf-8", errors="ignore")

    # Find HIGH and URGENT items
    pattern = r"(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3}).*\[(HIGH|URGENT)\]"
    matches = re.findall(pattern, content)

    for match in matches[:5]:  # Limit to first 5
        active_work.append(match[0])

    return active_work


def _load_existing_milestones() -> dict:
    """Discover milestones from work files AND backlog.md.

    Work files are primary source (new pattern - E2-173).
    Backlog.md is fallback for legacy items not yet migrated to work files.

    Returns:
        Merged dict of milestones from both sources.
    """
    # Primary: work files (new pattern - E2-173)
    work_milestones = _discover_milestones_from_work_files()
    # Fallback: backlog.md (legacy pattern)
    backlog_milestones = _discover_milestones_from_backlog()
    # Merge: work files take precedence (update backlog with work data)
    merged = {**backlog_milestones, **work_milestones}
    return merged


def _format_milestone_name(key: str) -> str:
    """Convert milestone key to display name.

    Args:
        key: Milestone key like "M6-WorkCycle"

    Returns:
        Display name like "WorkCycle"
    """
    if "-" in key:
        return key.split("-", 1)[1]
    return key


def _discover_milestones_from_backlog() -> dict:
    """Discover milestone structure from backlog.md.

    Parses backlog items to find milestone assignments and builds
    the milestone structure dynamically. Auto-discovers milestone
    names from **Milestone:** fields (E2-117).

    NOTE: Skips items that have work files - work files are source of truth (E2-173).
    """
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"
    plans_dir = PROJECT_ROOT / "docs" / "plans"
    work_dirs = [
        PROJECT_ROOT / "docs" / "work" / "active",
        PROJECT_ROOT / "docs" / "work" / "blocked",
        PROJECT_ROOT / "docs" / "work" / "archive",
    ]

    if not backlog_path.exists():
        return {}

    # Build set of items that have work files (to skip from backlog)
    # E2-212: Support both directory and flat file patterns
    items_with_work_files = set()
    for work_dir in work_dirs:
        if work_dir.exists():
            for wf in _iter_work_files(work_dir):
                # E2-212: Extract ID from directory name or filename
                if wf.name == "WORK.md":
                    # Directory structure: E2-123/WORK.md -> E2-123
                    item_id = wf.parent.name
                else:
                    # Flat file: WORK-E2-123-title.md -> E2-123
                    parts = wf.stem.split("-", 2)  # ['WORK', 'E2', '123-title']
                    if len(parts) >= 3:
                        item_id = f"{parts[1]}-{parts[2].split('-')[0]}"
                    else:
                        continue
                items_with_work_files.add(item_id)

    content = backlog_path.read_text(encoding="utf-8", errors="ignore")

    # E2-117: Auto-discover milestone keys from backlog content
    # Pattern matches: **Milestone:** M6-WorkCycle
    milestone_pattern = r'\*\*Milestone:\*\*\s*(M\d+-[A-Za-z]+)'
    discovered_keys = set(re.findall(milestone_pattern, content))

    # Build milestones dict from discovered keys
    milestones = {
        key: {"name": _format_milestone_name(key), "items": [], "complete": [], "progress": 0}
        for key in sorted(discovered_keys)
    }

    # Find items with milestone assignments: **Milestone:** M4-Research
    # Pattern: ### [PRIORITY] E2-XXX: Title ... **Milestone:** M?-Name
    pattern = r"###\s*\[[^\]]+\]\s*(E2-[A-Za-z]*-?\d+)[^\n]*\n(?:[^\n]*\n)*?.*\*\*Milestone:\*\*\s*(M\d+-[A-Za-z]+)"

    for match in re.finditer(pattern, content, re.MULTILINE):
        item_id = match.group(1)
        milestone_key = match.group(2)

        # Skip items that have work files - work file milestone takes precedence
        if item_id in items_with_work_files:
            continue

        if milestone_key in milestones:
            if item_id not in milestones[milestone_key]["items"]:
                milestones[milestone_key]["items"].append(item_id)

    # Check which items are complete (have plan with status: complete)
    for ms_key, milestone in milestones.items():
        for item_id in milestone["items"]:
            # Check for complete plan
            for plan_path in plans_dir.glob(f"PLAN-{item_id}*.md"):
                try:
                    plan_content = plan_path.read_text(encoding="utf-8", errors="ignore")
                    if re.search(r"status:\s*complete", plan_content):
                        if item_id not in milestone["complete"]:
                            milestone["complete"].append(item_id)
                        break
                except Exception:
                    continue

        # Calculate progress
        total = len(milestone["items"])
        done = len(milestone["complete"])
        milestone["progress"] = int((done / total * 100) if total > 0 else 0)

    # Filter out empty milestones (all items have work files)
    return {k: v for k, v in milestones.items() if v["items"]}


def _discover_milestones_from_work_files() -> dict:
    """Discover milestones from work file YAML frontmatter.

    Scans docs/work/{active,blocked,archive}/*.md for milestone: field.
    E2-173: Fixes stale vitals by reading M7 sub-milestones from work files.

    Returns:
        Dict mapping milestone keys to milestone data with items, complete, progress.
    """
    work_dirs = [
        PROJECT_ROOT / "docs" / "work" / "active",
        PROJECT_ROOT / "docs" / "work" / "blocked",
        PROJECT_ROOT / "docs" / "work" / "archive",
    ]

    milestones = {}

    for dir_path in work_dirs:
        # E2-212: Use dual-pattern iterator
        for file_path in _iter_work_files(dir_path):
            try:
                content = file_path.read_text(encoding="utf-8-sig")
                metadata = _parse_yaml_frontmatter(content)

                milestone_key = metadata.get("milestone")
                item_id = metadata.get("id")
                status = metadata.get("status", "").lower()

                # Skip if no milestone or no id
                if not milestone_key or milestone_key == "null" or not item_id:
                    continue

                # Initialize milestone if not seen
                if milestone_key not in milestones:
                    milestones[milestone_key] = {
                        "name": _format_milestone_name(milestone_key),
                        "items": [],
                        "complete": [],
                        "progress": 0,
                    }

                # Add item to milestone
                if item_id not in milestones[milestone_key]["items"]:
                    milestones[milestone_key]["items"].append(item_id)

                # Track complete items (includes terminal states like duplicate, archived, wontfix)
                if status in ("complete", "closed", "done", "duplicate", "archived", "wontfix"):
                    if item_id not in milestones[milestone_key]["complete"]:
                        milestones[milestone_key]["complete"].append(item_id)

            except Exception:
                continue

    # Calculate progress for each milestone
    for ms in milestones.values():
        total = len(ms["items"])
        done = len(ms["complete"])
        ms["progress"] = int((done / total * 100) if total > 0 else 0)

    return milestones


def _select_current_milestone(milestones: dict) -> Optional[dict]:
    """Select current milestone (highest progress non-complete)."""
    if not milestones:
        return None

    selected_key = None
    selected_progress = -1

    # Find highest-progress milestone that isn't 100%
    for key, m in milestones.items():
        prog = m.get("progress", 0)
        if prog < 100 and prog > selected_progress:
            selected_key = key
            selected_progress = prog

    # Fallback: if all complete, pick first one
    if not selected_key and milestones:
        selected_key = list(milestones.keys())[0]

    if not selected_key:
        return None

    m = milestones[selected_key]
    return {
        "id": selected_key,
        "name": m.get("name", selected_key),
        "progress": m.get("progress", 0),
        "prior_progress": m.get("prior_progress", 0),
        "delta_source": m.get("delta_source"),
    }


def write_slim_status(slim: dict, output_path: str) -> None:
    """Write slim status to JSON file.

    Args:
        slim: Slim status dict.
        output_path: Path to write JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(slim, f, indent=4)


def write_full_status(full: dict, output_path: str) -> None:
    """Write full status to JSON file.

    Args:
        full: Full status dict from generate_full_status().
        output_path: Path to write JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full, f, indent=4)


# CLI entry point
if __name__ == "__main__":
    import sys

    slim = generate_slim_status()

    if len(sys.argv) > 1 and sys.argv[1] == "--write":
        output_path = PROJECT_ROOT / ".claude" / "haios-status-slim.json"
        write_slim_status(slim, str(output_path))
        print(f"Written to {output_path}")
    else:
        print(json.dumps(slim, indent=2))
