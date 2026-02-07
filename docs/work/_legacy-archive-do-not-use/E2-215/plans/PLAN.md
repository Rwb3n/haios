---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-215
title: Create just close-work Recipe
author: Hephaestus
lifecycle_phase: plan
session: 134
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-28T14:20:52'
---
# Implementation Plan: Create just close-work Recipe

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

A single `just close-work <id>` recipe will atomically close work items by calling existing Python functions (status update, date update, archive move, cascade, status refresh), reducing closure from ~450 tokens to ~50 tokens.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `justfile`, `.claude/skills/close-work-cycle/SKILL.md` |
| Lines of code affected | ~5 | Adding recipe to justfile |
| New files to create | 0 | Uses existing Python functions |
| Tests to write | 1 | Integration test for recipe |
| Dependencies | 1 | `.claude/lib/work_item.py` (existing) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Wraps existing Python functions |
| Risk of regression | Low | New recipe, doesn't change existing code |
| External dependencies | Low | No APIs or services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Recipe creation | 5 min | High |
| Testing | 5 min | High |
| Skill update | 5 min | High |
| **Total** | 15 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/work_item.py:42-91 - Functions exist but not exposed as recipe
def update_work_file_status(path: Path, new_status: str) -> None:
    # Updates status field

def update_work_file_closed_date(path: Path, date: str) -> None:
    # Updates closed field

def move_work_file_to_archive(path: Path) -> Path:
    # Moves from active/ to archive/
```

**Behavior:** close-work-cycle skill calls these via 3 separate Edit + 1 Bash(mv) invocations

**Result:** ~450 tokens per closure, manual date formatting, potential for inconsistencies

### Desired State

```bash
# justfile - New recipe combining all operations
close-work id:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); \
    from work_item import find_work_file, update_work_file_status, update_work_file_closed_date; \
    from pathlib import Path; from datetime import date; \
    import shutil; \
    p = find_work_file('{{id}}'); \
    ... (atomic operations)"
    just cascade {{id}} complete
    just update-status
```

**Behavior:** Single `just close-work <id>` call performs all closure operations atomically

**Result:** ~50 tokens per closure, consistent date format, single point of failure

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Recipe Invocation
```bash
# Manual integration test - create temp work item and close it
just work TEST-001 "Close Work Test"
just close-work TEST-001
# Verify: TEST-001 now in docs/work/archive/, status: complete, closed: 2025-12-28
```

### Test 2: Error Handling (Not Found)
```bash
just close-work FAKE-999
# Expected output: "Not found: FAKE-999" and non-zero exit
```

### Test 3: Idempotency Check
```bash
# Running on already-archived item should fail gracefully
just close-work TEST-001  # Already archived from Test 1
# Expected: "Not found: TEST-001" (not in active/)
```

---

## Detailed Design

### Exact Code Change

**File:** `justfile`
**Location:** After line 48 (link-spawn recipe) in GOVERNANCE RECIPES section

**New Recipe:**
```bash
# Close work item atomically (E2-215)
# Combines: status update, closed date, archive move, cascade, status refresh
close-work id:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); from work_item import find_work_file, update_work_file_status, update_work_file_closed_date; from datetime import date; import shutil; p = find_work_file('{{id}}'); exit(print('Not found: {{id}}') or 1) if not p else None; update_work_file_status(p, 'complete'); update_work_file_closed_date(p, date.today().isoformat()); archive = p.parent.parent.parent / 'archive' / p.parent.name; archive.mkdir(parents=True, exist_ok=True); shutil.move(str(p.parent), str(archive)); print(f'Closed: {{id}} -> {archive}')"
    just cascade {{id}} complete
    just update-status
```

### Call Chain Context

```
/close E2-215 (command)
    |
    +-> close-work-cycle (skill)
    |       Invokes: validate, archive, capture
    |
    +-> just close-work E2-215  # <-- NEW RECIPE
            |
            +-> update_work_file_status(p, 'complete')
            +-> update_work_file_closed_date(p, date)
            +-> shutil.move(work_dir, archive)
            +-> just cascade
            +-> just update-status
```

### Behavior Logic

**Current Flow:**
```
close-work-cycle
    |-> Edit (status: complete)           # ~100 tokens
    |-> Edit (closed: date)               # ~100 tokens
    |-> Bash(mv work_dir archive/)        # ~100 tokens
    |-> just cascade                      # ~50 tokens
    |-> just update-status                # ~100 tokens
                                          # Total: ~450 tokens
```

**New Flow:**
```
close-work-cycle
    |-> just close-work E2-215            # ~50 tokens (single invocation)
        |-> Python (all 3 updates + move) # internal
        |-> cascade                        # internal
        |-> update-status                  # internal
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Single Python command | Multi-statement one-liner | Avoids multiple recipe lines, maintains atomicity |
| Move entire directory | `shutil.move(work_dir, archive)` | New work file architecture uses directories (E2-212) |
| Chain cascade + status | Separate just calls | Reuses existing recipes, easier maintenance |
| Fail-fast on not found | `exit(print(...) or 1)` | Clear error message, non-zero exit code |

### Input/Output Examples

**Before (current workflow):**
```
Agent: Edit status: active -> status: complete in WORK.md
Agent: Edit closed: null -> closed: 2025-12-28 in WORK.md
Agent: Bash(mv docs/work/active/E2-215 docs/work/archive/)
Agent: just cascade E2-215 complete
Agent: just update-status
# Total: 5 tool calls, ~450 tokens
```

**After (new recipe):**
```
Agent: just close-work E2-215
# Output: Closed: E2-215 -> docs/work/archive/E2-215
# Total: 1 tool call, ~50 tokens (87% reduction per INV-046)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work item not found | Print "Not found: {id}", exit 1 | Test 2 |
| Already archived | Not in active/, print "Not found" | Test 3 |
| Archive dir missing | `mkdir(parents=True, exist_ok=True)` | Handled in code |

---

## Implementation Steps

### Step 1: Add close-work recipe to justfile
- [ ] Add recipe after line 48 (link-spawn recipe)
- [ ] Test with `just close-work FAKE-999` (expect "Not found")

### Step 2: Test with real work item
- [ ] Create test work item: `just work TEST-001 "Close Work Test"`
- [ ] Close it: `just close-work TEST-001`
- [ ] Verify: `ls docs/work/archive/TEST-001/`
- [ ] Verify WORK.md has status: complete, closed: 2025-12-28

### Step 3: Update close-work-cycle skill
- [ ] Edit `.claude/skills/close-work-cycle/SKILL.md`
- [ ] Change ARCHIVE phase to reference `just close-work` recipe
- [ ] Remove manual Edit/Bash instructions

### Step 4: Clean up test data
- [ ] Remove test work item: `rm -rf docs/work/archive/TEST-001`

### Step 5: Consumer Verification
- [ ] Grep for manual closure patterns in skills
- [ ] Verify no other skills manually edit status/closed/archive

**SKIPPED: README Sync** - No new directories created, justfile already documented

---

## Verification

- [ ] `just close-work TEST-001` succeeds
- [ ] Work item moved to archive with correct status/date
- [ ] close-work-cycle skill references recipe

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Path calculation wrong | Medium | Test with real work item before updating skill |
| Cascade failure stops closure | Low | Cascade uses `-` prefix in just (ignore errors) |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 134 | 2025-12-28 | - | In Progress | Plan authored |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `justfile` | close-work recipe exists | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | References `just close-work` | [ ] | |
| `docs/work/archive/TEST-001/` | Does NOT exist (cleaned up) | [ ] | |

**Verification Commands:**
```bash
just close-work FAKE-999
# Expected: "Not found: FAKE-999"
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| Recipe added to justfile? | [Yes/No] | |
| Skill updated to use recipe? | [Yes/No] | |
| Test data cleaned up? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (manual integration test)
- [ ] WHY captured (reasoning stored to memory)
- [ ] close-work-cycle skill updated
- [ ] Test data removed

---

## References

- INV-046: Mechanical Action Automation (design source)
- Memory 79863: "Create just close-work recipe" directive

---
