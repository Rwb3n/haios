---
template: implementation_plan
status: complete
date: 2025-12-24
backlog_id: E2-160
title: "Work File Prerequisite Gate"
author: Hephaestus
lifecycle_phase: plan
session: 109
version: "1.5"
generated: 2025-12-24
last_updated: 2025-12-24T10:11:57
spawned_by: INVESTIGATION-E2-160
---
# Implementation Plan: Work File Prerequisite Gate

@docs/README.md
@docs/epistemic_state.md
@docs/investigations/INVESTIGATION-E2-160-work-file-prerequisite-gate-design.md

---

## Goal

L3 gate in scaffold.py prevents creation of investigations/plans without a corresponding work file, enforcing ADR-039 work-item-as-file architecture.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/scaffold.py` |
| Lines of code affected | ~15 | Add helper + check |
| New files to create | 0 | - |
| Tests to write | 4 | test_lib_scaffold.py |
| Dependencies | 0 | Glob only (already imported) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single file change |
| Risk of regression | Low | Existing tests cover scaffold |
| External dependencies | None | - |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Implementation | 10 min | High |
| Tests | 10 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/lib/scaffold.py:320-324`

```python
    # Ensure output directory exists
    full_output_path = PROJECT_ROOT / output_path
    full_output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output file
    full_output_path.write_text(content, encoding="utf-8")
```

**Behavior:** Any template can be scaffolded without checking prerequisites.

**Result:** Orphaned investigations/plans created without work files.

### Desired State

```python
    # Check work file prerequisite for gated templates (E2-160)
    if template in WORK_FILE_REQUIRED_TEMPLATES and backlog_id:
        if not _work_file_exists(backlog_id):
            raise ValueError(
                f"Work file required. Run '/new-work {backlog_id} \"{title}\"' first."
            )

    # Ensure output directory exists
    full_output_path = PROJECT_ROOT / output_path
    ...
```

**Behavior:** investigation/implementation_plan templates require work file.

**Result:** L3 enforcement - no orphaned documents.

---

## Tests First (TDD)

### Test 1: Work file exists - allows scaffold
```python
def test_scaffold_investigation_with_work_file_succeeds(tmp_path, monkeypatch):
    """Investigation scaffold succeeds when work file exists."""
    # Create work file
    work_dir = tmp_path / "docs/work/active"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK-E2-999-test.md").write_text("---\nid: E2-999\n---")
    # Scaffold should succeed
    result = scaffold_template("investigation", backlog_id="E2-999", title="Test")
    assert "INVESTIGATION-E2-999" in result
```

### Test 2: Work file missing - raises ValueError
```python
def test_scaffold_investigation_without_work_file_raises(tmp_path, monkeypatch):
    """Investigation scaffold fails when no work file exists."""
    with pytest.raises(ValueError, match="Work file required"):
        scaffold_template("investigation", backlog_id="E2-999", title="Test")
```

### Test 3: Work item template not gated
```python
def test_scaffold_work_item_not_gated(tmp_path, monkeypatch):
    """Work item template should not require existing work file."""
    result = scaffold_template("work_item", backlog_id="E2-999", title="Test")
    assert "WORK-E2-999" in result
```

### Test 4: Checkpoint not gated
```python
def test_scaffold_checkpoint_not_gated(tmp_path, monkeypatch):
    """Checkpoint template should not require work file."""
    result = scaffold_template("checkpoint", backlog_id="110", title="Test")
    assert "SESSION-110" in result
```

---

## Detailed Design

### Code Changes

**File:** `.claude/lib/scaffold.py`

**Add constant (after line 26):**
```python
# Templates that require work file to exist first (E2-160)
WORK_FILE_REQUIRED_TEMPLATES = {"investigation", "implementation_plan"}
```

**Add helper function (after line 66):**
```python
def _work_file_exists(backlog_id: str) -> bool:
    """Check if work file exists for backlog_id."""
    work_dir = PROJECT_ROOT / "docs" / "work" / "active"
    pattern = f"WORK-{backlog_id}-*.md"
    return len(list(work_dir.glob(pattern))) > 0
```

**Add gate check (before line 320, in scaffold_template()):**
```python
    # Check work file prerequisite for gated templates (E2-160)
    if template in WORK_FILE_REQUIRED_TEMPLATES and backlog_id:
        if not _work_file_exists(backlog_id):
            raise ValueError(
                f"Work file required. Run '/new-work {backlog_id} \"{title}\"' first."
            )
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Gate location | scaffold.py | Single enforcement point for all /new-* commands |
| Gated templates | investigation, implementation_plan | These require lifecycle tracking |
| Error type | ValueError | Standard Python exception, clear message |
| Non-gated | checkpoint, report, ADR, work_item | These don't require work files |

### Behavior Flow

```
scaffold_template(template="investigation", backlog_id="E2-160")
    │
    ├─ Is template in WORK_FILE_REQUIRED_TEMPLATES?
    │   └─ Yes
    │       ├─ Does docs/work/active/WORK-E2-160-*.md exist?
    │       │   ├─ Yes → Continue to write file
    │       │   └─ No → Raise ValueError
    │
    └─ Write file
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No backlog_id provided | Skip check (allow) | Test 3, 4 |
| Work file in blocked/ not active/ | Gate checks active/ only | By design |
| Template not in gated list | Skip check (allow) | Test 3, 4 |

---

## Implementation Steps

### Step 1: Write Tests
- [ ] Add 4 tests to `tests/test_lib_scaffold.py`
- [ ] Run tests - verify they fail (RED)

### Step 2: Add Gate Logic
- [ ] Add WORK_FILE_REQUIRED_TEMPLATES constant
- [ ] Add _work_file_exists() helper
- [ ] Add gate check before write in scaffold_template()
- [ ] Run tests - verify they pass (GREEN)

### Step 3: Verify Full Suite
- [ ] Run `pytest tests/` - no regressions
- [ ] Demo: Try `/new-investigation E2-999 "test"` without work file - should fail

### Step 4: Consumer Verification
**SKIPPED:** No consumers to update - this adds new behavior, doesn't change existing.

---

## Verification

- [ ] 4 new tests pass
- [ ] Full test suite passes (no regressions)
- [ ] Demo verified (gate blocks orphan creation)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaks existing workflows | Low | Only gates investigation/plan, not checkpoint/ADR |
| Error message unclear | Low | Message includes exact command to run |

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
| `[path/to/implementation.py]` | [Function X exists, does Y] | [ ] | |
| `[tests/test_file.py]` | [Tests exist and cover cases] | [ ] | |
| `[modified_dir/README.md]` | **MUST:** Reflects actual files present | [ ] | |
| `[parent_dir/README.md]` | **MUST:** Updated if structure changed | [ ] | |
| `Grep: old_path\|OldName` | **MUST:** Zero stale references (migrations only) | [ ] | |

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
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- [Related ADR or spec]
- [Related checkpoint]

---
