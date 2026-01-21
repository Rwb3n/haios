# generated: 2025-12-23
# System Auto: last updated on: 2026-01-03T14:36:01
"""Node-Cycle binding operations (E2-154 scaffold-on-entry, E2-155 exit gates).

This module provides functions for:
- Detecting work file node transitions
- Scaffolding required cycle documents based on node-cycle bindings
- Checking exit criteria before allowing node transitions (soft gates)

Architecture Reference: INV-022 (Work-Cycle-DAG Unified Architecture)
"""
from pathlib import Path
from typing import Optional, Dict, Any
import re
import yaml

def load_node_cycle_bindings() -> Dict[str, Any]:
    """Load node-cycle bindings from unified config (E2-246).

    Returns:
        Dict mapping node names to their binding configs.
        Empty dict if config missing or invalid.
    """
    try:
        from config import ConfigLoader
        return ConfigLoader.get().node_bindings
    except Exception:
        return {}


def get_node_binding(node: str) -> Optional[Dict[str, Any]]:
    """Get binding config for a specific node.

    Args:
        node: Node name (e.g., "plan", "discovery", "implement")

    Returns:
        Binding config dict with 'cycle' and 'scaffold' keys, or None.
    """
    bindings = load_node_cycle_bindings()
    return bindings.get(node)


def detect_node_change(old_content: str, new_content: str) -> Optional[str]:
    """Detect if current_node field changed in work file.

    Args:
        old_content: Previous file content
        new_content: Updated file content

    Returns:
        New node name if changed, None otherwise.
    """
    old_match = re.search(r'^current_node:\s*(\w+)', old_content, re.MULTILINE)
    new_match = re.search(r'^current_node:\s*(\w+)', new_content, re.MULTILINE)

    if not new_match:
        return None

    old_node = old_match.group(1) if old_match else None
    new_node = new_match.group(1)

    if old_node != new_node:
        return new_node
    return None


def check_doc_exists(pattern: str, base_path: Path = Path(".")) -> Optional[Path]:
    """Check if a document matching pattern exists.

    Args:
        pattern: Glob pattern (e.g., "docs/plans/PLAN-E2-154-*.md")
        base_path: Base path for glob search

    Returns:
        First matching Path if found, None otherwise.
    """
    matches = list(base_path.glob(pattern))
    return matches[0] if matches else None


def build_scaffold_command(template: str, work_id: str, title: str) -> str:
    """Build scaffold command from template.

    Args:
        template: Command template with {id} and {title} placeholders
        work_id: Work item ID (e.g., "E2-154")
        title: Work item title

    Returns:
        Complete command string with placeholders replaced.
    """
    return template.replace("{id}", work_id).replace("{title}", title)


def extract_work_id(path: Path) -> Optional[str]:
    """Extract work ID from work file path.

    E2-212: Supports both directory structure and flat file.

    Args:
        path: Path to work file
              - Directory: "docs/work/active/E2-154/WORK.md"
              - Flat: "docs/work/active/WORK-E2-154-foo.md"

    Returns:
        Work ID (e.g., "E2-154") or None if not a work file.
    """
    # E2-212: Check for directory structure first
    if path.name == "WORK.md":
        # Parent directory name is the work ID
        parent_name = path.parent.name
        if re.match(r'(?:E2|INV|TD|V)-\d+', parent_name):
            return parent_name

    # Fall back to flat file pattern
    match = re.search(r'WORK-((?:E2|INV|TD|V)-\d+)', path.name)
    return match.group(1) if match else None


def extract_title(content: str) -> str:
    """Extract title from work file frontmatter.

    Args:
        content: File content with YAML frontmatter

    Returns:
        Title string, or "Untitled" if not found.
    """
    match = re.search(r'^title:\s*["\']?([^"\'\n]+)["\']?', content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def update_cycle_docs(path: Path, doc_type: str, doc_path: str) -> None:
    """Update cycle_docs field in work file frontmatter.

    Args:
        path: Path to work file
        doc_type: Document type (e.g., "plan", "investigation")
        doc_path: Path to the scaffolded document
    """
    content = path.read_text(encoding="utf-8")

    # Find cycle_docs section and add/update entry
    if "cycle_docs: {}" in content:
        # Empty cycle_docs - replace with first entry
        content = content.replace(
            "cycle_docs: {}",
            f"cycle_docs:\n  {doc_type}: {doc_path}"
        )
    elif "cycle_docs:" in content:
        # Append to existing cycle_docs
        content = re.sub(
            r'(cycle_docs:\n)',
            f'\\1  {doc_type}: {doc_path}\n',
            content
        )
    else:
        # No cycle_docs field - don't modify
        return

    path.write_text(content, encoding="utf-8")


# =============================================================================
# Exit Gate Functions (E2-155)
# =============================================================================


def get_exit_criteria(node: str) -> list:
    """Get exit criteria for a node.

    Args:
        node: Node name (e.g., "discovery", "plan")

    Returns:
        List of criterion dicts, or empty list if none defined.
    """
    binding = get_node_binding(node)
    if not binding:
        return []
    return binding.get("exit_criteria", [])


def detect_node_exit_attempt(old_string: str, new_string: str) -> Optional[tuple]:
    """Detect if edit is changing current_node field.

    Args:
        old_string: The text being replaced (from Edit tool)
        new_string: The replacement text (from Edit tool)

    Returns:
        (from_node, to_node) tuple if changing, None otherwise.
    """
    old_match = re.search(r'current_node:\s*(\w+)', old_string)
    new_match = re.search(r'current_node:\s*(\w+)', new_string)

    # Both sides must have current_node for this to be a transition
    if not old_match or not new_match:
        return None

    old_node = old_match.group(1)
    new_node = new_match.group(1)

    if old_node != new_node:
        return (old_node, new_node)
    return None


def check_exit_criteria(node: str, work_id: str, base_path: Path = Path(".")) -> list:
    """Check all exit criteria for a node.

    Args:
        node: Node being exited (e.g., "discovery")
        work_id: Work item ID (e.g., "E2-155")
        base_path: Base path for file lookups

    Returns:
        List of failure messages (empty if all criteria pass).
    """
    criteria = get_exit_criteria(node)
    failures = []

    for criterion in criteria:
        result = _check_single_criterion(criterion, work_id, base_path)
        if result:
            failures.append(result)

    return failures


def _check_single_criterion(criterion: dict, work_id: str, base_path: Path) -> Optional[str]:
    """Check a single exit criterion.

    Args:
        criterion: Criterion dict from config
        work_id: Work item ID
        base_path: Base path for file lookups

    Returns:
        Failure message string, or None if criterion passes.
    """
    criterion_type = criterion.get("type")
    pattern = criterion.get("pattern", "").replace("{id}", work_id)
    message = criterion.get("message", "Exit criterion not met")

    # Find file matching pattern
    matches = list(base_path.glob(pattern))
    if not matches:
        return f"Required file not found: {pattern}"

    file_path = matches[0]
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return f"Cannot read file: {file_path}"

    if criterion_type == "file_status":
        field = criterion.get("field", "status")
        expected = criterion.get("value")
        match = re.search(rf'^{field}:\s*(\w+)', content, re.MULTILINE)
        if not match or match.group(1) != expected:
            return message

    elif criterion_type == "section_content":
        section = criterion.get("section", "")
        min_length = criterion.get("min_length", 1)
        # Find section content (from header to next ## or end)
        section_match = re.search(
            rf'{re.escape(section)}\n+(.*?)(?=\n## |\Z)',
            content,
            re.DOTALL
        )
        if not section_match:
            return message
        section_content = section_match.group(1).strip()
        if len(section_content) < min_length:
            return message

    return None


def build_exit_gate_warning(from_node: str, to_node: str, failures: list) -> str:
    """Build user-friendly warning message for exit gate violation.

    Args:
        from_node: Node being exited
        to_node: Target node
        failures: List of failure messages

    Returns:
        Formatted warning string for display to user.
    """
    lines = [
        f"[EXIT GATE] Transitioning from '{from_node}' to '{to_node}' with unmet criteria:",
    ]
    for failure in failures:
        lines.append(f"  - {failure}")
    lines.append("Consider completing these before proceeding.")
    return "\n".join(lines)
