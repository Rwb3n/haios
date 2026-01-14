---
template: implementation_plan
status: complete
date: 2025-12-29
backlog_id: E2-163
title: Work File Integrity Validation
author: Hephaestus
lifecycle_phase: plan
session: 146
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-29T20:34:58'
---
# Implementation Plan: Work File Integrity Validation

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

Add work file integrity validation to `/validate` command that checks `cycle_docs` matches `documents` list and `node_history` has consistent timestamps with no gaps.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/validate.py` |
| Lines of code affected | ~50 | New validation functions added |
| New files to create | 1 | `tests/test_work_file_integrity.py` |
| Tests to write | 6 | 3 for cycle_docs, 3 for node_history |
| Dependencies | 1 | `/validate` command uses validate.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single module, one command consumer |
| Risk of regression | Low | Adding new validation, not changing existing |
| External dependencies | Low | Pure Python, no external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement validation functions | 20 min | High |
| Integration with validate_template | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/validate.py:132-143 - work_item validation rules
"work_item": {
    "required_fields": ["template", "status", "id", "title", "current_node"],
    "optional_fields": [
        "owner", "created", "closed", "milestone", "priority", "effort",
        "category", "spawned_by", "spawned_by_investigation", "blocked_by",
        "blocks", "enables", "related", "node_history", "cycle_docs",
        "memory_refs", "documents", "version",
    ],
    "allowed_status": ["active", "blocked", "complete", "archived"],
    "expected_sections": ["Context", "Current State", "Deliverables"],
},
```

**Behavior:** Validates work_item templates for required fields, status values, and section presence only.

**Result:** No validation of work file integrity - cycle_docs can be empty while documents.plans has entries, node_history can have gaps or out-of-order timestamps.

### Desired State

```python
# .claude/lib/validate.py - new validation functions
def validate_cycle_docs_consistency(metadata: dict) -> list[str]:
    """Check cycle_docs matches documents list."""
    errors = []
    cycle_docs = metadata.get("cycle_docs", {})
    documents = metadata.get("documents", {})

    # If documents.plans exists, cycle_docs should have plan_id
    if documents.get("plans") and not cycle_docs.get("plan_id"):
        errors.append("documents.plans has entries but cycle_docs.plan_id missing")
    return errors

def validate_node_history_integrity(metadata: dict) -> list[str]:
    """Check node_history has consistent timestamps."""
    errors = []
    node_history = metadata.get("node_history", [])

    for i, entry in enumerate(node_history):
        # Check required fields
        if "node" not in entry or "entered" not in entry:
            errors.append(f"node_history[{i}] missing required fields")
        # Check timestamp ordering
        if i > 0 and prev_entered and entry.get("entered"):
            if entry["entered"] < prev_entered:
                errors.append(f"node_history[{i}] has out-of-order timestamp")
    return errors
```

**Behavior:** Validates work file internal consistency - cycle_docs reflects actual documents, node_history is temporally ordered.

**Result:** Catches drift between frontmatter sections, prevents invalid work file state.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: cycle_docs Missing plan_id When plans Exist
```python
def test_cycle_docs_missing_plan_id():
    """Detect cycle_docs without plan_id when documents.plans has entries."""
    metadata = {
        "documents": {"plans": ["PLAN.md"]},
        "cycle_docs": {}  # Missing plan_id
    }
    errors = validate_cycle_docs_consistency(metadata)
    assert "cycle_docs.plan_id missing" in errors[0]
```

### Test 2: cycle_docs Consistent With documents
```python
def test_cycle_docs_consistent():
    """Pass when cycle_docs matches documents."""
    metadata = {
        "documents": {"plans": ["PLAN.md"]},
        "cycle_docs": {"plan_id": "PLAN"}
    }
    errors = validate_cycle_docs_consistency(metadata)
    assert errors == []
```

### Test 3: node_history Missing Required Fields
```python
def test_node_history_missing_fields():
    """Detect node_history entry without node or entered."""
    metadata = {
        "node_history": [{"node": "backlog"}]  # Missing entered
    }
    errors = validate_node_history_integrity(metadata)
    assert "missing required fields" in errors[0]
```

### Test 4: node_history Out-of-Order Timestamps
```python
def test_node_history_out_of_order():
    """Detect timestamps that go backward."""
    metadata = {
        "node_history": [
            {"node": "backlog", "entered": "2025-12-29T10:00:00", "exited": "2025-12-29T11:00:00"},
            {"node": "plan", "entered": "2025-12-29T09:00:00"}  # Before previous!
        ]
    }
    errors = validate_node_history_integrity(metadata)
    assert "out-of-order timestamp" in errors[0]
```

### Test 5: node_history Consistent
```python
def test_node_history_consistent():
    """Pass when timestamps are in order."""
    metadata = {
        "node_history": [
            {"node": "backlog", "entered": "2025-12-29T09:00:00", "exited": "2025-12-29T10:00:00"},
            {"node": "plan", "entered": "2025-12-29T10:00:00", "exited": None}
        ]
    }
    errors = validate_node_history_integrity(metadata)
    assert errors == []
```

### Test 6: Integration With validate_template
```python
def test_validate_template_includes_work_file_checks(tmp_path):
    """Work file validation includes integrity checks."""
    work_file = tmp_path / "WORK.md"
    work_file.write_text('''---
template: work_item
id: TEST-001
title: "Test Work"
status: active
current_node: backlog
documents:
  plans: ["PLAN.md"]
cycle_docs: {}
node_history: []
---
# WORK-TEST-001: Test Work

@docs/README.md
@docs/epistemic_state.md

## Context
Test context.

## Current State
Test state.

## Deliverables
- [ ] Test deliverable
''')
    result = validate_template(str(work_file))
    assert not result["is_valid"]
    assert any("cycle_docs" in e for e in result["errors"])
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

**File:** `.claude/lib/validate.py`
**Location:** After line 361 (after `check_section_coverage`)

**New Functions to Add:**
```python
def validate_cycle_docs_consistency(metadata: dict) -> list[str]:
    """Validate cycle_docs matches documents list.

    Args:
        metadata: Parsed YAML frontmatter dict

    Returns:
        List of error messages, empty if valid.
    """
    errors = []
    cycle_docs = metadata.get("cycle_docs", {})
    documents = metadata.get("documents", {})

    # Check: If documents.plans exists, cycle_docs should have plan_id
    if documents.get("plans") and not cycle_docs.get("plan_id"):
        errors.append("documents.plans has entries but cycle_docs.plan_id missing")

    # Check: If documents.investigations exists, cycle_docs should have investigation_id
    if documents.get("investigations") and not cycle_docs.get("investigation_id"):
        errors.append("documents.investigations has entries but cycle_docs.investigation_id missing")

    return errors


def validate_node_history_integrity(metadata: dict) -> list[str]:
    """Validate node_history has consistent timestamps.

    Args:
        metadata: Parsed YAML frontmatter dict

    Returns:
        List of error messages, empty if valid.
    """
    errors = []
    node_history = metadata.get("node_history", [])

    prev_entered = None
    for i, entry in enumerate(node_history):
        # Check required fields
        if "node" not in entry:
            errors.append(f"node_history[{i}] missing 'node' field")
        if "entered" not in entry:
            errors.append(f"node_history[{i}] missing 'entered' field")
            continue  # Can't check ordering without entered

        current_entered = entry.get("entered")

        # Check timestamp ordering (must be >= previous)
        if prev_entered and current_entered:
            if current_entered < prev_entered:
                errors.append(f"node_history[{i}] has out-of-order timestamp ({current_entered} < {prev_entered})")

        prev_entered = current_entered

    return errors
```

**Integration Point in validate_template():**
```python
# .claude/lib/validate.py - add after section_coverage check (~line 514)
    # Work file integrity validation (E2-163)
    if template_type == "work_item":
        cycle_docs_errors = validate_cycle_docs_consistency(metadata)
        if cycle_docs_errors:
            result["is_valid"] = False
            for err in cycle_docs_errors:
                result["errors"].append(f"Work file integrity: {err}")

        node_history_errors = validate_node_history_integrity(metadata)
        if node_history_errors:
            result["is_valid"] = False
            for err in node_history_errors:
                result["errors"].append(f"Work file integrity: {err}")
```

### Call Chain Context

```
/validate command (or just validate)
    |
    +-> validate_template(file_path)
    |       |
    |       +-> extract_yaml_header()
    |       +-> parse_yaml()
    |       +-> check_section_coverage()
    |       +-> validate_cycle_docs_consistency()    # <-- NEW
    |       +-> validate_node_history_integrity()    # <-- NEW
    |       Returns: dict with is_valid, errors, warnings
```

### Function/Component Signatures

```python
def validate_cycle_docs_consistency(metadata: dict) -> list[str]:
    """Validate cycle_docs matches documents list.

    Checks:
    - If documents.plans has entries, cycle_docs.plan_id should exist
    - If documents.investigations has entries, cycle_docs.investigation_id should exist

    Args:
        metadata: Parsed YAML frontmatter dict with cycle_docs and documents keys

    Returns:
        List of error messages, empty if valid.
    """

def validate_node_history_integrity(metadata: dict) -> list[str]:
    """Validate node_history has consistent timestamps.

    Checks:
    - Each entry has 'node' and 'entered' fields
    - Timestamps are monotonically increasing (entered[i] >= entered[i-1])

    Args:
        metadata: Parsed YAML frontmatter dict with node_history key

    Returns:
        List of error messages, empty if valid.
    """
```

### Behavior Logic

**Current Flow:**
```
validate_template() → check required fields → check status → check sections → DONE
                                                                             (no integrity check)
```

**Fixed Flow:**
```
validate_template() → check required fields → check status → check sections
                                                                    |
                                            [if work_item template?]
                                              ├─ YES → validate_cycle_docs_consistency()
                                              |        validate_node_history_integrity()
                                              |        add any errors to result
                                              └─ NO  → skip
                                                                    |
                                                                  DONE
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Where to add validation | In validate_template() after section checks | Keeps all validation in one pass, consistent with existing pattern |
| Separate functions | Two functions, one per check | Easier testing, clearer error attribution |
| Error format | Prefix with "Work file integrity:" | Distinguishes from schema validation errors |
| Timestamp comparison | String comparison | ISO8601 strings sort correctly, no datetime parsing needed |

### Input/Output Examples

**Before Fix (with real data):**
```
validate_template("docs/work/active/E2-163/WORK.md")
  Returns: {"is_valid": True, ...}
  Problem: No check that documents.plans matches cycle_docs
```

**After Fix (expected):**
```
# If E2-163 had plans but empty cycle_docs:
validate_template("docs/work/active/E2-163/WORK.md")
  Returns: {
    "is_valid": False,
    "errors": ["Work file integrity: documents.plans has entries but cycle_docs.plan_id missing"]
  }
```

**Real Example with Current Data:**
```
Current work file E2-163:
  documents:
    plans: []  # Empty - no plan yet
  cycle_docs: {}  # Empty - consistent

After this plan is linked:
  documents:
    plans: ["PLAN.md"]
  cycle_docs: {"plan_id": "PLAN"}  # Would need to match

If cycle_docs not updated, validation would fail.
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty node_history | Valid (new work item) | Implicit - no errors returned |
| Empty documents | Valid (no plans yet) | Implicit - no errors returned |
| null timestamps | Skip ordering check for that entry | Test 3 covers missing fields |
| Single node_history entry | Valid (no ordering to check) | Implicit |

### Open Questions

**Q: Should we validate that node_history's last entry has exited: null?**

The last entry should have `exited: null` since it's the current node. However, this could be too strict for archived items. Decision: Skip for now - focus on timestamp ordering which catches most issues.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_work_file_integrity.py`
- [ ] Add Test 1-5 (unit tests for validation functions)
- [ ] Add Test 6 (integration test)
- [ ] Run `pytest tests/test_work_file_integrity.py` - all 6 tests FAIL (red)

### Step 2: Implement validate_cycle_docs_consistency
- [ ] Add `validate_cycle_docs_consistency()` function to `.claude/lib/validate.py` after line 361
- [ ] Tests 1, 2 pass (green)

### Step 3: Implement validate_node_history_integrity
- [ ] Add `validate_node_history_integrity()` function to `.claude/lib/validate.py`
- [ ] Tests 3, 4, 5 pass (green)

### Step 4: Integrate With validate_template
- [ ] Add work_item integrity checks to `validate_template()` around line 514
- [ ] Test 6 passes (green)
- [ ] All 6 tests pass

### Step 5: Full Test Suite Verification
- [ ] Run `pytest tests/ -v` - no regressions
- [ ] Run `just validate docs/work/active/E2-163/WORK.md` - passes (empty cycle_docs is OK)

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` to mention new validation functions
- [ ] **SKIPPED:** No parent directory structure changed

### Step 7: Consumer Verification
**SKIPPED:** Not a migration - adding new functionality, not moving/renaming existing code.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing work files fail validation | Medium | Validation is additive - only fails if integrity issues exist |
| False positives on edge cases | Low | Tests cover edge cases; empty values are valid |
| YAML parsing doesn't capture nested dicts | Medium | validate.py uses simple parser; need to verify dict handling |

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
| `.claude/lib/validate.py` | Has `validate_cycle_docs_consistency()` and `validate_node_history_integrity()` | [ ] | |
| `tests/test_work_file_integrity.py` | Has 6 tests, all passing | [ ] | |
| `.claude/lib/README.md` | **MUST:** Mentions new validation functions | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_work_file_integrity.py -v
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
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- ADR-033: Work Item Lifecycle Governance
- INV-022: Work File Schema v2 (defines node_history, cycle_docs)
- E2-155: Exit Gates (related validation work)
- Session 145: Checkpoint for preceding work

---
