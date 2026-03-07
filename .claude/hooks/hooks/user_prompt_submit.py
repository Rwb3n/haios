# generated: 2025-12-20
# System Auto: last updated on: 2026-01-29T21:01:15
"""
UserPromptSubmit Hook Handler (E2-085, E2-119).

Provides context injection before Claude processes user prompts:
1. Date/time context
2. Session state warning (E2-287)
3. Phase contract injection (WORK-188, ADR-048)
4. Lifecycle guidance (ADR-034)
5. RFC2119 governance reminders
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# Module-level cache: tracks last-injected phase contract key (WORK-216)
# Format: "{active_cycle}/{current_phase}" — reset to None on new Python process (= new session)
_LAST_INJECTED_KEY: Optional[str] = None



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

    # Part 1.2: Compact session state line (WORK-196)
    # Read slim once here — passed to all downstream consumers (WORK-195 pattern)
    cwd = hook_data.get("cwd", "")
    slim = _read_slim(cwd)
    session_parts = []
    session_num = _get_session_number(cwd)
    if session_num:
        session_parts.append(session_num)
    working_item = _get_working_item(slim)
    if working_item:
        session_parts.append(working_item)
    duration = _get_session_duration(cwd)
    if duration:
        session_parts.append(duration)
    if session_parts:
        output_parts.append(" ".join(session_parts))

    # Part 1.5: Context budget — relay .claude/context_remaining to slim for governance events
    # (Display removed: statusLine shows context in terminal; PreToolUse injects warnings when low)
    context_pct = _read_context_remaining(cwd)
    if context_pct is not None:
        _write_context_pct_to_slim(cwd, context_pct)

    # Part 2: Session state warning (E2-287)
    session_warning = _get_session_state_warning(cwd, slim)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    # Part 2.6: Phase contract injection (WORK-188, ADR-048)
    phase_contract = _get_phase_contract(cwd, slim)
    if phase_contract:
        output_parts.append("")
        output_parts.append(phase_contract)

    # Part 3: Lifecycle guidance
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


def _read_slim(cwd: str) -> Optional[dict]:
    """Read and parse haios-status-slim.json once per handle() call.

    Returns parsed dict or None if unavailable (graceful degradation).
    WORK-195: Extracted from per-function reads to avoid redundant I/O.
    """
    if not cwd:
        return None
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return None
    try:
        return json.loads(slim_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _get_session_number(cwd: str) -> Optional[str]:
    """
    Read session number from .claude/session (last non-blank, non-comment line).

    Returns "[SESSION: N]" or None if file unavailable.
    WORK-196: Session file has 3 lines; last line is integer session number.
    """
    if not cwd:
        return None
    session_path = Path(cwd) / ".claude" / "session"
    if not session_path.exists():
        return None
    try:
        text = session_path.read_text(encoding="utf-8").strip()
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith('#')]
        if not lines:
            return None
        session_num = int(lines[-1])
        return f"[SESSION: {session_num}]"
    except Exception:
        return None


def _get_working_item(slim: Optional[dict]) -> Optional[str]:
    """
    Extract active work_id from pre-parsed slim dict.

    Returns "[WORKING: WORK-XXX]" or None if no active work item.
    WORK-196: slim already parsed once by handle() — no file I/O here.
    """
    if slim is None:
        return None
    try:
        work_id = slim.get("session_state", {}).get("work_id")
        if not work_id:
            return None
        return f"[WORKING: {work_id}]"
    except Exception:
        return None


def _get_session_duration(cwd: str) -> Optional[str]:
    """
    Calculate session duration from .claude/session file mtime.

    Returns "[DURATION: Nm]" or None if mtime unavailable.
    WORK-196: Uses file mtime as session start proxy. Resolution: 1 minute.
    """
    if not cwd:
        return None
    session_path = Path(cwd) / ".claude" / "session"
    if not session_path.exists():
        return None
    try:
        mtime = session_path.stat().st_mtime
        start = datetime.fromtimestamp(mtime)
        elapsed_minutes = int((datetime.now() - start).total_seconds() / 60)
        return f"[DURATION: {elapsed_minutes}m]"
    except Exception:
        return None


def _get_session_state_warning(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
    """
    Check if agent is working outside an active governance cycle.

    E2-287: Soft enforcement - inject warning when session_state.active_cycle is null.
    This creates friction for governance bypass without blocking.

    WORK-195: Accepts pre-parsed slim dict from handle(). No internal file read.

    Args:
        cwd: Working directory path
        slim: Pre-parsed haios-status-slim.json dict, or None if unavailable.

    Returns:
        Warning message if no active cycle, None otherwise.
    """
    if not cwd:
        return None
    if slim is None:
        return None

    try:
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


def _get_phase_contract(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
    """
    Inject current phase's behavioral contract from phase file.

    ADR-048 belt-and-suspenders: on every prompt, if an active lifecycle cycle
    is running, read and inject the current phase's contract file so the agent
    always has the behavioral contract in context (recovery after compaction).

    WORK-216: Deduplication via module-level cache. Only injects on first prompt
    of session or phase transition. Within a single phase the contract is static
    so re-injection adds no value. ADR-048 compaction recovery is preserved:
    after compaction the module process may restart (new session = cache miss)
    or the phase may change (different key = cache miss).

    Phase files live at: .claude/skills/{cycle}/phases/{PHASE}.md

    Fall-permissive: returns None if no active cycle, phase file missing, or any error.

    WORK-195: Accepts pre-parsed slim dict from handle(). No internal file read.

    Args:
        cwd: Working directory path
        slim: Pre-parsed haios-status-slim.json dict, or None if unavailable.

    Returns:
        Formatted phase contract string on first call for a given key, None on repeat.
    """
    global _LAST_INJECTED_KEY

    if not cwd:
        return None
    if slim is None:
        return None

    try:
        session_state = slim.get("session_state", {})
        active_cycle = session_state.get("active_cycle")
        current_phase = session_state.get("current_phase")

        if not active_cycle or not current_phase:
            return None

        cache_key = f"{active_cycle}/{current_phase}"

        # WORK-216: Skip re-injection when phase unchanged since last injection
        if cache_key == _LAST_INJECTED_KEY:
            return None

        phase_file = (
            Path(cwd) / ".claude" / "skills" / active_cycle / "phases" / f"{current_phase}.md"
        )
        if not phase_file.exists():
            return None

        content = phase_file.read_text(encoding="utf-8")
        _LAST_INJECTED_KEY = cache_key
        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
    except Exception:
        return None




def _write_context_pct_to_slim(cwd: str, context_pct: float) -> None:
    """Write context_pct float to haios-status-slim.json for governance event relay.

    WORK-237: Slim relay pattern — UserPromptSubmit writes, _append_event reads.
    Fail-silent: stale/missing slim is better than broken hook.

    Args:
        cwd: Working directory path.
        context_pct: Remaining context percentage (0-100 float).
    """
    if not cwd:
        return
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return
    try:
        data = json.loads(slim_path.read_text(encoding="utf-8-sig"))
        data["context_pct"] = context_pct
        slim_path.write_text(json.dumps(data, indent=4), encoding="utf-8")
    except Exception:
        pass


def _read_context_remaining(cwd: str) -> Optional[float]:
    """Read remaining context percentage from .claude/context_remaining.

    File written by statusLine with Claude Code native context_window.remaining_percentage.
    Returns float 0-100 or None if unavailable. Fail-silent.

    WORK-247: Replaces _extract_context_pct (transcript parsing) for slim relay.
    """
    if not cwd:
        return None
    try:
        remaining_file = Path(cwd) / ".claude" / "context_remaining"
        if not remaining_file.exists():
            return None
        return float(remaining_file.read_text(encoding="utf-8").strip())
    except Exception:
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
