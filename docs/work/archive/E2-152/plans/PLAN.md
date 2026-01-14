---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-152
title: "Work-Item-Tooling-Cutover"
author: Hephaestus
lifecycle_phase: plan
session: 107
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-23T19:26:10
---
# Implementation Plan: Work-Item-Tooling-Cutover

@docs/README.md
@docs/epistemic_state.md
@docs/work/active/WORK-E2-152-work-item-tooling-cutover.md

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

The `/close` command will detect and update work files (`docs/work/active/WORK-*.md`) when closing work items, moving them to `docs/work/archive/` instead of only updating `backlog.md`.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/commands/close.md` |
| Lines of code affected | ~50 | Additional work file handling logic |
| New files to create | 1 | `tests/test_close_work_item.py` |
| Tests to write | 4 | Work file detection, update, move, backward compat |
| Dependencies | 0 | Command-only change, no lib modifications |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only `/close` command affected |
| Risk of regression | Low | Additive change, backlog.md flow preserved |
| External dependencies | Low | File system operations only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 20 min | High |
| Verification | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/commands/close.md - Step 1a

### 1a. Verify backlog entry exists

Read `docs/pm/backlog.md` and search for the backlog_id pattern:
### \[.*\] {backlog_id}:

If NOT found:
- Inform user: "Work item {backlog_id} not found in backlog.md"
- STOP
```

**Behavior:** `/close` only looks in `docs/pm/backlog.md` for work items.

**Result:** 66 work files in `docs/work/active/` are ignored; closing them requires manual steps.

### Desired State

```markdown
# .claude/commands/close.md - Step 1a (UPDATED)

### 1a. Check for work file first

1. Look for work file: `docs/work/active/WORK-{backlog_id}-*.md`
2. If found:
   - Use work file as primary source
   - Skip backlog.md lookup
3. If NOT found:
   - Fall back to backlog.md lookup (backward compatibility)
```

**Behavior:** `/close` first checks for a work file, then falls back to backlog.md.

**Result:** Work files can be closed properly; backward compatibility with backlog.md preserved.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

**Note:** The `/close` command is a markdown file with instructions, not executable code.
Tests will validate the *helper functions* in `.claude/lib/` that the command uses.

### Test 1: Find Work File
```python
def test_find_work_file_exists():
    """Test that find_work_file returns path when work file exists."""
    # Setup: Create temp work file
    # Action: Call find_work_file("E2-152")
    # Assert: Returns path to docs/work/active/WORK-E2-152-*.md
    assert result.exists()
    assert "WORK-E2-152" in result.name
```

### Test 2: Find Work File Fallback
```python
def test_find_work_file_not_found_returns_none():
    """Test that find_work_file returns None when no work file exists."""
    # Action: Call find_work_file("E2-999")  # non-existent
    # Assert: Returns None
    assert find_work_file("E2-999") is None
```

### Test 3: Update Work File Status
```python
def test_update_work_file_status():
    """Test that work file status field is updated correctly."""
    # Setup: Create temp work file with status: active
    # Action: Call update_work_file_status(path, "complete")
    # Assert: File now has status: complete in frontmatter
    content = path.read_text()
    assert "status: complete" in content
```

### Test 4: Move Work File to Archive
```python
def test_move_work_file_to_archive():
    """Test that work file is moved from active/ to archive/."""
    # Setup: Create temp work file in docs/work/active/
    # Action: Call move_work_file_to_archive(path)
    # Assert: File no longer in active/, now in archive/
    assert not active_path.exists()
    assert archive_path.exists()
```

---

## Detailed Design

### Architecture Decision

The `/close` command is a markdown instruction file, not executable Python code. To enable testable functionality, we will:

1. **Add helper functions** to `.claude/lib/work_item.py` (new file)
2. **Update close.md** to reference these helpers in instructions

This follows the pattern established by `scaffold.py`, `validate.py`, and `status.py`.

### New File: `.claude/lib/work_item.py`

```python
"""Work item file operations for /close command."""
from pathlib import Path
from typing import Optional
import re

WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"


def find_work_file(backlog_id: str) -> Optional[Path]:
    """
    Find work file for a backlog ID.

    Args:
        backlog_id: Work item ID (e.g., "E2-152")

    Returns:
        Path to work file if found, None otherwise
    """
    pattern = f"WORK-{backlog_id}-*.md"
    matches = list(ACTIVE_DIR.glob(pattern))
    return matches[0] if matches else None


def update_work_file_status(path: Path, new_status: str) -> None:
    """
    Update status field in work file frontmatter.

    Args:
        path: Path to work file
        new_status: New status value (e.g., "complete")
    """
    content = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'^status: .*$',
        f'status: {new_status}',
        content,
        flags=re.MULTILINE
    )
    path.write_text(updated, encoding="utf-8")


def move_work_file_to_archive(path: Path) -> Path:
    """
    Move work file from active/ to archive/.

    Args:
        path: Path to work file in active/

    Returns:
        New path in archive/
    """
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    new_path = ARCHIVE_DIR / path.name
    path.rename(new_path)
    return new_path
```

### Updated Instructions in close.md

**Step 1 Update:**

```markdown
## Step 1: Lookup Work Item (Runtime Query)

### 1a. Check for work file first (NEW)

Look for work file using pattern:
`Glob(pattern="docs/work/active/WORK-{backlog_id}-*.md")`

**If work file found:**
1. Read work file frontmatter for title, status
2. Proceed to Step 1b (find associated documents) using work file as source
3. SKIP backlog.md lookup

**If NO work file found:**
1. Fall back to backlog.md lookup (existing Step 1a behavior)
```

**Step 3 Update (Execute Closure):**

```markdown
### 3a. Archive the item

**If work file exists:**
1. Update frontmatter `status: active` → `status: complete`
2. Update `closed: null` → `closed: {date}`
3. Move file from `docs/work/active/` to `docs/work/archive/`

**If backlog.md only (legacy):**
1. Use existing archive logic (move to backlog-complete.md)
```

### Behavior Logic

```
/close {backlog_id}
    |
    +-> find_work_file(backlog_id)
            |
            ├─ Found → Use work file
            |           ├─ Validate DoD
            |           ├─ Update status: complete
            |           ├─ Update closed: {date}
            |           ├─ Move to archive/
            |           └─ Store to memory
            |
            └─ Not found → Fall back to backlog.md
                            └─ (existing logic unchanged)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Work file takes priority | Check work file before backlog.md | Work files are the new source of truth (ADR-039) |
| Preserve backlog.md fallback | Keep existing logic | Backward compatibility for items not yet migrated |
| New lib file | Create `work_item.py` | Keeps logic testable, follows existing `.claude/lib/` pattern |
| Move vs copy | Move file to archive/ | Directory = status pattern (INV-024) |

### Input/Output Examples

**Real Example - Closing E2-152:**

Before:
```
docs/work/active/WORK-E2-152-work-item-tooling-cutover.md
  - status: active
  - closed: null
```

After:
```
docs/work/archive/WORK-E2-152-work-item-tooling-cutover.md
  - status: complete
  - closed: 2025-12-23
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work file exists | Use work file, skip backlog.md | Test 1 |
| No work file | Fall back to backlog.md | Test 2 |
| Both exist | Work file takes priority | Implicit in Test 1 |
| Archive dir missing | Create on first use | Test 4 |

### Open Questions

**Q: Should we also update backlog.md when closing a work file?**

No - per ADR-039, work files are the source of truth. The migration script (E2-151) already copied items from backlog.md. Keeping both in sync would create maintenance burden. Backlog.md becomes legacy index only.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_close_work_item.py`
- [ ] Add 4 tests from "Tests First" section
- [ ] Verify all tests fail (red) - functions don't exist yet

### Step 2: Create work_item.py Library
- [ ] Create `.claude/lib/work_item.py` with 3 functions
- [ ] `find_work_file()` - Tests 1, 2 pass (green)
- [ ] `update_work_file_status()` - Test 3 passes (green)
- [ ] `move_work_file_to_archive()` - Test 4 passes (green)

### Step 3: Update close.md Command
- [ ] Update Step 1 to check for work file first
- [ ] Update Step 3 to handle work file closure
- [ ] Preserve backward compatibility with backlog.md

### Step 4: Integration Verification
- [ ] All 4 new tests pass
- [ ] Run full test suite (`pytest tests/ -v`)
- [ ] No regressions

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` to list `work_item.py`
- [ ] **MUST:** Update `.claude/commands/README.md` if close behavior documented

### Step 6: Consumer Verification
- [ ] Verify `/close` command instructions reference correct functions
- [ ] No stale references to old paths

---

## Verification

- [ ] 4 new tests pass
- [ ] Full test suite passes (no regressions)
- [ ] **MUST:** `.claude/lib/README.md` lists `work_item.py`
- [ ] Demo: Run `/close` on a test work item

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Break existing /close flow | High | Preserve backlog.md fallback logic |
| Archive directory missing | Low | Create on first use in move function |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 107 | 2025-12-23 | - | In Progress | Plan created, implementing |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/work_item.py` | 3 functions exist | [ ] | |
| `tests/test_close_work_item.py` | 4 tests exist and pass | [ ] | |
| `.claude/commands/close.md` | Work file logic added | [ ] | |
| `.claude/lib/README.md` | Lists work_item.py | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_close_work_item.py -v
# Expected: 4 tests passed
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
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- ADR-039: Work-Item-as-File Architecture
- INV-024: Work-Item-as-File Investigation
- E2-150: Work-Item Infrastructure (completed)
- E2-151: Backlog Migration Script (completed)

---
