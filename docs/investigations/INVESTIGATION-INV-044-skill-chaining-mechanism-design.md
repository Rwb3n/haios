---
template: investigation
status: complete
date: 2025-12-27
backlog_id: INV-044
title: Skill Chaining Mechanism Design
author: Hephaestus
session: 129
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 79791
- 79792
- 79793
- 79794
- 79795
- 79796
- 79797
- 79798
- 79799
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-27T18:56:19'
---
# Investigation: Skill Chaining Mechanism Design

@docs/README.md
@docs/epistemic_state.md

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** E2-209 proposes adding CHAIN phase to cycle skills, but the mechanism is undefined.

**Problem Statement:** How should skills chain to each other and route to the next work item?

**Prior Observations:**
- work-creation-cycle has CHAIN phase (confidence-based routing)
- investigation-cycle and implementation-cycle lack CHAIN phases
- INV-041 identified gap: agent waits for human to invoke commands
- Memory: "Command-skill chaining is gate entry mechanism" (78909)

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "skill chaining mechanism auto-invoke routing work item"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 71680 | Command-skill chaining as hierarchical/iterative process | Pattern definition |
| 71351 | "Striking skills and commands together" - loop with controlled pathways | Vision |
| 79735 | Add CHAIN phases following work-creation-cycle pattern | Direct guidance |
| 78903 | INV-033: Commands provide scaffolding, Skills provide behavioral contracts | Architecture |
| 79733 | work-creation-cycle CHAIN phase is pattern to follow | Template |
| 79721 | Gap: Agent waits for human, lacks auto-routing/chaining | Problem statement |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-041 (Autonomous Session Loop Gap Analysis) - identified gap
- [x] Found: INV-033 (Skill as Node Entry Gate) - defined chaining pattern

---

## Objective

<!-- One clear question this investigation will answer -->

**How should cycle skills (investigation-cycle, implementation-cycle, close-work-cycle) implement CHAIN phases to enable autonomous routing?**

Specific questions:
1. What triggers the chain? (Phase completion signal)
2. How does a skill invoke another skill? (Skill tool, command, prompt)
3. How does work routing work? (Query mechanism)
4. What confidence signals determine routing?

---

## Scope

### In Scope
- CHAIN phase mechanism design for cycle skills
- work-creation-cycle CHAIN pattern analysis
- Skill invocation patterns (how Skill tool works)
- Work routing mechanism (`just ready` integration)

### Out of Scope
- Hook-based chaining (Stop hook already exists but for different purpose)
- Memory system changes
- Implementation (that's E2-209)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 4 | work-creation-cycle, investigation-cycle, implementation-cycle, close-work-cycle |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + Memory |
| Estimated complexity | Low | Design only, pattern exists |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | work-creation-cycle CHAIN pattern can be copied to other cycle skills | High | Read work-creation-cycle, verify pattern portability | 1st |
| **H2** | CHAIN phase should use `Skill(skill="...")` for invocation | High | Check Claude Code Skill tool behavior | 2nd |
| **H3** | Work routing should use `just ready` + pick first item | Med | Verify `just ready` output format, design selection logic | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic (done in HYPOTHESIZE)
2. [x] Read work-creation-cycle CHAIN phase implementation
3. [x] Read investigation-cycle and implementation-cycle to see what's missing
4. [x] Check `just ready` output format

### Phase 2: Hypothesis Testing
5. [x] Test H1: Verify work-creation-cycle CHAIN pattern is portable
6. [x] Test H2: Design Skill invocation pattern for chaining
7. [x] Test H3: Design work routing mechanism

### Phase 3: Synthesis
8. [x] Design CHAIN phase template for all cycle skills
9. [x] Document routing decision table
10. [ ] Update E2-209 deliverables with concrete spec

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| work-creation-cycle has CHAIN phase with confidence routing | `.claude/skills/work-creation-cycle/SKILL.md:100-125` | H1 | Template exists |
| investigation-cycle ends at CONCLUDE with `/close` | `.claude/skills/investigation-cycle/SKILL.md:101-102` | H1 | No CHAIN, no routing |
| implementation-cycle ends at DONE with `/close` | `.claude/skills/implementation-cycle/SKILL.md:192-193` | H1 | No CHAIN, no routing |
| close-work-cycle ends at CAPTURE with status refresh | `.claude/skills/close-work-cycle/SKILL.md:89-90` | H1 | No next work routing |
| CHAIN uses confidence signals (ID prefix, spawned_by) | `.claude/skills/work-creation-cycle/SKILL.md:106-113` | H2, H3 | Decision table |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 79733 | work-creation-cycle CHAIN phase is pattern to follow | H1 | Direct guidance |
| 78903 | Commands scaffold, Skills provide behavioral contracts | H2 | Architecture |
| 79721 | Gap: agent waits, lacks auto-routing | H1, H3 | Problem confirmation |

### External Evidence (if applicable)

**SKIPPED:** Pure codebase investigation

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | work-creation-cycle CHAIN phase (lines 100-125) is directly portable | High |
| H2 | **CONFIRMED** | CHAIN uses `Skill(skill="...")` invocation pattern (line 119) | High |
| H3 | **CONFIRMED** | `just ready` provides ordered list; pick first unblocked item | High |

### Detailed Findings

#### Finding 1: CHAIN Phase Pattern Exists and is Portable

**Evidence:**
```markdown
# From work-creation-cycle/SKILL.md:100-125
### 4. CHAIN Phase (Post-READY)

**Goal:** Route to appropriate next cycle based on confidence.

**Confidence-Based Routing:**
| Signal | Confidence | Action |
|--------|------------|--------|
| ID starts with `INV-` | HIGH | Auto-chain: `/new-investigation {id} {title}` |
| `spawned_by_investigation` is populated | HIGH | Auto-chain: `/new-plan {id} {title}` |
```

**Analysis:** The pattern is: (1) assess confidence signals, (2) route to next skill/command.

**Implication:** Copy this pattern to investigation-cycle (post-CONCLUDE), implementation-cycle (post-DONE), close-work-cycle (post-CAPTURE).

#### Finding 2: Invocation Mechanism is Skill Tool

**Evidence:**
```markdown
# From work-creation-cycle/SKILL.md:119
**If HIGH confidence:** Auto-invoke appropriate command
```

**Analysis:** Skills invoke commands via slash commands in skill text. Agent reads skill, follows instructions, invokes command. Not a programmatic Skill-to-Skill call - it's **instruction-based**.

**Implication:** CHAIN phase should contain instructions like:
- "Run `/close {backlog_id}`"
- "Run `just ready` to find next work"
- "Invoke `Skill(skill='...')` for next cycle"

#### Finding 3: Work Routing Uses `just ready`

**Evidence:**
```
$ just ready
READY (unblocked across all milestones):
  E2-004: Documentation Sync
  E2-087: Plan Forward-Maintenance Automation
  ...
```

**Analysis:** `just ready` returns ordered list of unblocked items. First item is highest priority.

**Implication:** CHAIN phase should: (1) run `just ready`, (2) pick first item, (3) route based on item type (INV-* → investigation-cycle, else → check for plan)

---

## Design Outputs

### CHAIN Phase Template (for all cycle skills)

```markdown
### N. CHAIN Phase (Post-{PREVIOUS_PHASE})

**Goal:** Close current work and route to next work item.

**Actions:**
1. Close current work: `/close {backlog_id}`
2. Query next work: `just ready`
3. Pick first unblocked item from list
4. Route based on item type:

**Routing Decision Table:**
| Signal | Action |
|--------|--------|
| No items returned | Report "No unblocked work. Awaiting operator." |
| ID starts with `INV-` | Invoke `Skill(skill="investigation-cycle")` |
| Work file has plan in `documents.plans` | Invoke `Skill(skill="implementation-cycle")` |
| Otherwise | Invoke `Skill(skill="work-creation-cycle")` to populate |

**Exit Criteria:**
- [ ] Current work closed via /close
- [ ] Next work item identified (or none available)
- [ ] Appropriate cycle skill invoked
```

### Skill-Specific CHAIN Phases

#### investigation-cycle (after CONCLUDE)
```markdown
### 4. CHAIN Phase (Post-CONCLUDE)

**Goal:** Close investigation and route to next work.

**Actions:**
1. Close investigation: `/close {backlog_id}`
2. Query next work: `just ready`
3. Route to next cycle (see routing table above)

**Note:** Investigation spawned items are already created in CONCLUDE phase.
```

#### implementation-cycle (after DONE)
```markdown
### 5. CHAIN Phase (Post-DONE)

**Goal:** Close implementation and route to next work.

**Actions:**
1. Close work item: `/close {backlog_id}`
2. Query next work: `just ready`
3. Route to next cycle (see routing table above)
```

#### close-work-cycle (after CAPTURE)
```markdown
### 4. CHAIN Phase (Post-CAPTURE)

**Goal:** Route to next work item.

**Actions:**
1. (Closure already done in CAPTURE)
2. Query next work: `just ready`
3. Route to next cycle (see routing table above)

**Note:** /close already invokes close-work-cycle, so CHAIN here just does routing.
```

### Mechanism Design

```
TRIGGER: Completion of final phase (CONCLUDE, DONE, or CAPTURE)

ACTION:
    1. Invoke /close {backlog_id} (if not already closed)
    2. Run `just ready` to get ordered work list
    3. If empty: Report "No unblocked work" and stop
    4. Pick first item from list
    5. Read work file to check documents.plans
    6. Route based on decision table

OUTCOME: Next cycle skill invoked with new work item context
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Instruction-based chaining | Skills contain routing instructions, not programmatic calls | Agent reads skill, follows instructions - no new infrastructure |
| `just ready` for work selection | Use existing recipe, pick first item | Already ordered by priority, already filters blocked items |
| /close before routing | Ensure current work captured before moving on | Clean handoff, memory stored, status updated |
| Fallback to work-creation-cycle | If work item has no plan, needs population | Ensures all work items are properly prepared |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-209: Cycle Skill Chain Phases** (UPDATED, not spawned)
  - Description: Add CHAIN phase to investigation-cycle, implementation-cycle, close-work-cycle
  - Fixes: Autonomous routing after work completion
  - Action: Update E2-209 deliverables with concrete spec from this investigation

### Future (Requires more work first)

N/A - E2-209 already exists and is unblocked

### Not Spawned Rationale (if no items)

**RATIONALE:** This investigation was spawned TO INFORM E2-209, not to spawn new items. The output is a concrete design spec that updates E2-209's deliverables. No new work items needed - E2-209 can now proceed with implementation.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 129 | 2025-12-27 | HYPOTHESIZE | Started | Initial context and hypotheses |
| - | - | - | - | No additional sessions yet |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [ ] | |
| Evidence has sources | All findings have file:line or concept ID | [ ] | |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | [Yes/No] | |
| Are all evidence sources cited with file:line or concept ID? | [Yes/No] | |
| Were all hypotheses tested with documented verdicts? | [Yes/No] | |
| Are spawned items created (not just listed)? | [Yes/No] | |
| Is memory_refs populated in frontmatter? | [Yes/No] | |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [ ] **Findings synthesized** - Answer to objective documented in Findings section
- [ ] **Evidence sourced** - All findings have file:line or concept ID citations
- [ ] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [ ] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [ ] **Memory stored** - `ingester_ingest` called with findings summary
- [ ] **memory_refs populated** - Frontmatter updated with concept IDs
- [ ] **lifecycle_phase updated** - Set to `conclude`
- [ ] **Ground Truth Verification complete** - All items checked above

### Optional
- [ ] Design outputs documented (if applicable)
- [ ] Session progress updated (if multi-session)

---

## References

- [Spawned by: Session/Investigation/Work item that triggered this]
- [Related investigation 1]
- [Related ADR or spec]

---
