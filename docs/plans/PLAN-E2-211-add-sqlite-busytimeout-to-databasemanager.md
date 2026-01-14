---
template: implementation_plan
status: complete
date: 2025-12-27
backlog_id: E2-211
title: Add SQLite busy_timeout to DatabaseManager
author: Hephaestus
lifecycle_phase: plan
session: 128
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-27T16:45:14'
---
# Implementation Plan: Add SQLite busy_timeout to DatabaseManager

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

## Goal

SQLite concurrent write attempts will wait up to 30 seconds for locks instead of failing immediately, preventing crashes when ingester runs while synthesis is active.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/database.py` |
| Lines of code affected | ~1 | Single PRAGMA statement |
| New files to create | 0 | - |
| Tests to write | 1 | Verify busy_timeout is set |
| Dependencies | 0 | No new imports needed |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single file, single function |
| Risk of regression | Low | Additive change, existing tests pass |
| External dependencies | Low | SQLite built-in PRAGMA |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write test | 5 min | High |
| Implement | 2 min | High |
| Verify | 3 min | High |
| **Total** | 10 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/database.py:17-23
def get_connection(self):
    if self.conn is None:
        self.conn = sqlite3.connect(self.db_path)
        # Enable WAL mode for better concurrency
        self.conn.execute("PRAGMA journal_mode=WAL")
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
```

**Behavior:** Connection uses WAL mode but no busy_timeout

**Result:** Concurrent writes fail immediately with SQLITE_BUSY (0ms timeout default)

### Desired State

```python
# .claude/lib/database.py:17-25
def get_connection(self):
    if self.conn is None:
        self.conn = sqlite3.connect(self.db_path)
        # Enable WAL mode for better concurrency
        self.conn.execute("PRAGMA journal_mode=WAL")
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Wait up to 30s for locks (prevents immediate SQLITE_BUSY)
        self.conn.execute("PRAGMA busy_timeout=30000")
```

**Behavior:** Connection waits up to 30 seconds for locks before failing

**Result:** Concurrent writes succeed if lock released within 30s

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: busy_timeout is set
```python
def test_database_busy_timeout_is_set():
    """Verify busy_timeout PRAGMA is configured on connection."""
    db = DatabaseManager(":memory:")
    conn = db.get_connection()
    cursor = conn.execute("PRAGMA busy_timeout")
    timeout = cursor.fetchone()[0]
    assert timeout == 30000, f"Expected 30000ms, got {timeout}ms"
```

### Test 2: Backward Compatibility
```python
def test_database_connection_still_works():
    """Verify existing database operations work after adding busy_timeout."""
    db = DatabaseManager(":memory:")
    db.setup()  # Initialize schema
    # Existing insert should still work
    artifact_id = db.insert_artifact("test.py", "hash123", 100)
    assert artifact_id is not None
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does. -->

### Exact Code Change

**File:** `.claude/lib/database.py`
**Location:** Line 23, after foreign_keys PRAGMA in `get_connection()`

**Diff:**
```diff
             self.conn.execute("PRAGMA foreign_keys = ON")
+            # Wait up to 30s for locks (prevents immediate SQLITE_BUSY)
+            self.conn.execute("PRAGMA busy_timeout=30000")
```

### Call Chain Context

```
MCP ingester_ingest tool
    |
    +-> Ingester.ingest()
    |       |
    |       +-> DatabaseManager.get_connection()  # <-- Adding busy_timeout here
    |               Returns: sqlite3.Connection
    |
    +-> db_manager.insert_concept() etc
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Timeout value | 30000ms (30s) | Synthesis operations typically < 10s, provides 3x buffer |
| Implementation | PRAGMA | SQLite built-in, no external deps, well-documented |
| Location | get_connection() | Applied once per connection, before any operations |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Timeout exceeds 30s | SQLITE_BUSY returned | Handled by existing exception handlers |
| In-memory DB | Works same as file DB | Test 1 uses :memory: |

### Open Questions

**Q: Should timeout be configurable?**

No for MVP. 30s is reasonable default. Can add config option later if needed.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add `test_database_busy_timeout_is_set()` to `tests/test_database.py`
- [ ] Verify test fails (busy_timeout returns 0)

### Step 2: Add busy_timeout PRAGMA
- [ ] Edit `.claude/lib/database.py:23` - add PRAGMA busy_timeout=30000
- [ ] Test 1 passes (green)

### Step 3: Verify Backward Compatibility
- [ ] Run existing database tests
- [ ] All tests pass (no regressions)

### Step 4: Integration Verification
- [ ] Run full test suite: `pytest tests/`
- [ ] All tests pass

### Step 5: README Sync (MUST)
- [ ] **SKIPPED:** No README changes needed - additive internal change

### Step 6: Consumer Verification (MUST for migrations/refactors)
- [ ] **SKIPPED:** Not a migration/refactor - additive change only

---

## Verification

- [ ] Tests pass
- [ ] **SKIPPED:** READMEs - additive internal change
- [ ] Code review complete (self-review for trivial change)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 30s timeout too short | Low | Can increase if needed; most ops < 10s |
| 30s timeout too long | Low | Better than crash; can tune later |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 128 | 2025-12-27 | - | Planned | Plan populated |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/database.py` | busy_timeout PRAGMA after foreign_keys | [x] | Line 24-25 |
| `tests/test_database.py` | test_database_busy_timeout_is_set exists | [x] | Line 421-437 |

**Verification Commands:**
```bash
pytest tests/test_database.py -v
# Result: 18 passed in 0.23s (including busy_timeout test)
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Read both files |
| Test output pasted above? | Yes | 18 passed in 0.23s |
| Any deviations from plan? | No | Implemented as designed |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (18 passed in 0.23s)
- [x] WHY captured (INV-027 findings in memory 79743-79749)
- [x] **SKIPPED:** READMEs - additive internal change
- [x] **SKIPPED:** Consumer verification - not a migration
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## References

- INV-027: Root cause investigation
- Memory concepts: 79743-79749 (investigation findings)

---
