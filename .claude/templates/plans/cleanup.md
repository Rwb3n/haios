---
template: implementation_plan
subtype: cleanup
status: draft
date: {{DATE}}
backlog_id: {{BACKLOG_ID}}
title: "{{TITLE}}"
author: Hephaestus
lifecycle_phase: plan
session: {{SESSION}}
version: "1.5"
generated: {{DATE}}
last_updated: {{TIMESTAMP}}
---
# Cleanup Plan: {{TITLE}}

---

<!-- TEMPLATE GOVERNANCE (v1.4)
     Cleanup plan template — optimized for bug fixes, chores, and maintenance.
     Minimal sections. No design decisions, no risk analysis.
     WORK-152: Fractured from monolithic implementation_plan template.

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Goal

[One sentence: What will be fixed/cleaned after this plan is complete?]

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | [N] | `Glob pattern` or explicit list |
| Lines of code affected | [~N] | `wc -l` on target files |
| Tests to update | [N] | Based on affected test files |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Fix/Cleanup | [X min/hr] | [High/Med/Low] |
| Verify | [X min/hr] | [High/Med/Low] |
| **Total** | [X min/hr] | |

---

## Change List

<!-- List each change with file path and description -->

| # | File | Change | Done |
|---|------|--------|------|
| 1 | `[path/to/file]` | [What to fix/change] | [ ] |
| 2 | `[path/to/file]` | [What to fix/change] | [ ] |

---

## Implementation Steps

### Step 1: Apply Fixes
- [ ] [Specific fix 1]
- [ ] [Specific fix 2]

### Step 2: Verify
- [ ] Run affected tests: `pytest [test_file] -v`
- [ ] Run full suite (no regressions)

### Step 3: Consumer Check
- [ ] Grep for affected paths/names to ensure no stale references

---

## Verification

- [ ] All changes from Change List applied
- [ ] Tests pass (no regressions)
- [ ] **MUST:** READMEs current if structure changed

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/{{BACKLOG_ID}}/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| [Copy each deliverable from WORK.md] | [ ] | [How you verified it] |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `[path/to/file]` | [Fix applied, behavior correct] | [ ] | |

**Verification Commands:**
```bash
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
- [ ] All changes applied
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] WHY captured (reasoning stored to memory)
- [ ] Ground Truth Verification completed above

---

## References

- [Related work items or bug reports]

---
