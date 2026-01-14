# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 22:37:40
#!/usr/bin/env python3
"""
Error Capture - Store tool errors to memory for pattern detection.

Part of E2-007 Error Capture Hook implementation.

Usage:
    python error_capture.py "<tool_name>" "<error_message>" "<tool_input_summary>"

Stores error context to memory via ingester for future pattern analysis.
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set up logging
log_dir = PROJECT_ROOT / '.claude' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'error_capture.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
    ]
)
logger = logging.getLogger(__name__)


def store_error(tool_name: str, error_message: str, tool_input_summary: str = "") -> dict:
    """
    Store error to memory via direct database insertion.

    Simplified approach: No entity extraction (avoids Gemini API calls).
    Just stores the error as a concept for pattern detection.

    Args:
        tool_name: Name of the tool that errored
        error_message: The error message (truncated if too long)
        tool_input_summary: Summary of tool input (optional, truncated)

    Returns:
        dict with concept_id if successful
    """
    try:
        from haios_etl.database import DatabaseManager

        # Truncate long messages
        max_error_len = 500
        max_input_len = 200

        if len(error_message) > max_error_len:
            error_message = error_message[:max_error_len] + "... [truncated]"
        if len(tool_input_summary) > max_input_len:
            tool_input_summary = tool_input_summary[:max_input_len] + "... [truncated]"

        # Build error context
        timestamp = datetime.now().isoformat()

        content = f"[Error Capture] Tool: {tool_name} | Error: {error_message}"
        if tool_input_summary:
            content += f" | Input: {tool_input_summary}"

        source_path = f"error:{tool_name}:{timestamp[:10]}"

        # Initialize database
        db_path = PROJECT_ROOT / "haios_memory.db"
        db = DatabaseManager(str(db_path))

        # Direct insert as concept (no entity extraction needed for errors)
        # insert_concept(type, name, description) -> maps to (type, content, source_adr)
        concept_id = db.insert_concept(
            type="techne",  # debugging/how-to knowledge
            name=content,   # maps to content column
            description=source_path  # maps to source_adr column
        )

        logger.info(f"Stored error for {tool_name}: concept_id={concept_id}")

        return {
            "success": True,
            "concept_id": concept_id,
            "tool": tool_name
        }

    except Exception as e:
        logger.error(f"Failed to store error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 3:
        print("Usage: python error_capture.py <tool_name> <error_message> [tool_input_summary]")
        sys.exit(1)

    tool_name = sys.argv[1]
    error_message = sys.argv[2]
    tool_input_summary = sys.argv[3] if len(sys.argv) > 3 else ""

    result = store_error(tool_name, error_message, tool_input_summary)

    # Output JSON for PowerShell to parse
    print(json.dumps(result))


if __name__ == "__main__":
    main()
