# generated: 2025-12-24
# System Auto: last updated on: 2025-12-27T21:48:58
"""Governance audit functions for detecting drift.

Part of M7a-Recipes milestone (E2-143).
Provides functions to detect governance drift:
- audit_sync: Find investigations active but work archived
- audit_gaps: Find work items with complete plans still active
- audit_stale: Find investigations older than N sessions

E2-212: Updated to support directory structure for work items.
"""
import glob
import json
import yaml
from pathlib import Path
from typing import List


def _iter_work_files_glob(directory: str) -> List[str]:
    """Iterate work files supporting both directory and flat patterns (E2-212).

    Args:
        directory: Directory to scan (e.g., 'docs/work/active/')

    Returns:
        List of work file paths as strings.
    """
    files = []
    dir_path = Path(directory)
    if not dir_path.exists():
        return files

    # Check for directory structure first
    for subdir in dir_path.iterdir():
        if subdir.is_dir():
            work_md = subdir / "WORK.md"
            if work_md.exists():
                files.append(str(work_md))

    # Fall back to flat file pattern
    files.extend(glob.glob(f'{directory}/WORK-*.md'))

    return files


def _work_file_exists(directory: str, backlog_id: str) -> bool:
    """Check if work file exists for backlog_id (E2-212 dual pattern).

    Args:
        directory: Directory to check (e.g., 'docs/work/archive/')
        backlog_id: Work item ID

    Returns:
        True if work file exists.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return False

    # Check directory structure
    if (dir_path / backlog_id / "WORK.md").exists():
        return True

    # Check flat file pattern
    return len(glob.glob(f'{directory}/WORK-{backlog_id}-*.md')) > 0


def parse_frontmatter(file_path: str) -> dict:
    """Extract YAML frontmatter from markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        Dict of frontmatter fields, or empty dict if no frontmatter
    """
    try:
        content = Path(file_path).read_text(encoding='utf-8')
    except (FileNotFoundError, IOError):
        return {}

    if '---' not in content:
        return {}

    parts = content.split('---')
    if len(parts) < 2:
        return {}

    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def audit_sync() -> List[str]:
    """Find investigations still active but work file is archived.

    Detects status mismatch: investigation file says active,
    but work file has been moved to archive (completed).

    Returns:
        List of issue strings, empty if no issues
    """
    issues = []
    for inv in glob.glob('docs/investigations/INVESTIGATION-*.md'):
        fm = parse_frontmatter(inv)
        if fm.get('status') == 'active':
            inv_id = fm.get('backlog_id', '')
            # E2-212: Use helper for dual pattern support
            if inv_id and _work_file_exists('docs/work/archive', inv_id):
                issues.append(f'SYNC: {inv_id} investigation active but work archived')
    return issues


def audit_gaps() -> List[str]:
    """Find work items with complete plans but still active.

    Detects implementation gaps: plan is marked complete,
    but work file hasn't been closed yet.

    Returns:
        List of issue strings, empty if no issues
    """
    issues = []
    # E2-212: Use iterator for dual pattern support
    for work in _iter_work_files_glob('docs/work/active'):
        fm = parse_frontmatter(work)
        work_id = fm.get('id', '')
        if not work_id:
            continue
        # E2-212: Check both work directory plans and legacy location
        work_path = Path(work)
        plan_locations = [f'docs/plans/PLAN-{work_id}*.md']
        if work_path.name == "WORK.md":
            # Also check plans inside work directory
            plan_locations.append(str(work_path.parent / "plans" / "*.md"))
        for pattern in plan_locations:
            for plan in glob.glob(pattern):
                pfm = parse_frontmatter(plan)
                if pfm.get('status') == 'complete':
                    issues.append(f'GAP: {work_id} has complete plan but work still active')
                    break
    return issues


def audit_stale(threshold: int = 10) -> List[str]:
    """Find investigations older than threshold sessions.

    Detects stale investigations that may have been forgotten.

    Args:
        threshold: Number of sessions before considered stale (default: 10)

    Returns:
        List of issue strings, empty if no issues
    """
    issues = []
    try:
        status = json.loads(Path('.claude/haios-status.json').read_text())
        current = status.get('system', {}).get('last_session', 999)
    except (FileNotFoundError, json.JSONDecodeError):
        current = 999

    for inv in glob.glob('docs/investigations/INVESTIGATION-*.md'):
        fm = parse_frontmatter(inv)
        if fm.get('status') == 'active':
            sess = fm.get('session', 0)
            if current - sess > threshold:
                inv_id = fm.get('backlog_id', '?')
                issues.append(f'STALE: {inv_id} active since S{sess} (now S{current})')
    return issues


# CLI entry point for direct execution
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python audit.py [sync|gaps|stale]')
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'sync':
        for issue in audit_sync():
            print(issue)
    elif cmd == 'gaps':
        for issue in audit_gaps():
            print(issue)
    elif cmd == 'stale':
        for issue in audit_stale():
            print(issue)
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(1)
