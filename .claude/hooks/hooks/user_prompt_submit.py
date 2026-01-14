# generated: 2025-12-20
# System Auto: last updated on: 2026-01-14T22:10:00
"""
UserPromptSubmit Hook Handler (E2-085, E2-119).

Provides context injection before Claude processes user prompts:
1. Date/time context
2. HAIOS Vitals (from haios-status-slim.json) - refreshed on every prompt (E2-119)
3. Dynamic thresholds
4. Lifecycle guidance (ADR-034)
5. RFC2119 governance reminders
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def _refresh_slim_status(cwd: str) -> None:
    """
    Refresh haios-status-slim.json before reading vitals (E2-119).

    Ensures pm.last_session, session_delta, and metrics are fresh on every prompt.
    Uses direct Python import to minimize latency (vs subprocess).

    E2-264: Module-first import via ContextLoader.
    """
    if not cwd:
        return

    try:
        # E2-264: Module-first import via ContextLoader
        modules_path = Path(cwd) / ".claude" / "haios" / "modules"
        if modules_path.exists() and str(modules_path) not in sys.path:
            sys.path.insert(0, str(modules_path))

        # Import and call via ContextLoader module
        from context_loader import ContextLoader
        loader = ContextLoader(project_root=Path(cwd))
        slim = loader.generate_status(slim=True)
        slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
        slim_path.write_text(json.dumps(slim, indent=4), encoding="utf-8")
    except Exception:
        # Fail silently - stale status is better than broken hook
        pass


def handle(hook_data: dict) -> str:
    """
    Process UserPromptSubmit hook.

    Args:
        hook_data: Parsed JSON from Claude Code containing:
            - session_id: str
            - transcript_path: str
            - cwd: str (working directory)
            - hook_event_name: "UserPromptSubmit"
            - prompt: str (user's prompt text)

    Returns:
        Concatenated context string to inject before Claude sees the prompt.
    """
    output_parts = []

    # Part 1: Date/time context
    output_parts.append(_get_datetime_context())

    # Part 1.5: Context threshold check (E2-210)
    # DISABLED Session 179: Context estimate is unreliable, causes noise
    # transcript_path = hook_data.get("transcript_path", "")
    # context_warning = _check_context_threshold(transcript_path)
    # if context_warning:
    #     output_parts.append("")
    #     output_parts.append(context_warning)

    # Part 2: HAIOS Vitals (E2-119: refresh status before reading)
    # DISABLED Session 179: Vitals structure outdated after E2.2 chapter redesign
    # Milestones replaced by Chapters, slim status needs redesign
    # cwd = hook_data.get("cwd", "")
    # _refresh_slim_status(cwd)  # E2-119: Ensure fresh data on every prompt
    # vitals = _get_vitals(cwd)
    # if vitals:
    #     output_parts.append("")
    cwd = hook_data.get("cwd", "")
    # vitals disabled - no append

    # Part 2.5: Session state warning (E2-287)
    session_warning = _get_session_state_warning(cwd)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    # Part 3: Dynamic thresholds
    thresholds = _get_thresholds(cwd)
    if thresholds:
        output_parts.append(thresholds)

    # Part 4: Lifecycle guidance
    prompt = hook_data.get("prompt", "")
    lifecycle = _get_lifecycle_guidance(prompt, cwd)
    if lifecycle:
        output_parts.append("")
        output_parts.append(lifecycle)

    # Part 5: RFC2119 reminders
    rfc2119 = _get_rfc2119_reminders(prompt)
    if rfc2119:
        output_parts.append("")
        output_parts.append(rfc2119)

    return "\n".join(output_parts)


def _get_datetime_context() -> str:
    """Get current date/time formatted string."""
    now = datetime.now()
    day_of_week = now.strftime("%A")
    datetime_str = now.strftime("%Y-%m-%d %I:%M %p")
    return f"Today is {day_of_week}, {datetime_str}"


def _get_session_state_warning(cwd: str) -> Optional[str]:
    """
    Check if agent is working outside an active governance cycle.

    E2-287: Soft enforcement - inject warning when session_state.active_cycle is null.
    This creates friction for governance bypass without blocking.

    Args:
        cwd: Working directory path

    Returns:
        Warning message if no active cycle, None otherwise.
    """
    if not cwd:
        return None

    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return None

    try:
        slim = json.loads(slim_path.read_text(encoding="utf-8-sig"))

        # If session_state key doesn't exist, this is old format - no warning (backward compat)
        if "session_state" not in slim:
            return None

        session_state = slim["session_state"]

        # If active_cycle is null, warn
        if session_state.get("active_cycle") is None:
            return (
                "--- Session State Warning (E2-287) ---\n"
                "No active governance cycle detected.\n"
                "Invoke a skill (/coldstart, /implement, /close) to enter a cycle.\n"
                "Working outside cycles bypasses governance gates.\n"
                "---"
            )
        return None
    except Exception:
        return None


def _get_vitals(cwd: str) -> Optional[str]:
    """
    Read haios-status-slim.json and format vitals block.

    Returns compact operational awareness (~40 tokens).

    E2-206: Removed static infrastructure (commands, skills, agents, MCPs, recipes)
    as these are already documented in CLAUDE.md and don't change mid-session.
    """
    if not cwd:
        return None

    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return None

    try:
        # Use utf-8-sig to handle BOM (common in Windows-generated files)
        slim = json.loads(slim_path.read_text(encoding="utf-8-sig"))
        lines = ["--- HAIOS Vitals ---"]

        # Milestone with progress
        if milestone := slim.get("milestone"):
            milestone_str = f"{milestone.get('id', 'Unknown')} ({milestone.get('progress', 0)}%)"
            if milestone.get("delta_source") and milestone.get("progress", 0) > milestone.get("prior_progress", 0):
                delta = milestone["progress"] - milestone["prior_progress"]
                milestone_str += f" [+{delta} from {milestone['delta_source']}]"
            lines.append(f"Milestone: {milestone_str}")

        # Session delta (momentum awareness)
        if session_delta := slim.get("session_delta"):
            if session_delta.get("prior_session"):
                delta_parts = []
                if session_delta.get("completed_count", 0) > 0:
                    delta_parts.append(f"+{session_delta['completed_count']} done")
                if session_delta.get("added_count", 0) > 0:
                    delta_parts.append(f"+{session_delta['added_count']} new")
                if session_delta.get("milestone_delta"):
                    delta_parts.append(str(session_delta["milestone_delta"]))
                if delta_parts:
                    lines.append(f"Since S{session_delta['prior_session']}: {', '.join(delta_parts)}")

        # Work cycle state (E2-118)
        if work_cycle := slim.get("work_cycle"):
            cycle_id = work_cycle.get("id", "?")
            cycle_type = work_cycle.get("cycle_type", "?")
            node = work_cycle.get("current_node", "?")
            phase = work_cycle.get("lifecycle_phase")
            cycle_str = f"{cycle_id} [{cycle_type}:{node}"
            if phase:
                cycle_str += f"/{phase}"
            cycle_str += "]"
            lines.append(f"Working: {cycle_str}")

        # Blocked items (only show if any exist) - E2-206: slim vitals
        if blocked := slim.get("blocked_items"):
            if blocked:
                blocked_count = len(blocked) if isinstance(blocked, dict) else len(blocked)
                if blocked_count > 0:
                    lines.append(f"Blocked: {blocked_count} items")

        # E2-206: Removed static infrastructure (commands, skills, agents, MCPs, recipes)
        # These are documented in CLAUDE.md and don't change mid-session
        lines.append("---")

        return "\n".join(lines)

    except Exception:
        return None


def _get_thresholds(cwd: str) -> Optional[str]:
    """
    Check for threshold violations and return urgency signals.

    Uses full haios-status.json for workspace.stale access.
    """
    if not cwd:
        return None

    status_path = Path(cwd) / ".claude" / "haios-status.json"
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"

    messages = []

    try:
        if status_path.exists():
            status = json.loads(status_path.read_text(encoding="utf-8-sig"))

            # APPROACHING: milestone > 90% but < 100%
            if milestones := status.get("milestones"):
                for name, data in milestones.items():
                    progress = data.get("progress", 0)
                    if 90 < progress < 100:
                        remaining = len(data.get("items", [])) - len(data.get("complete", []))
                        messages.append(f"APPROACHING: {name} at {progress}% - {remaining} items to completion")

            # BOTTLENECK: blocked > 3
            if blocked := status.get("blocked_items"):
                blocked_count = len(blocked) if isinstance(blocked, dict) else 0
                if blocked_count > 3:
                    messages.append(f"BOTTLENECK: {blocked_count} items blocked - review dependencies")

            # ATTENTION: stale > 5
            if workspace := status.get("workspace"):
                if stale := workspace.get("stale"):
                    if items := stale.get("items"):
                        stale_count = len(items)
                        if stale_count > 5:
                            messages.append(f"ATTENTION: {stale_count} stale items need review")

        # MOMENTUM: completed > 3 in last session (from slim)
        if slim_path.exists():
            slim = json.loads(slim_path.read_text(encoding="utf-8-sig"))
            if session_delta := slim.get("session_delta"):
                if session_delta.get("completed_count", 0) > 3:
                    messages.append(
                        f"MOMENTUM: +{session_delta['completed_count']} items completed "
                        f"since S{session_delta['prior_session']} - great progress!"
                    )

    except Exception:
        pass

    if messages:
        return "\n".join(messages) + "\n---"
    return None


def _get_lifecycle_guidance(prompt: str, cwd: str) -> Optional[str]:
    """
    Check for plan-creation intent and missing prerequisite documents.

    Soft enforcement: inject guidance, don't block.
    """
    if not prompt:
        return None

    # Check for override
    if re.search(r"skip discovery|skip investigation|trivial|quick fix", prompt, re.I):
        return None

    # Detect plan-creation or implementation intent
    plan_intent = re.search(
        r"/new-plan|create.*plan|implement.*feature|add.*feature|build.*feature|start.*implement",
        prompt, re.I
    )
    impl_intent = re.search(r"implement\s+E2-|implement\s+INV-|implement\s+TD-", prompt, re.I)

    if not (plan_intent or impl_intent):
        return None

    # Extract backlog ID
    backlog_match = re.search(r"(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})", prompt)
    if not backlog_match:
        return None

    backlog_id = backlog_match.group(1)

    # Check for prerequisite documents
    has_discovery = False
    has_design = False

    if cwd:
        cwd_path = Path(cwd)

        # Check investigations
        inv_path = cwd_path / "docs" / "investigations"
        if inv_path.exists():
            for f in inv_path.glob(f"INVESTIGATION-{backlog_id}-*.md"):
                has_discovery = True
                break

        # Check legacy handoffs
        if not has_discovery:
            handoff_path = cwd_path / "docs" / "handoff"
            if handoff_path.exists():
                for f in handoff_path.glob(f"*INVESTIGATION*{backlog_id}*.md"):
                    has_discovery = True
                    break

        # Check ADRs via haios-status.json
        status_path = cwd_path / ".claude" / "haios-status.json"
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
                if work_items := status.get("work_items"):
                    if item := work_items.get(backlog_id):
                        if item.get("adrs"):
                            has_design = True
            except Exception:
                pass

    # Inject guidance if neither exists
    if not has_discovery and not has_design:
        return (
            "--- Lifecycle Guidance (ADR-034) ---\n"
            f"No discovery/design document found for {backlog_id}.\n"
            "Consider creating an INVESTIGATION-* to analyze the problem first.\n"
            f"Command: /new-investigation {backlog_id} <title>\n"
            "Override: Include 'skip discovery' in your message to proceed.\n"
            "--- End Lifecycle Guidance ---"
        )

    return None


def _estimate_context_usage(transcript_path: str) -> float:
    """
    Estimate context usage percentage from transcript file size.

    Uses rough heuristic: ~4 chars per token, 200k token context window.
    Returns 0-100 percentage.
    """
    if not transcript_path:
        return 0.0

    path = Path(transcript_path)
    if not path.exists():
        return 0.0

    try:
        # Get file size in bytes, convert to estimated tokens
        # Calibration (Session 132): ~8 chars per token accounts for JSON/tool overhead
        # Previous: 6 chars/token was ~15-20% too aggressive
        file_size = path.stat().st_size
        estimated_tokens = file_size // 8  # ~8 chars per token (recalibrated S132)
        context_limit = 200000  # Claude's context window

        return min(100.0, (estimated_tokens / context_limit) * 100)
    except Exception:
        return 0.0


def _check_context_threshold(transcript_path: str, threshold: float = 80.0) -> Optional[str]:
    """
    Check if context usage exceeds threshold.

    Args:
        transcript_path: Path to transcript JSONL file
        threshold: Percentage threshold (default 80%)

    Returns:
        Warning message if above threshold, None otherwise.
    """
    pct = _estimate_context_usage(transcript_path)
    if pct >= threshold:
        return (
            f"CONTEXT: ~{pct:.0f}% used. "
            "Consider /new-checkpoint before context exhaustion."
        )
    return None


def _get_rfc2119_reminders(prompt: str) -> Optional[str]:
    """
    Detect trigger keywords and inject MUST guidance.

    Override: Include "skip reminder" in message to bypass.
    """
    if not prompt or "skip reminder" in prompt.lower():
        return None

    reminders = []

    # MUST: Discovery -> /new-investigation
    discovery_trigger = (
        re.search(r"(bug|issue|gap|problem|broken|wrong|error)", prompt, re.I) and
        re.search(r"(found|discovered|noticed|identified|see|seeing)", prompt, re.I)
    )
    if discovery_trigger:
        reminders.append(
            "--- RFC 2119 Governance (MUST) ---\n"
            "Discovery detected. MUST use /new-investigation to document before fixing.\n"
            "Command: /new-investigation <backlog_id> <title>\n"
            "Override: Include 'skip reminder' in your message.\n"
            "--- End Governance Reminder ---"
        )

    # MUST: SQL -> schema-verifier
    sql_trigger = (
        re.search(r"(run|execute|write|check|query).*(sql|query|database)", prompt, re.I) or
        re.search(r"(select|insert|update|delete)\s+(from|into)", prompt, re.I)
    )
    if sql_trigger:
        reminders.append(
            "--- RFC 2119 Governance (MUST) ---\n"
            "SQL intent detected. MUST use schema-verifier subagent first.\n"
            "Command: Task(prompt='...', subagent_type='schema-verifier')\n"
            "Override: Include 'skip reminder' in your message.\n"
            "--- End Governance Reminder ---"
        )

    # MUST: Close -> /close
    close_match = re.search(
        r"(close|complete|finish|done|mark).*(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})",
        prompt, re.I
    )
    if close_match:
        backlog_id = re.search(r"(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})", prompt)
        if backlog_id:
            reminders.append(
                "--- RFC 2119 Governance (MUST) ---\n"
                "Work item closure detected. MUST use /close to validate DoD.\n"
                f"Command: /close {backlog_id.group(1)}\n"
                "Override: Include 'skip reminder' in your message.\n"
                "--- End Governance Reminder ---"
            )

    return "\n".join(reminders) if reminders else None
