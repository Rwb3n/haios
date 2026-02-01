---
template: implementation_plan
status: complete
date: 2026-02-01
backlog_id: WORK-064
title: PreToolUse additionalContext Implementation
author: Hephaestus
lifecycle_phase: plan
session: 277
version: '1.5'
generated: 2026-02-01
last_updated: '2026-02-01T22:14:11'
memory_refs:
- 82928
- 82751
---
# Implementation Plan: PreToolUse additionalContext Implementation

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory queried - 82928 confirms ADOPT decision |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

PreToolUse hook will inject `additionalContext` with current activity state and blocked primitives, giving agents visibility into governance constraints BEFORE tool execution.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/pre_tool_use.py` |
| Lines of code affected | ~30 | Add helper + modify handle() |
| New files to create | 0 | N/A |
| Tests to write | 3 | Unit tests for new helper |
| Dependencies | 0 | No downstream consumers to update |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single file, no imports change |
| Risk of regression | Low | Adding new field, not changing existing |
| External dependencies | Low | Uses existing GovernanceLayer |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 20 min | High |
| Verification | 10 min | High |
| **Total** | ~45 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/pre_tool_use.py:133-185
def _check_governed_activity(tool_name: str, tool_input: dict) -> Optional[dict]:
    """Check governed activity via GovernanceLayer (E2.4 CH-004)."""
    try:
        # ... imports and setup ...
        layer = GovernanceLayer()
        state = layer.get_activity_state()
        primitive = layer.map_tool_to_primitive(tool_name, tool_input)

        result = layer.check_activity(primitive, state, context)

        if not result.allowed:
            return _deny(result.reason)

        if result.reason and result.reason != "Activity allowed":
            return _allow_with_warning(result.reason)

        return None  # Allow silently - NO CONTEXT PROVIDED
    except Exception:
        return None
```

**Behavior:** Returns `hookSpecificOutput` only when action is blocked/warned.

**Result:** Agent has no visibility into current state before attempting tools. Repeatedly attempts blocked actions, wasting tokens.

### Desired State

```python
# .claude/hooks/hooks/pre_tool_use.py - Modified
def _check_governed_activity(tool_name: str, tool_input: dict) -> Optional[dict]:
    """Check governed activity via GovernanceLayer (E2.4 CH-004)."""
    try:
        # ... imports and setup ...
        layer = GovernanceLayer()
        state = layer.get_activity_state()
        primitive = layer.map_tool_to_primitive(tool_name, tool_input)

        result = layer.check_activity(primitive, state, context)

        if not result.allowed:
            return _deny_with_context(result.reason, state, layer)  # NEW

        if result.reason and result.reason != "Activity allowed":
            return _allow_with_context(result.reason, state, layer)  # NEW

        return _allow_with_context(None, state, layer)  # NEW - Always provide context
    except Exception:
        return None
```

**Behavior:** Always returns `additionalContext` with state visibility, regardless of decision.

**Result:** Agent sees `[STATE: DO] Blocked: user-query, memory-search, web-*` BEFORE attempting tools.

---

## Tests First (TDD)

> **Note (A3 revision):** Tests use actual mocking pattern from `test_governance_layer.py` - mock `subprocess.run` to control `just get-cycle` output.

### Test 1: additionalContext present on allow
```python
def test_additional_context_on_allow(mocker):
    """additionalContext should be present even when tool is allowed."""
    import subprocess
    from hooks.pre_tool_use import handle

    # Mock subprocess.run to simulate DO state
    mock_result = mocker.Mock()
    mock_result.stdout = "implementation-cycle/DO/WORK-064"
    mock_result.returncode = 0
    mocker.patch.object(subprocess, "run", return_value=mock_result)

    hook_data = {"tool_name": "Read", "tool_input": {"file_path": "/some/file.py"}}
    result = handle(hook_data)

    # Read is allowed in DO - should have additionalContext
    assert result is not None
    assert "hookSpecificOutput" in result
    assert "additionalContext" in result["hookSpecificOutput"]
```

### Test 2: additionalContext includes state and blocked primitives
```python
def test_additional_context_includes_state_and_blocked(mocker):
    """additionalContext should contain current state and blocked primitives."""
    import subprocess
    from hooks.pre_tool_use import handle

    mock_result = mocker.Mock()
    mock_result.stdout = "implementation-cycle/DO/WORK-064"
    mock_result.returncode = 0
    mocker.patch.object(subprocess, "run", return_value=mock_result)

    hook_data = {"tool_name": "Read", "tool_input": {}}
    result = handle(hook_data)

    context = result["hookSpecificOutput"].get("additionalContext", "")
    assert "[STATE: DO]" in context
    assert "Blocked:" in context
    # DO state blocks: user-query, web-fetch, web-search, memory-search, memory-store
    assert "user-query" in context
```

### Test 3: Backward compatibility - deny still works with context
```python
def test_deny_behavior_preserved_with_context(mocker):
    """Deny responses should still block with reason AND include context."""
    import subprocess
    from hooks.pre_tool_use import handle

    mock_result = mocker.Mock()
    mock_result.stdout = "implementation-cycle/DO/WORK-064"
    mock_result.returncode = 0
    mocker.patch.object(subprocess, "run", return_value=mock_result)

    # AskUserQuestion is blocked in DO state
    hook_data = {"tool_name": "AskUserQuestion", "tool_input": {}}
    result = handle(hook_data)

    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "permissionDecisionReason" in result["hookSpecificOutput"]
    assert "additionalContext" in result["hookSpecificOutput"]  # NEW
```

### Test 4: Graceful degradation when governance unavailable
```python
def test_graceful_degradation_on_governance_failure(mocker):
    """When GovernanceLayer fails, return None (fail-permissive)."""
    import subprocess
    from hooks.pre_tool_use import handle

    # Make subprocess.run raise exception
    mocker.patch.object(subprocess, "run", side_effect=Exception("Simulated failure"))

    hook_data = {"tool_name": "Read", "tool_input": {}}
    result = handle(hook_data)

    # Should return None (allow silently) on failure
    assert result is None
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/hooks/pre_tool_use.py`
**Location:** Lines 133-185 in `_check_governed_activity()` + new helper functions

#### Change 1: Add `_build_additional_context()` helper

**New Code (add after line 455):**
```python
def _build_additional_context(state: str, layer) -> str:
    """
    Build additionalContext string with state and blocked primitives.

    Args:
        state: Current activity state (EXPLORE, DESIGN, PLAN, DO, CHECK, DONE)
        layer: GovernanceLayer instance

    Returns:
        Context string like "[STATE: DO] Blocked: user-query, web-fetch, web-search"
    """
    try:
        matrix = layer._load_activity_matrix()
        rules = matrix.get("rules", {})

        # Find blocked primitives for this state
        blocked = []
        for primitive, state_rules in rules.items():
            if primitive.startswith("_"):
                continue
            rule = state_rules.get(state, state_rules.get("_all_states", {}))
            if rule.get("action") == "block":
                blocked.append(primitive)

        blocked_str = ", ".join(sorted(blocked)) if blocked else "none"
        return f"[STATE: {state}] Blocked: {blocked_str}"

    except Exception:
        return f"[STATE: {state}]"


def _allow_with_context(reason: str | None, state: str, layer) -> dict:
    """Return allow response with additionalContext."""
    context = _build_additional_context(state, layer)
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "additionalContext": context,
        }
    }
    if reason:
        result["hookSpecificOutput"]["permissionDecisionReason"] = reason
    return result


def _deny_with_context(reason: str, state: str, layer) -> dict:
    """Return deny response with additionalContext."""
    context = _build_additional_context(state, layer)
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
            "additionalContext": context,
        }
    }
```

#### Change 2: Modify `_check_governed_activity()` to use new helpers

**Current Code (lines 175-185):**
```python
        if not result.allowed:
            return _deny(result.reason)

        if result.reason and result.reason != "Activity allowed":
            return _allow_with_warning(result.reason)

        return None  # Allow silently
```

**Changed Code:**
```python
        if not result.allowed:
            return _deny_with_context(result.reason, state, layer)

        if result.reason and result.reason != "Activity allowed":
            return _allow_with_context(result.reason, state, layer)

        return _allow_with_context(None, state, layer)  # Always provide context
```

### Call Chain Context

```
Claude Code (PreToolUse event)
    |
    +-> handle(hook_data)
            |
            +-> _check_governed_activity()  # <-- What we're changing
            |       Now returns: {"hookSpecificOutput": {..., "additionalContext": "..."}}
            |
            +-> (other governance checks - unchanged)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Always return context | Yes, even on allow | Agent visibility is the goal; silent allow defeats purpose |
| Format of context | `[STATE: X] Blocked: a, b, c` | Compact, scannable, matches existing governance messages |
| Fail-permissive on errors | Return None (no context) | Governance failure should not break tool execution |
| Blocked list computation | Dynamic from activity_matrix.yaml | Single source of truth, no duplication |

### Input/Output Examples

**Before Fix (current behavior):**
```
Tool: AskUserQuestion in DO state
Result: {"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "..."}}
Problem: Agent doesn't know state until AFTER attempting blocked tool
```

**After Fix:**
```
Tool: Read in DO state (allowed)
Result: {
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "additionalContext": "[STATE: DO] Blocked: user-query, web-fetch, web-search, memory-search, memory-store"
  }
}
Improvement: Agent sees blocked primitives BEFORE attempting them
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| GovernanceLayer unavailable | Return None (fail-permissive) | Test 4 |
| No blocked primitives | "Blocked: none" | Implicit in Test 2 |
| Unknown state | Default to EXPLORE | Existing GovernanceLayer behavior |

### Open Questions

**Q: Should additionalContext be on ALL responses or only governed activity?**

Only on governed activity responses. Other governance checks (SQL, PowerShell) have different context that wouldn't benefit from activity state.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | - | - | No operator decisions needed - design follows WORK-057 investigation |

---

## Implementation Steps

### Step 0: Pre-Implementation Verification (A1 critique)
> **MUST verify BEFORE writing implementation code** - addresses A1 assumption about Claude Code additionalContext behavior.

- [ ] **Verify additionalContext display:** Create minimal test hook returning:
  ```python
  return {"hookSpecificOutput": {"permissionDecision": "allow", "additionalContext": "TEST"}}
  ```
- [ ] Confirm "TEST" appears in agent context before tool execution
- [ ] If NOT visible: STOP and investigate Claude Code documentation

### Step 1: Write Failing Tests
- [ ] Add tests to `tests/test_pre_tool_use.py`
- [ ] Test 1: `test_additional_context_on_allow`
- [ ] Test 2: `test_additional_context_includes_state_and_blocked`
- [ ] Test 3: `test_deny_behavior_preserved_with_context`
- [ ] Test 4: `test_graceful_degradation_on_governance_failure`
- [ ] Verify all tests fail (red)

### Step 2: Add Helper Functions
- [ ] Add `_build_additional_context()` to pre_tool_use.py
- [ ] Add `_allow_with_context()` to pre_tool_use.py
- [ ] Add `_deny_with_context()` to pre_tool_use.py
- [ ] Tests 1, 2, 3 should now be closer to passing

### Step 3: Modify `_check_governed_activity()`
- [ ] Replace `_deny()` calls with `_deny_with_context()`
- [ ] Replace `_allow_with_warning()` with `_allow_with_context()`
- [ ] Replace `return None` with `return _allow_with_context(None, state, layer)`
- [ ] Tests 1, 2, 3 pass (green)

### Step 4: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)
- [ ] Demo: Run a tool in DO state, verify additionalContext appears

### Step 5: Documentation Update
- [ ] Update CLAUDE.md with additionalContext note in Hooks section

### Step 6: N/A - No Migration
**SKIPPED:** No migration/rename - adding new functionality to existing file

---

## Verification

- [ ] Tests pass (`pytest tests/test_pre_tool_use.py -v`)
- [ ] N/A - No README changes needed (modifying existing file)
- [ ] Demo: Execute tool in DO state, verify context

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance overhead | Low | `_build_additional_context()` uses cached matrix |
| Output verbosity | Low | Context string is compact (~60 chars) |
| Breaking existing consumers | Low | Adding field, not changing existing |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 277 | 2026-02-01 | - | In Progress | Plan authored, starting implementation |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Modify pre_tool_use.py - Add additionalContext to hookSpecificOutput | [ ] | Read file, verify new helpers exist |
| Format state context - "[STATE: {state}] Blocked: {blocked_primitives}" | [ ] | Test output shows format |
| Test governance unchanged - Existing block/warn behavior preserved | [ ] | pytest passes, deny test passes |
| Document feature - Update CLAUDE.md with additionalContext usage | [ ] | Read CLAUDE.md |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/pre_tool_use.py` | 3 new helpers + modified `_check_governed_activity()` | [ ] | |
| `tests/test_pre_tool_use.py` | 4 tests for additionalContext | [ ] | |
| `CLAUDE.md` | Hook section mentions additionalContext | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_pre_tool_use.py -v
# Expected: 4 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [No] | Pending implementation |
| Test output pasted above? | [No] | Pending implementation |
| Any deviations from plan? | [No] | - |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** - PreToolUse hook is invoked by Claude Code on every tool call
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation updated (CLAUDE.md)
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-057/WORK.md (parent investigation)
- Memory ref 82928 (ADOPT decision)
- @.claude/haios/config/activity_matrix.yaml (blocked primitives source)

---
