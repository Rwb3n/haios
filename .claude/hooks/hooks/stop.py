# generated: 2025-12-20
# System Auto: last updated on: 2026-01-04T21:33:51
"""
Stop Hook Handler (E2-085).

Extracts learnings from completed sessions via MemoryBridge.extract_learnings().

The ReasoningBank Loop:
    RETRIEVE (UserPromptSubmit) -> INJECT -> EXECUTE -> EXTRACT (Stop) -> STORE
                                                              ^
                                                              |
                                                        THIS HANDLER

E2-264: Module-first import via MemoryBridge.
"""
import sys
from pathlib import Path
from typing import Optional


def handle(hook_data: dict) -> Optional[str]:
    """
    Process Stop hook.

    Args:
        hook_data: Parsed JSON from Claude Code containing:
            - session_id: str
            - transcript_path: str (path to session JSONL)
            - stop_hook_active: bool (if True, previous stop hook already ran)

    Returns:
        Optional extraction status message.

    Side effects:
        - Invokes MemoryBridge.extract_learnings() to store learnings
    """
    # CRITICAL: Check stop_hook_active to prevent infinite loops
    if hook_data.get("stop_hook_active", False):
        return None

    transcript_path = hook_data.get("transcript_path", "")
    if not transcript_path or not Path(transcript_path).exists():
        return None

    try:
        # E2-264: Module-first import via MemoryBridge
        modules_dir = Path(__file__).parent.parent / "haios" / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        from memory_bridge import MemoryBridge
        bridge = MemoryBridge()
        result = bridge.extract_learnings(transcript_path)

        if result.success:
            return f"[LEARNING] Extracted from session (outcome: {result.outcome})"
        elif result.reason == "qualified":
            return None  # Qualified but extraction failed
        else:
            return None  # Not qualified for extraction

    except Exception:
        pass  # Don't break on extraction errors

    return None
