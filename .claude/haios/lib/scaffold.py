# generated: 2025-12-21
# System Auto: last updated on: 2026-01-21T22:18:23
"""
DEPRECATED: Use GovernanceLayer.scaffold_template() instead.

Migration path (E2-252):
    from governance_layer import GovernanceLayer
    layer = GovernanceLayer()
    path = layer.scaffold_template(template, backlog_id=id, title=title)

Or via CLI:
    python .claude/haios/modules/cli.py scaffold <type> <id> <title>

Or via justfile:
    just scaffold <type> <id> <title>

---

Template scaffolding module for HAIOS plugin.

E2-120 Phase 2b: Migrated from ScaffoldTemplate.ps1.

Core functions:
1. generate_output_path() - Auto-generate path from template/backlog_id/title
2. load_template() - Read template file
3. substitute_variables() - Replace {{VAR}} placeholders
4. get_next_sequence_number() - Handle {{NN}} for same-day files
5. get_prev_session() - Read last session from haios-status.json
6. scaffold_template() - Main orchestrator
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# Project root is 4 levels up from .claude/haios/lib/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Template types that don't require backlog_id
NO_BACKLOG_ID_TEMPLATES = {"report", "handoff_investigation"}

# Templates that require work file to exist first (E2-160)
WORK_FILE_REQUIRED_TEMPLATES = {"investigation", "implementation_plan"}

# Templates that don't require title (E2-217)
NO_TITLE_REQUIRED_TEMPLATES = {"observations"}

# Template type to directory/prefix mapping
# E2-212: work_item now creates directory structure, plans/investigations go inside
TEMPLATE_CONFIG = {
    "investigation": {
        "dir": "docs/investigations",  # Legacy path for non-work investigations
        "prefix": "INVESTIGATION",
        "pattern": "{dir}/{prefix}-{backlog_id}-{slug}.md",
    },
    "implementation_plan": {
        "dir": "docs/plans",  # Legacy path - will be overridden for work items
        "prefix": "PLAN",
        "pattern": "{dir}/{prefix}-{backlog_id}-{slug}.md",
    },
    "checkpoint": {
        "dir": "docs/checkpoints",
        "prefix": None,
        "pattern": "{dir}/{date}-{{{{NN}}}}-SESSION-{backlog_id}-{slug}.md",
    },
    "report": {
        "dir": "docs/reports",
        "prefix": "REPORT",
        "pattern": "{dir}/{date}-{prefix}-{slug}.md",
    },
    "architecture_decision_record": {
        "dir": "docs/ADR",
        "prefix": "ADR",
        "pattern": "{dir}/{prefix}-{backlog_id}-{slug}.md",
    },
    "handoff_investigation": {
        "dir": "docs/handoff",
        "prefix": "HANDOFF",
        "pattern": "{dir}/{date}-{prefix}-{slug}.md",
    },
    "work_item": {
        "dir": "docs/work/active",
        "prefix": None,  # E2-212: No prefix - file is just WORK.md
        "pattern": "{dir}/{backlog_id}/WORK.md",  # E2-212: Directory per work item
        "subdirs": ["plans", "investigations", "reports"],  # E2-212: Auto-create
    },
    "observations": {
        "dir": "docs/work/active",  # E2-217: Goes into work directory
        "prefix": None,
        "pattern": "{dir}/{backlog_id}/observations.md",  # E2-217: Observation capture
    },
}


def _create_slug(title: str) -> str:
    """Create URL-friendly slug from title.

    - Lowercase
    - Replace spaces with hyphens
    - Remove special characters
    - Collapse multiple hyphens
    """
    slug = title.lower()
    # Remove special characters except spaces and hyphens
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    # Replace spaces with hyphens
    slug = re.sub(r"\s+", "-", slug)
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    # Trim leading/trailing hyphens
    slug = slug.strip("-")
    return slug


def _work_file_exists(backlog_id: str) -> bool:
    """Check if work file exists for backlog_id (E2-160).

    E2-212: Supports both directory structure and flat file patterns.

    Args:
        backlog_id: The backlog item ID to check

    Returns:
        True if work file exists in docs/work/active/, False otherwise.
    """
    work_dir = PROJECT_ROOT / "docs" / "work" / "active"
    if not work_dir.exists():
        return False

    # E2-212: Try directory structure first (new)
    dir_path = work_dir / backlog_id / "WORK.md"
    if dir_path.exists():
        return True

    # Fall back to flat file pattern (legacy)
    pattern = f"WORK-{backlog_id}-*.md"
    return len(list(work_dir.glob(pattern))) > 0


def _create_work_subdirs(work_dir: Path, subdirs: list[str]) -> None:
    """Create subdirectories for work item directory (E2-212).

    Args:
        work_dir: Path to work item directory (e.g., docs/work/active/E2-212/)
        subdirs: List of subdirectory names to create
    """
    for subdir in subdirs:
        (work_dir / subdir).mkdir(parents=True, exist_ok=True)


def get_next_work_id() -> str:
    """Generate next sequential WORK-XXX ID.

    WORK-001: Scans docs/work/active/ for highest WORK-NNN and returns WORK-(N+1).
    Ignores legacy E2-XXX and INV-XXX directories.

    Returns:
        Next sequential work ID in format WORK-XXX (e.g., "WORK-001", "WORK-042")
    """
    work_dir = PROJECT_ROOT / "docs" / "work" / "active"
    max_num = 0

    if work_dir.exists():
        for subdir in work_dir.iterdir():
            if subdir.is_dir() and subdir.name.startswith("WORK-"):
                try:
                    num = int(subdir.name.split("-")[1])
                    max_num = max(max_num, num)
                except (ValueError, IndexError):
                    pass  # Skip malformed WORK-* directories

    return f"WORK-{max_num + 1:03d}"


def generate_output_path(
    template: str,
    backlog_id: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """Auto-generate output path from template type, backlog_id, and title.

    E2-212: For plans/investigations, routes into work directory if it exists.

    Args:
        template: Template type (checkpoint, implementation_plan, etc.)
        backlog_id: Backlog item ID (optional for some templates)
        title: Document title

    Returns:
        Generated output path string.
    """
    if template not in TEMPLATE_CONFIG:
        raise ValueError(f"Unknown template type: {template}")

    config = TEMPLATE_CONFIG[template]
    today = datetime.now().strftime("%Y-%m-%d")
    slug = _create_slug(title) if title else "untitled"

    # E2-212: Route plans/investigations into work directory if it exists
    if template in ("implementation_plan", "investigation") and backlog_id:
        work_dir = PROJECT_ROOT / "docs" / "work" / "active" / backlog_id
        if work_dir.exists():
            if template == "implementation_plan":
                return f"docs/work/active/{backlog_id}/plans/PLAN.md"
            elif template == "investigation":
                # Get next sequence number for investigations
                inv_dir = work_dir / "investigations"
                inv_dir.mkdir(exist_ok=True)
                existing = list(inv_dir.glob("*.md"))
                seq = f"{len(existing) + 1:03d}"
                return f"docs/work/active/{backlog_id}/investigations/{seq}-{slug}.md"

    # Build path from pattern (legacy or non-work-item templates)
    path = config["pattern"].format(
        dir=config["dir"],
        prefix=config.get("prefix", ""),
        backlog_id=backlog_id or "",
        slug=slug,
        date=today,
    )

    return path


def load_template(template: str) -> str:
    """Load template content from file.

    Args:
        template: Template name (without .md extension)

    Returns:
        Template content string.

    Raises:
        FileNotFoundError: If template file doesn't exist.
    """
    template_path = PROJECT_ROOT / ".claude" / "templates" / f"{template}.md"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    return template_path.read_text(encoding="utf-8-sig")


def substitute_variables(content: str, variables: dict) -> str:
    """Replace {{VAR}} placeholders with variable values.

    Args:
        content: Template content with placeholders
        variables: Dict of variable names to values

    Returns:
        Content with placeholders replaced.
    """
    result = content
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    return result


def get_next_sequence_number(directory: str, date: str) -> str:
    """Get next sequence number for same-day files.

    Scans directory for files matching date-NN-* pattern and returns
    the next available number as zero-padded string.

    Args:
        directory: Directory to scan
        date: Date string (YYYY-MM-DD format)

    Returns:
        Next sequence number as zero-padded string (e.g., "01", "02")
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return "01"

    # Find files matching date-NN-* pattern
    pattern = re.compile(rf"^{re.escape(date)}-(\d{{2}})-")
    max_num = 0

    for file in dir_path.iterdir():
        match = pattern.match(file.name)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num

    return f"{max_num + 1:02d}"


def get_current_session() -> int | str:
    """Read current session number from events log, falling back to status file.

    Priority: haios-events.jsonl (last session_start) > haios-status.json

    Returns:
        Current session number as int, or "??" if unavailable.
    """
    # E2-134: Try events log first (most accurate - reflects just session-start)
    events_path = PROJECT_ROOT / ".claude" / "haios-events.jsonl"
    if events_path.exists():
        try:
            with open(events_path, encoding="utf-8") as f:
                lines = f.readlines()
            # Read backwards to find last session_start
            for line in reversed(lines):
                try:
                    event = json.loads(line.strip())
                    if event.get("type") == "session" and event.get("action") == "start":
                        return event.get("session", "??")
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass  # Fall through to status file

    # Fall back to haios-status.json
    status_path = PROJECT_ROOT / ".claude" / "haios-status.json"
    if not status_path.exists():
        return "??"

    try:
        with open(status_path, encoding="utf-8-sig") as f:
            status = json.load(f)
        current_session = status.get("session_delta", {}).get("current_session")
        return current_session if current_session is not None else "??"
    except Exception:
        return "??"


def get_prev_session() -> int | str:
    """Read previous session number from haios-status.json.

    Returns:
        Previous session number as int, or "??" if unavailable.
    """
    status_path = PROJECT_ROOT / ".claude" / "haios-status.json"

    if not status_path.exists():
        return "??"

    try:
        with open(status_path, encoding="utf-8-sig") as f:
            status = json.load(f)
        # Read from session_delta.prior_session (E2-133 fix)
        prev_session = status.get("session_delta", {}).get("prior_session")
        return prev_session if prev_session is not None else "??"
    except Exception:
        return "??"


def scaffold_template(
    template: str,
    output_path: Optional[str] = None,
    backlog_id: Optional[str] = None,
    title: Optional[str] = None,
    variables: Optional[dict] = None,
) -> str:
    """Scaffold a new document from template.

    Main orchestrator function that:
    1. Auto-generates output path if not provided
    2. Loads template
    3. Adds default variables (DATE, PREV_SESSION)
    4. Substitutes all variables
    5. Handles {{NN}} sequence numbering
    6. Writes output file

    Args:
        template: Template type
        output_path: Output file path (optional, auto-generated if not provided)
        backlog_id: Backlog item ID
        title: Document title
        variables: Additional variables to substitute

    Returns:
        Path to created file.
    """
    variables = variables or {}

    # Auto-generate output path if not provided
    if not output_path:
        if not title and template not in NO_TITLE_REQUIRED_TEMPLATES:
            raise ValueError("Either output_path or title must be provided")
        output_path = generate_output_path(template, backlog_id, title)

    # Load template
    content = load_template(template)

    # Add default variables
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if "DATE" not in variables:
        variables["DATE"] = today

    if "TIMESTAMP" not in variables:
        variables["TIMESTAMP"] = timestamp

    if "PREV_SESSION" not in variables:
        variables["PREV_SESSION"] = str(get_prev_session())

    # Auto-populate from backlog_id and title
    if backlog_id and "BACKLOG_ID" not in variables:
        variables["BACKLOG_ID"] = backlog_id
    if title and "TITLE" not in variables:
        variables["TITLE"] = title

    # Auto-populate SESSION for all templates (E2-133 fix)
    if "SESSION" not in variables:
        if template == "checkpoint" and backlog_id:
            # For checkpoints, backlog_id IS the session number
            variables["SESSION"] = backlog_id
        else:
            # For all other templates, read current session from status
            variables["SESSION"] = str(get_current_session())

    # Initialize BACKLOG_IDS if not set
    if "BACKLOG_IDS" not in variables:
        variables["BACKLOG_IDS"] = "[]"

    # E2-179: Default optional frontmatter variables to "null" if not provided
    if "SPAWNED_BY" not in variables:
        variables["SPAWNED_BY"] = "null"

    # Substitute variables
    content = substitute_variables(content, variables)

    # Remove auto-generated timestamp lines from template
    content = re.sub(r"# generated: .*\n?", "", content)
    content = re.sub(r"# System Auto: last updated on: .*\n?", "", content)

    # Handle {{NN}} sequence numbering
    if "{{NN}}" in output_path:
        output_dir = str(Path(output_path).parent)
        next_num = get_next_sequence_number(
            str(PROJECT_ROOT / output_dir),
            today
        )
        output_path = output_path.replace("{{NN}}", next_num)

    # Check work file prerequisite for gated templates (E2-160)
    if template in WORK_FILE_REQUIRED_TEMPLATES and backlog_id:
        if not _work_file_exists(backlog_id):
            raise ValueError(
                f"Work file required. Run '/new-work {backlog_id} \"{title}\"' first."
            )

    # Ensure output directory exists
    full_output_path = PROJECT_ROOT / output_path
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    # E2-212: Create subdirectories for work_item template
    config = TEMPLATE_CONFIG.get(template, {})
    if "subdirs" in config:
        _create_work_subdirs(full_output_path.parent, config["subdirs"])

    # Write output file
    full_output_path.write_text(content, encoding="utf-8")

    return str(full_output_path)


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python scaffold.py <template> <backlog_id> <title>")
        print("       python scaffold.py <template> --output <path> [--var KEY=VALUE ...]")
        sys.exit(1)

    template = sys.argv[1]

    if "--output" in sys.argv:
        output_idx = sys.argv.index("--output")
        output_path = sys.argv[output_idx + 1]
        result = scaffold_template(template, output_path=output_path)
    else:
        backlog_id = sys.argv[2]
        title = " ".join(sys.argv[3:])
        result = scaffold_template(template, backlog_id=backlog_id, title=title)

    print(f"Created: {result}")
