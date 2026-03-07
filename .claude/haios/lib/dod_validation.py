# generated: 2026-02-11
"""
DoD validation functions for closure ceremonies (CH-015, WORK-122).

Two file format parsers:
- _parse_frontmatter(): For WORK.md files (YAML between --- markers)
- _parse_markdown_field(): For chapter/arc/epoch files (bold markdown **Field:** Value)

Four validation functions:
- validate_work_dod: Work item status, traces_to, closed date
- validate_chapter_dod: All chapter work items complete + exit criteria
- validate_arc_dod: All arc chapters Complete
- validate_epoch_dod: All epoch arcs Complete

Usage:
    from dod_validation import validate_work_dod, validate_chapter_dod
    result = validate_chapter_dod("CH-015", "ceremonies")
    if not result.passed:
        print(result.failures)
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import yaml


# --- Data Classes ---


@dataclass
class DoDCheck:
    """Single DoD check result."""

    name: str
    passed: bool
    detail: str = ""


@dataclass
class DoDResult:
    """Result of DoD validation at any level."""

    level: str  # "work", "chapter", "arc", "epoch"
    entity_id: str
    passed: bool
    checks: List[DoDCheck] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)


# --- Parsers ---


def _parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a WORK.md file (--- delimited).

    Only use for WORK.md files. Chapter/arc/epoch files use bold markdown.
    """
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def _parse_markdown_field(content: str, field_name: str) -> Optional[str]:
    """Extract value from bold markdown field: **Field:** Value.

    Used for chapter, arc, epoch files which do NOT use YAML frontmatter.
    Example: _parse_markdown_field(content, "Status") -> "Complete"
    """
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s*(.+)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def _count_exit_criteria(content: str) -> Tuple[int, int]:
    """Count checked vs total exit criteria checkboxes.

    Looks for the ## Exit Criteria section and counts checkboxes within it.

    Returns: (checked_count, total_count)
    """
    # Find the Exit Criteria section
    ec_match = re.search(r"## Exit Criteria\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not ec_match:
        return 0, 0
    ec_section = ec_match.group(1)
    total = len(re.findall(r"- \[[ x]\]", ec_section))
    checked = len(re.findall(r"- \[x\]", ec_section))
    return checked, total


def _find_work_items_for_chapter(
    chapter_id: str, base_path: Path
) -> List[Tuple[str, dict]]:
    """Find all work items assigned to a chapter via frontmatter chapter: field.

    Scans docs/work/active/*/WORK.md, returns list of (work_id, frontmatter_dict).
    Uses chapter: field format "CH-015" (no arc prefix).
    """
    active_dir = base_path / "docs" / "work" / "active"
    results = []
    if not active_dir.exists():
        return results
    for work_dir in sorted(active_dir.iterdir()):
        if not work_dir.is_dir():
            continue
        work_file = work_dir / "WORK.md"
        if not work_file.exists():
            continue
        fm = _parse_frontmatter(work_file)
        if fm.get("chapter") == chapter_id:
            results.append((fm.get("id", work_dir.name), fm))
    return results


# --- Validation Functions ---


def validate_work_dod(
    work_id: str,
    base_path: Optional[Path] = None,
) -> DoDResult:
    """Validate work item meets Definition of Done.

    Checks:
    - Work item file exists
    - status == "complete"
    - closed date is set (not null/None)
    - traces_to is non-empty

    Args:
        work_id: Work item ID (e.g., "WORK-122")
        base_path: Optional base path (defaults to cwd for production use)

    Returns:
        DoDResult with check details.
    """
    if base_path is None:
        base_path = Path(".")

    checks = []
    failures = []

    # Check 1: Work item exists
    work_file = base_path / "docs" / "work" / "active" / work_id / "WORK.md"
    if not work_file.exists():
        checks.append(DoDCheck("file_exists", False, f"{work_id} not found"))
        failures.append(f"Work item {work_id} not found at {work_file}")
        return DoDResult(
            level="work",
            entity_id=work_id,
            passed=False,
            checks=checks,
            failures=failures,
        )

    fm = _parse_frontmatter(work_file)

    # Check 2: Status is complete
    status = fm.get("status", "unknown")
    status_ok = status == "complete"
    checks.append(
        DoDCheck("status_complete", status_ok, f"status={status}")
    )
    if not status_ok:
        failures.append(f"{work_id} status is '{status}', expected 'complete'")

    # Check 3: Closed date set
    closed = fm.get("closed")
    closed_ok = closed is not None and closed != "null"
    checks.append(
        DoDCheck("closed_date_set", closed_ok, f"closed={closed}")
    )
    if not closed_ok:
        failures.append(f"{work_id} has no closed date")

    # Check 4: traces_to non-empty
    traces = fm.get("traces_to", [])
    traces_ok = isinstance(traces, list) and len(traces) > 0
    checks.append(
        DoDCheck("traces_to_set", traces_ok, f"traces_to={traces}")
    )
    if not traces_ok:
        failures.append(f"{work_id} has empty traces_to (REQ-TRACE-002)")

    return DoDResult(
        level="work",
        entity_id=work_id,
        passed=len(failures) == 0,
        checks=checks,
        failures=failures,
    )


def validate_chapter_dod(
    chapter_id: str,
    arc: str,
    base_path: Optional[Path] = None,
    epoch_dir: str = ".claude/haios/epochs/E2_5",
) -> DoDResult:
    """Validate chapter meets Definition of Done.

    Checks:
    - All work items with chapter: {chapter_id} have status: complete
    - Exit criteria checkboxes all checked

    Uses _parse_markdown_field for chapter status (bold markdown format).
    Uses _find_work_items_for_chapter for work item discovery.

    Args:
        chapter_id: Chapter ID (e.g., "CH-015")
        arc: Arc name (e.g., "ceremonies")
        base_path: Optional base path
        epoch_dir: Epoch directory relative to base_path

    Returns:
        DoDResult with check details.
    """
    if base_path is None:
        base_path = Path(".")

    checks = []
    failures = []

    # Find chapter file — try subdirectory CHAPTER.md first, then flat file
    arc_dir = base_path / epoch_dir / "arcs" / arc
    chapter_files = list(arc_dir.glob(f"chapters/{chapter_id}-*/CHAPTER.md"))
    if not chapter_files:
        # Backward compat: flat file format
        chapter_files = list(arc_dir.glob(f"{chapter_id}-*.md"))
    if not chapter_files:
        checks.append(DoDCheck("chapter_exists", False, f"{chapter_id} not found in {arc}"))
        failures.append(f"Chapter {chapter_id} not found in {arc_dir}")
        return DoDResult(
            level="chapter",
            entity_id=chapter_id,
            passed=False,
            checks=checks,
            failures=failures,
        )

    chapter_file = chapter_files[0]
    content = chapter_file.read_text(encoding="utf-8")

    # Check 1: All work items complete
    work_items = _find_work_items_for_chapter(chapter_id, base_path)
    incomplete = []
    for wid, fm in work_items:
        if fm.get("status") != "complete":
            incomplete.append(wid)

    work_ok = len(incomplete) == 0
    checks.append(
        DoDCheck(
            "all_work_complete",
            work_ok,
            f"{len(work_items)} items, {len(incomplete)} incomplete",
        )
    )
    if not work_ok:
        for wid in incomplete:
            failures.append(f"Work item {wid} is not complete")

    # Check 2: Exit criteria all checked
    # Try frontmatter-aware reader first (WORK-244)
    from chapter_frontmatter import get_exit_criteria as _get_chapter_exit_criteria

    # chapter_file from glob may be a flat .md file or CHAPTER.md in subdirectory
    _chapter_md_path = chapter_file if chapter_file.name == "CHAPTER.md" else None
    if _chapter_md_path is None:
        # Try: look for CHAPTER.md in same directory
        candidate = chapter_file.parent / "CHAPTER.md"
        if candidate.exists():
            _chapter_md_path = candidate

    if _chapter_md_path is not None:
        criteria = _get_chapter_exit_criteria(_chapter_md_path)
    else:
        criteria = None

    if criteria is None:
        # Fallback: count from markdown body of chapter_file itself
        checked, total = _count_exit_criteria(content)
        criteria = {"checked": checked, "total": total, "all_checked": checked == total} if total > 0 else None

    if criteria is not None and criteria["total"] > 0:
        ec_ok = criteria["all_checked"]
        checks.append(
            DoDCheck(
                "exit_criteria_checked",
                ec_ok,
                f"{criteria['checked']}/{criteria['total']} checked",
            )
        )
        if not ec_ok:
            failures.append(
                f"Exit criteria incomplete: {criteria['checked']}/{criteria['total']} checked"
            )
    else:
        checks.append(
            DoDCheck("exit_criteria_checked", True, "No exit criteria found")
        )

    return DoDResult(
        level="chapter",
        entity_id=chapter_id,
        passed=len(failures) == 0,
        checks=checks,
        failures=failures,
    )


def validate_arc_dod(
    arc: str,
    base_path: Optional[Path] = None,
    epoch_dir: str = ".claude/haios/epochs/E2_5",
) -> DoDResult:
    """Validate arc meets DoD (all chapters Complete).

    Globs CH-*.md files in arc directory.
    Uses _parse_markdown_field to check **Status:** of each chapter.
    Skips chapters with Status containing "Deferred".

    Args:
        arc: Arc name (e.g., "ceremonies")
        base_path: Optional base path
        epoch_dir: Epoch directory relative to base_path

    Returns:
        DoDResult with check details.
    """
    if base_path is None:
        base_path = Path(".")

    checks = []
    failures = []

    arc_dir = base_path / epoch_dir / "arcs" / arc
    if not arc_dir.exists():
        checks.append(DoDCheck("arc_exists", False, f"Arc directory not found: {arc}"))
        failures.append(f"Arc directory not found: {arc_dir}")
        return DoDResult(
            level="arc", entity_id=arc, passed=False, checks=checks, failures=failures
        )

    # Glob chapter files (CH-*.md, excluding ARC.md)
    chapter_files = sorted(arc_dir.glob("CH-*.md"))
    if not chapter_files:
        checks.append(DoDCheck("chapters_found", True, "No chapter files found"))
        return DoDResult(
            level="arc", entity_id=arc, passed=True, checks=checks, failures=failures
        )

    incomplete = []
    skipped = []
    for ch_file in chapter_files:
        content = ch_file.read_text(encoding="utf-8")
        status = _parse_markdown_field(content, "Status") or "Unknown"

        # Skip deferred chapters
        if "deferred" in status.lower():
            skipped.append(ch_file.stem)
            continue

        if status != "Complete":
            incomplete.append((ch_file.stem, status))

    chapters_ok = len(incomplete) == 0
    detail = f"{len(chapter_files)} chapters, {len(incomplete)} incomplete"
    if skipped:
        detail += f", {len(skipped)} deferred"
    checks.append(DoDCheck("all_chapters_complete", chapters_ok, detail))

    if not chapters_ok:
        for ch_name, status in incomplete:
            failures.append(f"Chapter {ch_name} has Status: {status}")

    return DoDResult(
        level="arc",
        entity_id=arc,
        passed=len(failures) == 0,
        checks=checks,
        failures=failures,
    )


def validate_epoch_dod(
    epoch_id: str,
    base_path: Optional[Path] = None,
) -> DoDResult:
    """Validate epoch meets DoD (all arcs Complete).

    Globs arcs/*/ARC.md files in epoch directory.
    Uses _parse_markdown_field to check **Status:** of each arc.
    Skips arcs with Status containing "Deferred".

    Args:
        epoch_id: Epoch directory name (e.g., "E2_5")
        base_path: Optional base path

    Returns:
        DoDResult with check details.
    """
    if base_path is None:
        base_path = Path(".")

    checks = []
    failures = []

    epoch_dir = base_path / ".claude" / "haios" / "epochs" / epoch_id
    arcs_dir = epoch_dir / "arcs"
    if not arcs_dir.exists():
        checks.append(
            DoDCheck("epoch_exists", False, f"Epoch arcs directory not found: {epoch_id}")
        )
        failures.append(f"Epoch arcs directory not found: {arcs_dir}")
        return DoDResult(
            level="epoch",
            entity_id=epoch_id,
            passed=False,
            checks=checks,
            failures=failures,
        )

    # Find all ARC.md files
    arc_files = sorted(arcs_dir.glob("*/ARC.md"))
    if not arc_files:
        checks.append(DoDCheck("arcs_found", True, "No arc directories found"))
        return DoDResult(
            level="epoch",
            entity_id=epoch_id,
            passed=True,
            checks=checks,
            failures=failures,
        )

    incomplete = []
    skipped = []
    for arc_file in arc_files:
        arc_name = arc_file.parent.name
        content = arc_file.read_text(encoding="utf-8")
        status = _parse_markdown_field(content, "Status") or "Unknown"

        # Skip deferred arcs
        if "deferred" in status.lower():
            skipped.append(arc_name)
            continue

        if status != "Complete":
            incomplete.append((arc_name, status))

    arcs_ok = len(incomplete) == 0
    detail = f"{len(arc_files)} arcs, {len(incomplete)} incomplete"
    if skipped:
        detail += f", {len(skipped)} deferred"
    checks.append(DoDCheck("all_arcs_complete", arcs_ok, detail))

    if not arcs_ok:
        for arc_name, status in incomplete:
            failures.append(f"Arc {arc_name} has Status: {status}")

    return DoDResult(
        level="epoch",
        entity_id=epoch_id,
        passed=len(failures) == 0,
        checks=checks,
        failures=failures,
    )
