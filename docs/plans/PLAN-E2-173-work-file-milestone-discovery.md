---
template: implementation_plan
status: complete
date: 2025-12-24
backlog_id: E2-173
title: Work File Milestone Discovery
author: Hephaestus
lifecycle_phase: plan
session: 114
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-24T21:28:42'
---
# Implementation Plan: Work File Milestone Discovery

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

Status.py will discover milestones from work file YAML frontmatter (in addition to legacy backlog.md patterns), enabling vitals to show M7 sub-milestone progress correctly.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/status.py` |
| Lines of code affected | ~50 | Add new function + modify _load_existing_milestones |
| New files to create | 0 | None |
| Tests to write | 3 | Work file discovery, merge logic, integration |
| Dependencies | 1 | generate_slim_status() calls _load_existing_milestones() |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single file change, well-isolated |
| Risk of regression | Low | Additive change, keeps backlog fallback |
| External dependencies | Low | Only filesystem reads |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 10 min | High |
| Implementation | 15 min | High |
| Verification | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/status.py:879-886
def _load_existing_milestones() -> dict:
    """Discover milestones from backlog.md.

    Always discovers from backlog (source of truth) rather than caching.
    This ensures new milestones are picked up immediately (E2-117).
    """
    # Always discover from backlog - it's the source of truth
    return _discover_milestones_from_backlog()
```

**Behavior:** Only reads backlog.md for `**Milestone:** M?-Name` patterns.

**Result:** M7 sub-milestones (M7a-M7e) not discovered - vitals show stale M4-Research (50%).

### Desired State

```python
# .claude/lib/status.py - Target implementation
def _load_existing_milestones() -> dict:
    """Discover milestones from work files AND backlog.md."""
    # Primary source: work files (new pattern)
    work_milestones = _discover_milestones_from_work_files()
    # Fallback source: backlog.md (legacy pattern)
    backlog_milestones = _discover_milestones_from_backlog()
    # Merge: work files take precedence
    merged = {**backlog_milestones, **work_milestones}
    return merged
```

**Behavior:** Reads work files for `milestone:` YAML field, merges with backlog.md patterns.

**Result:** All milestones (M3-M8+) discovered correctly, vitals show M7a-Recipes progress.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Work file milestone discovery
```python
def test_discover_milestones_from_work_files(tmp_path, monkeypatch):
    """Test milestone discovery from work file YAML frontmatter."""
    # Setup: create mock work files with milestone field
    active_dir = tmp_path / "docs" / "work" / "active"
    active_dir.mkdir(parents=True)
    (active_dir / "WORK-E2-001-test.md").write_text(
        "---\nmilestone: M7a-Recipes\nid: E2-001\nstatus: active\n---\n"
    )
    monkeypatch.setattr("status.PROJECT_ROOT", tmp_path)

    from status import _discover_milestones_from_work_files
    result = _discover_milestones_from_work_files()

    assert "M7a-Recipes" in result
    assert "E2-001" in result["M7a-Recipes"]["items"]
```

### Test 2: Merge work files with backlog (work files take precedence)
```python
def test_load_existing_milestones_merges_sources(tmp_path, monkeypatch):
    """Test that work file milestones merge with backlog milestones."""
    # Work files have M7a, backlog has M4
    # Both should appear in result
    # ... setup ...
    result = _load_existing_milestones()
    assert "M7a-Recipes" in result  # from work files
    assert "M4-Research" in result   # from backlog (if exists)
```

### Test 3: Complete status calculation for work file milestones
```python
def test_complete_items_calculated_for_work_file_milestones(tmp_path, monkeypatch):
    """Test that complete items are counted correctly for work file milestones."""
    # Setup: work file with complete status
    archive_dir = tmp_path / "docs" / "work" / "archive"
    archive_dir.mkdir(parents=True)
    (archive_dir / "WORK-E2-001-test.md").write_text(
        "---\nmilestone: M7a-Recipes\nid: E2-001\nstatus: complete\n---\n"
    )
    # ...
    result = _discover_milestones_from_work_files()
    assert "E2-001" in result["M7a-Recipes"]["complete"]
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/lib/status.py`

**NEW Function (add after line ~960):**
```python
def _discover_milestones_from_work_files() -> dict:
    """Discover milestones from work file YAML frontmatter.

    Scans docs/work/{active,blocked,archive}/*.md for milestone: field.

    Returns:
        Dict mapping milestone keys to milestone data.
    """
    work_dirs = [
        PROJECT_ROOT / "docs" / "work" / "active",
        PROJECT_ROOT / "docs" / "work" / "blocked",
        PROJECT_ROOT / "docs" / "work" / "archive",
    ]

    milestones = {}

    for dir_path in work_dirs:
        if not dir_path.exists():
            continue

        for file_path in dir_path.glob("WORK-*.md"):
            try:
                content = file_path.read_text(encoding="utf-8-sig")
                metadata = _parse_yaml_frontmatter(content)

                milestone_key = metadata.get("milestone")
                item_id = metadata.get("id")
                status = metadata.get("status", "").lower()

                if not milestone_key or not item_id:
                    continue

                # Initialize milestone if not seen
                if milestone_key not in milestones:
                    milestones[milestone_key] = {
                        "name": _format_milestone_name(milestone_key),
                        "items": [],
                        "complete": [],
                        "progress": 0,
                    }

                # Add item to milestone
                if item_id not in milestones[milestone_key]["items"]:
                    milestones[milestone_key]["items"].append(item_id)

                # Track complete items
                if status in ("complete", "closed", "done"):
                    if item_id not in milestones[milestone_key]["complete"]:
                        milestones[milestone_key]["complete"].append(item_id)

            except Exception:
                continue

    # Calculate progress for each milestone
    for ms in milestones.values():
        total = len(ms["items"])
        done = len(ms["complete"])
        ms["progress"] = int((done / total * 100) if total > 0 else 0)

    return milestones
```

**MODIFIED Function (line ~879-886):**
```python
def _load_existing_milestones() -> dict:
    """Discover milestones from work files AND backlog.md.

    Work files are primary source (new pattern).
    Backlog.md is fallback for legacy items.
    """
    # Primary: work files (new pattern)
    work_milestones = _discover_milestones_from_work_files()
    # Fallback: backlog.md (legacy pattern)
    backlog_milestones = _discover_milestones_from_backlog()
    # Merge: work files take precedence (update backlog with work data)
    merged = {**backlog_milestones, **work_milestones}
    return merged
```

### Call Chain Context

```
generate_slim_status()
    |
    +-> _load_existing_milestones()      # <-- MODIFIED
    |       |
    |       +-> _discover_milestones_from_work_files()  # <-- NEW
    |       +-> _discover_milestones_from_backlog()     # Existing
    |
    +-> get_milestone_progress(existing_milestones)
    +-> _select_current_milestone(milestones)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Work files take precedence | `{**backlog, **work}` | Work files are new source of truth (INV-024) |
| Keep backlog fallback | Yes | Backward compatibility for M3-M6 legacy items |
| Track complete by status field | Check status in ("complete", "closed", "done") | Consistent with existing pattern in status.py |
| Reuse _parse_yaml_frontmatter | Yes | Already exists in status.py:542-562 |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No work files exist | Return empty dict | Implicit - dirs don't exist |
| milestone: null in YAML | Skip that file | `if not milestone_key` check |
| Same item in backlog and work | Work file wins | Merge order: `{**backlog, **work}` |
| Malformed YAML | Skip that file | try/except block |

### Open Questions

**Q: Should we read docs/pm/milestones/*.md files too?**

No - per INV-029 design decision, defer this. Only M8-Memory.md exists there.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add test_discover_milestones_from_work_files to tests/test_lib_status.py
- [ ] Add test_load_existing_milestones_merges_sources
- [ ] Verify tests fail (red) - function doesn't exist yet

### Step 2: Add _discover_milestones_from_work_files()
- [ ] Add new function after line ~960 in status.py
- [ ] Test 1 passes (green)

### Step 3: Modify _load_existing_milestones()
- [ ] Update to call both discovery functions and merge
- [ ] Tests 1, 2 pass (green)

### Step 4: Integration Verification
- [ ] Run `just update-status-slim`
- [ ] Verify M7a-Recipes appears in haios-status-slim.json
- [ ] Run full test suite (no regressions)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update .claude/lib/README.md to document new function

### Step 6: Consumer Verification (MUST for migrations/refactors)

**SKIPPED:** Not a migration/refactor - pure addition. No consumers to update.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** .claude/lib/README.md documents new function
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance on large work dirs | Low | Already scanning ~50 files, minimal overhead |
| Duplicate items across sources | Low | Work files take precedence, explicit merge |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 115 | 2025-12-24 | - | In progress | Plan complete, starting implementation |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/status.py` | _discover_milestones_from_work_files() exists | [ ] | |
| `tests/test_lib_status.py` | 2+ new tests for work file discovery | [ ] | |
| `.claude/lib/README.md` | Documents new function | [ ] | |
| `.claude/haios-status-slim.json` | Shows M7a-Recipes milestone | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_lib_status.py -v -k "work_file"
# Expected: 2+ tests passed
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
- [ ] **MUST:** .claude/lib/README.md updated
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- INV-029: Status Generation Architecture Gap (spawned this)
- INV-024: Work Item as File Architecture

---
