# generated: 2026-02-14
# WORK-075: L4 requirement coverage audit
"""L4 requirement coverage audit for HAIOS.

Scans all work items for traces_to fields, cross-references with L4 requirement
registry, and produces coverage tables + gap analysis.

Usage:
    python scripts/audit_l4_coverage.py
    python scripts/audit_l4_coverage.py --format markdown  # default
    python scripts/audit_l4_coverage.py --format summary   # counts only

Must be run from project root directory.
"""
import argparse
import re
from pathlib import Path

import yaml


def parse_traces_to(work_content: str) -> dict:
    """Extract id, traces_to, and status from WORK.md frontmatter.

    Returns traces_to=[] if field is missing (legacy items).

    Args:
        work_content: Raw content of a WORK.md file.

    Returns:
        Dict with keys: id, traces_to (list), status.
    """
    # Extract YAML frontmatter between --- markers
    match = re.match(r"^---\n(.*?)\n---", work_content, re.DOTALL)
    if not match:
        return {"id": "", "traces_to": [], "status": ""}

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {"id": "", "traces_to": [], "status": ""}

    if not isinstance(frontmatter, dict):
        return {"id": "", "traces_to": [], "status": ""}

    traces = frontmatter.get("traces_to", [])
    if traces is None:
        traces = []

    return {
        "id": str(frontmatter.get("id", "")),
        "traces_to": traces,
        "status": str(frontmatter.get("status", "")),
    }


def parse_all_work_items(work_dir: Path) -> list[dict]:
    """Scan all WORK.md files in work_dir for traces_to mappings.

    Includes both active/ and archive/ directories.

    Args:
        work_dir: Root work directory (e.g., docs/work).

    Returns:
        List of parsed work item dicts from parse_traces_to.
    """
    items = []
    for subdir_name in ["active", "archive"]:
        subdir = work_dir / subdir_name
        if not subdir.exists():
            continue
        for item_dir in sorted(subdir.iterdir()):
            if not item_dir.is_dir():
                continue
            work_file = item_dir / "WORK.md"
            if work_file.exists():
                content = work_file.read_text(encoding="utf-8")
                parsed = parse_traces_to(content)
                if parsed["id"]:
                    items.append(parsed)
    return items


def parse_l4_requirement_ids(req_file: Path) -> list[str]:
    """Extract all unique REQ-*-NNN IDs from functional_requirements.md.

    Args:
        req_file: Path to functional_requirements.md.

    Returns:
        Sorted list of unique requirement IDs.
    """
    content = req_file.read_text(encoding="utf-8")
    ids = set(re.findall(r"REQ-[A-Z]+-\d+", content))
    return sorted(ids)


def build_l4_coverage(
    work_items: list[dict], all_req_ids: list[str]
) -> dict[str, list[tuple[str, str]]]:
    """Map each requirement ID to list of (work_id, status) tuples.

    Args:
        work_items: Parsed work items from parse_all_work_items.
        all_req_ids: All known requirement IDs from the registry.

    Returns:
        Dict mapping req_id -> [(work_id, status), ...].
    """
    coverage: dict[str, list[tuple[str, str]]] = {
        req_id: [] for req_id in all_req_ids
    }
    for item in work_items:
        for req_id in item["traces_to"]:
            if req_id in coverage:
                coverage[req_id].append((item["id"], item["status"]))
    return coverage


def parse_epoch_decisions(epoch_content: str) -> dict[str, dict]:
    """Extract decision ID, title from EPOCH.md Decision headers.

    Parses headers like '### Decision 1: Five-Layer Hierarchy'.

    Args:
        epoch_content: Raw content of EPOCH.md file.

    Returns:
        Dict mapping decision key (e.g., "D1") to {"title": "..."}.
    """
    decisions = {}
    pattern = r"### Decision (\d+):\s*(.+)"
    for match in re.finditer(pattern, epoch_content):
        num = match.group(1)
        title = match.group(2).strip()
        decisions[f"D{num}"] = {"title": title}
    return decisions


def find_gaps(coverage: dict[str, list]) -> list[str]:
    """Return requirement IDs with no implementing work items.

    Args:
        coverage: Coverage map from build_l4_coverage.

    Returns:
        List of requirement IDs with empty coverage.
    """
    return [req_id for req_id, items in coverage.items() if len(items) == 0]


def _derive_domain(req_id: str) -> str:
    """Extract domain name from requirement ID (e.g., REQ-TRACE-001 -> Traceability)."""
    domain_map = {
        "TRACE": "Traceability",
        "CONTEXT": "Context",
        "GOVERN": "Governance",
        "MEMORY": "Memory",
        "WORK": "Work",
        "VALID": "Validation",
        "ACTIVITY": "Activities",
        "FLOW": "Flow",
        "CRITIQUE": "Critique",
        "TEMPLATE": "Templates",
        "DOD": "DoD",
        "LIFECYCLE": "Lifecycle",
        "QUEUE": "Queue",
        "CEREMONY": "Ceremony",
        "FEEDBACK": "Feedback",
        "ASSET": "Asset",
        "CONFIG": "Config",
        "OBSERVE": "Observability",
        "DISCOVER": "Discoverability",
        "REFERENCE": "Referenceability",
    }
    match = re.match(r"REQ-([A-Z]+)-\d+", req_id)
    if match:
        key = match.group(1)
        return domain_map.get(key, key)
    return "Unknown"


def _derive_status(items: list[tuple[str, str]]) -> str:
    """Derive coverage status from work item statuses."""
    if not items:
        return "Gap"
    statuses = [s for _, s in items]
    if any(s == "complete" for s in statuses):
        return "Implemented"
    return "In Progress"


def format_l4_coverage_table(coverage: dict[str, list[tuple[str, str]]]) -> str:
    """Render L4 coverage as markdown table.

    Args:
        coverage: Coverage map from build_l4_coverage.

    Returns:
        Markdown table string.
    """
    lines = [
        "| Requirement | Domain | Work Items | Status |",
        "|-------------|--------|------------|--------|",
    ]
    for req_id in sorted(coverage.keys()):
        items = coverage[req_id]
        domain = _derive_domain(req_id)
        if items:
            work_ids = ", ".join(wid for wid, _ in items)
        else:
            work_ids = "-"
        status = _derive_status(items)
        lines.append(f"| {req_id} | {domain} | {work_ids} | {status} |")
    return "\n".join(lines)


def format_decision_coverage_table(
    decisions: dict[str, dict], arc_mappings: dict[str, str]
) -> str:
    """Render decision-to-arc/chapter mapping as markdown table.

    Args:
        decisions: Parsed decisions from parse_epoch_decisions.
        arc_mappings: Dict mapping decision key to arc/chapter string.

    Returns:
        Markdown table string.
    """
    lines = [
        "| Decision | Title | Arcs/Chapters | Status |",
        "|----------|-------|---------------|--------|",
    ]
    for d_key in sorted(decisions.keys(), key=lambda k: int(k[1:])):
        title = decisions[d_key]["title"]
        mapping = arc_mappings.get(d_key, "-")
        status = "Mapped" if mapping != "-" else "Gap"
        lines.append(f"| {d_key} | {title} | {mapping} | {status} |")
    return "\n".join(lines)


def format_gap_analysis(
    req_gaps: list[str],
    decision_gaps: list[str],
    decisions: dict[str, dict],
) -> str:
    """Render gap analysis as markdown section.

    Args:
        req_gaps: Requirement IDs with no coverage.
        decision_gaps: Decision keys with no arc mapping.
        decisions: Parsed decisions for title lookup.

    Returns:
        Markdown section string.
    """
    lines = []
    lines.append("### L4 Requirements Without Implementation")
    lines.append("")
    if req_gaps:
        for req_id in sorted(req_gaps):
            domain = _derive_domain(req_id)
            lines.append(f"- **{req_id}** ({domain}): No work item traces to this requirement")
    else:
        lines.append("All L4 requirements have at least one implementing work item.")
    lines.append("")
    lines.append("### Epoch Decisions Without Arc/Chapter Mapping")
    lines.append("")
    if decision_gaps:
        for d_key in sorted(decision_gaps, key=lambda k: int(k[1:])):
            title = decisions.get(d_key, {}).get("title", "Unknown")
            lines.append(f"- **{d_key}**: {title} - No arc/chapter assigned")
    else:
        lines.append("All epoch decisions have arc/chapter assignments.")
    return "\n".join(lines)


def format_data_quality_summary(
    total_items: int, with_traces: int, without_traces: int
) -> str:
    """Render data quality summary showing traces_to field coverage.

    Args:
        total_items: Total work items scanned.
        with_traces: Items with non-empty traces_to.
        without_traces: Items with empty or missing traces_to.

    Returns:
        Markdown summary string.
    """
    if total_items == 0:
        pct = 0.0
    else:
        pct = (with_traces / total_items) * 100

    lines = [
        "### Data Quality",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total work items scanned | {total_items} |",
        f"| Items with `traces_to` populated | {with_traces} ({pct:.0f}%) |",
        f"| Items without `traces_to` (legacy/empty) | {without_traces} ({100 - pct:.0f}%) |",
        "",
        "**Note:** Many legacy work items (E2-xxx, INV-xxx, CH-xxx) predate the `traces_to` "
        "field (REQ-TRACE-001). \"Gap\" means no items *with `traces_to`* reference this "
        "requirement, not necessarily that no implementation exists.",
    ]
    return "\n".join(lines)


def _build_decision_arc_mappings() -> dict[str, str]:
    """Build decision-to-arc mappings from E2.6 arc structure.

    Maps E2.4 decisions to E2.6 arcs/chapters based on the requirements
    each arc implements. This uses arc definitions rather than EPOCH.md
    assigned_to fields (which are incomplete for Decisions 1-6).

    Returns:
        Dict mapping decision key to arc/chapter description.
    """
    # E2.4 decisions mapped to E2.6 arcs based on conceptual alignment.
    # Source: E2.4/EPOCH.md decisions + E2.6 arc definitions.
    return {
        "D1": "discoverability (CH-032..034), observability (CH-042)",
        "D2": "traceability (CH-038)",
        "D3": "traceability (CH-040: gate skip logging)",
        "D4": "traceability (CH-038: WORK-097 spawn_type)",
        "D5": "traceability (CH-038: lifecycle mappings)",
        "D6": "referenceability (CH-036: template bootstrap)",
        "D7": "traceability (CH-038: WORK-104 activity matrix)",
        "D8": "traceability (CH-039: L4 coverage audit)",
    }


def main():
    """Run full audit and print markdown output including data quality summary."""
    parser = argparse.ArgumentParser(description="L4 requirement coverage audit")
    parser.add_argument(
        "--format",
        choices=["markdown", "summary"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    args = parser.parse_args()

    # Resolve paths from project root
    project_root = Path(__file__).parent.parent
    work_dir = project_root / "docs" / "work"
    req_file = (
        project_root
        / ".claude"
        / "haios"
        / "manifesto"
        / "L4"
        / "functional_requirements.md"
    )
    epoch_file = (
        project_root / ".claude" / "haios" / "epochs" / "E2_4" / "EPOCH.md"
    )

    # Parse data
    work_items = parse_all_work_items(work_dir)
    all_req_ids = parse_l4_requirement_ids(req_file)
    epoch_content = epoch_file.read_text(encoding="utf-8")
    decisions = parse_epoch_decisions(epoch_content)

    # Build coverage
    coverage = build_l4_coverage(work_items, all_req_ids)
    req_gaps = find_gaps(coverage)

    # Build decision mappings
    arc_mappings = _build_decision_arc_mappings()
    decision_gaps = [
        d_key for d_key in decisions if arc_mappings.get(d_key, "-") == "-"
    ]

    # Data quality
    with_traces = sum(1 for item in work_items if item["traces_to"])
    without_traces = len(work_items) - with_traces

    if args.format == "summary":
        print(f"L4 Requirements: {len(all_req_ids)} total, {len(req_gaps)} gaps")
        print(f"E2.4 Decisions: {len(decisions)} total, {len(decision_gaps)} gaps")
        print(
            f"Work Items: {len(work_items)} total, "
            f"{with_traces} with traces_to ({without_traces} without)"
        )
        implemented = sum(
            1 for items in coverage.values() if _derive_status(items) == "Implemented"
        )
        in_progress = sum(
            1 for items in coverage.values() if _derive_status(items) == "In Progress"
        )
        print(
            f"Coverage: {implemented} implemented, {in_progress} in progress, "
            f"{len(req_gaps)} gaps"
        )
        return

    # Full markdown output
    print("## 21. L4 Requirement Coverage")
    print()
    print(format_data_quality_summary(len(work_items), with_traces, without_traces))
    print()
    print("### Coverage Table")
    print()
    print(format_l4_coverage_table(coverage))
    print()
    print("---")
    print()
    print("## 22. E2.4 Decision Coverage")
    print()
    print(format_decision_coverage_table(decisions, arc_mappings))
    print()
    print("---")
    print()
    print("## 23. Gap Analysis")
    print()
    print(
        format_gap_analysis(req_gaps, decision_gaps, decisions)
    )
    print()


if __name__ == "__main__":
    main()
