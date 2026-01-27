---
template: implementation_plan
status: complete
date: 2026-01-26
backlog_id: WORK-023
title: Fix scan_incomplete_work status filtering
author: Hephaestus
lifecycle_phase: plan
session: 247
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-26T23:51:20'
---
# Implementation Plan: Fix scan_incomplete_work status filtering

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

`scan_incomplete_work()` will correctly filter out work items with terminal status (complete, archived, dismissed, invalid, deferred), eliminating false positives in coldstart output.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/haios/lib/governance_events.py` |
| Lines of code affected | ~10 | Lines 227-239 in `scan_incomplete_work()` |
| New files to create | 0 | Test added to existing file |
| Tests to write | 3 | Status filtering tests |
| Dependencies | 1 | `coldstart_orchestrator.py` calls this function |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single function, one caller |
| Risk of regression | Low | Adding filter, not changing existing logic |
| External dependencies | Low | No APIs, just file reads |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement fix | 10 min | High |
| Verify coldstart | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/lib/governance_events.py:227-239
yaml_content = match.group(1)
# Check for exited: null in node_history
if "exited: null" in yaml_content or "exited: ~" in yaml_content:
    # Extract id
    id_match = re.search(r"id:\s*(\S+)", yaml_content)
    # Extract current node
    node_match = re.search(r"node:\s*(\S+)", yaml_content)
    if id_match:
        incomplete.append({
            "id": id_match.group(1).strip(),
            "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
            "path": str(work_file.relative_to(project_root)),
        })
```

**Behavior:** Reports ANY work item with `exited: null` as incomplete, regardless of status.

**Result:** Coldstart shows 80+ false positives including completed work (E2-236, E2-295).

### Desired State

```python
# .claude/haios/lib/governance_events.py:227-245
yaml_content = match.group(1)

# Extract status field
status_match = re.search(r"status:\s*(\S+)", yaml_content)
status = status_match.group(1).strip() if status_match else ""

# Skip terminal statuses (same set as WorkEngine.get_ready)
terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}
if status in terminal_statuses:
    continue

# Check for exited: null in node_history
if "exited: null" in yaml_content or "exited: ~" in yaml_content:
    # ... existing extraction logic
```

**Behavior:** Skip work items with terminal status before checking `exited: null`.

**Result:** Coldstart shows only genuinely incomplete work items.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Complete Status Excluded
```python
def test_scan_incomplete_work_excludes_complete_status(tmp_path):
    """Work items with status: complete should not appear in results."""
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("""---
id: E2-TEST
status: complete
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-01
  exited: null
---
""")
    result = scan_incomplete_work(tmp_path)
    assert len(result) == 0, "Complete items should be excluded"
```

### Test 2: Archived Status Excluded
```python
def test_scan_incomplete_work_excludes_archived_status(tmp_path):
    """Work items with status: archived should not appear in results."""
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("""---
id: E2-TEST
status: archived
current_node: complete
node_history:
- node: complete
  entered: 2026-01-01
  exited: null
---
""")
    result = scan_incomplete_work(tmp_path)
    assert len(result) == 0, "Archived items should be excluded"
```

### Test 3: Active Status Included
```python
def test_scan_incomplete_work_includes_active_status(tmp_path):
    """Work items with status: active and exited: null should appear."""
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-TEST"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("""---
id: E2-TEST
status: active
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-01
  exited: null
---
""")
    result = scan_incomplete_work(tmp_path)
    assert len(result) == 1, "Active items should be included"
    assert result[0]["id"] == "E2-TEST"
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

**File:** `.claude/haios/lib/governance_events.py`
**Location:** Lines 227-239 in `scan_incomplete_work()`

**Current Code:**
```python
# governance_events.py:227-239
            yaml_content = match.group(1)
            # Check for exited: null in node_history
            if "exited: null" in yaml_content or "exited: ~" in yaml_content:
                # Extract id
                id_match = re.search(r"id:\s*(\S+)", yaml_content)
                # Extract current node
                node_match = re.search(r"node:\s*(\S+)", yaml_content)
                if id_match:
                    incomplete.append({
                        "id": id_match.group(1).strip(),
                        "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
                        "path": str(work_file.relative_to(project_root)),
                    })
```

**Changed Code:**
```python
# governance_events.py:227-247
            yaml_content = match.group(1)

            # Extract status field and skip terminal statuses
            # Uses same terminal set as WorkEngine.get_ready() (Session 211)
            status_match = re.search(r"status:\s*(\S+)", yaml_content)
            status = status_match.group(1).strip() if status_match else ""
            terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}
            if status in terminal_statuses:
                continue

            # Check for exited: null in node_history
            if "exited: null" in yaml_content or "exited: ~" in yaml_content:
                # Extract id
                id_match = re.search(r"id:\s*(\S+)", yaml_content)
                # Extract current node
                node_match = re.search(r"node:\s*(\S+)", yaml_content)
                if id_match:
                    incomplete.append({
                        "id": id_match.group(1).strip(),
                        "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
                        "path": str(work_file.relative_to(project_root)),
                    })
```

**Diff:**
```diff
             yaml_content = match.group(1)
+
+            # Extract status field and skip terminal statuses
+            # Uses same terminal set as WorkEngine.get_ready() (Session 211)
+            status_match = re.search(r"status:\s*(\S+)", yaml_content)
+            status = status_match.group(1).strip() if status_match else ""
+            terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}
+            if status in terminal_statuses:
+                continue
+
             # Check for exited: null in node_history
```

### Call Chain Context

```
ColdstartOrchestrator.load_session_context()
    |
    +-> scan_incomplete_work(project_root)  # <-- What we're changing
    |       Returns: list[dict] with id, incomplete_node, path
    |
    +-> Format as "stuck in {node}" warnings in coldstart output
```

### Function/Component Signatures

```python
# Signature unchanged - only internal logic changes
def scan_incomplete_work(project_root: Path) -> list[dict]:
    """
    Scan WORK.md files for incomplete transitions (exited: null).

    Args:
        project_root: Project root path

    Returns:
        List of dicts with id, incomplete_node, path
        (Now excludes items with terminal status)
    """
```

### Behavior Logic

**Current Flow (buggy):**
```
For each WORK.md in active/blocked:
    Parse YAML → Has exited:null? → YES → Add to incomplete list
```

**Fixed Flow:**
```
For each WORK.md in active/blocked:
    Parse YAML → Status terminal?
                      ├─ YES → Skip (continue)
                      └─ NO  → Has exited:null?
                                    ├─ YES → Add to incomplete list
                                    └─ NO  → Skip
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Terminal status set | Same as WorkEngine: `{complete, archived, dismissed, invalid, deferred}` | Consistency with existing codebase (memory concept 82156, 82422) - single source of truth |
| Filter placement | Before `exited: null` check | Early exit is more efficient and clearer intent |
| Regex extraction | `r"status:\s*(\S+)"` | Matches existing pattern used for `id` and `node` extraction in same function |

### Input/Output Examples

**Before Fix (with real data):**
```
Run: scan_incomplete_work(project_root)
  Returns: 80+ items including:
    - E2-236 (status: complete, stuck in backlog)
    - E2-295 (status: archived, stuck in complete)
    - E2-293 (status: complete, stuck in complete)
  Problem: Completed/archived items pollute output
```

**After Fix (expected):**
```
Run: scan_incomplete_work(project_root)
  Returns: Only items with non-terminal status:
    - E2-306 (status: implement, stuck in implement) - genuine
    - WORK-023 (status: active, stuck in backlog) - genuine
  Improvement: 80+ false positives removed
```

**Real Example with Current Data:**
```
Current coldstart output:
  - "E2-236: stuck in 'backlog'" ← FALSE (status: complete)
  - "E2-295: stuck in 'complete'" ← FALSE (status: archived)

After fix:
  - E2-236 excluded (terminal status)
  - E2-295 excluded (terminal status)
  - Only genuinely active work shown
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Missing status field | Empty string, not in terminal set, included | Test 3 (active status) |
| Unknown status value | Not in terminal set, included | Implicit (fail-open) |
| Status with whitespace | `.strip()` handles it | Regex captures non-whitespace |

### Open Questions

**Q: Should terminal_statuses be a module-level constant shared with WorkEngine?**

Answer: Not in this PR. The duplication is acceptable for now. Future refactor could extract to a shared constants module, but that's scope creep for a bug fix.

---

## Open Decisions (MUST resolve before implementation)

No operator decisions required. Work item had no `operator_decisions` field.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 3 tests to `tests/test_governance_events.py`
- [ ] Verify tests 1 & 2 fail (complete/archived included), test 3 passes (active included)

### Step 2: Implement Status Filter
- [ ] Add status extraction regex after line 227
- [ ] Add terminal_statuses set (matching WorkEngine)
- [ ] Add continue statement for terminal statuses
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Integration Verification
- [ ] Run `just coldstart-orchestrator` and verify reduced output
- [ ] Confirm E2-236, E2-295 no longer appear
- [ ] Run full test suite: `pytest tests/test_governance_events.py -v`

### Step 4: README Sync
- [ ] **SKIPPED:** No new files, no structure change. Existing README adequate.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Terminal status set diverges from WorkEngine | Low | Comment references WorkEngine; future refactor could share constant |
| Missing status field treated as non-terminal | Low | Correct behavior - fail-open for incomplete data |
| Regex edge cases | Low | Same pattern as existing id/node extraction |

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

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-023/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Fix `scan_incomplete_work()` to filter out terminal statuses | [ ] | Read function, verify status filter exists |
| Verify coldstart no longer reports completed work as "stuck" | [ ] | Run `just coldstart-orchestrator`, count items |
| Add test coverage for the fix | [ ] | Run `pytest tests/test_governance_events.py -v` |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/governance_events.py` | `scan_incomplete_work()` has status filter | [ ] | |
| `tests/test_governance_events.py` | 3 new tests for status filtering | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- Memory concept 82156: Similar bug fix pattern in queue filtering
- Memory concept 82422: plan_tree.py same bug (only filtered `complete`)
- Memory concept 81605: Terminal status set definition
- `.claude/haios/modules/work_engine.py:300` - authoritative terminal_statuses
- Session 247 checkpoint - bug discovered during E2-306 coldstart

---
