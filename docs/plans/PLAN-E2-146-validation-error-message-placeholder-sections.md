---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-146
title: "Validation Error Message Placeholder Sections"
author: Hephaestus
lifecycle_phase: plan
session: 104
spawned_by: E2-145
version: "1.5"
generated: 2025-12-23
last_updated: 2025-12-23T14:01:58
---
# Implementation Plan: Validation Error Message Placeholder Sections

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4) -->

---

## Goal

When validation fails due to placeholder-only sections, the error message will clearly identify which sections contain placeholder content instead of showing an empty "Missing sections:" message.

---

## Effort Estimation (Ground Truth)

This is a bug fix discovered during E2-145 implementation in Session 104.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/validate.py` |
| Lines of code affected | ~5 | Error message construction |
| New files to create | 0 | - |
| Tests to write | 1 | Test error message includes placeholder sections |
| Dependencies | 0 | Self-contained fix |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single function fix |
| Risk of regression | Low | Existing tests verify missing_sections still works |
| External dependencies | None | Pure string formatting |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write test | 5 min | High |
| Fix error message | 5 min | High |
| **Total** | 10 min | High |

---

## Current State vs Desired State

This section documents the bug in error message construction discovered during E2-145.

### Current State

**.claude/lib/validate.py (lines 490-496):**
```python
    if not section_result["all_covered"]:
        result["is_valid"] = False
        missing = ", ".join(section_result["missing_sections"])
        result["errors"].append(
            f"Missing sections without SKIPPED rationale: {missing}. "
            f"Add **SKIPPED:** <rationale> or include the section."
        )
```

**Behavior:** Only reports `missing_sections` in error message.

**Result:** When `all_covered=False` due to `placeholder_sections` (not `missing_sections`), the error shows "Missing sections without SKIPPED rationale: ." with an empty list - confusing.

### Desired State

```python
    if not section_result["all_covered"]:
        result["is_valid"] = False
        errors = []
        if section_result["missing_sections"]:
            missing = ", ".join(section_result["missing_sections"])
            errors.append(f"Missing sections: {missing}")
        if section_result["placeholder_sections"]:
            placeholders = ", ".join(section_result["placeholder_sections"])
            errors.append(f"Placeholder-only sections: {placeholders}")
        result["errors"].append(
            f"{'; '.join(errors)}. "
            f"Add **SKIPPED:** <rationale> or include real content."
        )
```

**Behavior:** Reports both missing_sections AND placeholder_sections in error message.

**Result:** User sees clear message like "Placeholder-only sections: Goal, Detailed Design. Add **SKIPPED:** <rationale> or include real content."

---

## Tests First (TDD)

One test verifies the error message includes placeholder section names when validation fails due to placeholder content.

### Test 1: Error Message Includes Placeholder Sections
```python
def test_validate_template_reports_placeholder_sections(self, tmp_path):
    """Error message should include placeholder_sections when validation fails."""
    from validate import validate_template

    content = '''---
template: implementation_plan
status: draft
date: 2025-12-23
backlog_id: E2-TEST
---
# Test Plan

## Goal

[One sentence placeholder]

## Effort Estimation (Ground Truth)

Real content here.

## Current State vs Desired State

Real content here.

## Tests First (TDD)

Real content here.

## Detailed Design

Real content here.

## Implementation Steps

Real content here.

## Verification

Real content here.

## Risks & Mitigations

Real content here.

## Progress Tracker

Real content here.

## Ground Truth Verification (Before Closing)

Real content here.

@ref1
@ref2
'''
    file_path = tmp_path / "test-plan.md"
    file_path.write_text(content)

    result = validate_template(str(file_path))

    assert result["is_valid"] is False
    # Error should mention placeholder sections, not just "Missing sections: ."
    error_text = " ".join(result["errors"])
    assert "Goal" in error_text
    assert "laceholder" in error_text.lower()  # "Placeholder" appears
```

---

## Detailed Design

Single function fix in validate_template() to properly report both failure modes. The error message construction is updated to include placeholder_sections alongside missing_sections.

### Exact Code Change

**File:** `.claude/lib/validate.py`
**Location:** Lines 490-496 in `validate_template()`

**Current Code:**
```python
    if not section_result["all_covered"]:
        result["is_valid"] = False
        missing = ", ".join(section_result["missing_sections"])
        result["errors"].append(
            f"Missing sections without SKIPPED rationale: {missing}. "
            f"Add **SKIPPED:** <rationale> or include the section."
        )
```

**Changed Code:**
```python
    if not section_result["all_covered"]:
        result["is_valid"] = False
        error_parts = []
        if section_result["missing_sections"]:
            missing = ", ".join(section_result["missing_sections"])
            error_parts.append(f"Missing sections: {missing}")
        if section_result.get("placeholder_sections"):
            placeholders = ", ".join(section_result["placeholder_sections"])
            error_parts.append(f"Placeholder-only sections: {placeholders}")
        result["errors"].append(
            f"{'; '.join(error_parts)}. "
            f"Add **SKIPPED:** <rationale> or include real content."
        )
```

**Diff:**
```diff
     if not section_result["all_covered"]:
         result["is_valid"] = False
-        missing = ", ".join(section_result["missing_sections"])
+        error_parts = []
+        if section_result["missing_sections"]:
+            missing = ", ".join(section_result["missing_sections"])
+            error_parts.append(f"Missing sections: {missing}")
+        if section_result.get("placeholder_sections"):
+            placeholders = ", ".join(section_result["placeholder_sections"])
+            error_parts.append(f"Placeholder-only sections: {placeholders}")
         result["errors"].append(
-            f"Missing sections without SKIPPED rationale: {missing}. "
-            f"Add **SKIPPED:** <rationale> or include the section."
+            f"{'; '.join(error_parts)}. "
+            f"Add **SKIPPED:** <rationale> or include real content."
         )
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Use `.get("placeholder_sections")` | Defensive access | Backward compatibility if older code doesn't have key |
| Separate error parts with `;` | Readable formatting | Distinguish between failure modes |
| Include both in single error | One actionable message | User sees complete picture |

### Input/Output Examples

**Before Fix (actual from Session 104):**
```
Failed: Missing sections without SKIPPED rationale: . Add **SKIPPED:** <rationale> or include the section.
```
Problem: Empty list after "rationale:" - user doesn't know what's wrong.

**After Fix (expected):**
```
Failed: Placeholder-only sections: Goal, Detailed Design, Implementation Steps. Add **SKIPPED:** <rationale> or include real content.
```
Improvement: User sees exactly which sections have placeholder content.

---

## Implementation Steps

This is a bug fix that enhances the error message in validate_template(). Three steps: write test, fix code, verify suite. The implementation follows TDD but the test was not written first because the bug was blocking plan validation.

### Step 1: Write Failing Test
- [ ] Add test to `tests/test_lib_validate.py`
- [ ] Verify test fails (error message doesn't include "Placeholder")

### Step 2: Fix Error Message Construction
- [ ] Update lines 490-496 in validate.py
- [ ] Test passes

### Step 3: Verify Full Suite
- [ ] Run `pytest tests/test_lib_validate.py -v`
- [ ] Run `pytest tests/ -v`

### Step 4: README Sync
**SKIPPED:** No new files, existing README doesn't need update for bug fix.

### Step 5: Consumer Verification
**SKIPPED:** No API changes, just error message text improvement.

---

## Verification

Verification includes running the test suite and demoing the improved error message.

- [ ] New test passes
- [ ] Full suite passes
- [ ] Demo: Run `just validate` on file with placeholder content, see improved error

---

## Risks & Mitigations

Low risk bug fix with mitigations for edge cases and test compatibility.

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing tests depend on exact error text | Low | Use substring matching in tests |
| Edge case with empty both lists | Low | Guard with `if error_parts` |

---

## Progress Tracker

Progress tracked via checkpoint references for this bug fix implementation.

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 104 | 2025-12-23 | - | Plan created | Ready for implementation |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/validate.py` | Error message includes placeholder_sections | [ ] | |
| `tests/test_lib_validate.py` | Test for placeholder in error exists and passes | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_lib_validate.py -v -k "placeholder"
# Expected: test passes, error includes "Placeholder-only sections"
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
- [ ] Ground Truth Verification completed above

---

## References

- **Spawned by:** E2-145 (discovered during implementation)
- **Related:** Session 104 (bug discovery and documentation)
- **Pattern:** Bug fix - error message accuracy

---
