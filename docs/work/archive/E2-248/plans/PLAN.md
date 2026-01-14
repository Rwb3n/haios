---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-248
title: GovernanceLayer Error Visibility
author: Hephaestus
lifecycle_phase: complete
session: 168
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-04T18:57:35'
---
# Implementation Plan: GovernanceLayer Error Visibility

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

GovernanceLayer will log caught exceptions and return a `degraded` flag in GateResult when handlers fail, enabling agents to detect and recover from governance system failures.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `governance_layer.py`, `test_governance_layer.py` |
| Lines of code affected | ~15 | Lines 43-49, 187-188, 211-213 |
| New files to create | 0 | N/A |
| Tests to write | 3 | Exception logging, degraded flag, handler error visibility |
| Dependencies | 5 | cli.py, cycle_runner.py, work_engine.py (consumers) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Changes are internal to GovernanceLayer |
| Risk of regression | Low | 14 existing tests provide coverage |
| External dependencies | Low | Only Python logging, no external services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write failing tests | 15 min | High |
| Implement GateResult.degraded | 10 min | High |
| Add logging to exception handlers | 10 min | High |
| Update README | 5 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

```python
# governance_layer.py:43-49 - GateResult dataclass
@dataclass
class GateResult:
    """Result of a gate check."""
    allowed: bool
    reason: str
```

```python
# governance_layer.py:182-188 - load_handlers exception handling
        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            self._handlers = self._parse_handlers(config)
            return config
        except Exception:
            return {}  # Silent failure - no visibility
```

```python
# governance_layer.py:207-213 - on_event exception handling
        for handler in handlers:
            try:
                handler(payload)
            except Exception:
                # Log but don't fail on handler errors
                pass  # Silent failure - no visibility
```

**Behavior:** Exceptions are caught and swallowed silently. No logging, no return value indicating failure.

**Result:** Agents cannot detect when governance is degraded, violating L3 Agent UX requirement: "Can an agent recover from failure?"

### Desired State

```python
# governance_layer.py:43-50 - GateResult with degraded flag
@dataclass
class GateResult:
    """Result of a gate check."""
    allowed: bool
    reason: str
    degraded: bool = False  # NEW: Indicates system degradation
```

```python
# governance_layer.py - load_handlers with logging
        except Exception as e:
            import logging
            logging.warning(f"GovernanceLayer: Failed to load handlers from {config_path}: {e}")
            return {}  # Degraded but operational
```

```python
# governance_layer.py - on_event with logging
            except Exception as e:
                import logging
                logging.warning(f"GovernanceLayer: Handler failed for {event_type}: {e}")
                # Continue with other handlers
```

**Behavior:** Exceptions are logged with context (path, event type, error message). GateResult can indicate degraded state.

**Result:** Agents can detect governance degradation via logs and the `degraded` flag, enabling recovery strategies.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: GateResult Has Degraded Flag
```python
def test_gate_result_has_degraded_field():
    """GateResult should have optional degraded field."""
    from governance_layer import GateResult

    # Default should be False
    result = GateResult(allowed=True, reason="test")
    assert hasattr(result, "degraded")
    assert result.degraded is False

    # Explicit degraded state
    degraded_result = GateResult(allowed=True, reason="partial", degraded=True)
    assert degraded_result.degraded is True
```

### Test 2: Load Handlers Logs Errors
```python
def test_load_handlers_logs_yaml_error(tmp_path, caplog):
    """load_handlers should log errors when YAML parsing fails."""
    from governance_layer import GovernanceLayer
    import logging

    # Create invalid YAML
    bad_config = tmp_path / "bad.yaml"
    bad_config.write_text("invalid: yaml: content: [")

    layer = GovernanceLayer()
    with caplog.at_level(logging.WARNING):
        result = layer.load_handlers(str(bad_config))

    assert result == {}  # Graceful degradation
    assert "Failed to load handlers" in caplog.text
    assert str(bad_config) in caplog.text
```

### Test 3: On Event Logs Handler Errors
```python
def test_on_event_logs_handler_exception(mocker, caplog):
    """on_event should log when handler raises exception."""
    from governance_layer import GovernanceLayer
    import logging

    def failing_handler(payload):
        raise ValueError("Handler exploded")

    layer = GovernanceLayer()
    layer._handlers = {"test_event": [failing_handler]}

    with caplog.at_level(logging.WARNING):
        layer.on_event("test_event", {"data": "test"})

    assert "Handler failed" in caplog.text
    assert "test_event" in caplog.text
```

### Test 4: Backward Compatibility
```python
def test_existing_gate_result_behavior_unchanged():
    """Existing code using GateResult(allowed, reason) should still work."""
    from governance_layer import GateResult

    # Old-style construction still works
    result = GateResult(allowed=True, reason="test")
    assert result.allowed is True
    assert result.reason == "test"
    assert result.degraded is False  # Default value
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Exact Code Change

<!-- REQUIRED: Show the actual code, not pseudocode -->

#### Change 1: GateResult Dataclass

**File:** `.claude/haios/modules/governance_layer.py`
**Location:** Lines 43-49 in `GateResult` dataclass

**Current Code:**
```python
# governance_layer.py:43-49
@dataclass
class GateResult:
    """Result of a gate check."""

    allowed: bool
    reason: str
```

**Changed Code:**
```python
# governance_layer.py:43-50
@dataclass
class GateResult:
    """Result of a gate check."""

    allowed: bool
    reason: str
    degraded: bool = False  # Indicates governance system degradation
```

**Diff:**
```diff
 @dataclass
 class GateResult:
     """Result of a gate check."""

     allowed: bool
     reason: str
+    degraded: bool = False  # Indicates governance system degradation
```

#### Change 2: load_handlers Exception Logging

**File:** `.claude/haios/modules/governance_layer.py`
**Location:** Lines 182-188 in `load_handlers()`

**Current Code:**
```python
# governance_layer.py:182-188
        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            self._handlers = self._parse_handlers(config)
            return config
        except Exception:
            return {}
```

**Changed Code:**
```python
# governance_layer.py:182-191
        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            self._handlers = self._parse_handlers(config)
            return config
        except Exception as e:
            import logging
            logging.warning(f"GovernanceLayer: Failed to load handlers from {config_path}: {e}")
            return {}
```

**Diff:**
```diff
         except Exception:
-            return {}
+        except Exception as e:
+            import logging
+            logging.warning(f"GovernanceLayer: Failed to load handlers from {config_path}: {e}")
+            return {}
```

#### Change 3: on_event Exception Logging

**File:** `.claude/haios/modules/governance_layer.py`
**Location:** Lines 207-213 in `on_event()`

**Current Code:**
```python
# governance_layer.py:207-213
        for handler in handlers:
            try:
                handler(payload)
            except Exception:
                # Log but don't fail on handler errors
                pass
```

**Changed Code:**
```python
# governance_layer.py:207-216
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                import logging
                logging.warning(f"GovernanceLayer: Handler failed for {event_type}: {e}")
                # Continue with other handlers
```

**Diff:**
```diff
         for handler in handlers:
             try:
                 handler(payload)
-            except Exception:
-                # Log but don't fail on handler errors
-                pass
+            except Exception as e:
+                import logging
+                logging.warning(f"GovernanceLayer: Handler failed for {event_type}: {e}")
+                # Continue with other handlers
```

### Call Chain Context

```
WorkEngine/CycleRunner/CLI
    |
    +-> GovernanceLayer.check_gate()     # Returns GateResult
    |       Returns: GateResult(allowed, reason, degraded)
    |
    +-> GovernanceLayer.load_handlers()  # Config loading
    |       Returns: dict (empty on error, now with logging)
    |
    +-> GovernanceLayer.on_event()       # Event routing
            Side effect: calls handlers (now with logging on failure)
```

### Function/Component Signatures

```python
@dataclass
class GateResult:
    """Result of a gate check.

    Attributes:
        allowed: Whether the gate permits the operation
        reason: Human-readable explanation
        degraded: Whether governance is in degraded state (handler failures)
    """
    allowed: bool
    reason: str
    degraded: bool = False
```

### Behavior Logic

**Current Flow:**
```
Exception raised → except Exception: pass → No visibility
```

**Fixed Flow:**
```
Exception raised → except Exception as e:
                      ├─ Log warning with context (event type, error)
                      └─ Continue execution (graceful degradation)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Logging level | `WARNING` | Not ERROR (system continues), but visible enough to surface |
| Import location | Inline `import logging` | Matches existing pattern in file, avoids global import |
| GateResult.degraded default | `False` | Backward compatible - existing code unaffected |
| Continue after handler failure | Yes | Original behavior preserved (don't fail cascade) |
| Log format | Include event type + error | Context needed for debugging without stack trace |

### Input/Output Examples

**Before Fix (current behavior):**
```python
layer.load_handlers("/invalid/path.yaml")
  Returns: {}
  Logs: Nothing
  Problem: Agent cannot detect config load failure
```

**After Fix (expected):**
```python
layer.load_handlers("/invalid/path.yaml")
  Returns: {}
  Logs: "WARNING:root:GovernanceLayer: Failed to load handlers from /invalid/path.yaml: [Errno 2] No such file"
  Improvement: Agent sees warning in logs, can react
```

**Handler failure scenario:**
```python
# Before: silent failure
layer.on_event("work_transition", {"work_id": "E2-248"})
  # Handler raises ValueError
  # Logs: Nothing

# After: logged failure
layer.on_event("work_transition", {"work_id": "E2-248"})
  # Handler raises ValueError
  # Logs: "WARNING:root:GovernanceLayer: Handler failed for work_transition: ValueError message"
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Multiple handlers, one fails | Log error, continue to next handler | Implicit (not changing iteration behavior) |
| Empty handler list | No logging (no error to log) | Existing test coverage |
| Config file exists but invalid YAML | Log parsing error, return {} | Test 2 |

### Open Questions

**Q: Should we add a `logging.getLogger(__name__)` at module level instead of inline imports?**

Answer: The existing pattern in the file uses inline imports for optional dependencies. Consistency with existing code is preferred over theoretical cleanliness. If a future refactor adds module-level logger, all exception handlers can be updated then.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 4 new tests to `tests/test_governance_layer.py`
- [ ] Verify tests fail (red): `pytest tests/test_governance_layer.py -v -k "degraded or logs"`

### Step 2: Add GateResult.degraded Field
- [ ] Add `degraded: bool = False` to GateResult dataclass (line 49)
- [ ] Test 1 (degraded field) and Test 4 (backward compat) pass (green)

### Step 3: Add Logging to load_handlers
- [ ] Change `except Exception:` to `except Exception as e:` (line 187)
- [ ] Add `import logging; logging.warning(...)` with context
- [ ] Test 2 (load_handlers logs) passes (green)

### Step 4: Add Logging to on_event
- [ ] Change `except Exception:` to `except Exception as e:` (line 211)
- [ ] Add `import logging; logging.warning(...)` with event type
- [ ] Test 3 (on_event logs) passes (green)

### Step 5: Integration Verification
- [ ] All tests pass: `pytest tests/test_governance_layer.py -v`
- [ ] Run full test suite (no regressions): `pytest`

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` - document GateResult.degraded field
- [ ] **MUST:** Verify docstrings reflect new behavior

### Step 7: Consumer Verification
- [ ] Verify consumers of GateResult still work (cli.py, work_engine.py, cycle_runner.py)
- [ ] No changes needed - `degraded` has default value, backward compatible

**Consumer Locations (from grep):**
- `.claude/haios/modules/cli.py`
- `.claude/haios/modules/work_engine.py`
- `.claude/haios/modules/cycle_runner.py`
- `tests/test_governance_layer.py`
- `tests/test_cycle_runner.py`
- `tests/test_modules_cli.py`

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backward compatibility break | High | Use default value `degraded=False` - existing code unaffected |
| Logging noise | Low | Use WARNING level, include context for filtering |
| Import side effects | Low | Inline `import logging` matches existing pattern |
| Test flakiness with caplog | Low | Use standard pytest caplog fixture, well-tested |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/governance_layer.py` | GateResult has `degraded` field, exception handlers log | [ ] | |
| `tests/test_governance_layer.py` | 4 new tests for error visibility | [ ] | |
| `.claude/haios/modules/README.md` | Documents GateResult.degraded field | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_governance_layer.py -v
# Expected: 18 tests passed (14 existing + 4 new)
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-055: Agent Usability Requirements Detailing (spawn source)
- L3-requirements.md: Agent UX Test requirements (lines 76-113)
- Memory 80582: "Exception handling uses bare `except Exception: pass` pattern"
- Memory 80531: "Silent handler failures (try/except) to prevent cascading errors" (original rationale)

---
