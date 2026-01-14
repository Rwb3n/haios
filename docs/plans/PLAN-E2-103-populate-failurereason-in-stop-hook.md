---
template: implementation_plan
status: complete
date: 2025-12-20
backlog_id: E2-103
title: "Populate failure_reason in Stop Hook"
author: Hephaestus
lifecycle_phase: done
session: 89
spawned_by: INV-017
related: [E2-094, E2-095]
milestone: M3-Cycles
version: "1.3"
---
# generated: 2025-12-20
# System Auto: last updated on: 2025-12-20 20:57:58
# Implementation Plan: Populate failure_reason in Stop Hook

@docs/README.md
@docs/epistemic_state.md

---

## Goal

When a session ends with outcome="failure", the `failure_reason` column in reasoning_traces is populated with diagnostic context from the error_details.

---

## Current State vs Desired State

### Current State

```python
# haios_etl/retrieval.py:317-336
cursor.execute("""
    INSERT INTO reasoning_traces
    (query, query_embedding, approach_taken, strategy_details, outcome,
     memories_used, execution_time_ms, space_id,
     strategy_title, strategy_description, strategy_content, extraction_model)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    query, vector_bytes, approach, json.dumps(strategy_details), outcome,
    json.dumps(memories_used), execution_time_ms, space_id,
    strategy.get('title'), strategy.get('description'),
    strategy.get('content'), self.extractor.model_id
))
```

**Behavior:** INSERT has 12 columns, does NOT include `failure_reason`.

**Result:** 7 failure traces have `failure_reason = NULL` despite `error_details` being available.

### Desired State

```python
# haios_etl/retrieval.py:317-340
cursor.execute("""
    INSERT INTO reasoning_traces
    (query, query_embedding, approach_taken, strategy_details, outcome,
     memories_used, execution_time_ms, space_id,
     strategy_title, strategy_description, strategy_content, extraction_model,
     failure_reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    query, vector_bytes, approach, json.dumps(strategy_details), outcome,
    json.dumps(memories_used), execution_time_ms, space_id,
    strategy.get('title'), strategy.get('description'),
    strategy.get('content'), self.extractor.model_id,
    error_details if outcome in ('failure', 'partial_success') else None
))
```

**Behavior:** INSERT has 13 columns, includes `failure_reason` when outcome indicates failure.

**Result:** Failure traces have diagnostic context stored for analysis.

---

## Tests First (TDD)

### Test 1: failure_reason Populated on Failure
```python
def test_failure_reason_populated_on_failure():
    """When outcome is failure, failure_reason should contain error_details."""
    # Setup
    retrieval = ReasoningAwareRetrieval(db, extractor)
    error_msg = "Tool XYZ failed with exit code 1"

    # Action
    retrieval.record_reasoning_trace(
        query="test query",
        query_embedding=[0.1] * 768,
        approach="test approach",
        strategy_details={},
        outcome="failure",
        memories_used=[],
        execution_time_ms=100,
        space_id=None,
        error_details=error_msg
    )

    # Assert
    trace = db.get_connection().execute(
        "SELECT failure_reason FROM reasoning_traces ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert trace[0] == error_msg
```

### Test 2: failure_reason NULL on Success
```python
def test_failure_reason_null_on_success():
    """When outcome is success, failure_reason should be NULL."""
    retrieval.record_reasoning_trace(
        outcome="success",
        error_details=""  # Empty on success
    )
    trace = db.get_connection().execute(
        "SELECT failure_reason FROM reasoning_traces ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert trace[0] is None
```

### Test 3: Partial Success Gets failure_reason
```python
def test_partial_success_gets_failure_reason():
    """When outcome is partial_success, failure_reason should contain errors."""
    retrieval.record_reasoning_trace(
        outcome="partial_success",
        error_details="Some tools failed"
    )
    trace = db.get_connection().execute(
        "SELECT failure_reason FROM reasoning_traces ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert trace[0] == "Some tools failed"
```

---

## Detailed Design

### Exact Code Change

**File:** `haios_etl/retrieval.py`
**Location:** Lines 317-336 in `record_reasoning_trace()`

**Current Code:**
```python
# haios_etl/retrieval.py:317-336
        cursor.execute("""
            INSERT INTO reasoning_traces
            (query, query_embedding, approach_taken, strategy_details, outcome,
             memories_used, execution_time_ms, space_id,
             strategy_title, strategy_description, strategy_content, extraction_model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query,
            vector_bytes,
            approach,
            json.dumps(strategy_details),
            outcome,
            json.dumps(memories_used),
            execution_time_ms,
            space_id,
            strategy.get('title'),
            strategy.get('description'),
            strategy.get('content'),
            self.extractor.model_id
        ))
```

**Changed Code:**
```python
# haios_etl/retrieval.py:317-340
        # Compute failure_reason: populate for failure/partial_success outcomes
        failure_reason = None
        if outcome in ('failure', 'partial_success') and error_details:
            failure_reason = error_details

        cursor.execute("""
            INSERT INTO reasoning_traces
            (query, query_embedding, approach_taken, strategy_details, outcome,
             memories_used, execution_time_ms, space_id,
             strategy_title, strategy_description, strategy_content, extraction_model,
             failure_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query,
            vector_bytes,
            approach,
            json.dumps(strategy_details),
            outcome,
            json.dumps(memories_used),
            execution_time_ms,
            space_id,
            strategy.get('title'),
            strategy.get('description'),
            strategy.get('content'),
            self.extractor.model_id,
            failure_reason
        ))
```

**Diff:**
```diff
+        # Compute failure_reason: populate for failure/partial_success outcomes
+        failure_reason = None
+        if outcome in ('failure', 'partial_success') and error_details:
+            failure_reason = error_details
+
         cursor.execute("""
             INSERT INTO reasoning_traces
             (query, query_embedding, approach_taken, strategy_details, outcome,
              memories_used, execution_time_ms, space_id,
-             strategy_title, strategy_description, strategy_content, extraction_model)
-            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
+             strategy_title, strategy_description, strategy_content, extraction_model,
+             failure_reason)
+            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
         """, (
             ...existing params...,
-            self.extractor.model_id
+            self.extractor.model_id,
+            failure_reason
         ))
```

### Call Chain Context

```
reasoning_extraction.py:extract_and_store()
    |
    +-> retrieval.record_reasoning_trace()  # <-- What we're changing
    |       Receives: error_details from session_info
    |       Currently: Passes to extract_strategy, discards
    |       Fixed: Also stores in failure_reason column
    |
    +-> INSERT INTO reasoning_traces
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| When to populate | failure + partial_success | Both indicate problems worth recording |
| Source of data | error_details parameter | Already collected by reasoning_extraction.py |
| NULL for success | Yes | Avoid storing empty strings, cleaner queries |

### Input/Output Examples

**Real Data (from database query):**
```
Current: 7 failure traces, all with failure_reason = NULL
  - id=387, outcome='failure', failure_reason=NULL
  - id=386, outcome='failure', failure_reason=NULL
  ...
```

**After Fix:**
```
New failure traces will have:
  - id=388, outcome='failure', failure_reason='Tool Edit failed: file not found'
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty error_details | failure_reason = None | Test 2 |
| outcome = 'success' | failure_reason = None | Test 2 |
| outcome = 'partial_success' | failure_reason = error_details | Test 3 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add tests to tests/test_retrieval.py or new test_reasoning_traces.py
- [ ] Verify tests fail (red)

### Step 2: Modify record_reasoning_trace
- [ ] Add failure_reason computation (4 lines)
- [ ] Add column to INSERT statement
- [ ] Add placeholder to VALUES
- [ ] Add parameter to tuple
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Integration Verification
- [ ] Run full test suite (no regressions)
- [ ] Trigger manual test with intentional failure

---

## Verification

- [ ] Tests pass
- [ ] No regressions in existing retrieval tests
- [ ] Manual test shows failure_reason populated

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing traces unaffected | Low | Expected - only new traces get failure_reason |
| error_details too long | Low | Schema allows TEXT, no limit |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 89 | 2025-12-20 | - | Plan created | Detailed design complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `haios_etl/retrieval.py` | INSERT includes failure_reason | [ ] | |
| `tests/test_*.py` | 3 tests for failure_reason | [ ] | |

**Verification Commands:**
```bash
pytest tests/ -k "failure_reason" -v
# Expected: 3 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] Ground Truth Verification completed above

---

## References

- INV-017: ReasoningBank Quality Analysis (spawned this)
- Session 89: Implementation cycle demo

---
