# generated: 2025-12-21
# System Auto: last updated on: 2026-01-21T22:19:45
"""
DEPRECATED: Use GovernanceLayer.validate_template() instead.

Migration path (E2-252):
    from governance_layer import GovernanceLayer
    layer = GovernanceLayer()
    result = layer.validate_template(file_path)

Or via CLI:
    python .claude/haios/modules/cli.py validate <file>

Or via justfile:
    just validate <file>

---

Template validation module for HAIOS plugin.

E2-120 Phase 2c: Migrated from ValidateTemplate.ps1.

Core functions:
1. get_template_registry() - Return template type definitions
2. extract_yaml_header() - Parse YAML frontmatter from content
3. parse_yaml() - Convert YAML text to dict
4. count_references() - Count @ references in content
5. validate_template() - Main validation function
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

# Project root is 4 levels up from .claude/haios/lib/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def get_template_registry() -> dict[str, dict[str, Any]]:
    """Return template type registry with validation rules.

    Each template type defines:
    - required_fields: List of required YAML fields
    - optional_fields: List of optional YAML fields
    - allowed_status: List of valid status values
    - expected_sections: List of expected ## headings (v1.4 governance)

    Returns:
        Dictionary mapping template types to their validation rules.
    """
    return {
        "checkpoint": {
            "required_fields": ["template", "status", "date", "version", "author", "project_phase"],
            "optional_fields": [
                "previous_checkpoint", "directive_id", "title", "session", "lifecycle_phase",
                "subtype", "backlog_ids", "parent_id", "blocked_by", "related", "milestone",
                "prior_session", "memory_refs",
            ],
            "allowed_status": ["draft", "active", "complete", "archived"],
            "expected_sections": [],  # Checkpoints have flexible structure
        },
        "implementation_plan": {
            "required_fields": ["template", "status", "date", "backlog_id"],
            "optional_fields": [
                "version", "author", "plan_id", "title", "session", "priority",
                "lifecycle_phase", "subtype", "directive_id", "parent_id", "completed_session",
                "completion_note", "spawned_by", "blocked_by", "related", "milestone",
                "parent_plan", "children", "absorbs", "enables", "execution_layer",
            ],
            "allowed_status": ["draft", "ready", "approved", "rejected", "complete"],
            "expected_sections": [
                "Goal",
                "Effort Estimation (Ground Truth)",
                "Current State vs Desired State",
                "Tests First (TDD)",
                "Detailed Design",
                "Implementation Steps",
                "Verification",
                "Risks & Mitigations",
                "Progress Tracker",
                "Ground Truth Verification (Before Closing)",
            ],
        },
        "architecture_decision_record": {
            "required_fields": ["template", "status", "date", "adr_id"],
            "optional_fields": [
                "version", "author", "title", "session", "decision", "approved_by",
                "approved_date", "lifecycle_phase", "subtype", "backlog_id", "backlog_ids",
                "memory_refs", "spawned_by", "spawns", "blocked_by", "related", "milestone",
            ],
            "allowed_status": ["proposed", "accepted", "rejected", "superseded", "deprecated"],
            "expected_sections": [],  # ADRs have flexible structure
        },
        "investigation": {
            "required_fields": ["template", "status", "date", "backlog_id"],
            "optional_fields": [
                "title", "author", "session", "lifecycle_phase", "subtype",
                "spawned_by", "spawns", "blocked_by", "related", "milestone",
                "memory_refs",
            ],
            "allowed_status": ["draft", "active", "pending", "closed", "complete", "archived"],
            "expected_sections": [
                "Context",
                "Prior Work Query",
                "Objective",
                "Scope",
                "Hypotheses",
                "Exploration Plan",
                "Evidence Collection",
                "Findings",
                "Spawned Work Items",
                "Ground Truth Verification",
                "Closure Checklist",
            ],
        },
        "report": {
            "required_fields": ["template", "status", "date"],
            "optional_fields": [
                "title", "author", "session", "tags", "lifecycle_phase", "subtype",
                "backlog_ids", "directive_id", "report_id", "version", "spawned_by",
                "blocked_by", "related", "milestone",
            ],
            "allowed_status": ["draft", "active", "complete", "archived", "final", "reviewed", "disputed"],
            "expected_sections": [],  # Reports have flexible structure
        },
        "readme": {
            "required_fields": ["template", "status", "date", "component"],
            "optional_fields": [
                "version", "owner", "author", "title", "lifecycle_phase", "subtype",
                "spawned_by", "related",
            ],
            "allowed_status": ["draft", "active", "deprecated", "archived"],
            "expected_sections": [],  # READMEs have flexible structure
        },
        "backlog_item": {
            "required_fields": ["template", "status", "date", "backlog_id", "priority", "complexity", "category"],
            "optional_fields": [
                "version", "author", "title", "lifecycle_phase", "subtype",
                "spawned_by", "blocks", "blocked_by", "memory_refs", "related", "milestone",
            ],
            "allowed_status": ["proposed", "researching", "ready", "implementing", "cancelled", "complete"],
            "allowed_priority": ["critical", "high", "medium", "low"],
            "allowed_complexity": ["small", "medium", "large", "unknown"],
            "allowed_category": ["enhancement", "technical_debt", "bug", "research", "documentation"],
            "expected_sections": [],  # Backlog items have flexible structure
        },
        "work_item": {
            # WORK-001: Updated for universal work item structure
            "required_fields": ["template", "status", "id", "title", "current_node", "type"],
            "optional_fields": [
                # Universal fields
                "owner", "created", "closed", "priority", "effort",
                "requirement_refs", "source_files", "acceptance_criteria",  # WORK-001: Pipeline traceability
                "artifacts", "extensions",  # WORK-001: Build outputs and project-specific
                "blocked_by", "blocks", "enables", "node_history",
                "cycle_docs", "memory_refs", "version",
                # Legacy fields (backward compat)
                "milestone", "category", "spawned_by", "spawned_by_investigation",
                "operator_decisions", "documents", "related",
            ],
            "allowed_status": ["active", "blocked", "complete", "archived"],
            "allowed_types": ["feature", "investigation", "bug", "chore", "spike"],  # WORK-001
            "expected_sections": ["Context", "Deliverables"],  # Removed "Current State" as optional
        },
    }


def extract_yaml_header(content: str) -> Optional[str]:
    """Extract YAML frontmatter from content.

    Looks for content between --- markers at the start of the file.
    Skips lines starting with # generated: or # System Auto:

    Args:
        content: File content string

    Returns:
        YAML content string, or None if no valid header found.
    """
    # Strip BOM if present at start
    if content.startswith("\ufeff"):
        content = content[1:]

    lines = content.split("\n")
    in_yaml = False
    yaml_lines = []
    yaml_start = -1
    yaml_end = -1

    for i, line in enumerate(lines):
        stripped = line.rstrip("\r")

        if stripped == "---" and not in_yaml:
            in_yaml = True
            yaml_start = i
        elif stripped == "---" and in_yaml:
            yaml_end = i
            break
        elif in_yaml:
            # Skip timestamp lines added by PostToolUse hook
            if not re.match(r"^#\s*(generated:|System Auto:)", stripped):
                yaml_lines.append(stripped)

    if yaml_start >= 0 and yaml_end > yaml_start:
        return "\n".join(yaml_lines)

    return None


def parse_yaml_full(yaml_text: str) -> dict[str, Any]:
    """Parse YAML with full nested structure support.

    Uses PyYAML to handle nested dicts, lists, etc.
    Used for work file integrity validation which needs cycle_docs, documents, node_history.

    Args:
        yaml_text: YAML content string

    Returns:
        Dictionary with full nested structure.
    """
    try:
        return yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError:
        return {}


def parse_yaml(yaml_text: str) -> dict[str, str]:
    """Parse simple YAML key: value pairs into dict.

    Handles:
    - Simple key: value pairs
    - Quoted values (single or double quotes)
    - Empty values

    Args:
        yaml_text: YAML content string

    Returns:
        Dictionary of parsed key-value pairs.
    """
    result = {}
    lines = yaml_text.split("\n")

    for line in lines:
        match = re.match(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()

            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            result[key] = value

    return result


def count_references(content: str) -> int:
    """Count @ references in content.

    Matches patterns like @docs/README.md, @path/to/file.ext

    Args:
        content: File content string

    Returns:
        Number of @ references found.
    """
    pattern = r"@[a-zA-Z0-9_./-]+"
    matches = re.findall(pattern, content)
    return len(matches)


def get_expected_sections(template_type: str) -> list[str]:
    """Get expected sections for a template type.

    Part of v1.4 governance - section skip validation.

    Args:
        template_type: Template type (e.g., 'implementation_plan')

    Returns:
        List of expected section headings, or empty list if unknown type.
    """
    registry = get_template_registry()
    if template_type not in registry:
        return []
    return registry[template_type].get("expected_sections", [])


def extract_sections(content: str) -> list[str]:
    """Extract ## section headings from content.

    Args:
        content: File content string

    Returns:
        List of section heading names (without ## prefix).
    """
    pattern = r"^##\s+(.+)$"
    matches = re.findall(pattern, content, re.MULTILINE)
    return [m.strip() for m in matches]


def is_placeholder_content(text: str) -> bool:
    """Detect if text is placeholder-only content.

    Placeholder patterns:
    - [bracketed text] - common template placeholder
    - TODO, TBD, FIXME - work markers
    - Very short content (<20 chars after stripping)

    Args:
        text: Section content to check

    Returns:
        True if content appears to be placeholder-only.
    """
    if not text:
        return True

    # Strip markdown formatting
    stripped = re.sub(r'[#*_`\->\n\r]', ' ', text).strip()

    # Very short content is likely placeholder
    if len(stripped) < 20:
        return True

    # Check for placeholder patterns
    # Content is placeholder if ONLY placeholder patterns exist
    non_placeholder = re.sub(r'\[.*?\]', '', stripped)  # Remove [brackets]
    non_placeholder = re.sub(r'\bTODO\b.*', '', non_placeholder, flags=re.IGNORECASE)
    non_placeholder = re.sub(r'\bTBD\b.*', '', non_placeholder, flags=re.IGNORECASE)
    non_placeholder = re.sub(r'\bFIXME\b.*', '', non_placeholder, flags=re.IGNORECASE)
    non_placeholder = non_placeholder.strip()

    # If nothing left after removing placeholders, it's placeholder content
    return len(non_placeholder) < 20


def check_section_coverage(template_type: str, content: str) -> dict[str, Any]:
    """Check if all expected sections are present or have SKIPPED marker.

    Part of v1.4 governance - enforces skip rationale requirement.
    E2-145: Also detects placeholder-only content in sections.

    Args:
        template_type: Template type (e.g., 'implementation_plan')
        content: File content string

    Returns:
        Dict with:
        - all_covered: bool (True if all sections present or skipped)
        - missing_sections: list of sections without SKIPPED marker
        - skipped_sections: list of sections with SKIPPED marker
        - present_sections: list of sections with content
        - placeholder_sections: list of sections with only placeholder content
    """
    result = {
        "all_covered": True,
        "missing_sections": [],
        "skipped_sections": [],
        "present_sections": [],
        "placeholder_sections": [],
    }

    expected = get_expected_sections(template_type)
    if not expected:
        # No section requirements for this template type
        return result

    found_sections = extract_sections(content)

    for section in expected:
        # Check if section heading exists
        if section in found_sections:
            # Find the section content to check for SKIPPED marker
            section_pattern = rf"^##\s+{re.escape(section)}\s*\n(.*?)(?=^##|\Z)"
            match = re.search(section_pattern, content, re.MULTILINE | re.DOTALL)

            if match:
                section_content = match.group(1)
                # Check for SKIPPED marker first (case-insensitive)
                if re.search(r"\*\*SKIPPED:\*\*", section_content, re.IGNORECASE):
                    result["skipped_sections"].append(section)
                elif is_placeholder_content(section_content):
                    # Section exists but only has placeholder content
                    result["placeholder_sections"].append(section)
                    result["all_covered"] = False
                else:
                    result["present_sections"].append(section)
        else:
            # Section heading not found at all
            result["missing_sections"].append(section)
            result["all_covered"] = False

    return result


def validate_cycle_docs_consistency(metadata: dict) -> list[str]:
    """Validate cycle_docs matches documents list.

    Checks that if documents.plans or documents.investigations have entries,
    the corresponding cycle_docs.plan_id or cycle_docs.investigation_id exists.

    Args:
        metadata: Parsed YAML frontmatter dict with cycle_docs and documents keys

    Returns:
        List of error messages, empty if valid.
    """
    errors = []
    cycle_docs = metadata.get("cycle_docs", {}) or {}
    documents = metadata.get("documents", {}) or {}

    # Check: If documents.plans has entries, cycle_docs should have plan_id
    plans = documents.get("plans", []) or []
    if plans and not cycle_docs.get("plan_id"):
        errors.append("documents.plans has entries but cycle_docs.plan_id missing")

    # Check: If documents.investigations has entries, cycle_docs should have investigation_id
    investigations = documents.get("investigations", []) or []
    if investigations and not cycle_docs.get("investigation_id"):
        errors.append("documents.investigations has entries but cycle_docs.investigation_id missing")

    return errors


def validate_node_history_integrity(metadata: dict) -> list[str]:
    """Validate node_history has consistent timestamps.

    Checks:
    - Each entry has 'node' and 'entered' fields
    - Timestamps are monotonically increasing (entered[i] >= entered[i-1])

    Args:
        metadata: Parsed YAML frontmatter dict with node_history key

    Returns:
        List of error messages, empty if valid.
    """
    errors = []
    node_history = metadata.get("node_history", []) or []

    prev_entered = None
    for i, entry in enumerate(node_history):
        # Check required fields
        if "node" not in entry:
            errors.append(f"node_history[{i}] missing 'node' field")
        if "entered" not in entry:
            errors.append(f"node_history[{i}] missing 'entered' field")
            continue  # Can't check ordering without entered

        current_entered = entry.get("entered")

        # Check timestamp ordering (must be >= previous)
        if prev_entered and current_entered:
            if current_entered < prev_entered:
                errors.append(
                    f"node_history[{i}] has out-of-order timestamp "
                    f"({current_entered} < {prev_entered})"
                )

        prev_entered = current_entered

    return errors


def validate_template(file_path: str) -> dict[str, Any]:
    """Validate a template file against its schema.

    Main validation function that:
    1. Checks file exists
    2. Extracts and parses YAML header
    3. Validates template type
    4. Checks required fields
    5. Validates status enum
    6. Counts @ references (minimum 2 required)
    7. Warns about unknown fields

    Args:
        file_path: Path to template file

    Returns:
        Validation result dict with:
        - is_valid: bool
        - template_type: str or None
        - errors: list of error messages
        - warnings: list of warning messages
        - metadata: parsed YAML fields
        - reference_count: int
    """
    result = {
        "is_valid": True,
        "template_path": file_path,
        "template_type": None,
        "errors": [],
        "warnings": [],
        "metadata": {},
        "reference_count": 0,
        "validation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    registry = get_template_registry()

    # Check file exists
    path = Path(file_path)
    if not path.exists():
        result["is_valid"] = False
        result["errors"].append(f"File not found: {file_path}")
        return result

    # Read file content
    try:
        content = path.read_text(encoding="utf-8-sig")
    except Exception as e:
        result["is_valid"] = False
        result["errors"].append(f"Error reading file: {e}")
        return result

    if not content.strip():
        result["is_valid"] = False
        result["errors"].append("File is empty")
        return result

    # Extract YAML header
    yaml_content = extract_yaml_header(content)
    if not yaml_content:
        result["is_valid"] = False
        result["errors"].append("Missing YAML header in template")
        return result

    # Parse YAML
    metadata = parse_yaml(yaml_content)
    result["metadata"] = metadata

    # Validate template type
    if "template" not in metadata:
        result["is_valid"] = False
        result["errors"].append("Missing 'template' field in YAML header")
        return result

    template_type = metadata["template"]
    result["template_type"] = template_type

    if template_type not in registry:
        valid_types = ", ".join(sorted(registry.keys()))
        result["is_valid"] = False
        result["errors"].append(f"Unknown template type '{template_type}'. Valid types: {valid_types}")
        return result

    rules = registry[template_type]

    # Check required fields
    missing_fields = []
    for field in rules["required_fields"]:
        if field not in metadata:
            missing_fields.append(field)

    if missing_fields:
        result["is_valid"] = False
        result["errors"].append(f"Missing required fields: {', '.join(missing_fields)}")

    # Validate status enum
    if "status" in metadata:
        status = metadata["status"]
        if status not in rules["allowed_status"]:
            result["is_valid"] = False
            allowed = ", ".join(rules["allowed_status"])
            result["errors"].append(f"Invalid status '{status}' for {template_type} template. Allowed: {allowed}")

    # Validate additional enums for backlog_item
    if template_type == "backlog_item":
        if "priority" in metadata and metadata["priority"] not in rules.get("allowed_priority", []):
            result["is_valid"] = False
            allowed = ", ".join(rules.get("allowed_priority", []))
            result["errors"].append(f"Invalid priority '{metadata['priority']}'. Allowed: {allowed}")

        if "complexity" in metadata and metadata["complexity"] not in rules.get("allowed_complexity", []):
            result["is_valid"] = False
            allowed = ", ".join(rules.get("allowed_complexity", []))
            result["errors"].append(f"Invalid complexity '{metadata['complexity']}'. Allowed: {allowed}")

        if "category" in metadata and metadata["category"] not in rules.get("allowed_category", []):
            result["is_valid"] = False
            allowed = ", ".join(rules.get("allowed_category", []))
            result["errors"].append(f"Invalid category '{metadata['category']}'. Allowed: {allowed}")

    # WORK-001: Validate type enum for work_item template
    if template_type == "work_item":
        if "type" in metadata and metadata["type"] not in rules.get("allowed_types", []):
            result["is_valid"] = False
            allowed = ", ".join(rules.get("allowed_types", []))
            result["errors"].append(f"Invalid type '{metadata['type']}'. Allowed: {allowed}")

    # Check for unknown fields (warnings only)
    all_known_fields = set(rules["required_fields"]) | set(rules.get("optional_fields", []))
    for key in metadata.keys():
        if key not in all_known_fields:
            result["warnings"].append(f"Unknown field '{key}' for {template_type} template")

    # Count @ references
    ref_count = count_references(content)
    result["reference_count"] = ref_count

    if ref_count < 2:
        result["is_valid"] = False
        result["errors"].append(f"Only {ref_count} @ reference(s) found (minimum 2 required)")

    # Check section coverage (v1.4 governance)
    section_result = check_section_coverage(template_type, content)
    result["section_coverage"] = section_result

    if not section_result["all_covered"]:
        result["is_valid"] = False
        error_parts = []
        if section_result["missing_sections"]:
            missing = ", ".join(section_result["missing_sections"])
            error_parts.append(f"Missing sections: {missing}")
        if section_result.get("placeholder_sections"):
            placeholders = ", ".join(section_result["placeholder_sections"])
            error_parts.append(f"Placeholder-only sections: {placeholders}")
        result["errors"].append(
            f"{'; '.join(error_parts)}. "
            f"Add **SKIPPED:** <rationale> or include real content."
        )

    # Work file integrity validation (E2-163)
    if template_type == "work_item":
        # Need full YAML parsing for nested structures
        full_metadata = parse_yaml_full(yaml_content)

        cycle_docs_errors = validate_cycle_docs_consistency(full_metadata)
        if cycle_docs_errors:
            result["is_valid"] = False
            for err in cycle_docs_errors:
                result["errors"].append(f"Work file integrity: {err}")

        node_history_errors = validate_node_history_integrity(full_metadata)
        if node_history_errors:
            result["is_valid"] = False
            for err in node_history_errors:
                result["errors"].append(f"Work file integrity: {err}")

    return result


def classify_verification_type(file_path: str, expected_state: str) -> str:
    """Classify verification type based on file path and expected state patterns.

    Types (from INV-042):
    - file-check: Path to file, verify existence/content
    - grep-check: Grep: pattern prefix
    - test-run: tests/ path or pytest reference
    - json-verify: .json file reference
    - human-judgment: Semantic description only

    Args:
        file_path: File path from table (may include backticks)
        expected_state: Expected state description

    Returns:
        One of: 'file-check', 'grep-check', 'test-run', 'json-verify', 'human-judgment'
    """
    # Clean file_path (remove backticks if present)
    clean_path = file_path.strip('`')

    # Grep check: starts with Grep:
    if clean_path.lower().startswith('grep:'):
        return 'grep-check'

    # JSON verify: .json file
    if clean_path.endswith('.json'):
        return 'json-verify'

    # Test run: tests/ path or pytest in expected state
    if 'tests/' in clean_path or 'test_' in clean_path:
        return 'test-run'
    if 'pytest' in expected_state.lower() or 'tests pass' in expected_state.lower():
        return 'test-run'

    # File check: has file extension (indicates actual file)
    if '.' in clean_path and not clean_path.startswith('.'):
        return 'file-check'
    # Also catch paths starting with . but having extension after first component
    if clean_path.startswith('.') and '/' in clean_path:
        path_after_dot = clean_path.split('/', 1)[-1] if '/' in clean_path else ''
        if '.' in path_after_dot:
            return 'file-check'

    # Default: human judgment for semantic descriptions
    return 'human-judgment'


def parse_ground_truth_table(content: str) -> list[dict]:
    """Parse Ground Truth Verification table from plan content.

    Extracts rows from the markdown table in the Ground Truth Verification section.

    Args:
        content: Full markdown content of implementation plan

    Returns:
        List of dicts with keys: file_path, expected_state, is_checked, notes, verification_type
    """
    items = []

    # Find the Ground Truth Verification section
    section_pattern = r"## Ground Truth Verification.*?\n(.*?)(?=\n##|\Z)"
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)
    if not section_match:
        return items

    section_content = section_match.group(1)

    # Parse markdown table rows: | File | Expected State | Verified | Notes |
    # Skip header row (contains "File") and separator row (contains ---)
    row_pattern = r"\|\s*`([^`]+)`\s*\|\s*([^|]+)\s*\|\s*\[([x ])\]\s*\|\s*([^|]*)\|"

    for match in re.finditer(row_pattern, section_content, re.IGNORECASE):
        file_path = match.group(1).strip()
        expected_state = match.group(2).strip()
        is_checked = match.group(3).lower() == 'x'
        notes = match.group(4).strip()

        verification_type = classify_verification_type(file_path, expected_state)

        items.append({
            'file_path': file_path,
            'expected_state': expected_state,
            'is_checked': is_checked,
            'notes': notes,
            'verification_type': verification_type,
        })

    return items


# CLI entry point
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python validate.py <file_path> [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    json_output = "--json" in sys.argv

    result = validate_template(file_path)

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        if result["is_valid"]:
            print(f"Validation Passed")
            print(f"  Type: {result['template_type']}")
            print(f"  References: {result['reference_count']}")
        else:
            print(f"Validation Failed")
            print(f"  File: {file_path}")
            for error in result["errors"]:
                print(f"  {error}")

        if result["warnings"]:
            print("\nWarnings:")
            for warning in result["warnings"]:
                print(f"  {warning}")

    sys.exit(0 if result["is_valid"] else 1)
