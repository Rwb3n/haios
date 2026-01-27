---
template: implementation_plan
status: complete
date: 2026-01-27
backlog_id: E2-305
title: PreToolUse Bash Guard for Scaffold Recipes
author: Hephaestus
lifecycle_phase: plan
session: 252
version: '1.5'
generated: 2026-01-27
last_updated: '2026-01-27T22:36:42'
---
# Implementation Plan: PreToolUse Bash Guard for Scaffold Recipes

@docs/work/active/E2-305/WORK.md
@.claude/hooks/hooks/pre_tool_use.py

---

## Goal

The PreToolUse hook will block Bash calls to scaffold recipes (`just work`, `just plan`, `just inv`, `just scaffold`, `just new-investigation`) and redirect agents to `/new-*` commands.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `pre_tool_use.py`, `test_hooks.py` |
| Lines of code affected | ~30 new | New function + wiring |
| New files to create | 0 | - |
| Tests to write | 5 | See Tests First section |
| Dependencies | 0 | No new imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single hook file, existing pattern |
| Risk of regression | Low | Existing tests cover SQL/PowerShell guards |
| External dependencies | Low | None |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/pre_tool_use.py:71-84
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        result = _check_sql_governance(command)
        if result:
            return result
        result = _check_powershell_governance(command)
        if result:
            return result
        return None  # Allow other bash commands
```

**Behavior:** Bash commands checked for SQL and PowerShell only. Scaffold recipes pass through.

### Desired State

```python
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        result = _check_sql_governance(command)
        if result:
            return result
        result = _check_powershell_governance(command)
        if result:
            return result
        result = _check_scaffold_governance(command)
        if result:
            return result
        return None
```

**Behavior:** Scaffold recipe calls blocked with redirect to `/new-*` commands.

---

## Tests First (TDD)

### Test 1: Block `just work` command
```python
def test_blocks_just_work_recipe():
    from hooks.pre_tool_use import handle
    result = handle({"tool_name": "Bash", "tool_input": {"command": "just work E2-999 'test'"}})
    assert result is not None
    assert "deny" in str(result)
    assert "/new-work" in str(result)
```

### Test 2: Block `just plan` command
```python
def test_blocks_just_plan_recipe():
    from hooks.pre_tool_use import handle
    result = handle({"tool_name": "Bash", "tool_input": {"command": "just plan E2-999 'test'"}})
    assert result is not None
    assert "deny" in str(result)
    assert "/new-plan" in str(result)
```

### Test 3: Block `just inv` command
```python
def test_blocks_just_inv_recipe():
    from hooks.pre_tool_use import handle
    result = handle({"tool_name": "Bash", "tool_input": {"command": "just inv INV-999 'test'"}})
    assert result is not None
    assert "deny" in str(result)
```

### Test 4: Block `just scaffold` command
```python
def test_blocks_just_scaffold_recipe():
    from hooks.pre_tool_use import handle
    result = handle({"tool_name": "Bash", "tool_input": {"command": "just scaffold work E2-999 'test'"}})
    assert result is not None
    assert "deny" in str(result)
```

### Test 5: Allow non-scaffold `just` commands
```python
def test_allows_non_scaffold_just_commands():
    from hooks.pre_tool_use import handle
    result = handle({"tool_name": "Bash", "tool_input": {"command": "just ready"}})
    assert result is None  # Allowed
```

### Test 6: Allow `just scaffold-observations` (not a scaffold recipe)
```python
def test_allows_just_scaffold_observations():
    from hooks.pre_tool_use import handle
    result = handle({"tool_name": "Bash", "tool_input": {"command": "just scaffold-observations E2-305"}})
    assert result is None  # Allowed - hyphenated recipe, not scaffold
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/hooks/pre_tool_use.py`

**Change 1:** Add call in `handle()` at line 82 (before `return None`):

```diff
         result = _check_powershell_governance(command)
         if result:
             return result
+        result = _check_scaffold_governance(command)
+        if result:
+            return result
         return None  # Allow other bash commands
```

**Change 2:** Add new function `_check_scaffold_governance()`:

```python
def _check_scaffold_governance(command: str) -> Optional[dict]:
    """
    Block direct scaffold recipe calls (E2-305).

    Scaffold recipes predate cycle skills and produce files with unfilled
    template placeholders. Agents must use /new-* commands instead.
    """
    if not command:
        return None

    # Detect scaffold recipe patterns
    scaffold_patterns = {
        r'\bjust\s+work\b': "/new-work",
        r'\bjust\s+plan\b': "/new-plan",
        r'\bjust\s+inv\b': "/new-investigation",
        r'\bjust\s+scaffold(?:\s|$)': "/new-work, /new-plan, or /new-investigation",
        r'\bjust\s+new-investigation\b': "/new-investigation",
    }

    for pattern, redirect in scaffold_patterns.items():
        if re.search(pattern, command, re.IGNORECASE):
            return _deny(
                f"BLOCKED: Direct scaffold recipe call. Use '{redirect}' command instead. "
                "Scaffold recipes produce files with unfilled placeholders."
            )

    return None
```

### Call Chain Context

```
hook_dispatcher.dispatch_hook()
    |
    +-> pre_tool_use.handle()
            |
            +-> _check_sql_governance()
            +-> _check_powershell_governance()
            +-> _check_scaffold_governance()    # <-- NEW
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pattern matching approach | Regex with `\b` word boundaries | Avoids false positives on `just ready`, `just queue`, etc. |
| Redirect message | Specific `/new-*` per recipe | Agents know exactly which command to use |
| Allow `just scaffold` subcommands for non-governed types | Block all `just scaffold` | Conservative - all scaffold paths should go through commands |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| `just ready` (non-scaffold) | Allowed - no match | Test 5 |
| `just set-cycle` (non-scaffold) | Allowed - no match | Implicit |
| `just scaffold-observations` | Not matched — pattern requires whitespace or EOL after `scaffold` | Test 6 |
| `just coldstart-orchestrator` | Not matched | Implicit |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | Work item has no operator_decisions |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 5 tests to `tests/test_hooks.py`
- [ ] Verify all 5 fail (red)

### Step 2: Add `_check_scaffold_governance()` function
- [ ] Add function to `pre_tool_use.py`
- [ ] Tests 1-4 pass (green), Test 5 already passes

### Step 3: Wire into `handle()`
- [ ] Add call between PowerShell check and `return None`
- [ ] All 5 tests pass (green)

### Step 4: Integration Verification
- [ ] Full test suite passes: `pytest tests/ -v`
- [ ] No regressions

### Step 5: README Sync
- [ ] **SKIPPED:** No new files or directory changes. Hook file already documented.

### Step 6: Consumer Verification
- [ ] **SKIPPED:** Not a migration. Hook is consumed by `hook_dispatcher.py` which already routes to `pre_tool_use.handle()`.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positive on legitimate `just` commands | Medium | Word boundary regex + test for `just ready` |
| `just scaffold-observations` blocked | Medium | Pattern `\bjust\s+scaffold\b` won't match `scaffold-observations` (hyphen breaks word boundary) |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| PreToolUse Bash guard pattern matching `just (work\|plan\|inv\|scaffold\|new-investigation)` calls | [ ] | Function exists and blocks |
| Block message redirecting to appropriate `/new-*` command | [ ] | Deny message contains redirect |
| Test coverage for the new guard | [ ] | 5 tests pass |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/pre_tool_use.py` | `_check_scaffold_governance` exists, wired in `handle()` | [ ] | |
| `tests/test_hooks.py` | 5 new scaffold guard tests | [ ] | |

---

## References

- @docs/work/active/INV-070/WORK.md (parent investigation)
- @.claude/hooks/hooks/pre_tool_use.py (target file)

---
