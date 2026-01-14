---
template: implementation_plan
status: complete
date: 2025-12-21
backlog_id: E2-125
title: "Full Status Module"
author: Hephaestus
lifecycle_phase: done
session: 94
completed_session: 94
spawned_by: E2-120
related: [E2-120, E2-129, UpdateHaiosStatus.ps1]
milestone: M5-Plugin
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-21T20:56:48
---
# Implementation Plan: Full Status Module

@docs/plans/PLAN-E2-120-complete-powershell-to-python-migration.md
@.claude/lib/status.py

<!-- v1.4 Plan Review (Session 94):
     - Fixed overlap: get_valid_templates() now wraps validate.py's get_template_registry()
     - Related E2-129 added (section skip validation)
     - All sections present or have SKIPPED marker per v1.4 governance
-->

---

## Goal

Complete the status module with 8 deferred functions from E2-120, enabling full workspace analysis, lifecycle tracking, and haios-status.json generation.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/status.py` (627 LOC currently) |
| Lines of code affected | ~500 | 8 new functions, avg 60 LOC each |
| New files to create | 0 | Adding to existing module |
| Tests to write | ~20 | 2-3 tests per function × 8 functions |
| Dependencies | 2 | justfile, haios-status.json consumer |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Scans filesystem, reads backlog, generates JSON |
| Risk of regression | Low | Existing 28 tests cover core functions |
| External dependencies | Low | Pure filesystem operations |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| TDD: Write tests | 45 min | High |
| Implement 8 functions | 90 min | Medium |
| Integration/verification | 30 min | High |
| **Total** | ~3 hr | Medium |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/status.py - 9 core functions for slim status only
def generate_slim_status() -> dict:
    # Produces haios-status-slim.json (vitals + basic counts)
    # Missing: workspace analysis, lifecycle tracking, staleness
```

**Behavior:** `generate_slim_status()` creates minimal JSON for vitals injection (coldstart, UserPromptSubmit hook).

**Result:** `/haios` and full workspace analysis require PowerShell `UpdateHaiosStatus.ps1` (not migrated).

### Desired State

```python
# .claude/lib/status.py - 17 functions for full status
def generate_full_status() -> dict:
    # Produces complete haios-status.json with all metadata
    # Includes: templates, live files, outstanding items, staleness

def get_valid_templates() -> list[dict]:
    # Parse template definitions from .claude/templates/

def get_live_files() -> list[dict]:
    # Scan governed paths for lifecycle metadata
```

**Behavior:** `generate_full_status()` creates complete JSON with workspace analysis, lifecycle tracking, staleness detection.

**Result:** Full `/haios` functionality works via Python. PowerShell eliminated.

---

## Tests First (TDD)

Add to `tests/test_lib_status.py` (existing file with 28 tests).

### Test 1: get_valid_templates returns template list
```python
def test_get_valid_templates_returns_list():
    from status import get_valid_templates
    templates = get_valid_templates()
    assert isinstance(templates, list)
    assert len(templates) >= 7  # checkpoint, plan, adr, investigation, report, readme, backlog_item
```

### Test 2: get_live_files scans governed paths
```python
def test_get_live_files_finds_checkpoints():
    from status import get_live_files
    files = get_live_files()
    assert any(f["path"].startswith("docs/checkpoints/") for f in files)
```

### Test 3: get_outstanding_items detects pending work
```python
def test_get_outstanding_items_finds_pending():
    from status import get_outstanding_items
    items = get_outstanding_items()
    assert isinstance(items, list)
    # Each item has id, status, priority
```

### Test 4: get_stale_items detects old documents
```python
def test_get_stale_items_has_threshold():
    from status import get_stale_items
    items = get_stale_items(days=30)
    assert isinstance(items, list)
```

### Test 5: get_workspace_summary aggregates counts
```python
def test_get_workspace_summary_structure():
    from status import get_workspace_summary
    summary = get_workspace_summary()
    assert "total_files" in summary
    assert "by_template" in summary
```

### Test 6: check_alignment matches files to backlog
```python
def test_check_alignment_returns_mapping():
    from status import check_alignment
    alignment = check_alignment()
    assert isinstance(alignment, dict)
```

### Test 7: get_spawn_map tracks spawned items
```python
def test_get_spawn_map_structure():
    from status import get_spawn_map
    spawn_map = get_spawn_map()
    assert isinstance(spawn_map, dict)
```

### Test 8: generate_full_status orchestrates all
```python
def test_generate_full_status_includes_all_sections():
    from status import generate_full_status
    full = generate_full_status()
    assert "templates" in full
    assert "live_files" in full
    assert "workspace" in full
```

---

## Detailed Design

### Function Signatures (8 new functions)

```python
def get_valid_templates() -> list[dict]:
    """Get template definitions by wrapping validate.py's registry.
    NOTE: Reuses get_template_registry() from validate.py (E2-129 overlap fix).
    Returns: [{"name": "checkpoint", "required_fields": [...], ...}, ...]
    """

def get_live_files() -> list[dict]:
    """Scan governed paths for files with YAML frontmatter.
    Governed paths: docs/checkpoints/, docs/plans/, docs/investigations/, docs/ADR/
    Returns: [{"path": "...", "template": "...", "status": "...", "date": "..."}, ...]
    """

def get_outstanding_items() -> list[dict]:
    """Find items with status != complete/closed.
    Returns: [{"id": "E2-125", "status": "proposed", "priority": "low"}, ...]
    """

def get_stale_items(days: int = 30) -> list[dict]:
    """Find files not updated within threshold.
    Returns: [{"path": "...", "last_updated": "...", "days_stale": N}, ...]
    """

def get_workspace_summary() -> dict:
    """Aggregate counts by template type, status, staleness.
    Returns: {"total_files": N, "by_template": {...}, "by_status": {...}, "stale_count": N}
    """

def check_alignment() -> dict:
    """Match files to backlog items, detect orphans.
    Returns: {"aligned": [...], "orphan_files": [...], "missing_files": [...]}
    """

def get_spawn_map() -> dict:
    """Track spawned_by relationships from frontmatter.
    Returns: {"E2-120": ["E2-125", "E2-126"], ...}
    """

def generate_full_status() -> dict:
    """Orchestrate all functions into complete haios-status.json.
    Returns: Full status dict compatible with existing consumers.
    """
```

### Call Chain Context

```
/haios command or justfile recipe
    |
    +-> generate_full_status()
            |
            +-> get_valid_templates()
            +-> get_live_files()
            +-> get_outstanding_items()
            +-> get_stale_items()
            +-> get_workspace_summary()
            +-> check_alignment()
            +-> get_spawn_map()
            +-> generate_slim_status()  # Existing core
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Reuse existing functions | Yes | `generate_slim_status()` already does 60% of work |
| Staleness threshold | 30 days default | Matches current UpdateHaiosStatus.ps1 |
| Template source | `validate.py` registry | E2-129 added template rules there; reuse, don't duplicate |
| Output format | Match existing JSON | Backward compatible with consumers |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No templates exist | Return empty list | Test 1 |
| File without frontmatter | Skip file | Test 2 |
| Malformed YAML | Skip with warning | Test 2 |
| Circular spawned_by | Ignore cycles | Test 7 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 8 new tests to `tests/test_lib_status.py`
- [ ] Verify all 8 fail (red) - functions don't exist yet

### Step 2: Implement get_valid_templates()
- [ ] Parse `.claude/templates/*.md` for frontmatter
- [ ] Extract required_fields, allowed_status from each template
- [ ] Test 1 passes (green)

### Step 3: Implement get_live_files()
- [ ] Scan governed paths: checkpoints, plans, investigations, ADR
- [ ] Parse YAML frontmatter from each file
- [ ] Return list with path, template, status, date
- [ ] Test 2 passes (green)

### Step 4: Implement get_outstanding_items()
- [ ] Filter live_files for status != complete/closed
- [ ] Add priority from frontmatter or backlog
- [ ] Test 3 passes (green)

### Step 5: Implement get_stale_items(days=30)
- [ ] Calculate days since last_updated
- [ ] Filter for items exceeding threshold
- [ ] Test 4 passes (green)

### Step 6: Implement get_workspace_summary()
- [ ] Aggregate live_files by template type
- [ ] Aggregate by status
- [ ] Include stale count
- [ ] Test 5 passes (green)

### Step 7: Implement check_alignment()
- [ ] Match files to backlog_id references
- [ ] Detect orphan files (no backlog_id)
- [ ] Detect missing files (backlog has no plan)
- [ ] Test 6 passes (green)

### Step 8: Implement get_spawn_map()
- [ ] Extract spawned_by from frontmatter
- [ ] Build parent->children dict
- [ ] Test 7 passes (green)

### Step 9: Implement generate_full_status()
- [ ] Call all new functions
- [ ] Merge with generate_slim_status() output
- [ ] Test 8 passes (green)

### Step 10: Integration Verification
- [ ] All 36+ tests pass (28 existing + 8 new)
- [ ] Run full test suite: `pytest tests/test_lib_status.py -v`

### Step 11: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` with new functions
- [ ] **MUST:** Update justfile if adding new recipes

---

## Verification

- [ ] Tests pass: `pytest tests/test_lib_status.py -v`
- [ ] **MUST:** `.claude/lib/README.md` updated with new functions
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance with many files | Medium | Cache results, lazy evaluation |
| Breaking existing consumers | High | Extend, don't replace generate_slim_status() |
| Inconsistent frontmatter | Low | Skip malformed, log warning |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 94 | 2025-12-21 | Plan created | Draft | |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/status.py` | 8 new functions exist | [ ] | |
| `tests/test_lib_status.py` | 36+ tests, all pass | [ ] | |
| `.claude/lib/README.md` | Documents new functions | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_lib_status.py -v
# Expected: 36+ tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Test output pasted above? | [ ] | |
| Any deviations from plan? | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (36+)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** `.claude/lib/README.md` updated
- [ ] Ground Truth Verification completed above

---

## References

- E2-120: PowerShell to Python migration (spawned this)
- UpdateHaiosStatus.ps1: Original implementation reference
- ADR-033: Work item lifecycle

---
