# generated: 2026-03-07
# Context-aware statusLine handler
"""
StatusLine command for Claude Code.

Reads JSON from stdin (Claude Code runtime data), displays formatted status,
and writes context_window.remaining_percentage to .claude/context_remaining
for consumption by PreToolUse hook context budget gate.

Data flow:
    Claude Code runtime -> stdin JSON -> this script -> stdout (display)
                                                     -> .claude/context_remaining (file)
"""
import json
import sys
from pathlib import Path


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        print("\033[2mClaude\033[0m | \033[2mContext: initializing...\033[0m", end="")
        return

    model = data.get("model", {}).get("display_name", "Claude")
    cwd = data.get("workspace", {}).get("current_dir", "~")
    dirname = cwd.rsplit("/", 1)[-1] if "/" in cwd else cwd.rsplit("\\", 1)[-1] if "\\" in cwd else cwd

    ctx = data.get("context_window", {})
    used = ctx.get("used_percentage")
    remaining = ctx.get("remaining_percentage")
    total_in = ctx.get("total_input_tokens", 0)
    total_out = ctx.get("total_output_tokens", 0)

    # Write remaining % to file for hook consumption
    if remaining is not None:
        try:
            remaining_file = Path(".claude/context_remaining")
            remaining_file.write_text(str(remaining), encoding="utf-8")
        except Exception:
            pass  # Fail-silent: display must never break

    if used is not None:
        print(
            f"\033[2m{model}\033[0m | "
            f"\033[2m{dirname}\033[0m | "
            f"\033[2mContext: {used:.1f}% used ({remaining:.1f}% free) | "
            f"Total: {total_in // 1000}k in / {total_out // 1000}k out\033[0m",
            end="",
        )
    else:
        print(
            f"\033[2m{model}\033[0m | "
            f"\033[2m{dirname}\033[0m | "
            f"\033[2mContext: initializing...\033[0m",
            end="",
        )


if __name__ == "__main__":
    main()
