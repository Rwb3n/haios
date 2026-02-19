---
template: implementation_plan
status: complete
date: 2026-02-19
backlog_id: WORK-177
title: "Chapter Manifest Auto-Update on Work Creation"
author: Hephaestus
lifecycle_phase: plan
session: 407
version: "1.5"
generated: 2026-02-19
last_updated: 2026-02-19T22:50:00
---
# Implementation Plan: Chapter Manifest Auto-Update on Work Creation

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory DB locked during PLAN — proceeding without (non-blocking) |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

When a work item is scaffolded with a `CHAPTER` variable (or when `update_chapter_manifest()` is called explicitly), the chapter's CHAPTER.md work items table is auto-updated with the new work item row, using a fail-permissive pattern that never blocks work creation.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/haios/lib/scaffold.py` (add call after line 629) |
| New files to create | 1 | `tests/test_chapter_manifest_update.py` |
| New functions to add | 1 | `update_chapter_manifest()` in `scaffold.py` |
| Tests to write | 6 | See Tests First section |
| Dependencies | 2 | `scaffold.py` (host), `spawn_ceremonies.py` (consumer via scaffold) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single insertion point in scaffold_template() after file write |
| Risk of regression | Low | Fail-permissive: try/except wraps entire update, never raises |
| External dependencies | Low | Pure filesystem (read CHAPTER.md, regex replace, write back) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 15 min | High |
| Integration + CHECK | 10 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

```python
# scaffold.py:619-631 — end of scaffold_template()
    # Ensure output directory exists
    full_output_path = PROJECT_ROOT / output_path
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    # E2-212: Create subdirectories for work_item template
    config = TEMPLATE_CONFIG.get(template, {})
    if "subdirs" in config:
        _create_work_subdirs(full_output_path.parent, config["subdirs"])

    # Write output file
    full_output_path.write_text(content, encoding="utf-8")

    return str(full_output_path)
```

**Behavior:** Work item WORK.md is written to disk. No chapter manifest update occurs.

**Result:** Work items declare `chapter: CH-059` in frontmatter, but CH-059's CHAPTER.md work items table doesn't list them. Drift persists until manually caught (e.g., critique-agent in S406).

### Desired State

```python
# scaffold.py:619-637 — end of scaffold_template() with chapter auto-update
    # Ensure output directory exists
    full_output_path = PROJECT_ROOT / output_path
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    # E2-212: Create subdirectories for work_item template
    config = TEMPLATE_CONFIG.get(template, {})
    if "subdirs" in config:
        _create_work_subdirs(full_output_path.parent, config["subdirs"])

    # Write output file
    full_output_path.write_text(content, encoding="utf-8")

    # WORK-177: Auto-update chapter manifest if CHAPTER variable provided
    if template == "work_item" and variables.get("CHAPTER"):
        _try_update_chapter_manifest(
            backlog_id or "",
            title or "",
            variables.get("CHAPTER", ""),
            variables.get("TYPE", "implementation"),
        )

    return str(full_output_path)
```

**Behavior:** After writing work item, if `CHAPTER` variable was provided, auto-appends a row to the chapter's CHAPTER.md work items table. Fail-permissive — logged warning but never raises.

**Result:** Chapter manifests stay in sync with work items at creation time.

---

## Tests First (TDD)

### Test 1: Chapter manifest updated after work creation with CHAPTER variable
```python
def test_chapter_manifest_updated_on_scaffold(tmp_path):
    """When scaffold_template creates a work_item with CHAPTER variable,
    the chapter's CHAPTER.md work items table gets a new row."""
    # Setup: Create a CHAPTER.md with existing table
    # Action: scaffold_template("work_item", ..., variables={"CHAPTER": "CH-059"})
    # Assert: CHAPTER.md contains new row with work ID, title, status, type
```

### Test 2: Graceful failure when chapter file missing
```python
def test_chapter_manifest_missing_file_no_error(tmp_path):
    """When CHAPTER.md doesn't exist, scaffold_template still succeeds."""
    # Setup: No chapter file on disk
    # Action: scaffold_template("work_item", ..., variables={"CHAPTER": "CH-999"})
    # Assert: No exception raised, work item still created
```

### Test 3: No update when CHAPTER variable absent
```python
def test_no_chapter_update_without_variable(tmp_path):
    """When no CHAPTER variable, chapter manifest is not modified."""
    # Setup: Create a CHAPTER.md
    # Action: scaffold_template("work_item", ...) without CHAPTER
    # Assert: CHAPTER.md unchanged
```

### Test 4: Standalone update_chapter_manifest function
```python
def test_update_chapter_manifest_standalone(tmp_path):
    """update_chapter_manifest() can be called independently."""
    # Setup: Create a CHAPTER.md with table
    # Action: update_chapter_manifest("WORK-177", "Title", "CH-059", "implementation")
    # Assert: CHAPTER.md has new row
```

### Test 5: Duplicate row prevention
```python
def test_no_duplicate_row_on_second_call(tmp_path):
    """Calling update_chapter_manifest twice for same work ID doesn't duplicate."""
    # Setup: Create CHAPTER.md, call update once
    # Action: Call update again with same work ID
    # Assert: Only one row for that work ID
```

### Test 6: Table not found in existing chapter file
```python
def test_table_not_found_in_chapter_file(tmp_path):
    """When CHAPTER.md exists but has no '## Work Items' section, returns table_not_found."""
    # Setup: Create CHAPTER.md without a Work Items table
    # Action: update_chapter_manifest("WORK-180", "Title", "CH-099", "implementation")
    # Assert: result["updated"] == False, result["reason"] == "table_not_found"
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/lib/scaffold.py`
**Location:** After line 629 (after `full_output_path.write_text(content, encoding="utf-8")`)

**New function** `update_chapter_manifest()` added to `scaffold.py`:

```python
def update_chapter_manifest(
    work_id: str,
    title: str,
    chapter_id: str,
    work_type: str = "implementation",
    base_path: Optional[Path] = None,
) -> dict:
    """Update chapter CHAPTER.md work items table with new row. WORK-177.

    Locates the chapter file by glob pattern matching CH-{id}-* directory
    under the current epoch's arcs. Appends a row to the work items table
    if the work ID is not already present.

    Fail-permissive: returns result dict, never raises.

    Args:
        work_id: Work item ID (e.g., "WORK-177")
        title: Work item title
        chapter_id: Chapter ID (e.g., "CH-059")
        work_type: Work type (default: "implementation")
        base_path: Project root (injectable for testing)

    Returns:
        {"updated": True/False, "reason": str, "chapter_file": str|None}
    """
    root = base_path or PROJECT_ROOT
    # Glob for chapter directory: .claude/haios/epochs/*/arcs/*/chapters/{chapter_id}-*
    pattern = f".claude/haios/epochs/*/arcs/*/chapters/{chapter_id}-*/CHAPTER.md"
    matches = list(root.glob(pattern))
    if not matches:
        return {"updated": False, "reason": "chapter_file_not_found", "chapter_file": None}

    chapter_file = matches[0]  # First match (should be unique)
    content = chapter_file.read_text(encoding="utf-8")

    # Check for duplicate
    if f"| {work_id} |" in content:
        return {"updated": False, "reason": "already_present", "chapter_file": str(chapter_file)}

    # Find the work items table and append row before the next section
    # Table format: | ID | Title | Status | Type |
    new_row = f"| {work_id} | {title} | Backlog | {work_type} |"

    # Strategy: find last table row (starts with |) before the next --- or ## section
    lines = content.split("\n")
    insert_idx = None
    in_work_items = False
    for i, line in enumerate(lines):
        if line.strip().startswith("## Work Items"):
            in_work_items = True
            continue
        if in_work_items:
            if line.strip().startswith("|"):
                insert_idx = i  # Track last table row
            elif line.strip() == "---" or line.strip().startswith("##"):
                break  # Reached next section

    if insert_idx is None:
        return {"updated": False, "reason": "table_not_found", "chapter_file": str(chapter_file)}

    lines.insert(insert_idx + 1, new_row)
    chapter_file.write_text("\n".join(lines), encoding="utf-8")

    return {"updated": True, "reason": "row_added", "chapter_file": str(chapter_file)}
```

**Integration in `scaffold_template()`** — after line 629:

```python
    # WORK-177: Auto-update chapter manifest if CHAPTER variable provided
    if template == "work_item" and variables.get("CHAPTER"):
        _try_update_chapter_manifest(
            backlog_id or "",
            title or "",
            variables.get("CHAPTER", ""),
            variables.get("TYPE", "implementation"),
        )
```

**Fail-permissive wrapper (with observability — critique A5):**

```python
def _try_update_chapter_manifest(
    work_id: str, title: str, chapter_id: str, work_type: str
) -> None:
    """Fail-permissive wrapper for update_chapter_manifest. WORK-177.

    Never raises. Emits warnings.warn() on non-update or exception
    for operator observability (critique A5: fail-permissive != invisible).
    """
    import warnings
    try:
        result = update_chapter_manifest(work_id, title, chapter_id, work_type)
        if not result.get("updated"):
            warnings.warn(
                f"WORK-177: Chapter manifest not updated for {work_id}: {result.get('reason')}",
                stacklevel=2,
            )
    except Exception as exc:
        warnings.warn(
            f"WORK-177: Chapter manifest update failed (non-blocking): {exc}",
            stacklevel=2,
        )
```

### Call Chain Context

```
Agent or CLI
    |
    +-> scaffold_template("work_item", ..., variables={"CHAPTER": "CH-059"})
    |       |
    |       +-> write output file (line 629)
    |       +-> _try_update_chapter_manifest()        # <-- NEW (WORK-177)
    |               |
    |               +-> update_chapter_manifest()     # <-- NEW (WORK-177)
    |                       Reads CHAPTER.md
    |                       Appends table row
    |                       Returns result dict
    |
    +-> return path to created file

Also callable standalone:
    update_chapter_manifest("WORK-177", "Title", "CH-059", "implementation")
```

### Function/Component Signatures

```python
def update_chapter_manifest(
    work_id: str,
    title: str,
    chapter_id: str,
    work_type: str = "implementation",
    base_path: Optional[Path] = None,
) -> dict:
    """Update chapter CHAPTER.md work items table with new row. WORK-177.

    Args:
        work_id: Work item ID (e.g., "WORK-177")
        title: Work item title
        chapter_id: Chapter ID (e.g., "CH-059")
        work_type: Work type (default: "implementation")
        base_path: Project root (injectable for testing)

    Returns:
        {"updated": True/False, "reason": str, "chapter_file": str|None}
    """
```

### Behavior Logic

**Current Flow:**
```
scaffold_template() → write WORK.md → return path
                       (no chapter update)
```

**Fixed Flow:**
```
scaffold_template() → write WORK.md → CHAPTER var set?
                                        ├─ YES → _try_update_chapter_manifest()
                                        │          ├─ Chapter file found?
                                        │          │   ├─ YES → Already present?
                                        │          │   │         ├─ YES → skip (no-op)
                                        │          │   │         └─ NO  → append row
                                        │          │   └─ NO  → return (no error)
                                        │          └─ Exception? → swallow (fail-permissive)
                                        └─ NO  → skip
                                    → return path
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Integration point | `scaffold_template()` after file write | Central creation function — CLI, spawn, GovernanceLayer all flow through it. WorkEngine.create_work() is a separate path but lacks a chapter parameter and is used for low-level programmatic creation; out of scope for this work item (standalone `update_chapter_manifest()` covers after-the-fact use). |
| Chapter variable name | `CHAPTER` (passed via variables dict) | Consistent with existing variable convention (e.g., `TYPE`, `SPAWNED_BY`). Not a parameter because scaffold_template signature is stable. |
| Chapter file location | Glob pattern `epochs/*/arcs/*/chapters/{id}-*/CHAPTER.md` | Avoids hardcoding epoch version. Works across epoch transitions. |
| Fail-permissive wrapper | `_try_update_chapter_manifest()` with bare except | Work creation must never fail due to chapter manifest. AC-2 explicit requirement. |
| Standalone function | `update_chapter_manifest()` public API | Allows agents to call it after-the-fact when chapter is set via Edit (not scaffold). |
| Duplicate prevention | Check `| {work_id} |` in content | Simple string check. Idempotent — safe to call multiple times. |
| New row status | Always "Backlog" | Work items start at backlog queue position. Status can be updated later by StatusPropagator. |
| Test file | New `tests/test_chapter_manifest_update.py` | Keeps tests focused. Follows existing pattern (test_status_propagator.py is separate from status_propagator.py). |

### Input/Output Examples

**Before Fix (real data — S403 batch):**
```
Action: scaffold_template("work_item", backlog_id="WORK-176", title="Plan-Authoring-Cycle Subagent Delegation")
  Result: WORK.md created with chapter: CH-059 (set by agent later)
  Problem: CH-059/CHAPTER.md has no row for WORK-176
```

**After Fix (expected):**
```
Action: scaffold_template("work_item", backlog_id="WORK-176", title="...", variables={"CHAPTER": "CH-059", "TYPE": "implementation"})
  Result: WORK.md created AND CH-059/CHAPTER.md gets new row:
    | WORK-176 | Plan-Authoring-Cycle Subagent Delegation | Backlog | implementation |
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Chapter file doesn't exist | Return `{"updated": False, "reason": "chapter_file_not_found"}` | Test 2 |
| Work ID already in table | Return `{"updated": False, "reason": "already_present"}` — no duplicate | Test 5 |
| No CHAPTER variable | Skip entirely (no-op) | Test 3 |
| CHAPTER.md has no work items table | Return `{"updated": False, "reason": "table_not_found"}` | Test 6 |
| Exception during file I/O | Swallowed by `_try_update_chapter_manifest()` | Test 2 covers concept |
| Non-work_item template | Skip (only fires for `template == "work_item"`) | Implicit |

### Open Questions

None. All design decisions resolved during analysis.

---

## Open Decisions (MUST resolve before implementation)

No operator decisions exist in WORK-177's frontmatter. None required.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | - | - | No operator decisions in work item |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_chapter_manifest_update.py` with 6 tests
- [ ] Verify all tests fail (red) — function doesn't exist yet

### Step 2: Implement `update_chapter_manifest()` function
- [ ] Add `update_chapter_manifest()` to `scaffold.py`
- [ ] Add `_try_update_chapter_manifest()` wrapper
- [ ] Tests 1, 4, 5 pass (green)

### Step 3: Integrate into `scaffold_template()`
- [ ] Add chapter auto-update call after line 629 in `scaffold_template()`
- [ ] Test 1, 3 pass (green) via scaffold integration path

### Step 4: Integration Verification
- [ ] All 6 tests pass
- [ ] Run `pytest tests/test_lib_scaffold.py -v` — no regressions
- [ ] Run full test suite — no regressions

### Step 5: Consumer Verification
- [ ] `spawn_ceremonies.py` — verify CHAPTER can be passed via variables (document for future use)
- [ ] No migration/rename needed — this is additive

---

## Verification

- [ ] Tests pass
- [ ] No regressions in existing scaffold tests
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Chapter file glob matches multiple epochs | Low | First match wins; only active epoch has active chapters. Epochs are sequential. |
| CHAPTER.md format changes in future | Low | Regex-free approach (line scanning). Format is stable (established E2.8). |
| Performance: glob on every work_item scaffold | Low | Only triggers when CHAPTER variable is set. Glob is fast for known path patterns. |
| Consumers don't pass CHAPTER variable yet | Medium | Standalone `update_chapter_manifest()` available for after-the-fact calls. Document in CLAUDE.md. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 407 | 2026-02-19 | - | Plan authored | PLAN phase |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-177/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Auto-update function for chapter manifest on work creation (fail-permissive) | [ ] | `update_chapter_manifest()` exists in scaffold.py |
| Integration into scaffold or WorkEngine create path | [ ] | `_try_update_chapter_manifest()` called in scaffold_template() |
| Tests verifying chapter manifest updated after work creation | [ ] | test_chapter_manifest_updated_on_scaffold passes |
| Tests verifying graceful failure when chapter file missing | [ ] | test_chapter_manifest_missing_file_no_error passes |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/scaffold.py` | `update_chapter_manifest()` and `_try_update_chapter_manifest()` added, integration in scaffold_template() | [ ] | |
| `tests/test_chapter_manifest_update.py` | 6 tests, all passing | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_chapter_manifest_update.py -v
# Expected: 6 tests passed
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
- [ ] **Runtime consumer exists** (scaffold_template calls _try_update_chapter_manifest)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/lib/scaffold.py (scaffold_template — integration point)
- @.claude/haios/lib/status_propagator.py (sibling pattern — chapter file updates)
- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-059-CeremonyAutomation/CHAPTER.md (example chapter)
- @docs/work/active/WORK-177/WORK.md (work item)
- Memory: 86887, 86893 (retro-extract FEATURE-1)

---
