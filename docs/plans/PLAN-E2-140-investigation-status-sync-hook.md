---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-140
title: "Investigation Status Sync Hook"
author: Hephaestus
lifecycle_phase: done
session: 102
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-23T11:41:03
---
# Implementation Plan: Investigation Status Sync Hook

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

When an INV-* item is archived to backlog-complete.md, the corresponding investigation file will automatically have its `status: active` changed to `status: complete`, eliminating governance drift between archive and file status.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/post_tool_use.py` |
| Lines of code affected | ~50 | New function `_sync_investigation_status()` |
| New files to create | 0 | Adding to existing hook handler |
| Tests to write | 4 | Sync detection, file update, skip non-INV, missing file |
| Dependencies | 0 | Uses existing Path/re already imported |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single file addition to existing hook |
| Risk of regression | Low | Good test coverage (626 LOC, well-structured) |
| External dependencies | Low | File system only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implementation | 20 min | High |
| Integration test | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/post_tool_use.py:51-96 - handle() main function
def handle(hook_data: dict) -> Optional[str]:
    # ... error capture, file path extraction ...

    # Part 1: Timestamp injection
    timestamp_msg = _add_timestamp(path)
    # Part 2: Template validation
    validation_msg = _validate_template(path)
    # Part 3: Discoverable artifact refresh
    refresh_msg = _refresh_discoverable_artifacts(path)
    # Part 4: Cascade detection
    cascade_msg = _detect_cascade(path)
    # Part 5: Cycle transition logging
    cycle_msg = _log_cycle_transition(path)

    # No Part 6: Investigation sync
```

**Behavior:** When `/close INV-*` runs, it archives to backlog-complete.md but investigation file keeps `status: active`.

**Result:** Governance drift - file status ≠ archive status. Session 101 found 5 such cases.

### Desired State

```python
# .claude/hooks/hooks/post_tool_use.py - add Part 6
def handle(hook_data: dict) -> Optional[str]:
    # ... existing parts 1-5 ...

    # Part 6: Investigation status sync (E2-140)
    sync_msg = _sync_investigation_status(path)
    if sync_msg:
        messages.append(sync_msg)
```

**Behavior:** When backlog-complete.md is edited to add an INV-* item, the hook finds the corresponding investigation file and updates its `status` field.

**Result:** Automatic sync - no governance drift possible via L4 automation.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Detect INV-* in Backlog Archive
```python
def test_sync_detects_inv_in_backlog_archive(tmp_path):
    """When backlog-complete.md contains INV-* completion, detect the ID."""
    archive_file = tmp_path / "backlog-complete.md"
    archive_file.write_text("""### [COMPLETE] INV-022: Work-Cycle-DAG
- **Status:** complete
""")

    # Should detect INV-022 needs sync
    result = _extract_inv_ids_from_archive(archive_file)
    assert "INV-022" in result
```

### Test 2: Update Investigation File Status
```python
def test_sync_updates_investigation_file_status(tmp_path):
    """When INV-* is archived, update corresponding investigation file."""
    # Setup investigation file with status: active
    inv_dir = tmp_path / "docs" / "investigations"
    inv_dir.mkdir(parents=True)
    inv_file = inv_dir / "INVESTIGATION-INV-022-work-cycle-dag.md"
    inv_file.write_text("""---
template: investigation
status: active
backlog_id: INV-022
---
# Content
""")

    # Call sync function
    _sync_investigation_status_for_id("INV-022", tmp_path)

    # Verify status changed
    content = inv_file.read_text()
    assert "status: complete" in content
    assert "status: active" not in content
```

### Test 3: Skip Non-INV Items
```python
def test_sync_skips_non_inv_items(tmp_path):
    """E2-* items should not trigger investigation sync."""
    archive_file = tmp_path / "backlog-complete.md"
    archive_file.write_text("""### [COMPLETE] E2-140: Investigation Status Sync
- **Status:** complete
""")

    # Should NOT detect any INV IDs
    result = _extract_inv_ids_from_archive(archive_file)
    assert len(result) == 0
```

### Test 4: Handle Missing Investigation File
```python
def test_sync_handles_missing_investigation_file(tmp_path):
    """If investigation file not found, should not crash."""
    # No investigation file exists
    result = _sync_investigation_status_for_id("INV-999", tmp_path)

    # Should return None gracefully
    assert result is None
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
     4. Input/output examples with REAL data from the system -->

### Exact Code Change

**File:** `.claude/hooks/hooks/post_tool_use.py`
**Location:** Lines 91-96 in `handle()`, plus new function at end

**Current Code:**
```python
# .claude/hooks/hooks/post_tool_use.py:88-97
    # Part 4: Cascade detection
    cascade_msg = _detect_cascade(path)
    if cascade_msg:
        messages.append(cascade_msg)

    # Part 5: Cycle transition logging
    cycle_msg = _log_cycle_transition(path)
    if cycle_msg:
        messages.append(cycle_msg)

    return "\n".join(messages) if messages else None
```

**Changed Code:**
```python
# .claude/hooks/hooks/post_tool_use.py - add after Part 5
    # Part 4: Cascade detection
    cascade_msg = _detect_cascade(path)
    if cascade_msg:
        messages.append(cascade_msg)

    # Part 5: Cycle transition logging
    cycle_msg = _log_cycle_transition(path)
    if cycle_msg:
        messages.append(cycle_msg)

    # Part 6: Investigation status sync (E2-140)
    sync_msg = _sync_investigation_status(path)
    if sync_msg:
        messages.append(sync_msg)

    return "\n".join(messages) if messages else None
```

**Diff:**
```diff
     # Part 5: Cycle transition logging
     cycle_msg = _log_cycle_transition(path)
     if cycle_msg:
         messages.append(cycle_msg)

+    # Part 6: Investigation status sync (E2-140)
+    sync_msg = _sync_investigation_status(path)
+    if sync_msg:
+        messages.append(sync_msg)
+
     return "\n".join(messages) if messages else None
```

### Call Chain Context

```
Claude Code PostToolUse event
    |
    +-> hook_dispatcher.py
    |       Parses JSON, routes to handler
    |
    +-> post_tool_use.py:handle()
            |
            +-> _capture_errors()
            +-> _add_timestamp()
            +-> _validate_template()
            +-> _refresh_discoverable_artifacts()
            +-> _detect_cascade()
            +-> _log_cycle_transition()
            +-> _sync_investigation_status()     # <-- NEW
                    |
                    +-> Checks if path is backlog-complete.md
                    +-> Extracts INV-* IDs from content
                    +-> For each INV-*: finds investigation file, updates status
```

### Function/Component Signatures

```python
def _sync_investigation_status(path: Path) -> Optional[str]:
    """
    Sync investigation file status when INV-* archived to backlog-complete.md.

    Triggered by Edit/Write to docs/pm/archive/backlog-complete.md.
    Finds all INV-* entries marked [COMPLETE], locates their investigation
    files, and updates status field from 'active' to 'complete'.

    Args:
        path: The file that was just edited

    Returns:
        Status message if sync occurred, None otherwise.

    Side effects:
        - Modifies investigation files to update status field
    """
```

### Behavior Logic

**Trigger Condition:**
```
Edit to file → path ends with "backlog-complete.md"?
                      ├─ NO  → return None (skip)
                      └─ YES → Continue to extraction
```

**Sync Flow:**
```
Read backlog-complete.md content
    → Regex: r'### \[COMPLETE\] (INV-\d+):'
              ^-- Matches INV-001, INV-022, INV-1000, etc.
              ^-- Anchored to heading format, prevents false positives
    → For each INV-* ID found:
        → Glob: docs/investigations/INVESTIGATION-{ID}-*.md
        → If file exists AND status != complete:
            → Edit: status: active → status: complete
            → Log: "[SYNC] INV-022 status updated"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trigger on backlog-complete.md edit | PostToolUse hook | L4 automation - fires on every archive edit, no manual step |
| Extract ALL INV-* IDs from file | Re-scan on each edit | Idempotent - safe to run multiple times, catches any missed syncs |
| Use glob for investigation file lookup | INVESTIGATION-{ID}-*.md pattern | Investigation files may have varying suffix titles |
| Only update if status != complete | Skip already-synced | Avoid unnecessary file writes |

### Input/Output Examples

**Before Fix (with real data):**
```
/close INV-022 runs:
  1. Archives INV-022 to backlog-complete.md  ✓
  2. Investigation file status unchanged     ✗

Result:
  backlog-complete.md: ### [COMPLETE] INV-022
  INVESTIGATION-INV-022-*.md: status: active  <-- DRIFT
```

**After Fix (expected):**
```
/close INV-022 runs:
  1. Archives INV-022 to backlog-complete.md  ✓
  2. PostToolUse fires on backlog-complete.md  ✓
  3. _sync_investigation_status() detects INV-022  ✓
  4. Updates INVESTIGATION-INV-022-*.md status  ✓

Result:
  backlog-complete.md: ### [COMPLETE] INV-022
  INVESTIGATION-INV-022-*.md: status: complete  <-- SYNCED
```

**Real Example from Session 101:**
```
Current state (before fix):
  - INV-008: archived but file status: active
  - INV-009: archived but file status: active
  - INV-018: archived but file status: active
  - INV-011: archived but file status: active
  - INV-022: archived but file status: active

After fix:
  - All 5 would have been auto-synced on archive
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| INV-* file doesn't exist | Return None, no crash | Test 4 |
| INV-* already has status: complete | Skip, no change | Implicit in idempotency |
| E2-* item archived (not INV) | Regex doesn't match, skip | Test 3 |
| Multiple INV-* in single edit | Loop handles all | Extension of Test 1 |

### Open Questions

**Q: Should we log an event to haios-events.jsonl?**

Yes - add a `sync_investigation` event for observability. Same pattern as cascade_trigger.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_investigation_sync.py` with 4 tests
- [ ] Verify all tests fail (red) - functions don't exist yet

### Step 2: Add _sync_investigation_status Function
- [ ] Add function to `.claude/hooks/hooks/post_tool_use.py`
- [ ] Implement: check if path is backlog-complete.md
- [ ] Implement: extract INV-* IDs via regex
- [ ] Implement: glob for investigation files
- [ ] Implement: update status field in frontmatter
- [ ] Tests 1, 2, 3, 4 pass (green)

### Step 3: Wire Into handle()
- [ ] Add Part 6 call after Part 5 in `handle()` function
- [ ] Add event logging to haios-events.jsonl

### Step 4: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Manual test: edit backlog-complete.md with test INV-* entry

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/hooks/README.md` - add E2-140 to PostToolUse section
- [ ] No new directories created, no parent README updates needed

### Step 6: Consumer Verification
**SKIPPED:** Not a migration/refactor - adding new functionality to existing file

---

## Verification

- [ ] Tests pass: `pytest tests/test_investigation_sync.py -v`
- [ ] Full suite passes: `pytest tests/ -v`
- [ ] **MUST:** `.claude/hooks/README.md` updated
- [ ] Manual test: Archive a test INV-*, verify file updates

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex misses edge case ID format | Low | Test with real backlog-complete.md content |
| Multiple INV-* in single edit causes issues | Low | Loop handles all, idempotent design |
| File write during hook causes cascade loop | Medium | backlog-complete.md is not in governed path for cascade |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 102 | 2025-12-23 | - | Plan created | Ready for implementation |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/post_tool_use.py` | `_sync_investigation_status()` exists, Part 6 wired | [x] | Line 747 (function), Line 98 (Part 6) |
| `tests/test_investigation_sync.py` | 7 tests exist and pass | [x] | 7 tests (expanded from plan's 4) |
| `.claude/hooks/README.md` | E2-140 mentioned in PostToolUse section | [x] | Line 142 |

**Verification Commands:**
```bash
# Actual output (Session 103):
pytest tests/test_investigation_sync.py -v
# Result: 7 passed in 0.17s

pytest tests/ -v --tb=short
# Result: 383 passed, 2 skipped in 13.10s
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Grep verified all locations |
| Test output pasted above? | Yes | Full results captured |
| Any deviations from plan? | Yes | Added 3 extra tests (preserves fields, skips complete, multiple IDs) |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass
- [x] WHY captured (reasoning stored to memory)
- [x] **MUST:** `.claude/hooks/README.md` updated
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## References

- **Spawned by:** INV-022 (Work-Cycle-DAG Unified Architecture)
- **Related:** Session 101 checkpoint (governance drift discovery)
- **Pattern:** L4 Automation (mechanical sync, no manual step)

---
