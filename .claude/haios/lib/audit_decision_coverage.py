# generated: 2026-02-02
# System Auto: last updated on: 2026-02-02T08:57:59
"""Decision traceability validation for HAIOS.

Validates bidirectional traceability between epoch decisions and chapter files:
- Decisions in EPOCH.md should have assigned_to fields linking to arcs/chapters
- Chapter files should have implements_decisions fields back-referencing decisions
- Both directions should be consistent (no orphan claims)

Usage:
    from audit_decision_coverage import validate_decision_coverage, validate_bidirectional

    # Validate a single EPOCH.md content
    result = validate_decision_coverage(epoch_content)

    # Validate full bidirectional traceability
    result = validate_bidirectional(epoch_decisions, chapter_refs)
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    """Result of validation with warnings and errors."""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    is_consistent: bool = True
    orphan_decisions: list[str] = field(default_factory=list)
    orphan_chapters: list[str] = field(default_factory=list)


def parse_epoch_decisions(epoch_content: str) -> dict[str, dict]:
    """
    Parse decisions from EPOCH.md content.

    Extracts decision IDs and their assigned_to fields.

    Args:
        epoch_content: Content of EPOCH.md file

    Returns:
        Dict mapping decision ID (e.g., "D1") to decision data including assigned_to
    """
    decisions = {}

    # Find all decision headers: ### Decision N: Title
    decision_pattern = r'### Decision (\d+):\s*([^\n]+)'

    # Split content by decision headers
    parts = re.split(r'(### Decision \d+:[^\n]+)', epoch_content)

    current_decision_id = None
    for i, part in enumerate(parts):
        header_match = re.match(decision_pattern, part)
        if header_match:
            decision_num = header_match.group(1)
            current_decision_id = f"D{decision_num}"
            decisions[current_decision_id] = {
                "title": header_match.group(2).strip(),
                "assigned_to": []
            }
        elif current_decision_id and i > 0:
            # This is the content after a decision header
            # Look for assigned_to block
            assigned_to = _parse_assigned_to_block(part)
            if assigned_to:
                decisions[current_decision_id]["assigned_to"] = assigned_to

    return decisions


def _parse_assigned_to_block(content: str) -> list[dict]:
    """
    Parse assigned_to YAML-like block from decision content.

    Format:
        assigned_to:
          - arc: flow
            chapters: [CH-009, CH-010]
          - arc: activities
            chapters: [CH-001]

    Args:
        content: Decision content after header

    Returns:
        List of {arc, chapters} dicts
    """
    result = []

    # Look for assigned_to: block - capture until next section or double newline
    assigned_match = re.search(
        r'assigned_to:\s*\n((?:[ \t]+.*\n)*)',
        content
    )
    if not assigned_match:
        return result

    block = assigned_match.group(1)

    # Parse each arc entry - allow multiline with flexible whitespace
    arc_pattern = r'-\s*arc:\s*(\w+)\s*\n\s*chapters:\s*\[([^\]]+)\]'
    for arc_match in re.finditer(arc_pattern, block):
        arc_name = arc_match.group(1)
        chapters_str = arc_match.group(2)
        # Parse chapter list: CH-009, CH-010
        chapters = [ch.strip() for ch in chapters_str.split(',')]
        result.append({"arc": arc_name, "chapters": chapters})

    return result


def parse_chapter_refs(chapter_content: str, chapter_id: str) -> dict:
    """
    Parse implements_decisions from chapter file content.

    Args:
        chapter_content: Content of chapter file
        chapter_id: Chapter ID for reference

    Returns:
        Dict with chapter info including implements_decisions list
    """
    result = {
        "chapter_id": chapter_id,
        "implements_decisions": []
    }

    # Look for implements_decisions field
    # Format: **implements_decisions:** [D1, D3, D8]
    impl_match = re.search(r'\*\*implements_decisions:\*\*\s*\[([^\]]+)\]', chapter_content)
    if impl_match:
        decisions_str = impl_match.group(1)
        decisions = [d.strip() for d in decisions_str.split(',')]
        result["implements_decisions"] = decisions

    return result


def validate_decision_coverage(epoch_content: str) -> ValidationResult:
    """
    Validate that all decisions in EPOCH.md have assigned_to fields.

    Args:
        epoch_content: Content of EPOCH.md file

    Returns:
        ValidationResult with warnings for decisions lacking assigned_to
    """
    result = ValidationResult()
    decisions = parse_epoch_decisions(epoch_content)

    for decision_id, data in decisions.items():
        if not data.get("assigned_to"):
            result.warnings.append(f"{decision_id} has no assigned_to field")

    return result


def validate_chapter_traceability(chapter_content: str, chapter_id: str) -> ValidationResult:
    """
    Validate that chapter file has implements_decisions field.

    Args:
        chapter_content: Content of chapter file
        chapter_id: Chapter ID for error messages

    Returns:
        ValidationResult with warnings if field is missing
    """
    result = ValidationResult()
    chapter_data = parse_chapter_refs(chapter_content, chapter_id)

    if not chapter_data.get("implements_decisions"):
        result.warnings.append(f"{chapter_id} missing implements_decisions field")

    return result


def validate_bidirectional(
    epoch_decisions: dict[str, dict],
    chapter_refs: dict[str, dict]
) -> ValidationResult:
    """
    Validate bidirectional consistency between decisions and chapters.

    Checks:
    1. Every decision assigned_to a chapter is claimed by that chapter
    2. Every chapter implements_decisions entry exists in epoch

    Args:
        epoch_decisions: Dict mapping decision ID to {assigned_to: [{arc, chapters}]}
        chapter_refs: Dict mapping "arc/chapter_id" to {implements_decisions: []}

    Returns:
        ValidationResult with orphan_decisions and orphan_chapters
    """
    result = ValidationResult()
    result.is_consistent = True

    # Build set of all decision->chapter assignments from epoch
    decision_to_chapters: dict[str, set[str]] = {}
    for decision_id, data in epoch_decisions.items():
        decision_to_chapters[decision_id] = set()
        for assignment in data.get("assigned_to", []):
            arc = assignment["arc"]
            for chapter_id in assignment["chapters"]:
                decision_to_chapters[decision_id].add(f"{arc}/{chapter_id}")

    # Build set of all chapter->decision claims
    chapter_to_decisions: dict[str, set[str]] = {}
    for chapter_path, data in chapter_refs.items():
        chapter_to_decisions[chapter_path] = set(data.get("implements_decisions", []))

    # Check 1: Decisions assigned to chapters that don't claim them
    for decision_id, assigned_chapters in decision_to_chapters.items():
        for chapter_path in assigned_chapters:
            if chapter_path not in chapter_to_decisions:
                # Chapter doesn't exist or has no implements_decisions
                result.orphan_decisions.append(decision_id)
                result.is_consistent = False
            elif decision_id not in chapter_to_decisions.get(chapter_path, set()):
                # Chapter exists but doesn't claim this decision
                result.orphan_decisions.append(decision_id)
                result.is_consistent = False

    # Check 2: Chapters claiming decisions that don't exist
    all_decision_ids = set(epoch_decisions.keys())
    for chapter_path, claimed_decisions in chapter_to_decisions.items():
        for decision_id in claimed_decisions:
            if decision_id not in all_decision_ids:
                result.errors.append(f"{chapter_path} claims {decision_id} which doesn't exist")
                result.is_consistent = False

    # Deduplicate orphan lists
    result.orphan_decisions = list(set(result.orphan_decisions))

    return result


def validate_full_coverage(epoch_path: Path, arcs_dir: Path) -> ValidationResult:
    """
    Validate full decision-to-chapter traceability across the system.

    This is the main entry point for the audit command.

    Args:
        epoch_path: Path to EPOCH.md file
        arcs_dir: Path to arcs directory containing chapter files

    Returns:
        ValidationResult with all warnings and errors
    """
    result = ValidationResult()

    # Read and parse EPOCH.md
    if not epoch_path.exists():
        result.errors.append(f"EPOCH.md not found at {epoch_path}")
        result.is_consistent = False
        return result

    epoch_content = epoch_path.read_text(encoding="utf-8")
    epoch_decisions = parse_epoch_decisions(epoch_content)

    # Check decisions for assigned_to
    decision_result = validate_decision_coverage(epoch_content)
    result.warnings.extend(decision_result.warnings)

    # Find and parse all chapter files
    chapter_refs: dict[str, dict] = {}
    for arc_dir in arcs_dir.iterdir():
        if not arc_dir.is_dir():
            continue
        arc_name = arc_dir.name
        for chapter_file in arc_dir.glob("CH-*.md"):
            chapter_content = chapter_file.read_text(encoding="utf-8")
            # Extract chapter ID from filename or content
            chapter_id_match = re.search(r'\*\*Chapter ID:\*\*\s*(CH-\d+)', chapter_content)
            if chapter_id_match:
                chapter_id = chapter_id_match.group(1)
                chapter_path = f"{arc_name}/{chapter_id}"
                chapter_data = parse_chapter_refs(chapter_content, chapter_id)
                chapter_refs[chapter_path] = chapter_data

                # Check individual chapter for implements_decisions
                chapter_result = validate_chapter_traceability(chapter_content, chapter_id)
                result.warnings.extend(chapter_result.warnings)

    # Run bidirectional validation
    bidirectional_result = validate_bidirectional(epoch_decisions, chapter_refs)
    result.errors.extend(bidirectional_result.errors)
    result.orphan_decisions = bidirectional_result.orphan_decisions
    result.orphan_chapters = bidirectional_result.orphan_chapters
    result.is_consistent = bidirectional_result.is_consistent and len(result.errors) == 0

    return result


if __name__ == "__main__":
    import sys

    # Default paths for HAIOS
    epoch_path = Path(".claude/haios/epochs/E2_4/EPOCH.md")
    arcs_dir = Path(".claude/haios/epochs/E2_4/arcs")

    result = validate_full_coverage(epoch_path, arcs_dir)

    print("=== Decision Coverage Audit ===\n")

    if result.warnings:
        print("Warnings:")
        for w in result.warnings:
            print(f"  - {w}")
        print()

    if result.errors:
        print("Errors:")
        for e in result.errors:
            print(f"  - {e}")
        print()

    if result.orphan_decisions:
        print(f"Orphan Decisions: {result.orphan_decisions}")

    if result.is_consistent:
        print("Status: CONSISTENT")
        sys.exit(0)
    else:
        print("Status: INCONSISTENT")
        sys.exit(1)
