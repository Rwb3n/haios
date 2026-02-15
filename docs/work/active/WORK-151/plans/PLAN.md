---
template: implementation_plan
status: complete
date: 2026-02-14
backlog_id: WORK-151
title: "Implement Epistemic Review Step in Investigation CONCLUDE Phase"
author: Hephaestus
lifecycle_phase: plan
session: 373
version: "1.5"
generated: 2026-02-14
last_updated: 2026-02-14T17:40:05
---
# Implementation Plan: Implement Epistemic Review Step in Investigation CONCLUDE Phase

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

After this plan is complete, the investigation-cycle CONCLUDE phase will include a mandatory epistemic review sub-step that categorizes findings into KNOWN/INFERRED/UNKNOWN, renders a three-level verdict (PROCEED/DEFER/INVESTIGATE-MORE), and presents to the operator via AskUserQuestion when DEFER verdict applies.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | investigation-cycle/SKILL.md, investigation/CONCLUDE.md |
| Lines of code affected | ~60 (SKILL.md CONCLUDE section), ~52 (CONCLUDE.md template) | Read tool |
| New files to create | 0 | Pure modification |
| Tests to write | 0 pytest | Markdown-only changes; verification via structural content checks |
| Dependencies | 0 | No Python module changes |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Two markdown files, no code imports |
| Risk of regression | Low | No existing tests for CONCLUDE content; ceremony_runner test checks phase list only |
| External dependencies | Low | No APIs, services, or config changes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Plan + critique + validation | 15 min | High |
| DO (edit two files) | 15 min | High |
| CHECK (verify content) | 10 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/skills/investigation-cycle/SKILL.md:174-236` (CONCLUDE phase)

Current CONCLUDE actions (lines 183-191):
```markdown
1. Review findings against original objective
2. Synthesize answer to the investigation question
3. Identify spawned work items (ADRs, backlog items, new investigations)
4. Create spawned items using `/new-*` commands
5. Epoch Artifact Reconciliation (MUST)
6. Store findings summary to memory
7. Update investigation status
8. Populate memory_refs in work item frontmatter
```

**File:** `.claude/templates/investigation/CONCLUDE.md:56-86` (Output contract)

Current output contract:
```markdown
- [ ] Findings synthesized (answer to objective)
- [ ] Spawned work items created
- [ ] Memory stored via ingester_ingest
- [ ] memory_refs populated
- [ ] Rationale documented if no spawned work
```

**Behavior:** Agent synthesizes findings (step 2) then immediately spawns work (step 3) without distinguishing facts from inferences from unknowns.

**Result:** Implicit assumptions carry forward into spawned implementation work. Agent doesn't surface what it doesn't know.

### Desired State

**File:** `.claude/skills/investigation-cycle/SKILL.md` (CONCLUDE phase)

Target CONCLUDE actions:
```markdown
1. Review findings against original objective
2. Synthesize answer to the investigation question
3. **Epistemic Review (MUST)** - Categorize findings:
   a. KNOWN: Facts with citations (file:line, memory ID, URL)
   b. INFERRED: Reasoning chains (premise → conclusion)
   c. UNKNOWN: Gaps with impact assessment (blocking vs non-blocking)
   d. Render verdict: PROCEED / DEFER / INVESTIGATE-MORE
   e. If DEFER: Present K/I/U to operator via AskUserQuestion
4. Identify spawned work items (gated by verdict)
5. Create spawned items using `/new-*` commands
6. Epoch Artifact Reconciliation (MUST)
7. Store findings summary to memory
8. Update investigation status
9. Populate memory_refs in work item frontmatter
```

**File:** `.claude/templates/investigation/CONCLUDE.md` (Output contract)

Target output contract adds:
```markdown
- [ ] Epistemic review completed (K/I/U table + verdict)
- [ ] Verdict rendered (PROCEED/DEFER/INVESTIGATE-MORE)
- [ ] If DEFER: operator consulted via AskUserQuestion
```

**Behavior:** Agent must explicitly categorize what it knows, infers, and doesn't know before spawning work. Verdict gates spawning.

**Result:** Unknowns are surfaced at investigation boundary. Operator sees epistemic state before implementation begins.

---

## Tests First (TDD)

**SKIPPED (pytest):** Pure markdown/skill file changes — no Python code modified. Verification is structural content checks.

### Verification 1: SKILL.md contains epistemic review step
```
Grep(pattern="Epistemic Review.*MUST", path=".claude/skills/investigation-cycle/SKILL.md")
# Expected: Match found in CONCLUDE phase section
```

### Verification 2: SKILL.md contains K/I/U categories
```
Grep(pattern="KNOWN.*INFERRED.*UNKNOWN|K/I/U", path=".claude/skills/investigation-cycle/SKILL.md")
# Expected: Match found
```

### Verification 3: SKILL.md contains three-level verdict
```
Grep(pattern="PROCEED.*DEFER.*INVESTIGATE-MORE", path=".claude/skills/investigation-cycle/SKILL.md")
# Expected: Match found
```

### Verification 4: SKILL.md contains DEFER AskUserQuestion behavior
```
Grep(pattern="AskUserQuestion", path=".claude/skills/investigation-cycle/SKILL.md")
# Expected: Match found in CONCLUDE DEFER section
```

### Verification 5: CONCLUDE.md output contract includes epistemic review
```
Grep(pattern="Epistemic review|K/I/U|verdict", path=".claude/templates/investigation/CONCLUDE.md")
# Expected: Matches found in output contract and template sections
```

### Verification 6: CONCLUDE.md template has K/I/U table structure
```
Grep(pattern="KNOWN|INFERRED|UNKNOWN", path=".claude/templates/investigation/CONCLUDE.md")
# Expected: All three categories present in template
```

### Verification 7: Existing CONCLUDE content preserved (backward compat)
```
Grep(pattern="Epoch Artifact Reconciliation", path=".claude/skills/investigation-cycle/SKILL.md")
# Expected: Still present — epistemic review is additive, not replacing existing steps
```

### Verification 8: No external references to "section 4a" broken
```
Grep(pattern="section 4a|4a\\.", path=".")
# Expected: Only matches in SKILL.md itself (now "4a. Epistemic Review" and "4b. Epoch Artifact Reconciliation")
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
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Exact Changes

#### Change 1: SKILL.md CONCLUDE Phase

**File:** `.claude/skills/investigation-cycle/SKILL.md`
**Location:** Lines 182-191 (CONCLUDE Actions section)

**Current (SKILL.md:183-191):**
```markdown
**Actions:**
1. Review findings against original objective
2. Synthesize answer to the investigation question
3. Identify spawned work items (ADRs, backlog items, new investigations)
4. Create spawned items using `/new-*` commands with `spawned_by: {this_investigation_id}`
5. **Epoch Artifact Reconciliation (MUST - Session 276)** - see below
6. Store findings summary to memory via `ingester_ingest`
7. Update investigation status: `status: complete`
8. Populate `memory_refs` in work item frontmatter
```

**Changed (insert step 3 as epistemic review, renumber 4-9):**
```markdown
**Actions:**
1. Review findings against original objective
2. Synthesize answer to the investigation question
3. **Epistemic Review (MUST)** - see section 4a below
4. Identify spawned work items (ADRs, backlog items, new investigations)
5. Create spawned items using `/new-*` commands with `spawned_by: {this_investigation_id}`
6. **Epoch Artifact Reconciliation (MUST - Session 276)** - see below
7. Store findings summary to memory via `ingester_ingest`
8. Update investigation status: `status: complete`
9. Populate `memory_refs` in work item frontmatter
```

**Also add new section 4a (after existing 4a Epoch Artifact Reconciliation, renaming existing to 4b):**

```markdown
#### 4a. Epistemic Review (MUST)

Before spawning work, categorize all findings into three categories:

**Step 1: Categorize findings**

| Category | What to Include | Format |
|----------|----------------|--------|
| KNOWN | Facts verified from files, tests, or direct observation | Fact + citation (file:line, memory ID, URL) |
| INFERRED | Conclusions reached through reasoning | Premise → conclusion chain |
| UNKNOWN | Gaps in knowledge with impact assessment | Gap + impact (blocking / non-blocking) |

**Step 2: Render verdict**

| Verdict | Condition | Action |
|---------|-----------|--------|
| PROCEED | No blocking unknowns | Continue to spawn work items |
| DEFER | Significant unknowns exist | Present K/I/U to operator via AskUserQuestion for decision |
| INVESTIGATE-MORE | Critical unknowns block all progress | Spawn follow-up investigation before any implementation work |

**Step 3: If DEFER**

Present the K/I/U summary to the operator using AskUserQuestion:
- Header: "Epistemic Review"
- Question: "Investigation has significant unknowns. Review findings and choose direction."
- Options: "Proceed anyway" / "Investigate more" / "Defer to next session"

After operator responds:
1. **MUST** immediately write operator decision to CONCLUDE.md "Operator Decision" field BEFORE proceeding to step 4
2. Route based on response:
   - "Proceed anyway" → Continue to step 4 (spawn work normally); unknowns accepted
   - "Investigate more" → Spawn follow-up investigation instead of implementation work
   - "Defer to next session" → Skip spawn; record rationale; close CONCLUDE

If AskUserQuestion fails or times out: treat as "Defer to next session" (fail-safe).

**Rationale (WORK-082, Session 372):**
- Location inside CONCLUDE preserves investigation context (standalone ceremony loses it)
- Three-level verdict aligns with L3.6 Graceful Degradation (not binary block)
- K/I/U structure aligns with L3.2 Evidence Over Assumption
- DEFER respects L3.4 Duties Are Separated (operator decides on unknowns)
```

**Also update CONCLUDE Exit Criteria (SKILL.md:228-235):**

Add after existing exit criteria:
```markdown
- [ ] **MUST:** Epistemic review completed (K/I/U table populated with findings — not empty)
- [ ] **MUST:** Verdict rendered and documented (PROCEED/DEFER/INVESTIGATE-MORE)
- [ ] If DEFER: Operator consulted via AskUserQuestion and decision recorded in CONCLUDE.md
- [ ] Agent verification: Read own CONCLUDE.md to confirm K/I/U table + verdict present before marking CONCLUDE complete
```

#### Change 2: CONCLUDE.md Template

**File:** `.claude/templates/investigation/CONCLUDE.md`
**Location:** Lines 56-86 (Output Contract and Template sections)

**Current output contract (CONCLUDE.md:56-61):**
```markdown
- [ ] Findings synthesized (answer to objective)
- [ ] Spawned work items created via `/new-work` or `/new-plan`
- [ ] Memory stored via `ingester_ingest`
- [ ] `memory_refs` populated in work item frontmatter
- [ ] Rationale documented if no spawned work
```

**Changed output contract:**
```markdown
- [ ] Findings synthesized (answer to objective)
- [ ] Epistemic review completed (K/I/U table + verdict)
- [ ] Verdict rendered (PROCEED/DEFER/INVESTIGATE-MORE)
- [ ] If DEFER: operator consulted via AskUserQuestion
- [ ] Spawned work items created via `/new-work` or `/new-plan` (gated by verdict)
- [ ] Memory stored via `ingester_ingest`
- [ ] `memory_refs` populated in work item frontmatter
- [ ] Rationale documented if no spawned work
```

**Also update template section to add K/I/U table and verdict after Conclusion:**
```markdown
## Epistemic Review

### Findings Classification

| # | Category | Finding | Evidence/Reasoning |
|---|----------|---------|-------------------|
| K1 | KNOWN | [Fact] | [file:line / memory ID / URL] |
| I1 | INFERRED | [Conclusion] | [Premise → conclusion] |
| U1 | UNKNOWN | [Gap] | Impact: [blocking/non-blocking] |

### Verdict

**Verdict:** [PROCEED / DEFER / INVESTIGATE-MORE]

**Rationale:** [Why this verdict based on unknowns above]

<!-- If DEFER: AskUserQuestion was presented. Record operator decision: -->
**Operator Decision:** [proceed / investigate-more / defer-to-next-session]
**Decision Rationale:** [Why operator chose this direction]
```

### Behavior Logic

**Current Flow:**
```
CONCLUDE → Synthesize findings → Spawn work → Reconcile epoch → Store memory
```

**New Flow:**
```
CONCLUDE → Synthesize findings → Epistemic Review (K/I/U)
                                       |
                                  Verdict?
                                  ├─ PROCEED → Spawn work → Reconcile → Store
                                  ├─ DEFER → AskUserQuestion → Operator decides → ...
                                  └─ INVESTIGATE-MORE → Spawn follow-up investigation
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Location | Inside CONCLUDE, not standalone ceremony | Standalone loses investigation context (WORK-082 H2 refuted) |
| Verdict levels | Three (PROCEED/DEFER/INVESTIGATE-MORE) | Binary block too restrictive; L3.6 Graceful Degradation |
| DEFER behavior | AskUserQuestion, not auto-block | L3.4 Duties Are Separated; operator decides significance |
| K/I/U format | Table with citations | L3.2 Evidence Over Assumption; structured for machine parsing |
| Spawn gating | Verdict gates spawning | Prevents implicit assumptions carrying into implementation |
| Section numbering | Existing 4a (Epoch Reconciliation) becomes 4b | Additive change, preserves all existing content |

### Edge Cases

| Case | Handling | Verification |
|------|----------|--------------|
| Investigation with zero unknowns | PROCEED verdict, K/I/U table has empty UNKNOWN section | V1, V3 |
| All unknowns are non-blocking | PROCEED verdict (non-blocking = informational) | V3 |
| Operator chooses "Proceed anyway" on DEFER | Continue to spawn as normal, record decision | V4 |
| Operator chooses "Investigate more" on DEFER | Spawn follow-up investigation instead of implementation | V4 |
| Investigation that spawns no work | K/I/U still required; verdict still rendered | V5 |

### Open Questions

None. Design is fully specified by WORK-082 investigation.

---

## Open Decisions (MUST resolve before implementation)

**None.** All design decisions resolved by WORK-082 investigation (S372). No operator_decisions in WORK-151 frontmatter.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Edit SKILL.md CONCLUDE Actions
- [ ] Insert epistemic review as step 3 in CONCLUDE Actions list
- [ ] Renumber existing steps 3-8 to 4-9
- [ ] Verification 7 passes (existing content preserved)

### Step 2: Add Epistemic Review Sub-Section to SKILL.md
- [ ] Rename existing "4a. Epoch Artifact Reconciliation" to "4b. Epoch Artifact Reconciliation"
- [ ] Insert new "4a. Epistemic Review (MUST)" section with K/I/U table, verdict rules, DEFER behavior
- [ ] Verifications 1, 2, 3, 4 pass

### Step 3: Update SKILL.md CONCLUDE Exit Criteria
- [ ] Add three new exit criteria for epistemic review, verdict, and DEFER
- [ ] Verification 1 passes

### Step 4: Update CONCLUDE.md Output Contract
- [ ] Add epistemic review, verdict, and DEFER lines to output contract
- [ ] Reorder: findings → epistemic review → verdict → spawn (gated)
- [ ] Verification 5 passes

### Step 5: Update CONCLUDE.md Template
- [ ] Add "## Epistemic Review" section with K/I/U table and verdict template
- [ ] Verification 6 passes

### Step 6: Also update CONCLUDE.md output_contract frontmatter
- [ ] Add epistemic review fields to output_contract frontmatter (YAML): epistemic_review, verdict, operator_decision
- [ ] Verification 5 passes

### Step 7: Full Verification
- [ ] Run all 8 structural verifications (Grep checks)
- [ ] Run full test suite to verify no regressions
- [ ] Read both files end-to-end to verify coherence

### Step 8: README Sync
- [ ] **SKIPPED:** No new files created, no directory structure changes. Existing READMEs unaffected.

---

## Verification

- [ ] All 8 structural verifications pass (Grep checks)
- [ ] Full test suite: no regressions
- [ ] Both modified files read end-to-end and coherent

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing CONCLUDE content accidentally deleted | Medium | Verification 7 checks Epoch Artifact Reconciliation still present |
| Step numbering broken (references in other docs) | Low | No external docs reference CONCLUDE step numbers by index |
| Section "4a" rename breaks references | Low | Only SKILL.md itself references "section 4a" — update in same edit |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 373 | 2026-02-14 | - | PLAN complete | Plan authored, ready for critique + validation |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-151/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| investigation-cycle SKILL.md CONCLUDE phase step 3 (epistemic review) added | [ ] | Grep "Epistemic Review.*MUST" in SKILL.md |
| CONCLUDE.md template output contract includes K/I/U section | [ ] | Grep "KNOWN.*INFERRED.*UNKNOWN" in CONCLUDE.md |
| Verdict rules documented (PROCEED/DEFER/INVESTIGATE-MORE) | [ ] | Grep "PROCEED.*DEFER.*INVESTIGATE-MORE" in SKILL.md |
| DEFER behavior implemented (AskUserQuestion with K/I/U summary) | [ ] | Grep "AskUserQuestion" in SKILL.md |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/investigation-cycle/SKILL.md` | CONCLUDE has epistemic review step 3, section 4a, exit criteria | [ ] | |
| `.claude/templates/investigation/CONCLUDE.md` | Output contract + template include K/I/U and verdict | [ ] | |

**Verification Commands:**
```
Grep(pattern="Epistemic Review", path=".claude/skills/investigation-cycle/SKILL.md")
Grep(pattern="KNOWN|INFERRED|UNKNOWN", path=".claude/templates/investigation/CONCLUDE.md")
Grep(pattern="Epoch Artifact Reconciliation", path=".claude/skills/investigation-cycle/SKILL.md")
pytest tests/ -v  # No regressions
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| All 7 structural verifications pass? | [Yes/No] | |
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

- @docs/work/active/WORK-082/WORK.md (design source — investigation findings)
- @docs/work/active/WORK-151/WORK.md (work item)
- @.claude/skills/investigation-cycle/SKILL.md (primary artifact to modify)
- @.claude/templates/investigation/CONCLUDE.md (template to update)
- L3.2: Evidence Over Assumption (K/I/U structure)
- L3.4: Duties Are Separated (DEFER to operator)
- L3.6: Graceful Degradation (three-level verdict)
- Memory: 85419 (inside CONCLUDE), 85420 (K/I/U), 85421 (verdict levels)

---
