# generated: 2025-12-20
# System Auto: last updated on: 2026-01-05T20:49:59
"""
PostToolUse Hook Handler (E2-085).

Post-processing for file operations:
1. Error capture (E2-130) - captures tool failures to memory
2. Memory auto-link (E2-238) - auto-links memory_refs on ingester_ingest
3. Timestamp injection - adds generated/last updated timestamps
4. Template validation - validates governed documents
5. Discoverable artifact refresh (INV-012) - refreshes status on skill/agent/command changes
6. Cycle transition logging (E2-097) - logs phase changes in plans
7. Investigation status sync (E2-140) - syncs INV-* file status on archive
8. Scaffold-on-entry (E2-154) - suggests scaffold commands on work file node changes
"""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def handle(hook_data: dict) -> Optional[str]:
    """
    Process PostToolUse hook.

    Args:
        hook_data: Parsed JSON from Claude Code containing:
            - tool_name: str (e.g., "Edit", "Write", "Bash")
            - tool_input: dict (for Write: file_path)
            - tool_response: dict (for Edit: filePath)

    Returns:
        Optional status message (mostly for logging).

    Side effects:
        - Captures tool errors to memory
        - Modifies files to add timestamps
        - May trigger validation scripts
        - May refresh status files
        - May log events
    """
    tool_name = hook_data.get("tool_name", "")
    messages = []

    # Part 0: Error capture (runs for ALL tools) - E2-130
    error_msg = _capture_errors(hook_data)
    if error_msg:
        messages.append(error_msg)

    # Part 0.5: Memory auto-link (E2-238) - for MCP ingester
    if tool_name == "mcp__haios-memory__ingester_ingest":
        autolink_msg = _auto_link_memory_refs(hook_data)
        if autolink_msg:
            messages.append(autolink_msg)
        return "\n".join(messages) if messages else None

    # File-specific processing only for editing tools
    if tool_name not in ("Edit", "MultiEdit", "Write"):
        return "\n".join(messages) if messages else None

    # Get file path based on tool type
    if tool_name == "Write":
        file_path = hook_data.get("tool_input", {}).get("file_path", "")
    else:
        file_path = hook_data.get("tool_response", {}).get("filePath", "")

    if not file_path:
        return None

    path = Path(file_path)
    if not path.exists():
        return None

    # Skip JSON files (no comment syntax)
    if path.suffix.lower() in (".json", ".jsonc"):
        return "\n".join(messages) if messages else None

    # Part 1: Timestamp injection
    timestamp_msg = _add_timestamp(path)
    if timestamp_msg:
        messages.append(timestamp_msg)

    # Part 2: Template validation (for governed paths)
    validation_msg = _validate_template(path)
    if validation_msg:
        messages.append(validation_msg)

    # Part 3: Discoverable artifact refresh
    refresh_msg = _refresh_discoverable_artifacts(path)
    if refresh_msg:
        messages.append(refresh_msg)

    # Part 4: Cycle transition logging (E2-097)
    cycle_msg = _log_cycle_transition(path)
    if cycle_msg:
        messages.append(cycle_msg)

    # Part 6: Investigation status sync (E2-140)
    sync_msg = _sync_investigation_status(path)
    if sync_msg:
        messages.append(sync_msg)

    # Part 7: Scaffold-on-entry (E2-154)
    scaffold_msg = _scaffold_on_node_entry(path, hook_data)
    if scaffold_msg:
        messages.append(scaffold_msg)

    return "\n".join(messages) if messages else None


def _capture_errors(hook_data: dict) -> Optional[str]:
    """
    Capture tool errors to memory (E2-130).

    Only captures actual failures, not false positives.
    Stores with type='tool_error' for queryability.

    E2-264: Module-first import via MemoryBridge.

    Args:
        hook_data: Hook data containing tool_name and tool_response

    Returns:
        Status message if error captured, None otherwise.
    """
    try:
        tool_name = hook_data.get("tool_name", "")
        tool_response = hook_data.get("tool_response", {})

        # E2-264: Module-first import via MemoryBridge
        modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        from memory_bridge import MemoryBridge
        bridge = MemoryBridge()

        # Check if this is an actual error
        if not bridge.is_actual_error(tool_name, tool_response):
            return None

        # Extract error message
        if tool_name == "Bash":
            error_msg = tool_response.get("stderr", "") or tool_response.get("stdout", "")
        else:
            error_msg = tool_response.get("error", str(tool_response)[:200])

        # Extract tool input summary
        tool_input = hook_data.get("tool_input", {})
        if isinstance(tool_input, dict):
            input_summary = str(tool_input)[:100]
        else:
            input_summary = str(tool_input)[:100]

        # Store the error via MemoryBridge
        result = bridge.capture_error(tool_name, error_msg, input_summary)

        if result.get("success"):
            return f"[ERROR CAPTURE] {tool_name} error stored (concept_id={result.get('concept_id')})"

    except Exception:
        pass  # Don't break the hook flow on capture errors

    return None


def _add_timestamp(path: Path) -> Optional[str]:
    """
    Add generated and last_updated timestamps to file.

    For Markdown files with YAML frontmatter: injects as YAML fields INSIDE frontmatter.
    For other files: injects as comments (legacy behavior).

    Returns status message or None.
    """
    try:
        content = path.read_text(encoding="utf-8")
        if not content:
            return None

        # Handle BOM if present (common from PowerShell-created files)
        if content.startswith('\ufeff'):
            content = content[1:]

        lines = content.split("\n")
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Check for YAML frontmatter (must start with ---)
        has_yaml = lines and lines[0].strip() == "---"
        yaml_end = -1
        if has_yaml:
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    yaml_end = i
                    break

        # For Markdown files WITH YAML frontmatter: inject AS YAML fields
        if path.suffix.lower() == ".md" and yaml_end > 0:
            return _add_yaml_timestamp(path, lines, yaml_end, current_date, timestamp)

        # For other files: use comment-based timestamp (legacy)
        return _add_comment_timestamp(path, lines, current_date, timestamp)

    except Exception as e:
        return None


def _add_yaml_timestamp(
    path: Path, lines: list, yaml_end: int, current_date: str, timestamp: str
) -> Optional[str]:
    """
    Inject timestamps AS YAML FIELDS inside frontmatter.

    Uses proper YAML parsing to preserve nested structures like node_history arrays.
    (E2-172: Fixed naive line-by-line parsing that corrupted nested YAML)

    Expected output format:
        ---
        template: checkpoint
        generated: 2025-12-21
        last_updated: 2025-12-21T14:00:00
        ---
    """
    import yaml

    # Parse YAML content properly (preserves nested structures)
    yaml_content = "\n".join(lines[1:yaml_end])
    try:
        fm = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError:
        # If YAML is invalid, fall back to not modifying
        return None

    # Check if generated exists, preserve original date
    if "generated" not in fm:
        fm["generated"] = current_date

    # Always update last_updated
    fm["last_updated"] = timestamp

    # Serialize back with proper YAML formatting
    new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Get content after frontmatter
    after_yaml = lines[yaml_end + 1:]

    # Skip legacy comment timestamps after frontmatter
    content_start = 0
    while content_start < len(after_yaml):
        line = after_yaml[content_start]
        # Skip lines that are legacy timestamps (comments with generated/System Auto)
        if re.match(r'^(#|//|REM|--)\s*(generated:|System Auto:)', line):
            content_start += 1
        else:
            break

    remaining_content = after_yaml[content_start:]

    # Build final content
    final_content = "---\n" + new_fm + "---\n" + "\n".join(remaining_content)

    path.write_text(final_content, encoding="utf-8")
    return f"[TIMESTAMP] Updated YAML frontmatter: {path.name}"


def _add_comment_timestamp(
    path: Path, lines: list, current_date: str, timestamp: str
) -> Optional[str]:
    """
    Add timestamps as comments (for non-YAML files).

    Legacy behavior retained for .py, .js, .sql, etc.
    """
    comment_prefix, comment_suffix = _get_comment_syntax(path.suffix.lower())

    # Find existing timestamps at start of file
    content_start = 0
    has_generated = False

    while content_start < len(lines):
        line = lines[content_start]
        if re.match(r'^(//|#|REM|--|<!--|\s*/\*).*generated:\s*', line):
            has_generated = True
            content_start += 1
        elif re.match(r'^(//|#|REM|--|<!--|\s*/\*).*System Auto:.*last updated on:', line):
            content_start += 1
        else:
            break

    # Preserve original generated date if found
    if has_generated:
        # Re-scan for the generated line to preserve it
        generated_line = None
        for line in lines[:content_start]:
            if re.match(r'^(//|#|REM|--|<!--|\s*/\*).*generated:\s*', line):
                generated_line = line
                break
    else:
        if comment_suffix:
            generated_line = f"{comment_prefix}generated: {current_date}{comment_suffix}"
        else:
            generated_line = f"{comment_prefix}generated: {current_date}"

    # Build timestamp line
    if comment_suffix:
        timestamp_line = f"{comment_prefix}System Auto: last updated on: {timestamp}{comment_suffix}"
    else:
        timestamp_line = f"{comment_prefix}System Auto: last updated on: {timestamp}"

    # Get remaining content
    remaining_content = "\n".join(lines[content_start:])

    # Build final content
    if remaining_content:
        final_content = f"{generated_line}\n{timestamp_line}\n{remaining_content}"
    else:
        final_content = f"{generated_line}\n{timestamp_line}"

    path.write_text(final_content, encoding="utf-8")
    return f"[TIMESTAMP] Updated comments: {path.name}"


def _get_comment_syntax(extension: str) -> tuple[str, str]:
    """Return (prefix, suffix) for comment syntax based on extension."""
    multi_line = {
        ".html": ("<!-- ", " -->"),
        ".htm": ("<!-- ", " -->"),
        ".css": ("/* ", " */"),
        ".scss": ("/* ", " */"),
        ".sass": ("/* ", " */"),
        ".less": ("/* ", " */"),
    }

    single_line = {
        ".js": "// ",
        ".ts": "// ",
        ".jsx": "// ",
        ".tsx": "// ",
        ".cs": "// ",
        ".java": "// ",
        ".cpp": "// ",
        ".c": "// ",
        ".go": "// ",
        ".rs": "// ",
        ".php": "// ",
        ".py": "# ",
        ".sh": "# ",
        ".ps1": "# ",
        ".rb": "# ",
        ".r": "# ",
        ".pl": "# ",
        ".bat": "REM ",
        ".cmd": "REM ",
        ".sql": "-- ",
    }

    if extension in multi_line:
        return multi_line[extension]
    if extension in single_line:
        return (single_line[extension], "")
    return ("# ", "")  # Default


def _validate_template(path: Path) -> Optional[str]:
    """
    Run template validation on governed paths using Python validate module.

    Returns validation message or None.
    """
    if path.suffix.lower() != ".md":
        return None

    # Check if in a template directory
    template_dirs = ["templates", "directives", "plans", "reports", "checkpoints"]
    path_str = str(path).replace("\\", "/")

    should_validate = any(f"/{d}/" in path_str for d in template_dirs)
    if not should_validate:
        return None

    try:
        # Import Python validate module from .claude/lib/
        lib_dir = Path(__file__).parent.parent.parent / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from validate import validate_file

        result = validate_file(str(path))

        if result.get("is_valid"):
            return f"[TEMPLATE VALIDATION] Valid: {path.name}"
        else:
            errors = result.get("errors", [])
            if errors:
                return f"[TEMPLATE VALIDATION] Issues in {path.name}: {'; '.join(errors)}"

    except ImportError:
        # validate.py not available (fallback silently)
        pass
    except Exception:
        pass

    return None


def _refresh_discoverable_artifacts(path: Path) -> Optional[str]:
    """
    Refresh status when skills/agents/commands are modified (INV-012).

    Uses Python status module to regenerate slim status.

    Returns status message or None.
    """
    path_str = str(path).replace("\\", "/")

    discoverable_patterns = [
        r"\.claude[\\/]skills[\\/]",
        r"\.claude[\\/]agents[\\/]",
        r"\.claude[\\/]commands[\\/]"
    ]

    is_discoverable = any(re.search(p, path_str) for p in discoverable_patterns)
    if not is_discoverable:
        return None

    try:
        # Import Python status module from .claude/lib/
        lib_dir = Path(__file__).parent.parent.parent / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from status import generate_slim_status

        # Generate and write slim status
        slim_status = generate_slim_status()
        slim_path = Path(".claude/haios-status-slim.json")
        slim_path.write_text(json.dumps(slim_status, indent=4), encoding="utf-8")

        return "[STATUS] Refreshed discoverable artifacts"

    except ImportError:
        # status.py not available (fallback silently)
        pass
    except Exception:
        pass

    return None


def _log_cycle_transition(path: Path) -> Optional[str]:
    """
    Log events when lifecycle_phase changes in plan or investigation files.

    E2-097: Plans (PLAN-*.md in plans/)
    E2-113: Investigations (INVESTIGATION-*.md in investigations/)

    Returns cycle message or None.
    """
    path_str = str(path).replace("\\", "/")
    is_plan = "plans" in path_str and "PLAN-" in path_str
    is_investigation = "investigations" in path_str and "INVESTIGATION-" in path_str
    if not is_plan and not is_investigation:
        return None

    if path.suffix.lower() != ".md":
        return None

    try:
        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Check for YAML frontmatter
        if not lines or lines[0] != "---":
            return None

        yaml_end = -1
        for i in range(1, len(lines)):
            if lines[i] == "---":
                yaml_end = i
                break

        if yaml_end < 0:
            return None

        yaml_content = "\n".join(lines[0:yaml_end + 1])

        # Extract cycle_phase and backlog_id
        phase_match = re.search(r'lifecycle_phase:\s*(\S+)', yaml_content)
        backlog_match = re.search(r'backlog_id:\s*(\S+)', yaml_content)

        if not phase_match or not backlog_match:
            return None

        cycle_phase = phase_match.group(1).strip().upper()
        backlog_id = backlog_match.group(1).strip()

        # Find events file
        events_path = Path(".claude/haios-events.jsonl")
        from_phase = None

        # Find last cycle_transition for this backlog_id
        if events_path.exists():
            for line in events_path.read_text(encoding="utf-8").split("\n"):
                if not line.strip():
                    continue
                if '"type": "cycle_transition"' in line and f'"{backlog_id}"' in line:
                    try:
                        event = json.loads(line)
                        if event.get("backlog_id") == backlog_id:
                            from_phase = event.get("to_phase")
                    except json.JSONDecodeError:
                        pass

        # Only log if phase changed
        if from_phase == cycle_phase:
            return None

        # Get current session from haios-status.json
        session_num = 0
        status_path = Path(".claude/haios-status.json")
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
                if pm := status.get("pm"):
                    session_num = pm.get("last_session", 0)
            except Exception:
                pass

        # Log the event
        event = {
            "ts": datetime.now().isoformat(),
            "type": "cycle_transition",
            "backlog_id": backlog_id,
            "from_phase": from_phase,
            "to_phase": cycle_phase,
            "session": session_num,
            "source": "PostToolUse"
        }

        with events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        return f"[CYCLE] {backlog_id} : {from_phase} -> {cycle_phase}"

    except Exception:
        pass

    return None


def _extract_inv_ids_from_archive(archive_path: Path) -> list[str]:
    """
    Extract INV-* IDs from backlog-complete.md archive file.

    Args:
        archive_path: Path to the backlog-complete.md file

    Returns:
        List of INV-* IDs found in [COMPLETE] entries (e.g., ["INV-022", "INV-008"])
    """
    if not archive_path.exists():
        return []

    try:
        content = archive_path.read_text(encoding="utf-8")

        # Handle BOM
        if content.startswith('\ufeff'):
            content = content[1:]

        # Match: ### [COMPLETE] INV-NNN: Title
        # Captures INV-NNN (where NNN is one or more digits)
        pattern = r'###\s*\[COMPLETE\]\s*(INV-\d+):'
        matches = re.findall(pattern, content)

        return matches

    except Exception:
        return []


def _sync_investigation_status_for_id(inv_id: str, base_path: Path = None) -> Optional[str]:
    """
    Update investigation file status from 'active' to 'complete' for a given INV-* ID.

    Args:
        inv_id: The investigation ID (e.g., "INV-022")
        base_path: Base path for finding investigation files (defaults to cwd)

    Returns:
        Status message if sync occurred, None if skipped or not found.

    Side effects:
        - Modifies investigation file to update status field
    """
    if base_path is None:
        base_path = Path.cwd()

    # Find investigation file using glob pattern
    inv_dir = base_path / "docs" / "investigations"
    if not inv_dir.exists():
        return None

    # Look for INVESTIGATION-{inv_id}-*.md
    pattern = f"INVESTIGATION-{inv_id}-*.md"
    matches = list(inv_dir.glob(pattern))

    if not matches:
        return None

    inv_file = matches[0]  # Take first match

    try:
        content = inv_file.read_text(encoding="utf-8")

        # Handle BOM
        if content.startswith('\ufeff'):
            content = content[1:]

        # Check for YAML frontmatter
        lines = content.split("\n")
        if not lines or lines[0].strip() != "---":
            return None

        yaml_end = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                yaml_end = i
                break

        if yaml_end < 0:
            return None

        # Check current status
        yaml_content = "\n".join(lines[1:yaml_end])

        # Skip if already complete
        if re.search(r'status:\s*complete', yaml_content):
            return None

        # Update status: active -> status: complete
        new_yaml_lines = []
        for line in lines[1:yaml_end]:
            if re.match(r'\s*status:\s*', line):
                # Preserve indentation
                indent = len(line) - len(line.lstrip())
                new_yaml_lines.append(" " * indent + "status: complete")
            else:
                new_yaml_lines.append(line)

        # Reconstruct file
        new_lines = ["---"] + new_yaml_lines + ["---"] + lines[yaml_end + 1:]
        new_content = "\n".join(new_lines)

        inv_file.write_text(new_content, encoding="utf-8")

        return f"[SYNC] {inv_id} status updated to complete"

    except Exception:
        return None


def _sync_investigation_status(path: Path) -> Optional[str]:
    """
    Sync investigation file status when INV-* archived to backlog-complete.md.

    Triggered by Edit/Write to docs/pm/archive/backlog-complete.md.
    Finds all INV-* entries marked [COMPLETE], locates their investigation
    files, and updates status field from 'active' to 'complete'.

    Args:
        path: The file that was just edited

    Returns:
        Status message if sync occurred, None otherwise.

    Side effects:
        - Modifies investigation files to update status field
        - Logs sync events to haios-events.jsonl
    """
    # Only trigger for backlog-complete.md
    path_str = str(path).replace("\\", "/")
    if not path_str.endswith("backlog-complete.md"):
        return None

    # Extract INV-* IDs from the archive
    inv_ids = _extract_inv_ids_from_archive(path)
    if not inv_ids:
        return None

    # Find project root (parent of docs/pm/archive/)
    base_path = path.parent.parent.parent.parent

    synced = []
    for inv_id in inv_ids:
        result = _sync_investigation_status_for_id(inv_id, base_path)
        if result:
            synced.append(inv_id)

            # Log sync event
            try:
                events_path = base_path / ".claude" / "haios-events.jsonl"
                event = {
                    "ts": datetime.now().isoformat(),
                    "type": "sync_investigation",
                    "inv_id": inv_id,
                    "action": "status_updated",
                    "source": "PostToolUse"
                }
                with events_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(event) + "\n")
            except Exception:
                pass

    if synced:
        return f"[SYNC] Investigation status updated: {', '.join(synced)}"

    return None


def _auto_link_memory_refs(hook_data: dict) -> Optional[str]:
    """
    Auto-link memory concept IDs to source work item (E2-238).

    When ingester_ingest returns concept_ids, parse work_id from source_path
    and update the work item's memory_refs field.

    Args:
        hook_data: Hook data with tool_input.source_path and tool_response.concept_ids

    Returns:
        Status message if auto-linked, None otherwise.
    """
    try:
        tool_input = hook_data.get("tool_input", {})
        tool_response = hook_data.get("tool_response", {})

        # Extract source_path and concept_ids
        source_path = tool_input.get("source_path", "")

        # Handle tool_response which may be a string (JSON) or dict
        if isinstance(tool_response, str):
            tool_response = json.loads(tool_response)

        # Get concept_ids from response (may be nested in "result")
        result = tool_response.get("result", tool_response)
        if isinstance(result, str):
            result = json.loads(result)

        concept_ids = result.get("concept_ids", [])

        if not concept_ids:
            return None

        # Extract work_id from source_path
        work_id = _extract_work_id_from_source_path(source_path)
        if not work_id:
            return None

        # Import WorkEngine module
        modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        from work_engine import WorkEngine
        from governance_layer import GovernanceLayer

        engine = WorkEngine(governance=GovernanceLayer())
        engine.add_memory_refs(work_id, concept_ids)

        return f"[AUTO-LINK] {work_id} memory_refs += {concept_ids}"

    except Exception:
        # Don't break hook flow on auto-link errors
        return None


def _extract_work_id_from_source_path(source_path: str) -> Optional[str]:
    """
    Extract work ID from source_path patterns (E2-238).

    Patterns:
    - docs/work/active/E2-238/... -> E2-238
    - docs/work/archive/INV-052/... -> INV-052
    - closure:E2-269 -> E2-269

    Args:
        source_path: Source path from ingester_ingest call

    Returns:
        Work ID or None if not found.
    """
    # Pattern 1: closure:{id}
    if source_path.startswith("closure:"):
        return source_path[8:]  # Strip "closure:" prefix

    # Pattern 2: docs/work/(active|archive)/{id}/...
    # Work IDs: E2-NNN, INV-NNN, TD-NNN, etc.
    match = re.search(r"docs[/\\]work[/\\](?:active|archive)[/\\]([A-Z0-9]+-\d+)", source_path)
    if match:
        return match.group(1)

    return None


def _scaffold_on_node_entry(path: Path, hook_data: dict) -> Optional[str]:
    """
    Detect current_node changes in work files and suggest scaffold commands.

    Part of E2-154: Scaffold-on-Entry Hook (INV-022 Phase 2).

    When a work file's current_node field is edited, this handler:
    1. Detects the new node value
    2. Looks up the node-cycle binding configuration
    3. Checks if required cycle documents exist
    4. Returns a message with scaffold commands for missing docs

    Note: This hook cannot execute slash commands directly. It returns
    a message that the agent reads and acts upon. This follows the same
    pattern as error capture hooks (E2-007).

    Args:
        path: Path to the modified file
        hook_data: Hook data containing tool_name and tool_input

    Returns:
        Scaffold instruction message or None if not applicable.

    Side effects:
        - None (read-only analysis)
    """
    # Only process work files in docs/work/
    path_str = str(path).replace("\\", "/")
    if not path.name.startswith("WORK-") or "docs/work/" not in path_str:
        return None

    # Only process Edit operations (need to detect field change)
    tool_name = hook_data.get("tool_name", "")
    if tool_name != "Edit":
        return None

    # Check if the edit touched the current_node field
    tool_input = hook_data.get("tool_input", {})
    old_string = tool_input.get("old_string", "")
    new_string = tool_input.get("new_string", "")

    # Only proceed if current_node was in the edited text
    if "current_node:" not in old_string and "current_node:" not in new_string:
        return None

    try:
        # E2-264: Import from lib for helpers, module for build_scaffold_command
        lib_dir = Path(__file__).parent.parent.parent / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from node_cycle import (
            get_node_binding, check_doc_exists,
            extract_work_id, extract_title
        )

        # E2-264: Module-first import for build_scaffold_command via CycleRunner
        modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer
        runner = CycleRunner(governance=GovernanceLayer())

        # Read current file content to get new node value
        content = path.read_text(encoding="utf-8")
        if content.startswith('\ufeff'):
            content = content[1:]

        # Extract current_node value from file
        node_match = re.search(r'^current_node:\s*(\w+)', content, re.MULTILINE)
        if not node_match:
            return None

        new_node = node_match.group(1)

        # Get binding for new node
        binding = get_node_binding(new_node)
        if not binding or not binding.get("scaffold"):
            return f"[SCAFFOLD] Node changed to '{new_node}' (no scaffold required)"

        # Extract work ID and title
        work_id = extract_work_id(path)
        title = extract_title(content)
        if not work_id:
            return None

        # Check which docs need scaffolding
        commands_to_run = []
        for scaffold_spec in binding["scaffold"]:
            pattern = scaffold_spec["pattern"].replace("{id}", work_id)

            # Check if doc already exists
            if check_doc_exists(pattern):
                continue

            # E2-264: Build scaffold command via CycleRunner module
            command = runner.build_scaffold_command(
                scaffold_spec["command"], work_id, title
            )
            commands_to_run.append(command)

        if commands_to_run:
            return f"[SCAFFOLD] Node '{new_node}' requires: {' | '.join(commands_to_run)}"

        return f"[SCAFFOLD] Node '{new_node}' - all required docs exist"

    except Exception:
        pass

    return None
