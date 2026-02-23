---
template: implementation_plan
plan_version: "2.0"
status: approved
date: 2026-02-23
backlog_id: WORK-200
title: "Implement Proportional Close Ceremony"
author: Hephaestus
lifecycle_phase: plan
session: 429
generated: 2026-02-23
last_updated: 2026-02-23T11:53:40

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-200/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete content, not placeholders"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Implement Proportional Close Ceremony

---

## Goal

The `/close` command and close-work-cycle skill will detect effort tier and branch to a lightweight path for effort=small items, reducing close ceremony token cost by ~8,000-15,000 tokens while preserving all governance invariants.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No operator decisions | N/A | N/A | WORK-199 investigation resolved all design questions |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/commands/close.md` | MODIFY | 1 |
| `.claude/skills/close-work-cycle/SKILL.md` | MODIFY | 1 |
| `.claude/skills/dod-validation-cycle/SKILL.md` | MODIFY | 1 |
| `.claude/skills/checkpoint-cycle/SKILL.md` | MODIFY | 1 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/skills/retro-cycle/SKILL.md` | references close-work-cycle | Related section | REVIEW (no change — retro already scales via Phase 0) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_skill_template.py` | REVIEW | Verify skill files parse correctly after edits (existing) |
| `tests/test_close_work_cycle.py` | UPDATE | Add content-assertion test for lightweight path patterns |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 5 | 4 Primary Files + 1 test file |
| Tests to write | 1 | Content-assertion test for lightweight patterns |
| Total blast radius | 5 | 4 skill/command files + 1 test file |

---

## Layer 1: Specification

### Current State

**close.md** (command): Unconditionally chains to `retro-cycle` then `close-work-cycle`. No tier awareness.

**close-work-cycle SKILL.md**: Unconditionally invokes `dod-validation-cycle` as prerequisite, then runs full VALIDATE→ARCHIVE→CHAIN with full checkpoint-cycle.

**dod-validation-cycle SKILL.md**: Always runs 3-phase CHECK→VALIDATE→APPROVE regardless of work complexity.

**checkpoint-cycle SKILL.md**: Always invokes anti-pattern-checker subagent in VERIFY phase regardless of checkpoint content size.

**Behavior:** All close ceremonies run at full weight regardless of effort tier.
**Problem:** effort=small items consume ~15,000-25,000 tokens on ceremony for ~5,000 tokens of actual work. REQ-LIFECYCLE-005 and REQ-CEREMONY-005 require proportional scaling.

### Desired State

**close.md**: After finding work item, reads `effort:` and `source_files:` from WORK.md frontmatter (prospective predicate per REQ-LIFECYCLE-005). If `effort: small` AND `source_files` count <= 3, sets `lightweight_close: true`. This flag exists in agent working memory — all skill invocations (retro-cycle, close-work-cycle, checkpoint-cycle) execute within the same agent turn, so the flag is naturally available. No file write needed for propagation.

**close-work-cycle SKILL.md**: New "Lightweight Path (effort=small)" section. When lightweight:
1. Skip dod-validation-cycle 3-phase bridge
2. Run inline DoD checklist (5 checks: pytest gate if applicable, WHY captured, docs current, traced requirement, governance events)
3. Proceed directly to ARCHIVE (unchanged)
4. CHAIN with lightweight checkpoint (VERIFY as inline field check)

**dod-validation-cycle SKILL.md**: New "Lightweight Alternative" section documenting that effort=small items use inline checklist in close-work-cycle instead of this bridge skill.

**checkpoint-cycle SKILL.md**: New "Lightweight VERIFY (effort=small)" subsection. When lightweight, VERIFY is inline field check (load_memory_refs populated? required fields present?) instead of anti-pattern-checker subagent.

**Behavior:** Close ceremony scales proportionally with effort tier.
**Result:** ~50-60% token reduction for effort=small closures.

### Tests

#### Test: Content-Assertion for Lightweight Patterns
- **file:** `tests/test_close_work_cycle.py`
- **function:** `test_lightweight_close_patterns_present()`
- **setup:** Read the 4 modified skill/command files
- **assertion:** Each file contains the expected lightweight path pattern: close.md has "Detect Effort Tier", close-work-cycle has "Lightweight Path", dod-validation-cycle has "Lightweight Alternative", checkpoint-cycle has "Lightweight VERIFY"

### Design

#### File 1 (MODIFY): `.claude/commands/close.md`

Add tier detection after Step 1 (work item lookup), before Chain to Retro Cycle:

```markdown
## Step 1.1: Detect Effort Tier (Prospective Predicate — REQ-LIFECYCLE-005)

After finding work item, determine close ceremony tier using WORK.md frontmatter (prospective predicate, not retrospective git diff):

1. Read `effort:` field from WORK.md frontmatter
2. Read `source_files:` list and count entries
3. If `effort: small` AND `source_files` count <= 3: Set `lightweight_close: true`
4. If `effort: medium` or higher: Set `lightweight_close: false`
5. Default (effort field missing): Set `lightweight_close: false` (conservative — absent data MUST NOT produce more permissive classification per REQ-LIFECYCLE-005)

**Note:** This is a prospective predicate (declared scope before work begins). retro-cycle Phase 0's `assess_scale()` is a retrospective predicate (git diff after work). Both are valid for their lifecycle position. Close ceremony tier uses the prospective predicate because tier detection happens before retro-cycle runs.

**Lightweight close path:** If `lightweight_close: true`:
- retro-cycle runs with trivial scaling (Phase 0 assess_scale handles this independently)
- close-work-cycle uses inline DoD checklist (skip dod-validation-cycle)
- checkpoint-cycle uses inline VERIFY (skip anti-pattern-checker)

**Full close path:** If `lightweight_close: false`:
- All ceremonies run at full weight (current behavior, unchanged)

**Flag propagation:** All skill invocations (retro-cycle, close-work-cycle, checkpoint-cycle) execute within the same agent turn. The `lightweight_close` flag persists in agent working memory across skill boundaries. No file write needed.
```

#### File 2 (MODIFY): `.claude/skills/close-work-cycle/SKILL.md`

Add lightweight path section after prerequisites, before VALIDATE phase:

```markdown
### Lightweight Path (effort=small)

**When:** `/close` command sets `lightweight_close: true` (effort=small + source_files <= 3).

**Skip:** dod-validation-cycle 3-phase bridge (near-zero signal for planless small items per WORK-199 H2).

**Replace VALIDATE with inline DoD checklist:**

1. **Pytest gate** (if type=implementation AND source_files contains .py): Run `pytest` — INVARIANT, never skipped
2. **WHY captured**: Check memory_refs populated in WORK.md or retro COMMIT produced concept IDs
3. **Docs current**: If source_files touch CLAUDE.md consumers, prompt. Otherwise N/A.
4. **Traced requirement** (REQ-TRACE-003): Read traces_to, verify deliverables address requirement
5. **Governance events** (soft gate): Grep for work_id in governance-events.jsonl

**If all pass:** Proceed to ARCHIVE (unchanged).
**If any hard gate fails:** BLOCK — revert to full path.

**ARCHIVE and CHAIN proceed normally**, except checkpoint-cycle uses lightweight VERIFY.
```

#### File 3 (MODIFY): `.claude/skills/dod-validation-cycle/SKILL.md`

Add note after "When to Use" section:

```markdown
### Lightweight Alternative (effort=small)

For `effort: small` items where `/close` sets `lightweight_close: true`, this skill is **not invoked**. Instead, close-work-cycle runs an inline DoD checklist that covers the same criteria with reduced overhead.

**Rationale (WORK-199 H2):** For planless effort=small items, the 3-phase CHECK→VALIDATE→APPROVE bridge yields near-zero signal — no plans to check, no Ground Truth tables, no Agent UX Test triggers. The inline checklist preserves all DoD gates (including tier-independent pytest hard gate) at ~500 tokens vs ~2500.

Full dod-validation-cycle remains required for effort=medium+ items.
```

#### File 4 (MODIFY): `.claude/skills/checkpoint-cycle/SKILL.md`

Add lightweight VERIFY subsection within VERIFY phase:

```markdown
### Lightweight VERIFY (effort=small)

When invoked during a lightweight close path (effort=small closure), VERIFY uses inline field check instead of anti-pattern-checker subagent:

**Inline checks:**
1. `load_memory_refs` is not empty (principle: no learning loss)
2. `pending` field populated (or explicitly empty with rationale)
3. `completed` field has content

**If all pass:** Proceed to CAPTURE.
**If any fail:** Fix inline, then proceed.

**Rationale (WORK-199 H3):** Small checkpoints have minimal anti-pattern surface area. The subagent invocation cost (~1500 tokens) exceeds the value of checking 3 fields. Inline check preserves the phase (REQ-LIFECYCLE-005: "phases lightweight, not skipped") at ~100 tokens.

Full anti-pattern-checker VERIFY remains for standard+ closures.
```

### Call Chain

```
/close {id}
  |
  +-> Step 1: Find work item
  +-> Step 1.1: Detect effort tier (NEW)
  |     lightweight_close = effort:small AND source_files<=3 (prospective)
  |
  +-> retro-cycle (trivial scaling already implemented)
  |
  +-> close-work-cycle
        |
        +-- IF lightweight_close:
        |     Inline DoD checklist (5 checks)
        |     ARCHIVE (unchanged)
        |     CHAIN with lightweight checkpoint
        |
        +-- IF NOT lightweight_close:
              dod-validation-cycle (full 3-phase)
              VALIDATE (full phase)
              ARCHIVE (unchanged)
              CHAIN with full checkpoint
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tier detection in /close command | Read effort + source_files from WORK.md frontmatter (prospective) | Centralizes decision at entry point. Prospective predicate per REQ-LIFECYCLE-005 (not retrospective git diff). Skills don't need to re-detect. |
| Inline checklist vs reduced bridge | Inline checklist | Bridge skill invocation itself costs ~500 tokens. Inline eliminates that overhead entirely. |
| Lightweight = effort:small AND source_files<=3 | Both conditions required | Matches REQ-LIFECYCLE-005 Small tier predicate. Conservative: more source files → more ceremony. |
| Prospective vs retrospective predicate | Prospective (WORK.md frontmatter) | REQ-LIFECYCLE-005 distinguishes: source_files is prospective, files_changed is retrospective. Close tier detection is pre-retro, so prospective is correct. |
| Flag propagation via agent memory | No file write for lightweight_close | All /close skill invocations execute in same agent turn. Flag naturally available across Skill() boundaries. |
| Pytest gate invariant | Never skip regardless of tier | Per close-work-cycle SKILL.md:109 and REQ-CEREMONY-005. Code correctness is non-negotiable. |
| Checkpoint VERIFY inline vs skip | Inline field check | REQ-LIFECYCLE-005 says "phases lightweight, not skipped." Preserves phase at minimal cost. |
| Missing effort field defaults to full | Conservative safe default | REQ-LIFECYCLE-005 invariant: absent data MUST NOT produce more permissive classification. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| effort field missing in WORK.md | Default to full close path | Grep for "Default.*conservative" in close.md |
| effort=small but source_files > 3 | Full close path (conservative) | Grep for "source_files.*3" in close.md |
| type=investigation + effort=small | Lightweight path, pytest gate skipped (type exempt) | Grep for "type.*investigation.*Skip" in close-work-cycle |
| Memory store fails during lightweight checkpoint | Proceed (COMMIT degradation already defined in retro-cycle) | Existing retro-cycle degradation |
| Inline DoD hard gate fails | BLOCK, revert to full path for operator review | Grep for "BLOCK.*revert" in close-work-cycle |
| WORK-200 itself has effort=medium | Closes via full path, not lightweight (correct behavior) | N/A — WORK-200 designs for effort=small, doesn't use it itself |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill wording ambiguity causes agent to skip checks | Med | Explicit "INVARIANT" labels on pytest gate. "MUST" on each inline check. |
| Future effort=small items with plans | Low | Small tier predicate (source_files <= 3) doesn't check plan existence. But REQ-LIFECYCLE-005 Small tier allows plans ("plan MAY exist"). Items with plans still get lightweight close if effort=small + source_files <= 3. Plan-specific DoD checks (Ground Truth) are N/A since dod-validation is skipped — the inline checklist handles what's needed. |
| Inconsistency between /close command and close-work-cycle | Med | Single flag `lightweight_close` set once in /close, consumed downstream. No re-detection. |

---

## Layer 2: Implementation Steps

### Step 1: Update close.md with tier detection
- **spec_ref:** Layer 1 > Design > File 1
- **input:** Current close.md read
- **action:** Add Step 1.1 (Detect Effort Tier) section after Step 1
- **output:** close.md has tier detection logic
- **verify:** `Grep(pattern="lightweight_close", path=".claude/commands/close.md")` returns 1+ match

### Step 2: Update close-work-cycle SKILL.md with lightweight path
- **spec_ref:** Layer 1 > Design > File 2
- **input:** Step 1 complete
- **action:** Add "Lightweight Path" section with inline DoD checklist
- **output:** close-work-cycle SKILL.md documents both paths
- **verify:** `Grep(pattern="Lightweight Path", path=".claude/skills/close-work-cycle/SKILL.md")` returns 1+ match

### Step 3: Update dod-validation-cycle SKILL.md with lightweight alternative note
- **spec_ref:** Layer 1 > Design > File 3
- **input:** Step 2 complete
- **action:** Add "Lightweight Alternative" section
- **output:** dod-validation-cycle documents when it's skipped
- **verify:** `Grep(pattern="Lightweight Alternative", path=".claude/skills/dod-validation-cycle/SKILL.md")` returns 1+ match

### Step 4: Update checkpoint-cycle SKILL.md with lightweight VERIFY
- **spec_ref:** Layer 1 > Design > File 4
- **input:** Step 3 complete
- **action:** Add "Lightweight VERIFY" subsection within VERIFY phase
- **output:** checkpoint-cycle documents inline VERIFY option
- **verify:** `Grep(pattern="Lightweight VERIFY", path=".claude/skills/checkpoint-cycle/SKILL.md")` returns 1+ match

### Step 5: Write content-assertion test (RED then GREEN)
- **spec_ref:** Layer 1 > Tests > Content-Assertion
- **input:** Steps 1-4 complete (all 4 files modified)
- **action:** Add `test_lightweight_close_patterns_present()` to `tests/test_close_work_cycle.py`. Test reads 4 modified files and asserts lightweight path patterns are present.
- **output:** Test passes (GREEN — patterns already present from Steps 1-4)
- **verify:** `pytest tests/test_close_work_cycle.py::test_lightweight_close_patterns_present -v` exits 0

### Step 6: Run full test suite
- **spec_ref:** Layer 0 > Test Files
- **input:** Steps 1-5 complete
- **action:** Run `pytest tests/test_skill_template.py tests/test_close_work_cycle.py -v` to verify no regressions
- **output:** All existing tests pass
- **verify:** `pytest tests/test_skill_template.py tests/test_close_work_cycle.py -v` exits 0

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_close_work_cycle.py::test_lightweight_close_patterns_present -v` | 1 passed, 0 failed |
| `pytest tests/test_skill_template.py tests/test_close_work_cycle.py -v` | All passed, 0 failed |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| /close detects effort tier | `Grep(pattern="lightweight_close", path=".claude/commands/close.md")` | 1+ match |
| close-work-cycle lightweight VALIDATE | `Grep(pattern="Lightweight Path", path=".claude/skills/close-work-cycle/SKILL.md")` | 1+ match |
| dod-validation-cycle lightweight alternative | `Grep(pattern="Lightweight Alternative", path=".claude/skills/dod-validation-cycle/SKILL.md")` | 1+ match |
| checkpoint-cycle lightweight VERIFY | `Grep(pattern="Lightweight VERIFY", path=".claude/skills/checkpoint-cycle/SKILL.md")` | 1+ match |
| Full path unchanged | `Grep(pattern="dod-validation-cycle", path=".claude/skills/close-work-cycle/SKILL.md")` | 1+ match (still referenced for standard+ path) |
| Pytest gate invariant | `Grep(pattern="INVARIANT\\|tier-independent\\|never skip", path=".claude/skills/close-work-cycle/SKILL.md")` | 1+ match |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| retro-cycle unmodified | `git diff .claude/skills/retro-cycle/SKILL.md` | No changes (retro already scales) |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Steps 5-6 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] No stale references to removed content
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- @docs/work/active/WORK-199/WORK.md (investigation source — findings and hypothesis verdicts)
- @docs/work/active/WORK-200/WORK.md (work item)
- @.claude/skills/close-work-cycle/SKILL.md (primary target)
- @.claude/skills/dod-validation-cycle/SKILL.md (lightweight alternative)
- @.claude/skills/checkpoint-cycle/SKILL.md (VERIFY reduction)
- @.claude/commands/close.md (entry point)
- @.claude/haios/lib/retro_scale.py (tier detection prototype)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-005:374, REQ-CEREMONY-005:434)
- Memory: 87692-87708 (WORK-199 investigation findings)
- Memory: 85534 (computable predicate gating pattern)

---
