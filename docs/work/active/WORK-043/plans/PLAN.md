---
template: implementation_plan
status: complete
date: 2026-02-01
backlog_id: WORK-043
title: CH-001 InvestigationFracture - Split Monolithic Template
author: Hephaestus
lifecycle_phase: plan
session: 271
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-01T15:28:58'
---
# Implementation Plan: CH-001 InvestigationFracture - Split Monolithic Template

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

The investigation template will be fractured from one 368-line monolithic file into four phase-specific templates (~30-50 lines each) with explicit input/output contracts and governed activity references.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | No existing files modified |
| Lines of code affected | 0 | Pure creation, no modification |
| New files to create | 5 | 4 phase templates + 1 chapter file |
| Tests to write | 0 | Templates are markdown, no runtime tests needed |
| Dependencies | 2 | investigation-cycle skill references templates, scaffold.py may need update |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Templates are passive - skills read them |
| Risk of regression | Low | Old template remains, new templates are additive |
| External dependencies | None | Pure markdown files |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create 4 phase templates | 30 min | High |
| Create chapter file | 10 min | High |
| Store to memory | 5 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```
.claude/templates/
├── investigation.md    (368 lines, all phases combined)
└── implementation_plan.md
```

**Behavior:** All investigation phases (EXPLORE, HYPOTHESIZE, VALIDATE, CONCLUDE) are in one 368-line file. Agent must scroll past irrelevant sections. No explicit input/output contracts. Governed activities not referenced.

**Result:** "Template Tax" (WORK-036) - cognitive overload, phases coupled, agents skip sections they can't parse.

### Desired State

```
.claude/templates/
├── investigation/
│   ├── EXPLORE.md       (~40 lines)
│   ├── HYPOTHESIZE.md   (~40 lines)
│   ├── VALIDATE.md      (~40 lines)
│   └── CONCLUDE.md      (~40 lines)
├── investigation.md     (PRESERVED for backward compat)
└── implementation_plan.md
```

**Behavior:** Each phase has its own template with:
- Input Contract: What must exist before this phase
- Output Contract: What must exist after this phase
- Governed Activities: Activities allowed in this phase (from activity_matrix.yaml)
- Template: Minimal structure for phase outputs

**Result:** Agent loads only the template for their current phase. Contracts are explicit. Activities match governance enforcement.

---

## Tests First (TDD)

**SKIPPED:** Templates are static markdown files - no runtime code to test. Validation is manual review that:
1. Each template file exists in `.claude/templates/investigation/`
2. Each template has Input Contract, Output Contract, Governed Activities, Template sections
3. Each template is 30-50 lines (REQ-TEMPLATE-002)
4. Governed activities match those defined in `activity_matrix.yaml` for the corresponding state

---

## Detailed Design

This is a documentation task - creating markdown templates, not runtime code.

### Phase Template Structure (per Templates arc)

Each phase template follows this pattern from ARC.md:

```markdown
---
template: investigation_phase
phase: {PHASE_NAME}
version: "1.0"
---
# {PHASE_NAME} Phase

## Input Contract
- [ ] {Prerequisite 1}
- [ ] {Prerequisite 2}

## Governed Activities
*From activity_matrix.yaml for state {MAPPED_STATE}*
- {activity-1}: {description}
- {activity-2}: {description}

## Output Contract
- [ ] {Required output 1}
- [ ] {Required output 2}

## Template
{Minimal markdown structure for phase outputs}
```

### Phase-to-State Mapping (from activity_matrix.yaml)

| Phase | Maps to State | Key Governed Activities |
|-------|---------------|------------------------|
| EXPLORE | EXPLORE | file-read (allow), file-search (allow), content-search (allow), web-fetch (allow), memory-search (allow) |
| HYPOTHESIZE | DESIGN | file-read (allow), file-write (allow), user-query (allow) |
| VALIDATE | CHECK | shell-execute (allow), file-read (allow), memory-search (allow) |
| CONCLUDE | DONE | file-write (allow), memory-store (allow), file-read (allow) |

### Individual Template Specifications

#### EXPLORE.md (~35 lines)

**Input Contract:**
- Work item exists with Context and Objective

**Governed Activities:**
- file-read, file-search, content-search (allow)
- web-fetch, web-search (allow)
- memory-search (allow)
- file-write (warn - prefer notes)

**Output Contract:**
- Evidence Collection table populated with sources
- Prior Work Query completed

**Template Content:**
```markdown
## Evidence Collection
| Finding | Source (file:line) | Notes |
|---------|-------------------|-------|

## Memory Evidence
| Concept ID | Summary | Relevance |
|------------|---------|-----------|
```

#### HYPOTHESIZE.md (~35 lines)

**Input Contract:**
- EXPLORE phase complete (evidence documented)

**Governed Activities:**
- file-read (allow)
- file-write, file-edit (allow)
- user-query (allow)

**Output Contract:**
- Hypotheses table with confidence and test method
- Scope defined (in/out)

**Template Content:**
```markdown
## Hypotheses
| # | Hypothesis | Confidence | Test Method |
|---|------------|------------|-------------|
| H1 | | High/Med/Low | |
```

#### VALIDATE.md (~35 lines)

**Input Contract:**
- HYPOTHESIZE phase complete (hypotheses defined)

**Governed Activities:**
- shell-execute (allow)
- file-read (allow)
- memory-search (allow)

**Output Contract:**
- Verdict for each hypothesis (Confirmed/Refuted/Inconclusive)
- Key evidence cited with sources

**Template Content:**
```markdown
## Hypothesis Verdicts
| Hypothesis | Verdict | Key Evidence |
|------------|---------|--------------|
| H1 | | |
```

#### CONCLUDE.md (~40 lines)

**Input Contract:**
- VALIDATE phase complete (verdicts documented)

**Governed Activities:**
- file-write (allow)
- memory-store (allow)
- skill-invoke (allow - for spawning work)

**Output Contract:**
- Spawned work items created (or rationale if none)
- Memory stored with memory_refs populated
- Findings synthesized

**Template Content:**
```markdown
## Spawned Work
| ID | Title | spawned_by |
|----|-------|------------|

## Memory Storage
- [ ] ingester_ingest called
- [ ] memory_refs populated in WORK.md
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep old investigation.md | Preserve for backward compatibility | Existing documents reference it; skills can migrate gradually |
| Use frontmatter with phase field | `phase: EXPLORE` etc. | Enables template routing by phase |
| Reference activity_matrix.yaml | List activities from matrix, not hardcode | Single source of truth for governed activities |
| ~35 lines per template | Within 30-50 line budget | Sufficient for contracts + minimal structure without bloat |
| Phase maps to state | EXPLORE→EXPLORE, HYPOTHESIZE→DESIGN, etc. | Matches activity_matrix.yaml phase_to_state mapping |

### Edge Cases

| Case | Handling |
|------|----------|
| Multi-session investigation | Each session reads phase template for current phase |
| Phase skipped | Agent must provide SKIPPED rationale per template governance |
| Activity blocked | Agent sees governance message, adjusts approach |

---

## Open Decisions (MUST resolve before implementation)

**No unresolved operator decisions.** Work item WORK-043 has no `operator_decisions` field - requirements are clear from Templates arc and E2.4 EPOCH.md.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | - | - | Requirements defined in arc: 4 phase templates, contract pattern, 30-50 lines each |

---

## Implementation Steps

### Step 1: Create investigation/ directory
- [ ] Create `.claude/templates/investigation/` directory

### Step 2: Create EXPLORE.md
- [ ] Create `.claude/templates/investigation/EXPLORE.md`
- [ ] Add frontmatter with `phase: EXPLORE`
- [ ] Add Input Contract (work item exists)
- [ ] Add Governed Activities from activity_matrix.yaml EXPLORE state
- [ ] Add Output Contract (evidence documented)
- [ ] Add Template section with evidence collection structure
- [ ] Verify ~35 lines

### Step 3: Create HYPOTHESIZE.md
- [ ] Create `.claude/templates/investigation/HYPOTHESIZE.md`
- [ ] Add frontmatter with `phase: HYPOTHESIZE`
- [ ] Add Input Contract (EXPLORE complete)
- [ ] Add Governed Activities from activity_matrix.yaml DESIGN state
- [ ] Add Output Contract (hypotheses defined)
- [ ] Add Template section with hypothesis table
- [ ] Verify ~35 lines

### Step 4: Create VALIDATE.md
- [ ] Create `.claude/templates/investigation/VALIDATE.md`
- [ ] Add frontmatter with `phase: VALIDATE`
- [ ] Add Input Contract (HYPOTHESIZE complete)
- [ ] Add Governed Activities from activity_matrix.yaml CHECK state
- [ ] Add Output Contract (verdicts documented)
- [ ] Add Template section with verdict table
- [ ] Verify ~35 lines

### Step 5: Create CONCLUDE.md
- [ ] Create `.claude/templates/investigation/CONCLUDE.md`
- [ ] Add frontmatter with `phase: CONCLUDE`
- [ ] Add Input Contract (VALIDATE complete)
- [ ] Add Governed Activities from activity_matrix.yaml DONE state
- [ ] Add Output Contract (spawned work, memory stored)
- [ ] Add Template section with spawned work and memory structure
- [ ] Verify ~40 lines

### Step 6: Create Chapter File
- [ ] Create `.claude/haios/epochs/E2_4/arcs/templates/CH-001-InvestigationFracture.md`
- [ ] Document design decisions with WHY
- [ ] Reference all 4 template files
- [ ] Link to Templates arc

### Step 7: Store to Memory
- [ ] `ingester_ingest` with design decisions and WHY
- [ ] Update WORK-043 memory_refs

### Step 8: README Sync
- [ ] Create `.claude/templates/investigation/README.md` documenting phase templates
- [ ] Update `.claude/templates/README.md` if it exists

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment | Low | Templates arc clearly defines contract pattern; activity_matrix.yaml is authoritative source |
| Integration | Low | Templates are passive markdown; skills read but don't execute them |
| Regression | Low | Old investigation.md preserved; new templates are additive |
| Scope creep | Low | Work item has 6 specific deliverables; no runtime code needed |
| Knowledge gaps | Low | activity_matrix.yaml already exists and is well-documented |

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

**MUST** read `docs/work/active/WORK-043/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| EXPLORE.md | [ ] | Read file, verify ~35 lines with contracts |
| HYPOTHESIZE.md | [ ] | Read file, verify ~35 lines with contracts |
| VALIDATE.md | [ ] | Read file, verify ~35 lines with contracts |
| CONCLUDE.md | [ ] | Read file, verify ~40 lines with contracts |
| CH-001-InvestigationFracture.md | [ ] | Chapter file exists with design decisions |
| Memory stored | [ ] | memory_refs populated in WORK-043 |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/templates/investigation/EXPLORE.md` | ~35 lines, Input/Output/Activities/Template | [ ] | |
| `.claude/templates/investigation/HYPOTHESIZE.md` | ~35 lines, Input/Output/Activities/Template | [ ] | |
| `.claude/templates/investigation/VALIDATE.md` | ~35 lines, Input/Output/Activities/Template | [ ] | |
| `.claude/templates/investigation/CONCLUDE.md` | ~40 lines, Input/Output/Activities/Template | [ ] | |
| `.claude/haios/epochs/E2_4/arcs/templates/CH-001-InvestigationFracture.md` | Design decisions documented | [ ] | |
| `.claude/templates/investigation/README.md` | Directory documented | [ ] | |

**Verification Commands:**
```bash
# Count lines in each template
wc -l .claude/templates/investigation/*.md
# Expected: Each ~30-50 lines
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Line counts within 30-50 range? | [Yes/No] | |
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

- @.claude/haios/epochs/E2_4/arcs/templates/ARC.md (arc definition)
- @.claude/haios/epochs/E2_4/EPOCH.md (Decision 6: Fractured Templates)
- @.claude/templates/investigation.md (current monolithic template)
- @.claude/haios/config/activity_matrix.yaml (governed activities source)
- @docs/work/active/WORK-036/ (Template Tax investigation)
- Memory: 82724-82728 (Session 265 fractured templates decisions)

---
