---
template: implementation_plan
status: complete
date: 2025-12-21
backlog_id: E2-130
title: "Error Capture Rebuild"
author: Hephaestus
lifecycle_phase: done
session: 95
category: tech-debt
absorbs: [E2-FIX-003, E2-104]
version: "1.4"
generated: 2025-12-21
last_updated: 2025-12-21T23:02:26
---
# Implementation Plan: Error Capture Rebuild

@docs/pm/backlog.md
@.claude/hooks/error_capture.py
@.claude/hooks/hooks/post_tool_use.py

---

<!-- TEMPLATE GOVERNANCE (v1.4) - Reviewed -->

---

## Goal

A working error capture system that: (1) only captures actual tool failures (not false positives), (2) stores errors with dedicated `type: tool_error` for queryability, and (3) enables learning from failure patterns to inform safer abstractions.

---

## Effort Estimation (Ground Truth)

> Based on actual file/code analysis.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | settings.local.json, post_tool_use.py, error_capture.py |
| Lines of code affected | ~200 | error_capture.py rebuild + post_tool_use.py integration |
| New files to create | 1 | tests/test_error_capture.py |
| Tests to write | 6 | Detection logic + integration tests |
| Dependencies | 2 | database.py, hook_dispatcher.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Hook dispatcher, database, PostToolUse flow |
| Risk of regression | Low | error_capture was broken, no working behavior to break |
| External dependencies | Low | Only internal modules |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Config cleanup + tests | 30 min | High |
| Phase 2: Detection logic | 45 min | Medium |
| Phase 3: Integration + cleanup | 45 min | Medium |
| **Total** | ~2 hours | |

---

## Current State vs Desired State

### Current State

**1. settings.local.json (lines 169-177) - Stale hook config:**
```json
{
  "matcher": "Bash|Read|Write|Edit|Grep|Glob",
  "hooks": [{
    "type": "command",
    "command": "powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/ErrorCapture.ps1"
  }]
}
```

**2. error_capture.py (line 57) - Deprecated import:**
```python
from haios_etl.database import DatabaseManager  # DEPRECATED
```

**3. Detection logic - No error validation:**
```python
# ErrorCapture.ps1 (archived) - captured ALL tool responses containing "error" substring
# Result: 93% false positives (189 captures, ~176 false)
```

**Behavior:** Stale hook throws error on every tool use. No actual error capture working.

**Result:** Error spam in console + polluted memory with 176 false positive concepts.

### Desired State

**1. settings.local.json - Remove stale hook entirely:**
```json
// Remove the PostToolUse entry pointing to ErrorCapture.ps1
```

**2. error_capture.py - Modern imports, proper detection:**
```python
from database import get_connection  # From .claude/lib/

def is_actual_error(tool_name: str, tool_response: dict) -> bool:
    """Only return True for actual failures, not successful tool responses."""
    if tool_name == "Bash":
        return tool_response.get("exit_code", 0) != 0
    # Other tools: check for error structure, not substring
    return "error" in tool_response and isinstance(tool_response.get("error"), str)
```

**3. Dedicated type for queryability:**
```python
# Store with type="tool_error" instead of "techne"
INSERT INTO concepts (type, content, ...) VALUES ('tool_error', ...)
```

**Behavior:** Only actual failures captured. Errors queryable by type.

**Result:** Learn from real errors to inform safer abstractions.

---

## Tests First (TDD)

### Test 1: Bash Error Detection (exit_code != 0)
```python
def test_is_actual_error_bash_failure():
    """Bash with non-zero exit code is an error."""
    response = {"exit_code": 1, "stderr": "command not found"}
    assert is_actual_error("Bash", response) == True

def test_is_actual_error_bash_success():
    """Bash with exit_code 0 is NOT an error."""
    response = {"exit_code": 0, "stdout": "success"}
    assert is_actual_error("Bash", response) == False
```

### Test 2: Read/Edit/Write False Positive Prevention
```python
def test_is_actual_error_read_success_not_captured():
    """Successful Read response should NOT be captured as error."""
    response = {"type": "text", "file": {"filePath": "...", "content": "has error in code"}}
    assert is_actual_error("Read", response) == False

def test_is_actual_error_edit_success_not_captured():
    """Successful Edit response should NOT be captured as error."""
    response = {"filePath": "...", "oldString": "error handling", "newString": "..."}
    assert is_actual_error("Edit", response) == False
```

### Test 3: Actual Error Detection
```python
def test_is_actual_error_real_error_captured():
    """Real error response IS captured."""
    response = {"error": "File not found: /path/to/missing.txt"}
    assert is_actual_error("Read", response) == True
```

### Test 4: Storage with Dedicated Type
```python
def test_store_error_uses_tool_error_type():
    """Errors stored with type='tool_error' for queryability."""
    result = store_error("Bash", "command not found", "git foo")
    # Verify in DB
    conn = get_connection()
    concept = conn.execute("SELECT type FROM concepts WHERE id = ?", (result["concept_id"],)).fetchone()
    assert concept["type"] == "tool_error"
```

---

## Detailed Design

### Architecture Decision: Integration Approach

Two options for wiring error capture:

**Option A: Separate PostToolUse matcher** (like current broken setup)
- Pros: Isolated, clear separation
- Cons: Adds another hook entry, more config to maintain

**Option B: Integrate into existing PostToolUse flow** (CHOSEN)
- Pros: Single entry point, consistent with Python migration pattern
- Cons: post_tool_use.py grows slightly

**Decision:** Option B. Add `_capture_errors()` function to post_tool_use.py that calls error_capture.py logic.

### Call Chain Context

```
Claude Code PostToolUse event
    |
    v
hook_dispatcher.py (routes by event)
    |
    v
post_tool_use.py::handle()
    |
    +-- _add_timestamp()
    +-- _validate_template()
    +-- _refresh_discoverable_artifacts()
    +-- _detect_cascade()
    +-- _log_cycle_transition()
    +-- _capture_errors()          # <-- NEW (call for ALL tools)
            |
            +-- is_actual_error()  # Detection logic
            +-- store_error()      # DB storage with type=tool_error
```

### Function Signatures

```python
# .claude/lib/error_capture.py (new location, moved from hooks/)

def is_actual_error(tool_name: str, tool_response: dict) -> bool:
    """
    Determine if tool response represents an actual failure.

    Args:
        tool_name: Name of the tool (Bash, Read, Edit, Write, Grep, Glob)
        tool_response: The tool's response dict from Claude Code

    Returns:
        True only for actual failures, False for successes or false positives.
    """

def store_error(tool_name: str, error_message: str, tool_input: str = "") -> dict:
    """
    Store error to memory with dedicated type.

    Args:
        tool_name: Tool that failed
        error_message: The error message (truncated if long)
        tool_input: Summary of what was attempted

    Returns:
        {"success": True, "concept_id": N} or {"success": False, "error": "..."}
    """
```

### Detection Logic by Tool

| Tool | Is Error When | Is NOT Error When |
|------|---------------|-------------------|
| **Bash** | exit_code != 0 | exit_code == 0 (even if output contains "error") |
| **Read** | Response has "error" key with string value | Has "file" key with content |
| **Edit** | Response has "error" key | Has "filePath" + success structure |
| **Write** | Response has "error" key | Has "type": "create" or "update" |
| **Grep** | Response has "error" key | Has "numFiles" or "content" |
| **Glob** | Response has "error" key | Has file list result |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Where to put logic | .claude/lib/error_capture.py | Consistent with Python migration, importable |
| How to integrate | Add to post_tool_use.py | Single hook entry point, DRY |
| Error type | `tool_error` | Queryable, distinct from techne/doxa/episteme |
| False positive cleanup | DELETE from concepts | 176 garbage entries polluting memory |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Read of non-existent file | Capture (is error) | Test 3 |
| Edit with "error" in oldString | Don't capture (false positive) | Test 2 |
| Bash echo "error" | Don't capture (exit_code=0) | Test 1 |
| Grep with 0 results | Don't capture (not an error) | TBD |

### Open Questions

**Q: Should we capture Read errors for non-existent files?**

Yes - this is valuable. If agent repeatedly tries to Read missing files, that's a pattern worth learning from.

**Q: What about Glob with no matches?**

No - zero matches is valid behavior, not an error. Only capture if Glob returns actual error structure.

---

## Implementation Steps

### Phase 1: Config Cleanup + Test Setup

#### Step 1.1: Remove Stale Hook Entry
- [ ] Edit `.claude/settings.local.json`
- [ ] Remove PostToolUse entry at lines 169-177 (ErrorCapture.ps1 reference)
- [ ] Verify no more "hook error" messages on tool use

#### Step 1.2: Create Test File
- [ ] Create `tests/test_error_capture.py`
- [ ] Add 6 tests from TDD section above
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Phase 2: Detection Logic

#### Step 2.1: Create error_capture.py in lib
- [ ] Move/recreate `.claude/hooks/error_capture.py` → `.claude/lib/error_capture.py`
- [ ] Implement `is_actual_error()` with tool-specific logic
- [ ] Tests 1-3 pass (green)

#### Step 2.2: Implement Storage with Dedicated Type
- [ ] Update `store_error()` to use `type='tool_error'`
- [ ] Use `.claude/lib/database.py` instead of deprecated import
- [ ] Test 4 passes (green)

### Phase 3: Integration + Cleanup

#### Step 3.1: Wire into PostToolUse
- [ ] Add `_capture_errors()` to `.claude/hooks/hooks/post_tool_use.py`
- [ ] Call `_capture_errors()` in `handle()` for ALL tool types
- [ ] Import from `.claude/lib/error_capture`

#### Step 3.2: Update PostToolUse Matcher for Python Dispatcher
- [ ] Edit settings.local.json **line 160** (existing Python dispatcher entry)
- [ ] Current: `"matcher": "Edit|Write|MultiEdit"`
- [ ] New: `"matcher": "Edit|Write|MultiEdit|Bash|Read|Grep|Glob"`
- [ ] **CRITICAL:** This ensures `_capture_errors()` is invoked for ALL tool types
- [ ] Note: Removing stale entry (Step 1.1) only stops the error - this step enables capture

#### Step 3.3: Clean Up False Positives
- [ ] Run cleanup query:
```sql
DELETE FROM concepts WHERE content LIKE '%[Error Capture]%' AND type = 'techne';
```
- [ ] Verify 176 garbage entries removed

#### Step 3.4: Integration Test
- [ ] Manually trigger a Bash error (`cat /nonexistent`)
- [ ] Verify captured with `type='tool_error'`
- [ ] Query: `SELECT * FROM concepts WHERE type = 'tool_error' ORDER BY id DESC LIMIT 5`

### Step 4: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` - add error_capture.py
- [ ] **MUST:** Update `.claude/hooks/README.md` - note error_capture moved to lib
- [ ] **MUST:** Archive old `.claude/hooks/error_capture.py`

---

## Verification

- [ ] `pytest tests/test_error_capture.py -v` passes (6 tests)
- [ ] `pytest tests/ -v` passes (no regressions)
- [ ] **MUST:** All READMEs current (lib, hooks)
- [ ] No more "hook error" messages on tool use
- [ ] Manual test: Bash error captured with type=tool_error

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Extending PostToolUse matcher may slow hooks | Low | Only adds detection logic, not heavy operations |
| Cleanup DELETE affects real data | Low | Only deleting obvious garbage (content contains "[Error Capture]") |
| Miss edge case in detection logic | Medium | TDD approach - add tests for discovered edge cases |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 95 | 2025-12-21 | - | Plan created | Ready for implementation |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/error_capture.py` | Contains is_actual_error(), store_error() | [ ] | |
| `.claude/hooks/hooks/post_tool_use.py` | Contains _capture_errors() | [ ] | |
| `.claude/settings.local.json` | No ErrorCapture.ps1 reference | [ ] | |
| `tests/test_error_capture.py` | 6 tests exist | [ ] | |
| `.claude/lib/README.md` | Lists error_capture.py | [ ] | |
| `.claude/hooks/README.md` | Notes error_capture moved | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_error_capture.py -v
# Expected: 6 tests passed

# Verify cleanup
sqlite3 haios_memory.db "SELECT COUNT(*) FROM concepts WHERE content LIKE '%[Error Capture]%'"
# Expected: 0 (all cleaned up)

# Verify new type queryable
sqlite3 haios_memory.db "SELECT COUNT(*) FROM concepts WHERE type = 'tool_error'"
# Expected: >0 after manual test
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- E2-007: Original Error Capture Hook implementation
- E2-FIX-003: False Positive Tuning (absorbed)
- E2-104: Dedicated tool_error Type (absorbed)
- INV-017: Observability Gap Analysis (identified issues)
- Session 95 checkpoint

---
