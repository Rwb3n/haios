---
template: implementation_plan
status: complete
date: 2026-02-05
backlog_id: WORK-099
title: Fix Scaffold Template Loading and Broken Tests
author: Hephaestus
lifecycle_phase: plan
session: 247
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-05T19:23:19'
---
# Implementation Plan: Fix Scaffold Template Loading and Broken Tests

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

Fix all consumer breakage caused by CH-006 TemplateFracturing: restore 5 broken tests, update 2 skill docs, fix 1 justfile recipe, all by adding `_legacy/` fallback to `load_template()`.

---

## Effort Estimation (Ground Truth)

**SKIPPED:** effort=small per WORK-098 scoping. 7 deliverables, all single-line or few-line fixes across 5 files + 1 already done.

---

## Current State vs Desired State

| Component | Current | Desired |
|-----------|---------|---------|
| `load_template("implementation_plan")` | FileNotFoundError (DONE - fixed) | Loads from `_legacy/` fallback |
| 3 tests in TestImplementationPlanTemplate | FAIL (file not found) | PASS (point to `_legacy/`) |
| 1 test in test_template_rfc2119 | FAIL (file not found) | PASS (point to `_legacy/`) |
| 1 test in test_known_templates_exist | FAIL (FileNotFoundError) | PASS (load_template resolves) |
| plan-authoring-cycle SKILL.md | References deleted path | References `_legacy/` path |
| plan-validation-cycle SKILL.md | References deleted path | References `_legacy/` path |
| justfile commit-close | Uses flat `WORK-{id}-*` pattern | Uses `{id}/` directory pattern |

---

## Tests First (TDD)

**SKIPPED:** Tests already exist and are currently FAILING. The fix will make them pass. No new tests needed.

Broken tests (5 total):
1. `test_lib_validate.py::TestImplementationPlanTemplate::test_implementation_plan_template_has_open_decisions_section`
2. `test_lib_validate.py::TestImplementationPlanTemplate::test_open_decisions_section_has_table`
3. `test_lib_validate.py::TestImplementationPlanTemplate::test_open_decisions_section_has_block_comment`
4. `test_template_rfc2119.py::test_implementation_plan_template_has_rfc2119_section`
5. `test_lib_scaffold.py::TestLoadTemplate::test_known_templates_exist`

---

## Detailed Design

### Fix 1: scaffold.py:load_template() (DONE)

Added `_legacy/` fallback path when primary template not found. Already implemented and verified.

### Fix 2: test_lib_validate.py (3 tests, lines 119-141)

Tests hardcode `Path(__file__).parent.parent / ".claude" / "templates" / "implementation_plan.md"`. Add fallback:
```python
template_path = Path(__file__).parent.parent / ".claude" / "templates" / "implementation_plan.md"
if not template_path.exists():
    template_path = Path(__file__).parent.parent / ".claude" / "templates" / "_legacy" / "implementation_plan.md"
```

### Fix 3: test_template_rfc2119.py (1 test, line 29)

Same pattern - add `_legacy/` fallback for `TEMPLATES_DIR / "implementation_plan.md"`.

### Fix 4: test_lib_scaffold.py (1 test)

No code change needed - `load_template()` fix resolves this automatically.

### Fix 5-6: Skill doc references

Update `plan-authoring-cycle/SKILL.md:333` and `plan-validation-cycle/SKILL.md:257` to reference `_legacy/implementation_plan.md`.

### Fix 7: justfile commit-close (line 390)

Change from flat file pattern to directory pattern:
```diff
-    git add "docs/work/archive/WORK-{{id}}-*" "docs/plans/PLAN-{{id}}*" "docs/investigations/INVESTIGATION-{{id}}*" .claude/haios-status*.json
+    git add "docs/work/archive/{{id}}/" .claude/haios-status*.json
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| How to resolve missing template | `_legacy/` fallback in load_template() | Monolithic template differs from fractured phase templates; `_legacy/` is correct location for scaffolding |
| Test fix approach | Add fallback path in tests | Tests validate template content, not scaffold module; direct path resolution is appropriate |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Template resolution strategy | A) _legacy/ fallback, B) Update TEMPLATE_CONFIG | A | Monolithic template is different content from fractured phase template |

No blocked decisions.

---

## Implementation Steps

- [x] 1. Fix `scaffold.py:load_template()` with `_legacy/` fallback (DONE)
- [ ] 2. Fix `test_lib_validate.py` TestImplementationPlanTemplate (3 tests) - add `_legacy/` path fallback
- [ ] 3. Fix `test_template_rfc2119.py` implementation_plan test - add `_legacy/` path fallback
- [ ] 4. Verify `test_lib_scaffold.py::test_known_templates_exist` passes (no code change needed)
- [ ] 5. Update `plan-authoring-cycle/SKILL.md` reference
- [ ] 6. Update `plan-validation-cycle/SKILL.md` reference
- [ ] 7. Fix `justfile` commit-close recipe to use directory pattern

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | [High/Medium/Low] | [Mitigation strategy] |

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

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-099/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| [Copy each deliverable from WORK.md] | [ ] | [How you verified it] |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

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
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @docs/work/active/WORK-098/WORK.md (investigation that scoped this)
- @docs/work/active/WORK-099/WORK.md
- @.claude/haios/lib/scaffold.py

---
