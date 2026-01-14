---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-141
title: "Backlog ID Uniqueness Gate"
author: Hephaestus
lifecycle_phase: done
session: 103
version: "1.5"
generated: 2025-12-23
last_updated: 2025-12-23T12:39:59
---
# Implementation Plan: Backlog ID Uniqueness Gate

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

When creating or editing a file with a `backlog_id:` field, the PreToolUse hook will verify no other document already uses that ID, preventing duplicate IDs that cause confusion and broken references.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/pre_tool_use.py` |
| Lines of code affected | ~40 | New function `_check_backlog_id_uniqueness()` |
| New files to create | 0 | Adding to existing hook handler |
| Tests to write | 4 | Uniqueness detection, allow existing, skip non-backlog, allow edits |
| Dependencies | 0 | Uses existing Path/re, adds subprocess for grep |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single check in existing hook |
| Risk of regression | Low | Additive change, doesn't modify existing checks |
| External dependencies | Low | File system grep only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 10 min | High |
| Implementation | 15 min | High |
| Integration test | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/pre_tool_use.py:40-61 - handle() function
    # Check Write/Edit for governance
    if tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")

        # Plan validation (E2-015)
        result = _check_plan_validation(file_path, content)
        if result:
            return result

        # Memory reference warning (E2-021)
        result = _check_memory_refs(file_path, new_string or content)
        if result:
            return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
        if result:
            return result

    return None  # Allow all other tools
```

**Behavior:** No check for duplicate backlog_id values across documents.

**Result:** Two files can have the same backlog_id (e.g., two INV-011 files existed - command-skill and work-item-as-file).

### Desired State

```python
# .claude/hooks/hooks/pre_tool_use.py - add after memory refs check
        # Memory reference warning (E2-021)
        result = _check_memory_refs(file_path, new_string or content)
        if result:
            return result

        # Backlog ID uniqueness (E2-141)
        result = _check_backlog_id_uniqueness(file_path, content)
        if result:
            return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
        if result:
            return result
```

**Behavior:** Before allowing file creation, extracts `backlog_id:` from content and greps docs/ for existing files with same ID.

**Result:** Duplicate IDs blocked at write time with message showing existing file path.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Block Duplicate Backlog ID
```python
def test_blocks_duplicate_backlog_id(tmp_path, monkeypatch):
    """When backlog_id already exists in another file, block creation."""
    from pre_tool_use import _check_backlog_id_uniqueness

    # Setup: Create existing file with backlog_id
    docs_dir = tmp_path / "docs" / "plans"
    docs_dir.mkdir(parents=True)
    existing = docs_dir / "PLAN-E2-141-existing.md"
    existing.write_text("---\nbacklog_id: E2-141\n---\n# Content")

    # Mock cwd to tmp_path
    monkeypatch.chdir(tmp_path)

    # Try to create new file with same ID
    new_file = str(docs_dir / "PLAN-E2-141-new.md")
    content = "---\nbacklog_id: E2-141\n---\n# New Content"

    result = _check_backlog_id_uniqueness(new_file, content)

    assert result is not None
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "E2-141" in result["hookSpecificOutput"]["permissionDecisionReason"]
```

### Test 2: Allow Unique Backlog ID
```python
def test_allows_unique_backlog_id(tmp_path, monkeypatch):
    """When backlog_id is new, allow creation."""
    from pre_tool_use import _check_backlog_id_uniqueness

    docs_dir = tmp_path / "docs" / "plans"
    docs_dir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path)

    new_file = str(docs_dir / "PLAN-E2-999-new.md")
    content = "---\nbacklog_id: E2-999\n---\n# Content"

    result = _check_backlog_id_uniqueness(new_file, content)

    assert result is None  # Allow
```

### Test 3: Skip Files Without Backlog ID
```python
def test_skips_files_without_backlog_id(tmp_path, monkeypatch):
    """Files without backlog_id field should pass through."""
    from pre_tool_use import _check_backlog_id_uniqueness

    monkeypatch.chdir(tmp_path)

    result = _check_backlog_id_uniqueness(
        "docs/random.md",
        "# Just some content\nNo frontmatter here"
    )

    assert result is None  # Allow
```

### Test 4: Allow Edits to Same File
```python
def test_allows_edits_to_same_file(tmp_path, monkeypatch):
    """Editing an existing file with its own ID should be allowed."""
    from pre_tool_use import _check_backlog_id_uniqueness

    docs_dir = tmp_path / "docs" / "plans"
    docs_dir.mkdir(parents=True)
    existing = docs_dir / "PLAN-E2-141-existing.md"
    existing.write_text("---\nbacklog_id: E2-141\n---\n# Content")

    monkeypatch.chdir(tmp_path)

    # Edit the SAME file (not a new file)
    result = _check_backlog_id_uniqueness(
        str(existing),  # Same file path
        "---\nbacklog_id: E2-141\n---\n# Updated Content"
    )

    assert result is None  # Allow - editing same file
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

**File:** `.claude/hooks/hooks/pre_tool_use.py`
**Location:** Lines 52-56, after `_check_memory_refs()` call

**Current Code:**
```python
# .claude/hooks/hooks/pre_tool_use.py:52-60
        # Memory reference warning (E2-021)
        result = _check_memory_refs(file_path, new_string or content)
        if result:
            return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
```

**Changed Code:**
```python
# .claude/hooks/hooks/pre_tool_use.py - add check after memory refs
        # Memory reference warning (E2-021)
        result = _check_memory_refs(file_path, new_string or content)
        if result:
            return result

        # Backlog ID uniqueness (E2-141)
        result = _check_backlog_id_uniqueness(file_path, content)
        if result:
            return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
```

**Diff:**
```diff
         # Memory reference warning (E2-021)
         result = _check_memory_refs(file_path, new_string or content)
         if result:
             return result

+        # Backlog ID uniqueness (E2-141)
+        result = _check_backlog_id_uniqueness(file_path, content)
+        if result:
+            return result
+
         # Path governance - only for new files
         result = _check_path_governance(file_path)
```

### Call Chain Context

```
Claude Code PreToolUse event
    |
    +-> hook_dispatcher.py
    |       Parses JSON, routes to handler
    |
    +-> pre_tool_use.py:handle()
            |
            +-> _check_sql_governance()       # Bash
            +-> _check_plan_validation()      # Write/Edit
            +-> _check_memory_refs()          # Write/Edit
            +-> _check_backlog_id_uniqueness()   # <-- NEW
            +-> _check_path_governance()      # Write/Edit
```

### Function/Component Signatures

```python
def _check_backlog_id_uniqueness(file_path: str, content: str) -> Optional[dict]:
    """
    Block creation of files with duplicate backlog_id values (E2-141).

    Extracts backlog_id from content, greps docs/ for existing files with
    same ID, blocks if duplicate found (excluding the file being edited).

    Args:
        file_path: Path to file being created/edited
        content: Content being written (contains frontmatter with backlog_id)

    Returns:
        None: Allow operation (no duplicate found)
        dict: Deny with hookSpecificOutput showing existing file

    Side effects:
        - Runs grep subprocess to find existing files
    """
```

### Behavior Logic

**Trigger Condition:**
```
Write/Edit to file → content has "backlog_id: XXX"?
                      ├─ NO  → return None (skip check)
                      └─ YES → Continue to uniqueness check
```

**Uniqueness Check Flow:**
```
Extract backlog_id from content (regex)
    → Grep docs/ for "backlog_id:\s*{id}"
    → Filter out the current file_path from results
    → Any remaining matches?
        ├─ NO  → return None (allow)
        └─ YES → return _deny("Duplicate: {id} exists in {path}")
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Use grep not Glob+Read | subprocess grep | Faster, single operation, matches pattern exactly |
| Check content not file | Extract from content arg | File may not exist yet (Write) |
| Exclude current file | Filter by path | Allows edits to existing files |
| Scope to docs/ only | docs/ directory | All governed documents are there, avoids checking tests/archive |

### Input/Output Examples

**Before Fix (with real data from Session 101):**
```
Write INVESTIGATION-INV-011-work-item-as-file.md:
  backlog_id: INV-011

  Result: File created ✓

But INVESTIGATION-INV-011-command-skill.md already exists:
  backlog_id: INV-011

  Problem: TWO files with same ID - confusion, broken references
```

**After Fix (expected):**
```
Write INVESTIGATION-INV-011-work-item-as-file.md:
  backlog_id: INV-011

  PreToolUse check:
    - Extract: INV-011
    - Grep: docs/**/*backlog_id*INV-011*
    - Found: INVESTIGATION-INV-011-command-skill.md

  Result: BLOCKED
  Message: "Duplicate backlog_id: INV-011 already exists in
            docs/investigations/INVESTIGATION-INV-011-command-skill.md"
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No backlog_id in content | Return None (skip check) | Test 3 |
| Editing same file | Filter out current path | Test 4 |
| Multiple matches | Show first match in error | Implicit |
| backlog_id in code block | Could false positive | Acceptable - rare edge case |
| Empty content | Return None | Implicit |

### Open Questions

**Q: Should we check backlog_ids (plural list) as well?**

TBD - Currently checkpoints use `backlog_ids: [E2-001, E2-002]` format. These are references, not ownership. Only `backlog_id:` (singular) indicates the document's own ID. Skip for now, monitor.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_backlog_id_uniqueness.py` with 4 tests
- [ ] Verify all tests fail (red) - function doesn't exist yet

### Step 2: Add _check_backlog_id_uniqueness Function
- [ ] Add function to `.claude/hooks/hooks/pre_tool_use.py`
- [ ] Implement: extract backlog_id from content via regex
- [ ] Implement: grep docs/ for existing files with same ID
- [ ] Implement: filter out current file path
- [ ] Implement: return deny if duplicates found
- [ ] Tests 1, 2, 3, 4 pass (green)

### Step 3: Wire Into handle()
- [ ] Add call after `_check_memory_refs()` in `handle()` function
- [ ] Update module docstring with "5. Backlog ID uniqueness (E2-141)"

### Step 4: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite: `pytest tests/ -v`

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/hooks/README.md` - add E2-141 to PreToolUse section
- [ ] No new directories created, no parent README updates needed

### Step 6: Consumer Verification
**SKIPPED:** Not a migration/refactor - adding new functionality to existing file

---

## Verification

- [ ] Tests pass: `pytest tests/test_backlog_id_uniqueness.py -v`
- [ ] Full suite passes: `pytest tests/ -v`
- [ ] **MUST:** `.claude/hooks/README.md` updated

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Grep subprocess fails | Low | Catch exception, log, allow operation |
| False positive from code block | Low | Acceptable - rare, can refine pattern later |
| Performance on large docs/ | Low | Grep is fast, only runs on Write/Edit |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 103 | 2025-12-23 | - | Plan created | Ready for implementation |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/pre_tool_use.py` | `_check_backlog_id_uniqueness()` exists, wired in handle() | [ ] | |
| `tests/test_backlog_id_uniqueness.py` | 4 tests exist and pass | [ ] | |
| `.claude/hooks/README.md` | E2-141 mentioned in PreToolUse section | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_backlog_id_uniqueness.py -v
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
- [ ] **MUST:** `.claude/hooks/README.md` updated
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **Spawned by:** INV-022 (Work-Cycle-DAG Unified Architecture)
- **Related:** Session 101 checkpoint (ID collision discovery)
- **Pattern:** L3 Gate (prevent wrong action before it happens)
- **Similar:** E2-140 (PostToolUse sync pattern)

---
