# generated: 2025-12-20
# System Auto: last updated on: 2026-02-01T14:53:28
"""
PreToolUse Hook Handler (E2-085).

Governance enforcement:
1. SQL blocking (E2-020) - blocks direct SQL without schema-verifier
2. PowerShell blocking (Session 133) - blocks PowerShell through bash (toggle-controlled)
3. Scaffold recipe blocking (E2-305, refined E2-304) - blocks just work/scaffold work_item only
4. Path governance - blocks raw writes to governed paths
5. Plan validation (E2-015) - requires backlog_id in plans
6. Memory reference warning (E2-021) - warns on missing memory_refs
7. Backlog ID uniqueness (E2-141) - blocks duplicate backlog_id values
8. Exit gates (E2-155) - warns on node transitions with unmet criteria
"""
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import yaml

# E2-264: GovernanceLayer module-first import (no caching needed)


def _load_governance_toggles() -> dict:
    """
    Load governance toggles from unified config (E2-246).

    E2-264: Module-first import via GovernanceLayer.

    Returns:
        dict with toggle settings, or defaults if config missing.
    """
    defaults = {
        "block_powershell": True,  # Default: block PowerShell
    }

    try:
        # E2-264: Module-first import via GovernanceLayer
        modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        from governance_layer import GovernanceLayer
        layer = GovernanceLayer()
        return {
            "block_powershell": layer.get_toggle("block_powershell", defaults.get("block_powershell", True))
        }
    except Exception:
        return defaults


def handle(hook_data: dict) -> Optional[dict]:
    """
    Process PreToolUse hook.

    Args:
        hook_data: Parsed JSON from Claude Code containing:
            - tool_name: str (e.g., "Bash", "Write", "Edit")
            - tool_input: dict (tool-specific input)

    Returns:
        None: Allow operation (no output)
        dict: Block/warn with hookSpecificOutput structure
    """
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})

    # E2.4 CH-004: State-aware governed activity check (checked FIRST)
    result = _check_governed_activity(tool_name, tool_input)
    if result:
        return result

    # Check Bash for SQL and PowerShell
    if tool_name == "Bash":
        command = tool_input.get("command", "")

        # Check SQL first
        result = _check_sql_governance(command)
        if result:
            return result

        # Check PowerShell (toggle-controlled)
        result = _check_powershell_governance(command)
        if result:
            return result

        # Check scaffold recipes (E2-305)
        result = _check_scaffold_governance(command)
        if result:
            return result

        return None  # Allow other bash commands

    # Check Write/Edit for governance
    if tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")

        # Plan validation (E2-015)
        result = _check_plan_validation(file_path, content)
        if result:
            return result

        # Memory reference warning (E2-021)
        result = _check_memory_refs(file_path, new_string or content)
        if result:
            return result

        # Backlog ID uniqueness (E2-141)
        result = _check_backlog_id_uniqueness(file_path, content)
        if result:
            return result

        # Exit gate check (E2-155) - only for Edit with old_string
        if tool_name == "Edit" and old_string:
            result = _check_exit_gate(file_path, old_string, new_string)
            if result:
                return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
        if result:
            return result

    return None  # Allow all other tools


def _check_governed_activity(tool_name: str, tool_input: dict) -> Optional[dict]:
    """
    Check governed activity via GovernanceLayer (E2.4 CH-004).

    State-aware governance: same tool can have different rules per workflow state.

    Returns:
        None: Allow operation
        dict: Block/warn response
    """
    try:
        # Import GovernanceLayer (module-first pattern per E2-264)
        modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        from governance_layer import GovernanceLayer

        layer = GovernanceLayer()

        # 1. Get current state
        state = layer.get_activity_state()

        # 2. Map tool to primitive
        primitive = layer.map_tool_to_primitive(tool_name, tool_input)

        # 3. Build context
        context = {
            "file_path": tool_input.get("file_path", ""),
            "tool_input": tool_input,
        }

        # 4. Special handling for skill-invoke
        if primitive == "skill-invoke":
            skill_name = tool_input.get("skill", "")
            skill_result = layer._check_skill_restriction(skill_name, state)
            if skill_result is not None and not skill_result.allowed:
                return _deny(skill_result.reason)

        # 5. Check activity
        result = layer.check_activity(primitive, state, context)

        if not result.allowed:
            return _deny(result.reason)

        if result.reason and result.reason != "Activity allowed":
            return _allow_with_warning(result.reason)

        return None  # Allow silently

    except Exception:
        # Fail-permissive on any error
        return None


def _check_sql_governance(command: str) -> Optional[dict]:
    """
    Block direct SQL queries without schema-verifier (E2-020).

    Returns deny response if SQL detected, None otherwise.
    """
    if not command:
        return None

    # Detect SQL keywords with FROM (to avoid false positives)
    sql_pattern = r'(?i)(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)'

    if not re.search(sql_pattern, command):
        return None

    # Allow safe patterns
    safe_patterns = [
        r'(?i)PRAGMA\s+table_info',
        r'(?i)\.tables',
        r'(?i)\.schema',
        r'(?i)sqlite3.*--version',
        r'(?i)sqlite_master',
        r'(?i)PRAGMA\s+table_list',
        r'(?i)from\s+haios_etl',
        r'(?i)DatabaseManager',
        r'(?i)pytest',
        r'(?i)python\s+-m\s+haios_etl'
    ]

    for pattern in safe_patterns:
        if re.search(pattern, command):
            return None  # Safe pattern, allow

    # Block with guidance
    return _deny(
        "BLOCKED: Direct SQL not allowed. Run this instead: "
        "Task(prompt='<your query intent>', subagent_type='schema-verifier')"
    )


def _check_powershell_governance(command: str) -> Optional[dict]:
    """
    Block PowerShell commands through Bash (Session 133).

    PowerShell through bash mangles $_ and $variable references, causing
    cryptic errors. Toggle-controlled via .claude/haios/config/haios.yaml.

    Returns deny response if PowerShell detected and toggle enabled, None otherwise.
    """
    if not command:
        return None

    # Check if blocking is enabled
    toggles = _load_governance_toggles()
    if not toggles.get("block_powershell", True):
        return None  # Toggle disabled, allow

    # Detect PowerShell invocations
    powershell_patterns = [
        r'^powershell\b',          # powershell at start
        r'^powershell\.exe\b',     # powershell.exe at start
        r'^pwsh\b',                # pwsh (PowerShell Core) at start
        r'^pwsh\.exe\b',           # pwsh.exe at start
        r'\bpowershell\s+-',       # powershell with flags anywhere
        r'\bpowershell\.exe\s+-',  # powershell.exe with flags anywhere
    ]

    for pattern in powershell_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return _deny(
                "BLOCKED: PowerShell through Bash mangles $_ and $variable references. "
                "Use instead: just recipes, Glob/Grep/Read tools, or Python scripts. "
                "MUST NOT enable PowerShell bypass without operator permission. "
                "Toggle: .claude/haios/config/haios.yaml (toggles.block_powershell)"
            )

    return None


def _check_scaffold_governance(command: str) -> Optional[dict]:
    """
    Block direct scaffold recipe calls for work_item only (E2-305, E2-304 refinement).

    Work items require full work-creation-cycle to populate placeholders.
    Other scaffold types (plan, inv, checkpoint) are called by /new-* commands
    which chain to their respective cycles for placeholder population.

    Session 253 fix: Removed overly broad blocking that broke /new-plan and
    /new-investigation commands. Only `just work` and `just scaffold work_item`
    are blocked because work items have the most complex placeholder requirements.

    Returns deny response if work_item scaffold detected, None otherwise.
    """
    if not command:
        return None

    # Only block work_item scaffolding - other types are called by governed commands
    # that chain to cycles which fill placeholders
    #
    # Session 257 fix: More specific patterns to avoid false positives on heredoc content.
    # Pattern must match actual command invocation, not text in commit messages.
    # - `just work WORK-XXX` or `just work "title"` = actual scaffold command
    # - `removed 'just work' suggestion` = text in heredoc, not a command
    scaffold_patterns = {
        # Match: just work WORK-XXX "title" or just work "title"
        # Requires argument after 'just work' to confirm it's a scaffold command
        r'(?:^|&&|;|\|)\s*just\s+work\s+(?:WORK-\d+|"[^"]+"|\'[^\']+\')': "/new-work",
        r'(?:^|&&|;|\|)\s*just\s+scaffold\s+work_item\b': "/new-work",
    }

    for pattern, redirect in scaffold_patterns.items():
        if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
            return _deny(
                f"BLOCKED: Direct work_item scaffold. Use '{redirect}' command instead. "
                "Work items require work-creation-cycle to populate placeholders."
            )

    return None


def _check_plan_validation(file_path: str, content: str) -> Optional[dict]:
    """
    Validate plan files have backlog_id (E2-015).

    Returns deny response if missing, None otherwise.
    """
    if not file_path or not content:
        return None

    # Normalize path
    normalized = file_path.replace("\\", "/")

    # Check for plan paths (new directory structure or legacy flat structure)
    is_new_plan_path = "/plans/PLAN.md" in normalized and "docs/work/active/" in normalized
    is_legacy_plan_path = "docs/plans/PLAN-" in normalized

    if not is_new_plan_path and not is_legacy_plan_path:
        return None

    # Check for backlog_id in YAML frontmatter
    if not re.search(r'backlog_id:\s*E2-\d{3}', content):
        return _deny(
            "BLOCKED: Plans require backlog_id field in YAML frontmatter. "
            "Use '/new-plan <backlog_id> <title>' command."
        )

    return None


def _check_memory_refs(file_path: str, text_to_check: str) -> Optional[dict]:
    """
    Warn on missing memory_refs for investigation-spawned items (E2-021).

    Returns allow with warning, None otherwise.

    NOTE: Updated 2025-12-25 to check work files instead of backlog.md (ADR-039 migration).
    """
    if not file_path or not text_to_check:
        return None

    normalized = file_path.replace("\\", "/")

    # Check work files (new system) instead of backlog.md (deprecated)
    if "docs/work/" not in normalized:
        return None

    # Check for spawned_by: INV-* pattern in YAML frontmatter
    spawned_pattern = r'spawned_by:\s*(INV-\d{3}|INVESTIGATION-\S+)'
    if not re.search(spawned_pattern, text_to_check):
        return None

    # Check for memory_refs in YAML frontmatter
    if re.search(r'memory_refs:\s*\[', text_to_check):
        return None  # Has memory_refs array, allow silently
    if re.search(r'memory_refs:\s*\n\s*-', text_to_check):
        return None  # Has memory_refs list, allow silently

    # Warn but allow
    return _allow_with_warning(
        "WARNING: Investigation-spawned work item should include memory_refs. "
        "Add 'memory_refs: [concept IDs]' to link to source insights. "
        "(RFC 2119 SHOULD per E2-021)"
    )


def _check_path_governance(file_path: str) -> Optional[dict]:
    """
    Block raw writes to governed paths (new files only).

    Returns deny response if governed path, None otherwise.
    """
    if not file_path:
        return None

    # If file already exists, allow edits
    if Path(file_path).exists():
        return None

    normalized = file_path.replace("\\", "/")
    file_name = Path(normalized).name

    # Governed paths and their commands
    # Legacy flat paths
    governed_paths = {
        "docs/checkpoints/": ("/new-checkpoint", "*.md"),
        "docs/plans/": ("/new-plan", "PLAN-*.md"),
        "docs/handoff/": ("/new-handoff", "*.md"),
        "docs/reports/": ("/new-report", "*.md"),
        "docs/ADR/": ("/new-adr", "ADR-*.md"),
    }

    # New work directory structure (E2-212, E2-225)
    # Check for work directory paths - more specific patterns
    if "docs/work/active/" in normalized:
        # Block raw WORK.md creation - use /new-work
        # Note: 'just work' is also blocked by scaffold recipe guard (E2-305)
        if file_name == "WORK.md":
            return _deny(
                "BLOCKED: Governed path. Use '/new-work <id> <title>' instead of raw Write."
            )
        # Block raw PLAN.md creation - use /new-plan
        if "/plans/" in normalized and file_name == "PLAN.md":
            return _deny(
                "BLOCKED: Governed path. Use '/new-plan <id> <title>' instead of raw Write."
            )
        # Block raw observations.md creation - use just scaffold-observations
        if file_name == "observations.md":
            return _deny(
                "BLOCKED: Governed path. Use 'just scaffold-observations <id>' instead of raw Write."
            )

    for gov_path, (command, pattern) in governed_paths.items():
        if gov_path in normalized:
            # Check if file matches pattern
            if _matches_pattern(file_name, pattern):
                return _deny(
                    f"BLOCKED: Governed path. Use '{command}' command instead of raw Write/Edit."
                )

    return None  # Not a governed path


def _matches_pattern(file_name: str, pattern: str) -> bool:
    """Check if filename matches glob-like pattern."""
    import fnmatch
    return fnmatch.fnmatch(file_name, pattern)


def _deny(reason: str) -> dict:
    """Return deny response with standard structure."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }


def _allow_with_warning(reason: str) -> dict:
    """Return allow response with warning."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": reason
        }
    }


def _check_backlog_id_uniqueness(file_path: str, content: str) -> Optional[dict]:
    """
    Block creation of files with duplicate backlog_id values (E2-141).

    Extracts backlog_id from content, greps docs/ for existing files with
    same ID, blocks if duplicate found (excluding the file being edited).

    Args:
        file_path: Path to file being created/edited
        content: Content being written (contains frontmatter with backlog_id)

    Returns:
        None: Allow operation (no duplicate found)
        dict: Deny with hookSpecificOutput showing existing file

    Side effects:
        - Runs grep subprocess to find existing files
    """
    if not content:
        return None

    # Extract backlog_id from content
    # Match: backlog_id: E2-NNN or backlog_id: INV-NNN
    match = re.search(r'backlog_id:\s*([A-Z0-9]+-\d+)', content)
    if not match:
        return None

    backlog_id = match.group(1)

    # Grep docs/ for existing files with same backlog_id
    try:
        # Use grep to find files (cross-platform via findstr on Windows)
        import platform
        docs_path = Path("docs")

        if not docs_path.exists():
            return None  # No docs directory, allow

        # Build search pattern
        search_pattern = f"backlog_id:\\s*{backlog_id}"

        # Use Python glob + read instead of grep for portability
        matching_files = []
        for md_file in docs_path.rglob("*.md"):
            try:
                file_content = md_file.read_text(encoding="utf-8")
                if re.search(search_pattern, file_content):
                    matching_files.append(str(md_file))
            except Exception:
                continue

        # Filter out the current file being edited
        if file_path:
            normalized_path = Path(file_path).resolve()
            matching_files = [
                f for f in matching_files
                if Path(f).resolve() != normalized_path
            ]

        # If any matches remain, block
        if matching_files:
            existing_file = matching_files[0]
            return _deny(
                f"BLOCKED: Duplicate backlog_id. {backlog_id} already exists in {existing_file}. "
                "Each work item must have a unique ID."
            )

    except Exception:
        pass  # On any error, allow the operation

    return None  # No duplicate found, allow


def _check_exit_gate(file_path: str, old_string: str, new_string: str) -> Optional[dict]:
    """
    Check exit criteria when changing work file current_node (E2-155).

    Soft gate: warns but allows operation if criteria unmet.

    Args:
        file_path: Path to file being edited
        old_string: Text being replaced
        new_string: Replacement text

    Returns:
        None: Allow operation (no issues found or not applicable)
        dict: Allow with warning (hookSpecificOutput with warning message)
    """
    if not file_path or not old_string or not new_string:
        return None

    # Only check work files in docs/work/
    normalized = file_path.replace("\\", "/")
    file_name = Path(file_path).name
    if "docs/work/" not in normalized or not file_name.startswith("WORK-"):
        return None

    # Only check if current_node is being changed
    if "current_node:" not in old_string and "current_node:" not in new_string:
        return None

    try:
        # Import node_cycle library (lazy import)
        # WORK-006: Use lib inside haios/ for portability
        lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from node_cycle import (
            detect_node_exit_attempt, check_exit_criteria,
            build_exit_gate_warning, extract_work_id
        )

        # Detect if this is a node transition
        transition = detect_node_exit_attempt(old_string, new_string)
        if not transition:
            return None

        from_node, to_node = transition

        # Get work ID from file path
        work_id = extract_work_id(Path(file_path))
        if not work_id:
            return None

        # Check exit criteria for current node
        failures = check_exit_criteria(from_node, work_id)
        if not failures:
            return None  # All criteria met, allow silently

        # Build warning message (soft gate - allow with warning)
        warning = build_exit_gate_warning(from_node, to_node, failures)
        return _allow_with_warning(warning)

    except Exception:
        pass  # On error, allow operation

    return None
