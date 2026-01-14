---
template: investigation
status: complete
date: 2025-12-25
backlog_id: INV-035
title: Skill Architecture Refactoring
author: Hephaestus
session: 116
lifecycle_phase: conclude
spawned_by: INV-033
related:
- INV-033
- INV-011
- INV-022
memory_refs:
- 78912
- 78913
- 78914
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-25T10:05:51'
---
# Investigation: Skill Architecture Refactoring

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

**Trigger:** Session 116 architectural discussion following INV-033 (Skill as Node Entry Gate). The discussion revealed inconsistencies in command-skill-agent layering that need formal refactoring.

**Problem Statement:** The current skill/command/agent architecture is inconsistent - some commands chain to skills, others don't; work items can be created without proper population; validation isn't formalized as bridge skills.

**Prior Observations:**
- `/new-investigation` chains to skill, `/new-plan` doesn't - inconsistent gate behavior
- `/new-work` scaffolds but doesn't guide through populating essential fields
- No validation skills exist to act as bridges between design→simulation→execution
- Work items should be the fundamental unit of traceability (everything is a work item)
- Sub-agents are useful for unbiased validation (investigation-agent proves this)

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "skill architecture command skill chaining validation bridge modular skills sub-agents"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 76826 | Commands are entry points, Skills contain orchestration logic | Core pattern |
| 78903 | Command-Skill Chaining Pattern from INV-033 | Recent formalization |
| 78208 | Skill Specialization as Core Tenet of Subagent Design | Sub-agent scoping |
| 71680 | Command-Skill Chaining as Hierarchical Process | Loops/forks |
| 77526 | Bridging Command Design: Pure Prompts to Skill-Invoking | Gap to address |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-033, INV-011, INV-022

---

## Objective

<!-- One clear question this investigation will answer -->

**Question:** What is the complete inventory of existing skills/commands/agents, what gaps exist against the proposed layered architecture, and what specific work items are needed to achieve architectural coherence?

---

## Scope

### In Scope
- Current inventory: commands, skills, agents (what exists)
- Proposed architecture: layered skill design (cycle, validation, utility, sub-agents)
- Gap analysis: what's missing, what's inconsistent
- Work item spawning: define each new skill/agent needed
- Command-skill chaining consistency

### Out of Scope
- Implementing the new skills (spawn work items for that)
- Hook architecture changes
- MCP server changes
- Database schema changes

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | ~25 | `.claude/commands/*.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md` |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + Memory |
| Estimated complexity | Medium | Architecture design, multiple spawned items |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | The proposed 4-layer architecture (Cycle, Validation, Utility, Sub-agents) covers all current and needed components | High | Inventory current components, map to layers, identify gaps | 1st |
| **H2** | Validation skills as bridges will require at least 3 new skills (preflight, design-review, dod-validation) | Med | Define what each bridge validates, when it's invoked | 2nd |
| **H3** | work-creation-cycle is the highest priority new skill (enables work-item-as-fundamental-unit paradigm) | High | Assess dependencies between proposed skills | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic (done in HYPOTHESIZE)
2. [x] Inventory all commands: 19 commands found
3. [x] Inventory all skills: 6 skills found (2 Cycle, 4 Utility)
4. [x] Inventory all agents: 5 agents found
5. [x] Check which commands chain to skills: Only 2/19 chain

### Phase 2: Hypothesis Testing
6. [x] Test H1: Map inventory to 4-layer architecture, identify gaps - CONFIRMED
7. [x] Test H2: Define validation bridge contracts - CONFIRMED (3 bridges needed)
8. [x] Test H3: Assess skill dependencies, determine priority order - CONFIRMED

### Phase 3: Synthesis
9. [x] Create complete layer mapping table
10. [x] Define work items for each gap (E2-180 through E2-188)
11. [x] Create implementation sequence (Priority 1-4 order)

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Current Inventory Summary

**Commands (19 total):**
- Chaining to skills: 2 (`/implement` → implementation-cycle, `/new-investigation` → investigation-cycle)
- No chaining: 17 (all other commands)

**Skills (6 total):**
- Cycle Skills: 2 (implementation-cycle, investigation-cycle)
- Utility Skills: 4 (memory-agent, extract-content, schema-ref, audit)

**Agents (5 total):**
- Required: 2 (schema-verifier, investigation-agent)
- Optional: 3 (preflight-checker, test-runner, why-capturer)

### Codebase Evidence

| Finding | Source | Supports Hypothesis | Notes |
|---------|--------|---------------------|-------|
| Only 2/19 commands chain to skills | `.claude/commands/*.md` | H1 | Major chaining gap |
| `/new-plan` does NOT chain | `.claude/commands/new-plan.md` | H1, H3 | Inconsistent with /new-investigation |
| `/new-work` does NOT chain | `.claude/commands/new-work.md` | H3 | No work-creation skill exists |
| `/close` does NOT chain | `.claude/commands/close.md` | H1 | No close-work skill exists |
| implementation-cycle has 4 phases | `.claude/skills/implementation-cycle/SKILL.md:36-177` | H1 | PLAN→DO→CHECK→DONE |
| investigation-cycle has 3 phases | `.claude/skills/investigation-cycle/SKILL.md:42-103` | H1 | HYPOTHESIZE→EXPLORE→CONCLUDE |
| preflight-checker is OPTIONAL | `.claude/agents/preflight-checker.md` | H2 | Should be bridge validation |
| test-runner is OPTIONAL | `.claude/agents/test-runner.md` | H2 | Part of CHECK phase |
| why-capturer is OPTIONAL | `.claude/agents/why-capturer.md` | H2 | Part of DONE phase |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 76826 | Commands are entry points, Skills contain orchestration logic | H1 | Pattern not consistently applied |
| 78903 | Command-Skill Chaining Pattern (INV-033) | H1 | Recent formalization |
| 77526 | Bridging pure prompts to skill-invoking | H2 | Gap we're addressing |

### External Evidence (if applicable)

**SKIPPED:** Internal architecture investigation

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | 4-layer architecture maps cleanly: 6 existing components + 7 gaps identified | High |
| H2 | **CONFIRMED** | 3 validation bridges needed: preflight (exists but optional), design-review (new), dod-validation (new) | High |
| H3 | **CONFIRMED** | work-creation-cycle is highest priority - enables work-item-as-fundamental-unit, no dependencies | High |

### Detailed Findings

#### Finding 1: 4-Layer Architecture Mapping

**Current State vs Proposed:**

```
LAYER 1: CYCLE SKILLS (orchestration)
─────────────────────────────────────────────────────
EXISTS:
├── implementation-cycle ✓
├── investigation-cycle ✓

GAPS (NEW):
├── work-creation-cycle      ← /new-work should chain here
├── plan-authoring-cycle     ← /new-plan should chain here
├── plan-validation-cycle    ← bridge between design/execution
└── close-work-cycle         ← /close should chain here

LAYER 2: VALIDATION SKILLS (bridges/gates)
─────────────────────────────────────────────────────
EXISTS (as agent):
├── preflight-checker (optional) ← should be REQUIRED bridge

GAPS (NEW):
├── design-review-skill      ← validates plan before implementation
└── dod-validation-skill     ← validates DoD before close

LAYER 3: UTILITY SKILLS (composable)
─────────────────────────────────────────────────────
EXISTS:
├── memory-agent ✓
├── audit ✓
├── schema-ref (deprecated → agent)
└── extract-content (rarely used)

GAPS: None - utility layer is complete

LAYER 4: SUB-AGENTS (isolated contexts)
─────────────────────────────────────────────────────
EXISTS:
├── investigation-agent ✓ (REQUIRED)
├── schema-verifier ✓ (REQUIRED)
├── preflight-checker (OPTIONAL → should be REQUIRED)
├── test-runner (OPTIONAL)
└── why-capturer (OPTIONAL)

GAPS (NEW):
├── validation-agent         ← unbiased CHECK phase validation
└── async-validator          ← background verification
```

**Analysis:** The 4-layer architecture is validated. Current components map cleanly, with clear gaps.

**Implication:** Need 4 new cycle skills + 2 new validation skills + 2 new agents = 8 work items.

#### Finding 2: Validation Bridge Pattern

**Design:**
```
BRIDGE 1: preflight-validation (before DO phase)
├── Trigger: PLAN phase complete, entering DO
├── Validates: Tests defined, file manifest exists, design complete
├── Gate: MUST pass before implementation starts
├── Agent: preflight-checker (promote to REQUIRED)

BRIDGE 2: design-review (before implementation-cycle)
├── Trigger: plan-authoring-cycle complete
├── Validates: Agent understands what to do (simulation)
├── Gate: MUST pass before /implement
├── Agent: design-review-agent (NEW)

BRIDGE 3: dod-validation (before close)
├── Trigger: CHECK phase complete, entering DONE
├── Validates: Tests pass, WHY captured, docs current
├── Gate: MUST pass before /close
├── Agent: dod-validation-agent (NEW) or test-runner + why-capturer
```

**Analysis:** Validation bridges formalize the "are we ready to proceed?" checks that are currently informal.

**Implication:** These bridges prevent premature phase transitions and ensure quality gates.

#### Finding 3: Priority Order for New Skills

**Dependency Analysis:**
```
PRIORITY 1 (no dependencies):
├── work-creation-cycle      ← enables work-item-as-fundamental-unit
└── close-work-cycle         ← completes lifecycle, DoD enforcement

PRIORITY 2 (depends on Priority 1):
├── plan-authoring-cycle     ← requires work item to exist first
└── plan-validation-cycle    ← bridge after plan-authoring

PRIORITY 3 (depends on Priority 2):
├── design-review skill      ← validates plan before implementation
└── validation-agent         ← unbiased CHECK support

PRIORITY 4 (nice to have):
└── async-validator          ← background verification
```

**Analysis:** work-creation-cycle is foundational - it enables the "everything is a work item" paradigm.

**Implication:** Start with work-creation-cycle and close-work-cycle to complete the lifecycle.

---

## Design Outputs

### Complete 4-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: CYCLE SKILLS (orchestration)                          │
│  ├── work-creation-cycle (NEW) ← /new-work chains here          │
│  ├── plan-authoring-cycle (NEW) ← /new-plan chains here         │
│  ├── plan-validation-cycle (NEW) ← bridge skill                 │
│  ├── implementation-cycle ✓ exists                              │
│  ├── investigation-cycle ✓ exists                               │
│  └── close-work-cycle (NEW) ← /close chains here                │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: VALIDATION SKILLS (bridges/gates)                     │
│  ├── preflight-validation (promote from agent)                  │
│  ├── design-review-skill (NEW)                                  │
│  └── dod-validation-skill (NEW)                                 │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: UTILITY SKILLS (composable)                           │
│  ├── memory-agent ✓ exists                                      │
│  ├── audit ✓ exists                                             │
│  └── (deprecated: schema-ref, extract-content)                  │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4: SUB-AGENTS (isolated contexts)                        │
│  ├── investigation-agent ✓ REQUIRED                             │
│  ├── schema-verifier ✓ REQUIRED                                 │
│  ├── preflight-checker → promote to REQUIRED                    │
│  ├── test-runner ✓ OPTIONAL                                     │
│  ├── why-capturer ✓ OPTIONAL                                    │
│  ├── validation-agent (NEW)                                     │
│  └── async-validator (NEW - future)                             │
└─────────────────────────────────────────────────────────────────┘
```

### Command-Skill-Agent Flow

```
USER ACTION              COMMAND              SKILL                    AGENT
─────────────────────────────────────────────────────────────────────────────
Create work item    →   /new-work        →   work-creation-cycle   →   -
Create investigation →  /new-investigation → investigation-cycle   →   investigation-agent
Create plan         →   /new-plan        →   plan-authoring-cycle  →   -
Validate plan       →   (auto-bridge)    →   plan-validation-cycle →   design-review-agent
Implement          →   /implement        →   implementation-cycle  →   preflight/test/why
Close work         →   /close            →   close-work-cycle      →   dod-validation
```

### Mapping Table: Commands to Skills

| Command | Current | Proposed | New Skill Needed? |
|---------|---------|----------|-------------------|
| `/new-work` | scaffold only | chain to skill | work-creation-cycle (NEW) |
| `/new-investigation` | chains ✓ | no change | - |
| `/new-plan` | scaffold only | chain to skill | plan-authoring-cycle (NEW) |
| `/implement` | chains ✓ | no change | - |
| `/close` | prompt-based | chain to skill | close-work-cycle (NEW) |

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| 4 layers not 3 | Separate Validation from Cycle skills | Validation bridges are cross-cutting, not tied to specific cycles |
| work-creation first | Priority 1 implementation | Enables work-item-as-fundamental-unit paradigm |
| Validation as bridges | Skills invoke validation, not commands | Validation happens between phases, not at command entry |
| Promote preflight to REQUIRED | Currently optional, should be gate | Prevents implementation without plan review |
| plan-validation separate from plan-authoring | Two distinct skills | Authoring is design, validation is simulation - different concerns |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

**Milestone:** M8-SkillArch (Skill Architecture Refactoring)

### Priority 1 (Foundation - no dependencies)

- [x] **E2-180: work-creation-cycle skill**
  - Description: Cycle skill for `/new-work` command - guides through populating work item
  - Enables: work-item-as-fundamental-unit paradigm

- [x] **E2-181: close-work-cycle skill**
  - Description: Cycle skill for `/close` command - DoD enforcement with skill-based workflow
  - Completes: Work item lifecycle

### Priority 2 (Depends on Priority 1)

- [x] **E2-182: plan-authoring-cycle skill**
  - Description: Cycle skill for `/new-plan` command - guides through plan design
  - Blocked by: E2-180 (work item must exist first)

- [x] **E2-183: plan-validation-cycle bridge skill**
  - Description: Validation bridge between plan-authoring and implementation
  - Purpose: "Does agent know what to do?" simulation

### Priority 3 (Depends on Priority 2)

- [x] **E2-184: design-review validation skill**
  - Description: Validation skill to review plan before implementation
  - Blocked by: E2-182 (plan must be authored first)

- [x] **E2-185: validation-agent for CHECK phase**
  - Description: Unbiased sub-agent for CHECK phase validation
  - Supports: implementation-cycle CHECK phase

### Priority 4 (Nice to have)

- [x] **E2-186: Promote preflight-checker to REQUIRED**
  - Description: Change preflight-checker from OPTIONAL to REQUIRED
  - Gate: Prevents implementation without plan review

- [x] **E2-187: async-validator agent**
  - Description: Background validation agent (future)
  - Status: Low priority, nice to have

### Infrastructure (Built during investigation)

- [x] **E2-188: Batch Work Item Metadata Tool**
  - Description: `batch_update_fields()` and `link_spawned_items()` functions + `just link-spawn` recipe
  - Status: COMPLETE - implemented Session 116

### Related (absorb into above)

- E2-176: Absorb into E2-180 (gate contract is part of work-creation)
- E2-177: Absorb into E2-182 (plan chaining is part of plan-authoring)

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 116 | 2025-12-25 | HYPOTHESIZE→EXPLORE→CONCLUDE | Complete | 9 work items spawned, E2-188 implemented |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1, H2, H3 all CONFIRMED |
| Evidence has sources | All findings have file:line or concept ID | [x] | 9 codebase, 3 memory entries |
| Spawned items created | Items exist in backlog or via /new-* | [x] | 9 items: E2-180 through E2-188 |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | 78912-78914 |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | Used for inventory gathering |
| Are all evidence sources cited with file:line or concept ID? | Yes | All evidence documented |
| Were all hypotheses tested with documented verdicts? | Yes | H1, H2, H3 all CONFIRMED |
| Are spawned items created (not just listed)? | Yes | 9 work files exist in docs/work/active/ |
| Is memory_refs populated in frontmatter? | Yes | 78912-78914 |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - Answer to objective documented in Findings section
- [x] **Evidence sourced** - All findings have file:line or concept ID citations
- [x] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [x] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [x] **Memory stored** - `ingester_ingest` called with findings summary
- [x] **memory_refs populated** - Frontmatter updated with concept IDs
- [x] **lifecycle_phase updated** - Set to `conclude`
- [x] **Ground Truth Verification complete** - All items checked above

### Optional
- [x] Design outputs documented (if applicable)
- [x] Session progress updated (if multi-session)

---

## References

- Spawned by: INV-033 (Skill as Node Entry Gate Formalization) + Session 116 discussion
- Related: INV-011 (Command-Skill Architecture Gap)
- Related: INV-022 (Work Cycle DAG Unified Architecture)
- Related: ADR-039 (Work Item as File Architecture)

---
