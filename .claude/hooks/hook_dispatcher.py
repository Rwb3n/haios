# generated: 2025-12-20
# System Auto: last updated on: 2025-12-20 22:35:49
#!/usr/bin/env python3
"""
HAIOS Hook Dispatcher (E2-085).

Single entry point for all Claude Code hooks. Routes events to appropriate handlers.

Architecture:
    Claude Code (bash layer)
        |
        v
    python hook_dispatcher.py   <-- This file
        |
        +-- Reads JSON from stdin
        +-- Routes by hook_event_name:
        |       "UserPromptSubmit" -> hooks/user_prompt_submit.py
        |       "PreToolUse"       -> hooks/pre_tool_use.py
        |       "PostToolUse"      -> hooks/post_tool_use.py
        |       "Stop"             -> hooks/stop.py
        |
        +-- Outputs text (UserPromptSubmit) or JSON (PreToolUse) to stdout

Usage:
    Configure in settings.local.json:
    {
        "hooks": {
            "UserPromptSubmit": [...{"command": "python .claude/hooks/hook_dispatcher.py"}...]
        }
    }
"""
import json
import sys
import logging
from pathlib import Path
from typing import Optional, Union

# Setup logging to stderr (stdout is for hook output)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Add hooks submodule directory to path
HOOKS_DIR = Path(__file__).parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))


def dispatch_hook(hook_data: dict) -> Optional[Union[str, dict]]:
    """
    Route hook event to appropriate handler.

    Args:
        hook_data: Parsed JSON from Claude Code

    Returns:
        str: For UserPromptSubmit (text injection)
        dict: For PreToolUse (JSON with permissionDecision)
        None: For PostToolUse/Stop (side effects only) or on error
    """
    event_name = hook_data.get("hook_event_name", "")

    try:
        if event_name == "UserPromptSubmit":
            from user_prompt_submit import handle
            return handle(hook_data)

        elif event_name == "PreToolUse":
            from pre_tool_use import handle
            return handle(hook_data)

        elif event_name == "PostToolUse":
            from post_tool_use import handle
            return handle(hook_data)

        elif event_name == "Stop":
            from stop import handle
            return handle(hook_data)

        else:
            logger.warning(f"Unknown hook event: {event_name}")
            return None

    except Exception as e:
        logger.error(f"Hook handler error for {event_name}: {e}")
        return None


def main() -> None:
    """Entry point. Read JSON from stdin, route to handler, output to stdout."""
    try:
        # Read JSON from stdin
        json_input = sys.stdin.read()
        if not json_input.strip():
            sys.exit(0)

        hook_data = json.loads(json_input)
        result = dispatch_hook(hook_data)

        # Output result
        if result is not None:
            if isinstance(result, dict):
                # JSON output for PreToolUse
                print(json.dumps(result))
            else:
                # Text output for UserPromptSubmit
                print(result)

        sys.exit(0)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON input: {e}")
        sys.exit(0)  # Don't break workflow on parse error

    except Exception as e:
        logger.error(f"Hook dispatcher error: {e}")
        sys.exit(0)  # Don't break workflow on error


if __name__ == "__main__":
    main()
