# generated: 2025-12-21
# System Auto: last updated on: 2026-01-21T22:20:17
"""
Error Capture Module (E2-130).

Provides error detection and storage for tool failures.
Part of HAIOS observability infrastructure.

Key functions:
- is_actual_error(): Determine if tool response is a real failure
- store_error(): Store error to memory with type='tool_error'
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

# Lazy import to avoid circular dependencies and allow testing is_actual_error without DB
_db = None


def _get_db():
    """Get database connection (lazy initialization)."""
    global _db
    if _db is None:
        from database import DatabaseManager
        # 4 levels up from .claude/haios/lib/ to project root
        db_path = Path(__file__).parent.parent.parent.parent / "haios_memory.db"
        _db = DatabaseManager(str(db_path))
    return _db.get_connection()


def is_actual_error(tool_name: str, tool_response: dict) -> bool:
    """
    Determine if tool response represents an actual failure.

    This function prevents false positives by checking tool-specific
    success/failure indicators rather than just looking for "error" substring.

    Args:
        tool_name: Name of the tool (Bash, Read, Edit, Write, Grep, Glob)
        tool_response: The tool's response dict from Claude Code

    Returns:
        True only for actual failures, False for successes or false positives.

    Detection Logic by Tool:
        - Bash: exit_code != 0
        - Read: Has "error" key with string value (not file content)
        - Edit: Has "error" key (not filePath with success structure)
        - Write: Has "error" key (not type: create/update)
        - Grep/Glob: Has "error" key (not results structure)
    """
    if not tool_response:
        return False

    # Bash: Check exit code (most reliable indicator)
    if tool_name == "Bash":
        exit_code = tool_response.get("exit_code")
        # exit_code of 0 means success, anything else is error
        # None means we can't determine, treat as not-error
        if exit_code is None:
            return False
        return exit_code != 0

    # Read: Success has "file" key with content, error has "error" key
    if tool_name == "Read":
        if "file" in tool_response:
            return False  # Has file content = success
        if "error" in tool_response and isinstance(tool_response["error"], str):
            return True
        return False

    # Edit: Success has "filePath" without "error" key
    if tool_name == "Edit":
        if "filePath" in tool_response and "error" not in tool_response:
            return False  # Successful edit
        if "error" in tool_response and isinstance(tool_response["error"], str):
            return True
        return False

    # Write: Success has "type" of "create" or "update"
    if tool_name == "Write":
        if tool_response.get("type") in ("create", "update"):
            return False  # Successful write
        if "error" in tool_response and isinstance(tool_response["error"], str):
            return True
        return False

    # Grep: Success has "numFiles" or "content" or "filenames"
    if tool_name == "Grep":
        if any(k in tool_response for k in ("numFiles", "content", "filenames")):
            return False  # Has results structure = success
        if "error" in tool_response and isinstance(tool_response["error"], str):
            return True
        return False

    # Glob: Success returns file list, error has "error" key
    if tool_name == "Glob":
        # Glob typically returns a list of files or empty list (both success)
        if isinstance(tool_response, list):
            return False
        if "error" in tool_response and isinstance(tool_response["error"], str):
            return True
        return False

    # Unknown tool: Only capture if explicit error structure
    if "error" in tool_response and isinstance(tool_response["error"], str):
        return True

    return False


def store_error(
    tool_name: str, error_message: str, tool_input: str = ""
) -> dict:
    """
    Store error to memory with dedicated type for queryability.

    Args:
        tool_name: Tool that failed
        error_message: The error message (truncated if long)
        tool_input: Summary of what was attempted (optional)

    Returns:
        {"success": True, "concept_id": N} or {"success": False, "error": "..."}
    """
    try:
        # Truncate long messages
        max_error_len = 500
        max_input_len = 200

        if len(error_message) > max_error_len:
            error_message = error_message[:max_error_len] + "... [truncated]"
        if tool_input and len(tool_input) > max_input_len:
            tool_input = tool_input[:max_input_len] + "... [truncated]"

        # Build error content
        timestamp = datetime.now().isoformat()
        content = f"[Tool Error] {tool_name}: {error_message}"
        if tool_input:
            content += f" | Input: {tool_input}"

        # Store with dedicated type
        # Schema: concepts(id, type, content, source_adr, synthesis_*, ...)
        conn = _get_db()
        cursor = conn.execute(
            """
            INSERT INTO concepts (type, content, source_adr)
            VALUES (?, ?, ?)
            """,
            ("tool_error", content, f"error:{tool_name}:{timestamp[:10]}"),
        )
        concept_id = cursor.lastrowid
        conn.commit()

        return {"success": True, "concept_id": concept_id, "tool": tool_name}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_error_summary(limit: int = 20) -> list[dict]:
    """
    Get recent tool errors for analysis.

    Args:
        limit: Maximum number of errors to return

    Returns:
        List of error records with id, content, created_at
    """
    try:
        conn = _get_db()
        rows = conn.execute(
            """
            SELECT id, content, created_at
            FROM concepts
            WHERE type = 'tool_error'
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]

    except Exception:
        return []
