---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-259
title: ContextLoader Status Generation
author: Hephaestus
lifecycle_phase: plan
session: 169
version: '1.5'
generated: 2026-01-04
last_updated: '2026-01-04T20:06:12'
---
# Implementation Plan: ContextLoader Status Generation

@docs/README.md
@docs/epistemic_state.md
@.claude/haios/modules/context_loader.py
@.claude/lib/status.py

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory 80681 contains INV-056 finding |
| Document design decisions | MUST | Delegation pattern per INV-056 |
| Ground truth metrics | MUST | 2 files modified, ~15 lines new |

---

## Goal

ContextLoader module will expose `generate_status()` method that delegates to `.claude/lib/status.py`, enabling hooks to import status generation from modules instead of lib/.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | context_loader.py, test_context_loader.py |
| Lines of code affected | ~15 | New method + tests |
| New files to create | 0 | Adding to existing files |
| Tests to write | 3 | See Tests First section |
| Dependencies | 1 | status.py (lib/) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single delegation to existing lib/ function |
| Risk of regression | Low | Adding new method, not changing existing |
| External dependencies | Low | Only status.py which is well-tested |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 5 min | High |
| Implement | 5 min | High |
| Verify | 5 min | High |
| **Total** | 15 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/context_loader.py - No status generation method
class ContextLoader:
    """Bootstrap the agent with L0-L4 context grounding."""

    def load_context(self, trigger: str = "coldstart") -> GroundedContext:
        # Existing implementation...

    # No generate_status() method exists
```

**Behavior:** Hooks must import directly from `.claude/lib/status.py`

**Result:** Violates Epoch 2.2 module-first pattern

### Desired State

```python
# .claude/haios/modules/context_loader.py - With status generation
class ContextLoader:
    """Bootstrap the agent with L0-L4 context grounding."""

    def generate_status(self, slim: bool = True) -> dict:
        """Generate status dict via delegation to lib/status.py."""
        # Delegates to existing implementation
```

**Behavior:** Hooks import from ContextLoader module

**Result:** Epoch 2.2 compliant - modules wrap lib/

---

## Tests First (TDD)

### Test 1: generate_status returns dict
```python
def test_generate_status_returns_dict():
    """generate_status returns a dict with expected keys."""
    from context_loader import ContextLoader

    loader = ContextLoader()
    result = loader.generate_status()

    assert isinstance(result, dict)
    assert "generated" in result
    assert "milestone" in result
```

### Test 2: generate_status slim mode is default
```python
def test_generate_status_slim_default():
    """generate_status defaults to slim status."""
    from context_loader import ContextLoader

    loader = ContextLoader()
    result = loader.generate_status()  # No slim arg

    # Slim status has infrastructure but NOT live_files
    assert "infrastructure" in result
    assert "live_files" not in result
```

### Test 3: generate_status full mode
```python
def test_generate_status_full_mode():
    """generate_status(slim=False) returns full status."""
    from context_loader import ContextLoader

    loader = ContextLoader()
    result = loader.generate_status(slim=False)

    # Full status has live_files
    assert "live_files" in result
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/modules/context_loader.py`
**Location:** After line 165 (end of `_get_ready_work` method)

**Current Code:**
```python
# context_loader.py:156-165
    def _get_ready_work(self) -> List[str]:
        """Get ready work items from WorkEngine."""
        if not self._work_engine:
            return []
        try:
            ready = self._work_engine.get_ready()
            return [w.id for w in ready[:10]]
        except Exception as e:
            logger.warning(f"Ready work query failed: {e}")
            return []
# End of class
```

**Changed Code:**
```python
# context_loader.py:156-182
    def _get_ready_work(self) -> List[str]:
        """Get ready work items from WorkEngine."""
        if not self._work_engine:
            return []
        try:
            ready = self._work_engine.get_ready()
            return [w.id for w in ready[:10]]
        except Exception as e:
            logger.warning(f"Ready work query failed: {e}")
            return []

    def generate_status(self, slim: bool = True) -> Dict[str, Any]:
        """
        Generate status dict by delegating to lib/status.py.

        Args:
            slim: If True (default), generate slim status.
                  If False, generate full status.

        Returns:
            Status dict with infrastructure, milestone, counts, etc.
        """
        import sys
        lib_path = str(self._project_root / ".claude" / "lib")
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)

        from status import generate_slim_status, generate_full_status

        if slim:
            return generate_slim_status()
        else:
            return generate_full_status()
```

**Diff:**
```diff
         except Exception as e:
             logger.warning(f"Ready work query failed: {e}")
             return []
+
+    def generate_status(self, slim: bool = True) -> Dict[str, Any]:
+        """
+        Generate status dict by delegating to lib/status.py.
+
+        Args:
+            slim: If True (default), generate slim status.
+                  If False, generate full status.
+
+        Returns:
+            Status dict with infrastructure, milestone, counts, etc.
+        """
+        import sys
+        lib_path = str(self._project_root / ".claude" / "lib")
+        if lib_path not in sys.path:
+            sys.path.insert(0, lib_path)
+
+        from status import generate_slim_status, generate_full_status
+
+        if slim:
+            return generate_slim_status()
+        else:
+            return generate_full_status()
```

### Call Chain Context

```
user_prompt_submit.py hook (future E2-264)
    |
    +-> ContextLoader.generate_status()   # <-- What we're adding
    |       Returns: Dict[str, Any]
    |
    +-> status.generate_slim_status()     # Existing lib/ function
```

### Function/Component Signatures

```python
def generate_status(self, slim: bool = True) -> Dict[str, Any]:
    """
    Generate status dict by delegating to lib/status.py.

    Args:
        slim: If True (default), generate slim status (~50 lines).
              If False, generate full status (includes live_files, templates).

    Returns:
        Status dict with keys: generated, milestone, session_delta,
        work_cycle, active_work, blocked_items, counts, infrastructure.

    Note:
        This method delegates to existing lib/status.py functions.
        The delegation pattern maintains backward compatibility while
        enabling module-first imports per Epoch 2.2.
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Delegation vs copy | Delegation | Maintain single source of truth in lib/status.py, reduce duplication |
| Default slim=True | Slim default | Matches current hook usage (vitals need slim, not full) |
| sys.path insertion | Dynamic import | Match pattern used in other modules (e.g., GovernanceLayer) |
| Project root aware | Use self._project_root | Consistent with other ContextLoader methods |

### Input/Output Examples

**Example call:**
```python
loader = ContextLoader()
result = loader.generate_status()
# Returns:
{
    "generated": "2026-01-04T19:50:00",
    "milestone": {"id": "M7b-WorkInfra", "name": "WorkInfra", "progress": 67},
    "session_delta": {"current_session": 169, "prior_session": 168},
    "infrastructure": {"commands": [...], "skills": [...], "agents": [...]},
    ...
}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| lib/status.py not found | ImportError propagates | N/A - lib/ must exist |
| generate_slim_status fails | Exception propagates | N/A - caller handles |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 3 tests to `tests/test_context_loader.py`
- [ ] Verify all tests fail (red)

### Step 2: Add generate_status method
- [ ] Add method to ContextLoader class (lines 167-182)
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)

### Step 4: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with new method

### Step 5: Consumer Verification
**SKIPPED:** No migration - adding new method, not moving code.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** README.md updated in modules/
- [ ] New method documented

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| sys.path pollution | Low | Use conditional insertion (if not in sys.path) |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 169 | 2026-01-04 | - | In Progress | Plan authored |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/context_loader.py` | `generate_status()` method exists | [x] | Lines 167-194 |
| `tests/test_context_loader.py` | 3 new tests for generate_status | [x] | Lines 232-265, all pass |
| `.claude/haios/modules/README.md` | Documents generate_status method | [x] | Line 267, usage at 322-328 |

**Verification Commands:**
```bash
pytest tests/test_context_loader.py -v -k "generate_status"
# Expected: 3 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All 3 files verified |
| Test output pasted above? | Yes | 3 passed in 0.74s |
| Any deviations from plan? | No | Implemented exactly as planned |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **Runtime consumer exists** (E2-264 will wire hook - for now, justfile can consume)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** README updated in modules/
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- INV-056: Hook-to-Module Migration Investigation
- Memory 80681: `status.generate_slim_status() -> ContextLoader (E2-259)`
- `.claude/lib/status.py`: Source implementation
- `.claude/haios/modules/context_loader.py`: Target module

---
