---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-261
title: MemoryBridge Error Capture
author: Hephaestus
lifecycle_phase: plan
session: 169
version: '1.5'
generated: 2026-01-04
last_updated: '2026-01-04T20:20:27'
---
# Implementation Plan: MemoryBridge Error Capture

@docs/README.md
@.claude/haios/modules/memory_bridge.py
@.claude/lib/error_capture.py

---

## Goal

MemoryBridge module will expose `is_actual_error()` and `capture_error()` methods that delegate to `.claude/lib/error_capture.py`, enabling hooks to import error capture from modules instead of lib/.

---

## Effort Estimation (Ground Truth)

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | memory_bridge.py, test_memory_bridge.py |
| Lines of code affected | ~25 | Two new methods + tests |
| Tests to write | 2 | is_actual_error, capture_error |

---

## Tests First (TDD)

### Test 1: is_actual_error detects bash failure
```python
def test_is_actual_error_bash_failure(self):
    """is_actual_error returns True for bash exit code != 0."""
    from memory_bridge import MemoryBridge
    bridge = MemoryBridge()
    result = bridge.is_actual_error("Bash", {"exit_code": 1})
    assert result is True
```

### Test 2: capture_error stores error
```python
def test_capture_error_stores(self, mocker):
    """capture_error delegates to error_capture.store_error."""
    from memory_bridge import MemoryBridge
    # Mock the underlying function to avoid DB
    mock_store = mocker.patch("error_capture.store_error", return_value={"success": True, "concept_id": 123})
    bridge = MemoryBridge()
    result = bridge.capture_error("Bash", "Command failed")
    assert result["success"] is True
```

---

## Detailed Design

**File:** `.claude/haios/modules/memory_bridge.py`
**Location:** After line 341 (end of _rewrite_query method)

**New Code:**
```python
# =========================================================================
# E2-261: Error Capture
# =========================================================================

def is_actual_error(self, tool_name: str, tool_response: dict) -> bool:
    """
    Determine if tool response represents an actual failure.

    Delegates to lib/error_capture.is_actual_error().

    Args:
        tool_name: Name of the tool (Bash, Read, Edit, Write, Grep, Glob)
        tool_response: The tool's response dict from Claude Code

    Returns:
        True only for actual failures, False for successes or false positives.
    """
    import sys
    lib_path = str(Path(__file__).parent.parent.parent / "lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

    from error_capture import is_actual_error as _is_actual_error
    return _is_actual_error(tool_name, tool_response)

def capture_error(self, tool_name: str, error_message: str, tool_input: str = "") -> dict:
    """
    Store error to memory with dedicated type for queryability.

    Delegates to lib/error_capture.store_error().

    Args:
        tool_name: Tool that failed
        error_message: The error message
        tool_input: Summary of what was attempted (optional)

    Returns:
        {"success": True, "concept_id": N} or {"success": False, "error": "..."}
    """
    import sys
    lib_path = str(Path(__file__).parent.parent.parent / "lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

    from error_capture import store_error
    return store_error(tool_name, error_message, tool_input)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Two methods | is_actual_error + capture_error | Match lib/ API surface |
| Delegation | Wrap existing functions | Single source of truth |
| Lazy import | Inside methods | Match existing module patterns |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 2 tests to `tests/test_memory_bridge.py`
- [ ] Verify tests fail (red)

### Step 2: Add methods to MemoryBridge
- [ ] Add is_actual_error and capture_error methods
- [ ] Tests pass (green)

### Step 3: Update README
- [ ] Update `.claude/haios/modules/README.md` with new methods

---

## Ground Truth Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/memory_bridge.py` | `is_actual_error()` and `capture_error()` exist | [ ] | |
| `tests/test_memory_bridge.py` | 2 new tests | [ ] | |
| `.claude/haios/modules/README.md` | Documents new methods | [ ] | |

---

## References

- INV-056: Hook-to-Module Migration Investigation
- Memory 80683: `error_capture.is_actual_error() -> MemoryBridge (E2-261)`
- `.claude/lib/error_capture.py`: Source implementation

---
