---
template: implementation_plan
status: complete
date: 2025-12-27
backlog_id: E2-212
title: Work Directory Structure Migration
author: Hephaestus
lifecycle_phase: plan
session: 130
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-27T22:23:12'
---
# Implementation Plan: Work Directory Structure Migration

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

Work items will be organized as directories (not flat files), with each work item having its own directory containing WORK.md and subdirectories for investigations, plans, and reports, enabling artifact co-location per INV-043.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 6 | `.claude/lib/status.py`, `scaffold.py`, `work_item.py`, `audit.py`, `node_cycle.py`, `scripts/plan_tree.py` |
| Lines of code affected | ~120 | Glob patterns and path constants in above files |
| New files to create | 0 | Modifying existing files only |
| Tests to write | 5 | Migration script, path resolution, directory creation |
| Work files to migrate | 51 | `docs/work/active/WORK-*.md` (convert to directories) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | High | 6 Python files + 2 commands + tests |
| Risk of regression | Medium | Existing tests exist but need updates |
| External dependencies | Low | File system only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Infrastructure | 45 min | High |
| Phase 2: Migration script | 30 min | High |
| Phase 3: Cutover | 30 min | Medium |
| **Total** | 1.75 hr | High |

---

## Current State vs Desired State

### Current State

```
docs/work/
├── active/
│   ├── WORK-E2-212-work-directory-structure-migration.md
│   ├── WORK-E2-213-investigation-subtype-field.md
│   └── ... (51 flat files)
├── archive/
│   └── ... (completed work files)

docs/plans/
├── PLAN-E2-212-work-directory-structure-migration.md
└── ...

docs/investigations/
├── INVESTIGATION-INV-043-work-item-directory-architecture.md
└── ...
```

**Behavior:** Work artifacts scattered across multiple directories. Plans in `docs/plans/`, investigations in `docs/investigations/`, work files in `docs/work/`.

**Result:** Related artifacts are hard to find. E2-091 has 14+ files across 4 directories.

### Desired State

```
docs/work/
├── active/
│   ├── E2-212/
│   │   ├── WORK.md                  # Main work file
│   │   ├── plans/
│   │   │   └── PLAN.md              # Implementation plan
│   │   └── investigations/
│   │       ├── 001-landscape.md     # Investigation subtype files
│   │       └── 002-deep-dive.md
│   └── E2-213/
│       └── WORK.md
├── archive/
│   └── E2-210/
│       ├── WORK.md
│       └── plans/PLAN.md
```

**Behavior:** All artifacts for a work item live in its directory. Plans scaffold into `{id}/plans/PLAN.md`, investigations into `{id}/investigations/NNN-*.md`.

**Result:** Related artifacts co-located. Single directory contains all context for a work item.

---

## Tests First (TDD)

### Test 1: Work Directory Structure Created
```python
def test_scaffold_work_item_creates_directory():
    """Work item scaffold creates directory structure, not flat file."""
    result = scaffold_template('work_item', backlog_id='E2-TEST', title='Test Item')
    assert Path(result).parent.name == 'E2-TEST'  # Directory named after ID
    assert Path(result).name == 'WORK.md'  # File is WORK.md not WORK-E2-TEST-*.md
    assert (Path(result).parent / 'plans').exists()  # plans subdir created
    assert (Path(result).parent / 'investigations').exists()  # inv subdir created
```

### Test 2: Find Work File Resolves Directory Structure
```python
def test_find_work_file_resolves_directory():
    """find_work_file finds WORK.md in directory structure."""
    # Setup: create docs/work/active/E2-TEST/WORK.md
    result = find_work_file('E2-TEST')
    assert result is not None
    assert result.name == 'WORK.md'
    assert result.parent.name == 'E2-TEST'
```

### Test 3: Migration Script Converts Flat to Directory
```python
def test_migrate_work_file_creates_directory():
    """Migration converts WORK-E2-TEST-title.md to E2-TEST/WORK.md."""
    # Setup: create flat file WORK-E2-TEST-title.md
    migrate_work_files()
    assert not Path('docs/work/active/WORK-E2-TEST-title.md').exists()
    assert Path('docs/work/active/E2-TEST/WORK.md').exists()
```

### Test 4: Plan Scaffolds Into Work Directory
```python
def test_plan_scaffolds_into_work_directory():
    """Plan creates inside work item's plans/ subdirectory."""
    result = scaffold_template('implementation_plan', backlog_id='E2-TEST', title='Test')
    assert 'E2-TEST/plans/PLAN.md' in str(result)
```

### Test 5: Backward Compatibility (Archive Unchanged)
```python
def test_archive_structure_unchanged():
    """Completed items in archive stay as-is (no migration of archive)."""
    # Archive still uses flat structure for completed items
    archived_files = list(Path('docs/work/archive').glob('WORK-*.md'))
    assert len(archived_files) > 0  # Archive format unchanged
```

---

## Detailed Design

### Key Files to Modify

1. **`.claude/lib/scaffold.py`** - Template path generation
2. **`.claude/lib/work_item.py`** - Work file operations
3. **`.claude/lib/status.py`** - Work file discovery (8 glob patterns)
4. **`.claude/lib/audit.py`** - Work file auditing
5. **`.claude/lib/node_cycle.py`** - Node transitions
6. **`scripts/plan_tree.py`** - Plan tree visualization

### Exact Code Changes

**File:** `.claude/lib/scaffold.py`
**Location:** `TEMPLATE_CONFIG` dict (lines 32-68)

**Current Code:**
```python
# scaffold.py:63-67
    "work_item": {
        "dir": "docs/work/active",
        "prefix": "WORK",
        "pattern": "{dir}/{prefix}-{backlog_id}-{slug}.md",
    },
```

**Changed Code:**
```python
# scaffold.py:63-67 - Directory structure
    "work_item": {
        "dir": "docs/work/active",
        "prefix": None,  # No prefix - file is just WORK.md
        "pattern": "{dir}/{backlog_id}/WORK.md",  # Directory per work item
        "subdirs": ["plans", "investigations", "reports"],  # Auto-create
    },
    "implementation_plan": {
        "dir": "docs/work/active",  # NOW inside work dir
        "prefix": None,
        "pattern": "{dir}/{backlog_id}/plans/PLAN.md",
    },
    "investigation": {
        "dir": "docs/work/active",
        "prefix": None,
        "pattern": "{dir}/{backlog_id}/investigations/{seq}-{slug}.md",
    },
```

**File:** `.claude/lib/work_item.py`
**Location:** `find_work_file()` (lines 19-31)

**Current Code:**
```python
# work_item.py:29-31
    pattern = f"WORK-{backlog_id}-*.md"
    matches = list(ACTIVE_DIR.glob(pattern))
    return matches[0] if matches else None
```

**Changed Code:**
```python
# work_item.py:29-35 - Directory structure
    # First try directory structure (new)
    dir_path = ACTIVE_DIR / backlog_id / "WORK.md"
    if dir_path.exists():
        return dir_path
    # Fall back to flat file (legacy/archive)
    pattern = f"WORK-{backlog_id}-*.md"
    matches = list(ACTIVE_DIR.glob(pattern))
    return matches[0] if matches else None
```

### Call Chain Context

```
/new-work E2-212 "Title"
    |
    +-> scaffold.scaffold_template()
    |       |
    |       +-> generate_output_path()  # <-- Update pattern
    |       +-> _create_subdirs()       # <-- NEW: Create plans/, investigations/
    |       Returns: "docs/work/active/E2-212/WORK.md"
    |
    +-> work-creation-cycle skill reads WORK.md
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Archive migration | NO - Archive stays flat | Completed items don't need artifact co-location |
| Plan path change | Plans move INSIDE work dir | Full co-location per INV-043 decision |
| Dual lookup | Try dir first, then flat | Backward compat during migration |
| Subdir creation | Eager (on work create) | Ensures plans/inv have destination |

### Input/Output Examples

**Before (flat structure):**
```
scaffold_template('work_item', backlog_id='E2-212', title='Migration')
  Returns: "docs/work/active/WORK-E2-212-migration.md"
```

**After (directory structure):**
```
scaffold_template('work_item', backlog_id='E2-212', title='Migration')
  Returns: "docs/work/active/E2-212/WORK.md"
  Side effect: Creates E2-212/plans/, E2-212/investigations/, E2-212/reports/
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work file exists (flat) | Dual lookup finds it | Test 2 |
| Work file exists (dir) | Dual lookup finds it | Test 2 |
| Archive files | Stay flat, no migration | Test 5 |
| ID with prefix (INV-043) | Directory name is INV-043 | Test 3 |

### Open Questions

**Q: Should plans currently in docs/plans/ be moved to work directories?**

Answer: Yes for active work items. Migration script will find associated plans and move them.

---

## Implementation Steps

### Phase 1: Infrastructure (Tests 1, 2, 4)

#### Step 1.1: Write Failing Tests
- [ ] Add 5 tests to `tests/test_work_item.py` (or new test file)
- [ ] Verify all tests fail (red)

#### Step 1.2: Update scaffold.py TEMPLATE_CONFIG
- [ ] Change work_item pattern to directory structure
- [ ] Add `subdirs` field for auto-creation
- [ ] Add `_create_subdirs()` helper function
- [ ] Test 1 passes (green)

#### Step 1.3: Update work_item.py find_work_file()
- [ ] Add dual lookup (directory first, then flat)
- [ ] Test 2 passes (green)

#### Step 1.4: Update scaffold.py for plans/investigations
- [ ] Change implementation_plan pattern to inside work dir
- [ ] Change investigation pattern to inside work dir with sequence
- [ ] Test 4 passes (green)

### Phase 2: Status Discovery Updates

#### Step 2.1: Update status.py glob patterns
- [ ] Update `get_active_work_cycle()` to check for `{id}/WORK.md`
- [ ] Update `get_outstanding_items()` dual pattern
- [ ] Update `get_spawn_map()` dual pattern
- [ ] Update all 8 locations with `WORK-*.md` pattern

#### Step 2.2: Update audit.py
- [ ] Update work file glob pattern (line 74)
- [ ] Add dual lookup support

#### Step 2.3: Update node_cycle.py
- [ ] Update `_extract_backlog_id()` to handle both patterns
- [ ] Update path handling for directory structure

#### Step 2.4: Update plan_tree.py
- [ ] Update work file glob (line 72)
- [ ] Add dual pattern support

### Phase 3: Migration Script (Test 3)

#### Step 3.1: Create migration script
- [ ] Create `scripts/migrate_work_dirs.py`
- [ ] Implement `migrate_work_file()` - flat to directory
- [ ] Implement `migrate_all_active()` - batch migration
- [ ] Test 3 passes (green)

#### Step 3.2: Run migration
- [ ] Execute migration script (dry-run first)
- [ ] Verify 51 work files converted
- [ ] Move associated plans into work directories

### Phase 4: Verification

#### Step 4.1: Integration Testing
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] No regressions
- [ ] Test 5 passes (archive unchanged)

#### Step 4.2: README Sync (MUST)
- [ ] **MUST:** Update `docs/work/README.md` with new structure
- [ ] **MUST:** Update `.claude/lib/README.md` with changed modules
- [ ] **MUST:** Update `/new-work` command docs if needed

#### Step 4.3: Consumer Verification (MUST)

**Known Consumers to Verify:**
| Consumer | Module | Test File |
|----------|--------|-----------|
| `pre_tool_use.py` | `node_cycle` | `test_hooks.py` |
| `post_tool_use.py` | `status`, `node_cycle` | `test_hooks.py` |
| `user_prompt_submit.py` | `status` | `test_hooks.py` |
| `/close` command | `work_item` | `test_close_work_item.py` |
| `/new-work` command | `scaffold` | `test_lib_scaffold.py` |
| `close-work-cycle` skill | Work file paths | Manual test |
| `work-creation-cycle` skill | Work file paths | Manual test |

**Pre-Migration Baseline:**
```bash
# Capture current test state before any changes
pytest tests/ -v --tb=short 2>&1 | tee baseline_tests.txt
```

**Post-Migration Regression Suite:**
```bash
# Run full test suite
pytest tests/ -v

# Specifically test affected modules
pytest tests/test_close_work_item.py tests/test_lib_scaffold.py tests/test_work_item.py tests/test_hooks.py -v
```

**Integration Smoke Tests (manual):**
```bash
# Test /new-work creates directory structure
just work E2-TEST "Test Item"
ls -la docs/work/active/E2-TEST/  # Should have WORK.md, plans/, investigations/

# Test /new-plan scaffolds into work directory
just plan E2-TEST "Test Plan"
ls docs/work/active/E2-TEST/plans/  # Should have PLAN.md

# Test find_work_file resolves directory structure
python -c "import sys; sys.path.insert(0, '.claude/lib'); from work_item import find_work_file; print(find_work_file('E2-TEST'))"
# Should print: docs/work/active/E2-TEST/WORK.md

# Cleanup test item
rm -rf docs/work/active/E2-TEST/
```

**Stale Reference Detection:**
```bash
# Find all references to old flat file pattern
grep -rn "WORK-.*-\*\.md" .claude/ scripts/ tests/
grep -rn "docs/work/active/WORK-" .claude/ scripts/
grep -rn "pattern.*WORK-{backlog_id}" .claude/lib/

# Expected: 0 matches (or only in archive-handling/backward-compat code)
```

- [ ] **MUST:** Run pre-migration baseline
- [ ] **MUST:** Update test files for directory structure
- [ ] **MUST:** Run post-migration regression suite (all pass)
- [ ] **MUST:** Run integration smoke tests
- [ ] **MUST:** Verify zero stale references in grep output
- [ ] **MUST:** Update all consumers with stale patterns

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Broken glob patterns | High | Dual lookup supports both old and new patterns |
| Lost files during migration | High | Dry-run first, git commit before migration |
| Performance of dual lookup | Low | Check directory first (faster), fall back to glob |
| Commands/skills broken | Medium | Consumer verification step catches stale refs |

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
| `.claude/lib/scaffold.py` | TEMPLATE_CONFIG has directory patterns | [ ] | |
| `.claude/lib/work_item.py` | find_work_file() has dual lookup | [ ] | |
| `.claude/lib/status.py` | All 8 glob patterns updated | [ ] | |
| `tests/test_work_item.py` | 5 new tests for directory structure | [ ] | |
| `docs/work/active/E2-212/WORK.md` | Migration successful (directory exists) | [ ] | |
| `Grep: WORK-.*-\*\.md` | **MUST:** Zero stale references | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_work_item.py -v
# Expected: 5+ tests passed

# Check for stale references
grep -r "WORK-.*-\*\.md" .claude/lib/ scripts/
# Expected: 0 matches
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

- **INV-043:** Work Item Directory Architecture (spawned this work)
- **ADR-039:** Work Item as File Architecture (design decision)
- **Memory 77322:** Design decision for directory structure
- **Memory 77323:** 3-phase migration approach
- **Memory 79787:** Plans/investigations move inside work directories

---
