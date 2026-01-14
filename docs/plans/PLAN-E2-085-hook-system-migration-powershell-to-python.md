---
template: implementation_plan
status: complete
date: 2025-12-20
backlog_id: E2-085
title: "Hook System Migration PowerShell to Python"
author: Hephaestus
lifecycle_phase: done
session: 91
spawned_by: Session-80-operator-question
related: [E2-076d, E2-037, E2-007, E2-117]
milestone: M4-Research
enables: [E2-117]
version: "1.3"
---
# generated: 2025-12-20
# System Auto: last updated on: 2025-12-20 22:33:48
# Implementation Plan: Hook System Migration PowerShell to Python

@docs/investigations/INVESTIGATION-E2-085-hook-migration-powershell-to-python.md
@docs/epistemic_state.md

---

## Goal

Migrate all 4 PowerShell hooks (UserPromptSubmit, PreToolUse, PostToolUse, Stop) to a single Python dispatcher, eliminating bash/PowerShell escaping issues and enabling cross-platform operation.

---

## Current State vs Desired State

### Current State

```
.claude/hooks/
  UserPromptSubmit.ps1  (~385 lines) - Date/time, vitals, thresholds, lifecycle, RFC2119
  PreToolUse.ps1        (~223 lines) - SQL blocking, path governance, backlog_id validation
  PostToolUse.ps1       (~430 lines) - Timestamps, validation, cascade, cycle events
  Stop.ps1              (~108 lines) - Calls reasoning_extraction.py

settings.local.json:
  "PreToolUse": "powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/PreToolUse.ps1"
  (similar for all hooks)
```

**Behavior:** PowerShell scripts invoked through bash/Claude Code. Variables like `$_`, `$Matches`, `$variable` get mangled by shell layer.

**Result:** Recurring bugs (Sessions 49, 50, 80, 90). Every inline PowerShell command fails. Development friction.

### Desired State

```
.claude/hooks/
  hook_dispatcher.py    (~500 lines) - Single entry point for all hooks
  hooks/                 - Optional: submodules per hook type
    user_prompt_submit.py
    pre_tool_use.py
    post_tool_use.py
    stop.py

settings.local.json:
  "PreToolUse": "python .claude/hooks/hook_dispatcher.py"
  (same script for all hooks - event type comes from JSON input)
```

**Behavior:** Python handles JSON parsing, no escaping issues. Cross-platform. Can import haios_etl.

**Result:** No variable mangling. Clean JSON handling. Single codebase to maintain.

---

## Tests First (TDD)

Test file: `tests/test_hooks.py`

### Test 1: Dispatcher Routes to Correct Handler
```python
def test_dispatcher_routes_user_prompt_submit():
    """Verify dispatcher routes UserPromptSubmit to correct handler."""
    hook_input = {"hook_event_name": "UserPromptSubmit", "prompt": "test"}
    result = dispatch_hook(hook_input)
    assert "Today is" in result  # Date/time injection

def test_dispatcher_routes_pre_tool_use():
    hook_input = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "ls"}}
    result = dispatch_hook(hook_input)
    assert result is None or "hookSpecificOutput" in str(result)
```

### Test 2: UserPromptSubmit Vitals Injection
```python
def test_vitals_injection_with_slim_json():
    """Verify vitals block is injected when haios-status-slim.json exists."""
    hook_input = {"hook_event_name": "UserPromptSubmit", "prompt": "test", "cwd": TEST_CWD}
    result = dispatch_hook(hook_input)
    assert "HAIOS Vitals" in result
    assert "Milestone:" in result

def test_vitals_graceful_fail_no_slim():
    """Verify no crash if slim.json missing."""
    hook_input = {"hook_event_name": "UserPromptSubmit", "prompt": "test", "cwd": "/nonexistent"}
    result = dispatch_hook(hook_input)
    assert "Today is" in result  # Still outputs date
```

### Test 3: PreToolUse SQL Blocking
```python
def test_pretooluse_blocks_direct_sql():
    """Verify SQL queries are blocked without schema-verifier."""
    hook_input = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "sqlite3 db.sqlite 'SELECT * FROM concepts'"}
    }
    result = dispatch_hook(hook_input)
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

def test_pretooluse_allows_safe_sql():
    """Verify safe patterns like PRAGMA are allowed."""
    hook_input = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "sqlite3 db.sqlite 'PRAGMA table_info(concepts)'"}
    }
    result = dispatch_hook(hook_input)
    assert result is None  # No blocking
```

### Test 4: PostToolUse Timestamp Injection
```python
def test_posttooluse_adds_timestamp():
    """Verify timestamps are added to edited files."""
    # Create temp file
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(b"# original content\n")
        temp_path = f.name
    try:
        hook_input = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_response": {"filePath": temp_path}
        }
        dispatch_hook(hook_input)
        content = Path(temp_path).read_text()
        assert "System Auto: last updated on:" in content
    finally:
        Path(temp_path).unlink()
```

### Test 5: Stop Hook Calls Extraction
```python
def test_stop_hook_calls_extraction():
    """Verify Stop hook invokes reasoning_extraction.py."""
    hook_input = {
        "hook_event_name": "Stop",
        "transcript_path": "/tmp/test_transcript.jsonl",
        "stop_hook_active": False
    }
    # Should not crash, may skip if transcript doesn't exist
    result = dispatch_hook(hook_input)
    assert result is None or isinstance(result, str)

def test_stop_hook_prevents_infinite_loop():
    """Verify stop_hook_active=True causes early exit."""
    hook_input = {"hook_event_name": "Stop", "stop_hook_active": True}
    result = dispatch_hook(hook_input)
    assert result is None
```

### Test 6: Backward Compatibility - JSON Output Format
```python
def test_pretooluse_json_output_format():
    """Verify PreToolUse returns exact JSON structure expected by Claude Code."""
    hook_input = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "docs/checkpoints/new-file.md"}
    }
    result = dispatch_hook(hook_input)
    assert "hookSpecificOutput" in result
    assert result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert result["hookSpecificOutput"]["permissionDecision"] in ["allow", "deny", "ask"]
```

---

## Detailed Design

### Architecture: Single Dispatcher Pattern

```
Claude Code (bash layer)
    |
    v
python .claude/hooks/hook_dispatcher.py   <-- Single entry point
    |
    +-- Reads JSON from stdin
    +-- Routes by hook_event_name:
    |       "UserPromptSubmit" -> user_prompt_submit()
    |       "PreToolUse"       -> pre_tool_use()
    |       "PostToolUse"      -> post_tool_use()
    |       "Stop"             -> stop()
    |
    +-- Outputs text (UserPromptSubmit) or JSON (PreToolUse) to stdout
```

### File Structure

```
.claude/hooks/
  hook_dispatcher.py      # Main entry point (new)
  hooks/                  # Submodules (new)
    __init__.py
    user_prompt_submit.py # Migrated from .ps1
    pre_tool_use.py       # Migrated from .ps1
    post_tool_use.py      # Migrated from .ps1
    stop.py               # Migrated from .ps1
  archive/                # Archived PowerShell (new)
    UserPromptSubmit.ps1
    PreToolUse.ps1
    PostToolUse.ps1
    Stop.ps1
  memory_retrieval.py     # Existing - unchanged
  reasoning_extraction.py # Existing - unchanged
```

### Function Signatures

```python
# hook_dispatcher.py
def main() -> None:
    """Entry point. Read JSON from stdin, route to handler, output to stdout."""

def dispatch_hook(hook_data: dict) -> Optional[Union[str, dict]]:
    """
    Route hook event to appropriate handler.

    Args:
        hook_data: Parsed JSON from Claude Code

    Returns:
        str: For UserPromptSubmit (text injection)
        dict: For PreToolUse (JSON with permissionDecision)
        None: For PostToolUse/Stop (side effects only)
    """

# hooks/user_prompt_submit.py
def handle(hook_data: dict) -> str:
    """
    Process UserPromptSubmit hook.

    Returns:
        Concatenated context string:
        - Date/time
        - HAIOS Vitals
        - Dynamic thresholds
        - Lifecycle guidance
        - RFC2119 reminders
    """

# hooks/pre_tool_use.py
def handle(hook_data: dict) -> Optional[dict]:
    """
    Process PreToolUse hook.

    Returns:
        None: Allow operation (no output)
        dict: Block/warn with hookSpecificOutput structure
    """

# hooks/post_tool_use.py
def handle(hook_data: dict) -> Optional[str]:
    """
    Process PostToolUse hook.

    Side effects:
        - Add timestamps to files
        - Trigger template validation
        - Refresh discoverable artifacts
        - Trigger cascade hooks
        - Log cycle transitions

    Returns:
        Optional status message
    """

# hooks/stop.py
def handle(hook_data: dict) -> Optional[str]:
    """
    Process Stop hook.

    Side effects:
        - Call reasoning_extraction.py for learning capture

    Returns:
        Optional extraction status
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Single dispatcher vs 4 scripts | Single dispatcher | Cleaner config, shared utilities, consistent error handling |
| Submodule per hook | Yes | Keeps individual handlers focused, easier to test |
| Import haios_etl | Yes for Stop/extraction | Enables database access, embedding generation |
| Keep existing Python scripts | Yes | memory_retrieval.py, reasoning_extraction.py already work |
| Archive PowerShell | Archive folder | Preserve for reference, easy rollback |

### Input/Output Examples

**UserPromptSubmit Input:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/haios/transcript.jsonl",
  "cwd": "D:\\PROJECTS\\haios",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "/coldstart"
}
```

**UserPromptSubmit Output:**
```
Today is Saturday, 2025-12-20 10:15 PM

--- HAIOS Vitals ---
Milestone: M4-Research (14%)
Since S88: +1 done, +12 new
Commands: /new-*, /close, /validate, /status
Skills: extract-content, implementation-cycle, memory-agent, schema-ref
Agents: preflight-checker, schema-verifier, test-runner, why-capturer
MCPs: haios-memory(13), context7(2)
Recipes: just --list
---
```

**PreToolUse Input (blocked):**
```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {"command": "sqlite3 haios_memory.db 'SELECT * FROM concepts'"}
}
```

**PreToolUse Output (blocked):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "BLOCKED: Direct SQL not allowed. Use Task(subagent_type='schema-verifier')"
  }
}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Missing haios-status-slim.json | Graceful skip, still output date | Test 2 |
| Empty or malformed JSON input | Try/except, exit 0 | Implicit |
| stop_hook_active=True | Early exit to prevent loops | Test 5 |
| Unknown hook_event_name | Log warning, exit 0 | New test |
| File not found (PostToolUse) | Skip timestamp, no crash | New test |
| Non-.md file in governed path | Allow (only block .md) | Test 6 |

### Migration Mapping

| PowerShell Feature | Python Equivalent |
|--------------------|-------------------|
| `$jsonInput = [Console]::In.ReadToEnd()` | `sys.stdin.read()` |
| `ConvertFrom-Json` | `json.loads()` |
| `ConvertTo-Json -Compress` | `json.dumps()` |
| `Get-Date -Format "yyyy-MM-dd"` | `datetime.now().strftime("%Y-%m-%d")` |
| `Test-Path` | `Path.exists()` |
| `Get-Content -Raw` | `Path.read_text()` |
| `Set-Content` | `Path.write_text()` |
| `-match` regex | `re.search()` |
| `Write-Output` | `print()` |
| `exit 0` | `sys.exit(0)` |

---

## Implementation Steps

### Step 1: Create Directory Structure & Write Failing Tests
- [ ] Create `.claude/hooks/hooks/` directory
- [ ] Create `tests/test_hooks.py` with tests from "Tests First" section
- [ ] Verify all tests fail (red) - import errors expected

### Step 2: Implement Dispatcher Skeleton
- [ ] Create `.claude/hooks/hook_dispatcher.py` with main() and dispatch_hook()
- [ ] Create `.claude/hooks/hooks/__init__.py`
- [ ] Create stub handlers that return None
- [ ] Tests for routing pass (green)

### Step 3: Migrate UserPromptSubmit
- [ ] Create `.claude/hooks/hooks/user_prompt_submit.py`
- [ ] Implement date/time output
- [ ] Implement vitals injection (read haios-status-slim.json)
- [ ] Implement dynamic thresholds
- [ ] Implement lifecycle guidance
- [ ] Implement RFC2119 reminders
- [ ] Tests 1, 2 pass (green)

### Step 4: Migrate PreToolUse
- [ ] Create `.claude/hooks/hooks/pre_tool_use.py`
- [ ] Implement SQL blocking logic
- [ ] Implement governed path checks
- [ ] Implement backlog_id validation
- [ ] Implement memory_refs warning
- [ ] Tests 3, 6 pass (green)

### Step 5: Migrate PostToolUse
- [ ] Create `.claude/hooks/hooks/post_tool_use.py`
- [ ] Implement timestamp injection
- [ ] Implement template validation call
- [ ] Implement discoverable artifact refresh
- [ ] Implement cascade detection
- [ ] Implement cycle event logging
- [ ] Test 4 passes (green)

### Step 6: Migrate Stop
- [ ] Create `.claude/hooks/hooks/stop.py`
- [ ] Implement stop_hook_active check
- [ ] Implement reasoning_extraction.py invocation
- [ ] Tests 5 pass (green)

### Step 7: Update Configuration
- [ ] Update `.claude/settings.local.json` to use Python dispatcher
- [ ] Archive PowerShell hooks to `.claude/hooks/archive/`
- [ ] All tests pass

### Step 8: Integration Verification
- [ ] Run full test suite (`pytest tests/ -v`)
- [ ] Manual test: `/coldstart` produces vitals
- [ ] Manual test: Write to governed path is blocked
- [ ] Manual test: Edit file gets timestamp
- [ ] No regressions in full suite

---

## Verification

- [ ] All 6 test categories pass
- [ ] Manual demo of each hook type
- [ ] CLAUDE.md updated (remove PowerShell warnings if no longer applicable)
- [ ] hooks/README.md updated with new architecture

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python startup delay (~250ms) | Low | Already tolerated; hooks have multi-second budget |
| Missing functionality | High | Comprehensive tests, side-by-side comparison |
| Breaking existing behavior | High | Archive PS1 for rollback, test each feature |
| Path handling Windows vs Unix | Medium | Use pathlib.Path throughout |
| Unicode/encoding issues | Medium | Explicit UTF-8 in all file operations |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 91 | 2025-12-20 | - | PLAN | Initial plan creation |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hook_dispatcher.py` | Entry point with dispatch_hook() | [x] | 3470 bytes |
| `.claude/hooks/hooks/user_prompt_submit.py` | Date, vitals, thresholds, lifecycle, RFC2119 | [x] | 12526 bytes |
| `.claude/hooks/hooks/pre_tool_use.py` | SQL blocking, path governance | [x] | 6642 bytes |
| `.claude/hooks/hooks/post_tool_use.py` | Timestamps, validation, cascade, cycle | [x] | 14396 bytes |
| `.claude/hooks/hooks/stop.py` | Extraction invocation, loop prevention | [x] | 1956 bytes |
| `.claude/hooks/archive/` | All 4 .ps1 files archived | [x] | All present |
| `.claude/settings.local.json` | Python commands for all hooks | [x] | Updated |
| `tests/test_hooks.py` | All tests exist and pass | [x] | 22 tests |

**Verification Commands:**
```bash
pytest tests/test_hooks.py -v
# Result: 22 passed in 0.16s
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All files confirmed |
| Test output pasted above? | Yes | 22 passed |
| Any deviations from plan? | Yes | Added utf-8-sig encoding for BOM handling (Windows) |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (22/22)
- [x] WHY captured (memory_refs: 76916-76923)
- [x] Documentation current (CLAUDE.md PowerShell warnings still apply to utility scripts)
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## References

- INVESTIGATION-E2-085-hook-migration-powershell-to-python.md
- epistemic_state.md (PowerShell-Bash Interop pattern)
- Session 49, 50, 80, 90 (escaping bug occurrences)
- E2-117 (milestone auto-discovery, blocked by this)

---


<!-- VALIDATION ERRORS (2025-12-20 22:23:08):
  - ERROR: Missing required fields: directive_id
-->


<!-- VALIDATION ERRORS (2025-12-20 22:33:41):
  - ERROR: Missing required fields: directive_id
-->


<!-- VALIDATION ERRORS (2025-12-20 22:33:48):
  - ERROR: Missing required fields: directive_id
-->


<!-- VALIDATION ERRORS (2025-12-20 22:43:01):
  - ERROR: Missing required fields: directive_id
-->


<!-- VALIDATION ERRORS (2025-12-20 22:43:45):
  - ERROR: Missing required fields: directive_id
-->


<!-- VALIDATION ERRORS (2025-12-20 22:44:27):
  - ERROR: Missing required fields: directive_id
-->


<!-- VALIDATION ERRORS (2025-12-20 22:44:32):
  - ERROR: Missing required fields: directive_id
-->


<!-- VALIDATION ERRORS (2025-12-20 22:44:41):
  - ERROR: Missing required fields: directive_id
-->
