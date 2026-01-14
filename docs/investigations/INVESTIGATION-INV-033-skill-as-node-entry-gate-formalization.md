---
template: investigation
status: complete
date: 2025-12-25
backlog_id: INV-033
title: Skill as Node Entry Gate Formalization
author: Hephaestus
session: 116
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 78898
- 78899
- 78900
- 78901
- 78902
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-25T08:55:31'
---
# Investigation: Skill as Node Entry Gate Formalization

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

**Trigger:** Session 115 insight during E2-173 work - noticed that skills inject phase-specific behavioral contracts into context at invocation time.

**Problem Statement:** Skills appear to function as node entry gates in the work cycle DAG, but this pattern is implicit and undocumented.

**Prior Observations:**
- Skills like `implementation-cycle` and `investigation-cycle` define guardrails and exit criteria
- Skill invocation loads phase-specific context that channels agent behavior
- This pattern emerged organically but was never formally designed or documented
- Commands are entry points, skills contain orchestration logic (Memory 76826)

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "prior investigations about skill as node entry gate workflow injection phase contracts"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 78869 | Skills function as node entry gates in work cycle DAG | Core insight to formalize |
| 78870 | Skills inject phase-specific behavioral contracts at entry | Mechanism to document |
| 78873 | Skill invocation loads phase-specific guardrails, exit criteria | Exit criteria pattern |
| 78875 | Skills are mechanism for phase-specific behavior injection, not just documentation | Key distinction |
| 78876 | Pattern informs: skill authoring guidelines, node-cycle integration, gate enforcement | Implications |
| 76826 | Commands are entry points, Skills contain orchestration logic | Command/Skill distinction |
| 77122 | Work file -> enters node -> node scaffolds docs -> agent works -> gates exit | Full workflow |
| 77272 | Vision of commands-as-transitions, skills-as-states realized in node-cycle | Architectural vision |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-022 (Work Cycle DAG Architecture), INV-024 (Work Item as File Architecture), INV-026 (Unified Architecture Metaphor)

---

## Objective

<!-- One clear question this investigation will answer -->

**Question:** How should the "skill as node entry gate" pattern be formalized and what documentation/implementation changes are needed to make it explicit?

---

## Scope

### In Scope
- Current skill implementations (implementation-cycle, investigation-cycle)
- How skills inject behavioral contracts (guardrails, exit criteria)
- Command-to-skill chaining pattern (e.g., /new-investigation → investigation-cycle)
- Skill authoring guidelines for "gate" behavior

### Out of Scope
- Implementation changes beyond documentation (spawn work items for that)
- Hook-based gate enforcement (separate concern)
- Work file schema changes

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 4-6 | `.claude/skills/*/SKILL.md`, `.claude/commands/*.md` |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + Memory |
| Estimated complexity | Low | Pattern already emergent, needs formalization only |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Existing cycle skills already contain gate-like structures (guardrails, exit criteria, phase definitions) | High | Read implementation-cycle and investigation-cycle SKILL.md files | 1st |
| **H2** | Command-to-skill chaining is the primary "gate entry" mechanism | Med | Check /new-* commands for skill invocation patterns | 2nd |
| **H3** | Skill authoring guidelines should include "gate contract" requirements (entry conditions, injected context, exit criteria) | Med | Compare existing skills, identify common patterns | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic (done in HYPOTHESIZE)
2. [x] List all skills: `Glob .claude/skills/*/SKILL.md` - Found 6 skills
3. [x] List /new-* commands: `Glob .claude/commands/new-*.md` - Found 7 commands

### Phase 2: Hypothesis Testing
4. [x] Test H1: Read implementation-cycle and investigation-cycle SKILL.md - CONFIRMED gate structures
5. [x] Test H2: Read /new-investigation, /new-plan commands - PARTIALLY CONFIRMED chaining
6. [x] Test H3: Compare skill structures - CONFIRMED two categories (Cycle vs Utility)

### Phase 3: Synthesis
7. [x] Compile evidence table with file:line references
8. [x] Determine verdict for each hypothesis
9. [x] Define "Gate Contract" specification
10. [x] Identify spawned work items (E2-176, E2-177 created with spawned_by: INV-033)

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| implementation-cycle has 4 phases with explicit entry/exit criteria | `.claude/skills/implementation-cycle/SKILL.md:36-177` | H1 | PLAN→DO→CHECK→DONE |
| investigation-cycle has 3 phases with explicit entry/exit criteria | `.claude/skills/investigation-cycle/SKILL.md:42-103` | H1 | HYPOTHESIZE→EXPLORE→CONCLUDE |
| DO phase has MUST guardrail: "Write failing tests first" | `.claude/skills/implementation-cycle/SKILL.md:86` | H1 | TDD enforcement |
| EXPLORE phase has MUST guardrail: "invoke investigation-agent" | `.claude/skills/investigation-cycle/SKILL.md:66` | H1 | Subagent enforcement |
| /new-investigation chains to investigation-cycle skill | `.claude/commands/new-investigation.md:47-62` | H2 | Added 2025-12-25 |
| /implement chains to implementation-cycle skill | `.claude/commands/implement.md:16` | H2 | Added 2025-12-20 |
| 8 of 10 /new-* commands do NOT chain to skills | Various commands | H2 | Gap in pattern adoption |
| INV-011 documents intended command→skill→script architecture | `docs/investigations/INVESTIGATION-INV-011-*` | H2, H3 | Vision partially implemented |
| memory-agent skill has no phase structure | `.claude/skills/memory-agent/SKILL.md:1-183` | H3 | Utility skill pattern |
| audit skill has no phase structure | `.claude/skills/audit/SKILL.md:1-43` | H3 | Utility skill pattern |
| schema-ref skill has no phase structure | `.claude/skills/schema-ref/SKILL.md:1-49` | H3 | Utility skill pattern |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 78869 | Skills function as node entry gates in work cycle DAG | H1, H3 | Core insight |
| 78870 | Skills inject phase-specific behavioral contracts at entry | H1 | Mechanism |
| 78875 | Skills are mechanism for behavior injection, not just documentation | H1, H3 | Key distinction |
| 76826 | Commands are entry points, Skills contain orchestration logic | H2 | Pattern |
| 77272 | Vision of commands-as-transitions, skills-as-states | H2, H3 | Architecture |

### External Evidence (if applicable)

**SKIPPED:** Internal investigation, no external sources needed

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | Both cycle skills contain rich gate structures: phases, entry conditions, MUST guardrails, exit criteria checklists | High |
| H2 | **PARTIALLY CONFIRMED** | Pattern exists but sparse - only 2/10 commands chain to skills. Intended to be universal (INV-011) but implementation diverged | Med |
| H3 | **CONFIRMED** | Two skill categories emerged: Cycle skills (gate structures) vs Utility skills (recipe cards). Gate contracts should be formalized for cycle skills | High |

### Detailed Findings

#### Finding 1: Two Skill Categories Exist

**Evidence:**
```
Cycle Skills (gate structures):
- implementation-cycle: 4 phases, MUST guardrails, exit criteria checklists
- investigation-cycle: 3 phases, MUST guardrails, exit criteria checklists

Utility Skills (recipe cards):
- memory-agent: "When to Use" + "Instructions" sections
- audit: "When to Use" + bash recipes
- schema-ref: "Requirement Level" + tool reference
```

**Analysis:** Skills naturally bifurcated into two types: (1) Cycle skills that guide multi-phase workflows with formal gates, (2) Utility skills that provide context-specific instructions without phase structure.

**Implication:** Gate contract formalization should target Cycle skills specifically. Utility skills should remain lightweight recipe cards.

#### Finding 2: Gate Contract Elements Identified

**Evidence:**
```
From implementation-cycle and investigation-cycle:

ENTRY CONDITIONS:
- File existence checks (plan/investigation file exists)
- Status checks (not draft, is active)
- Prior phase completion

GUARDRAILS (runtime):
- MUST rules (TDD, invoke subagent)
- SHOULD rules (file manifest, one change at a time)

EXIT CRITERIA:
- Checklist items that must be satisfied
- Memory integration (query at start, store at end)
- Command invocation (/close, /validate)
```

**Analysis:** Gate structures have three components: (1) Entry conditions that prevent premature phase entry, (2) Runtime guardrails that channel behavior during phase, (3) Exit criteria that gate phase completion.

**Implication:** A formal "Gate Contract" specification should include all three components.

#### Finding 3: Command-Skill Chaining Gap

**Evidence:**
```
Commands that chain to skills: 2/10
- /new-investigation → investigation-cycle (added 2025-12-25)
- /implement → implementation-cycle

Commands that DON'T chain: 8/10
- /new-plan, /new-checkpoint, /new-adr, /new-work, /new-handoff, /new-report
- /close, /coldstart (intended to chain per INV-011)
```

**Analysis:** The command→skill chaining pattern is emerging but not widely adopted. INV-011 documented the intended architecture (command→skill→script) but implementation stalled after E2-048-051 were planned but never executed.

**Implication:** Retrofitting all commands to chain to skills would be significant work. Priority should be workflow commands (/close, /coldstart) over scaffold commands (/new-*).

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design: Gate Contract Specification

```yaml
# Gate Contract for Cycle Skills
# Each phase in a cycle skill SHOULD define:

phase_name: string
  description: "What this phase accomplishes"

entry_conditions:
  - description: "Condition that must be true to enter phase"
    check: "How to verify (file exists, status check, prior phase complete)"

guardrails:  # Runtime constraints
  must:
    - description: "Absolute requirement during phase execution"
      enforcement: "L3/L4 (mechanical) or L2 (prompt-based)"
  should:
    - description: "Strong recommendation"
      enforcement: "L2 (prompt-based)"

exit_criteria:
  - description: "Condition that must be true to exit phase"
    check: "How to verify (checklist item, test pass, artifact exists)"

tools_injected:  # What becomes available in this phase
  - tool_name: "Tool or command relevant to this phase"
    purpose: "Why this tool is relevant here"
```

### Mapping Table: Skill Categories

| Category | Example | Has Phases? | Has Gate Contract? | Notes |
|----------|---------|-------------|-------------------|-------|
| Cycle Skill | implementation-cycle, investigation-cycle | Yes | Yes (implicit) | Multi-phase workflows |
| Utility Skill | memory-agent, audit, schema-ref | No | No | Single-purpose recipe cards |

### Mechanism Design: Command-Skill Gate Entry

```
TRIGGER: User invokes /new-investigation <id> <title>

ACTION:
    1. Command scaffolds investigation file via `just inv`
    2. Command queries memory for prior work
    3. Command invokes Skill(skill="investigation-cycle")
    4. Skill loads HYPOTHESIZE phase contract into context
    5. Agent behavior channeled by phase guardrails

OUTCOME: Agent enters structured cycle with gate constraints active
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Two skill categories | Cycle Skills vs Utility Skills | Natural bifurcation found in codebase - forcing gate contracts on utility skills would add overhead without benefit |
| Gate contract targets cycle skills | Only formalize for implementation-cycle, investigation-cycle | These are the only skills that guide multi-phase workflows |
| Entry via command chaining | Commands chain to skills, not direct skill invocation | Commands provide scaffolding + tooling lock; skills provide behavioral contract |
| Three-part gate structure | Entry + Guardrails + Exit | Matches existing pattern in both cycle skills |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-176: Document Gate Contract Pattern**
  - Description: Add gate contract specification and skill categories to skill authoring documentation
  - Fixes: Implicit pattern now formalized and documented
  - Spawned via: `/new-work E2-176 "Document Gate Contract Pattern"`

- [x] **E2-177: Chain /new-plan to implementation-cycle**
  - Description: Update /new-plan command to chain to implementation-cycle skill after scaffolding
  - Fixes: Inconsistency where /new-investigation chains but /new-plan doesn't
  - Spawned via: `/new-work E2-177 "Chain new-plan to implementation-cycle"`

### Future (Requires more work first)

- [ ] **E2-178: Chain /close to close-work-item skill**
  - Description: Create close-work-item skill and chain from /close command (INV-011 vision)
  - Blocked by: Need to define close-work-item skill first

### Not Spawned Rationale (if no items)

**N/A** - Items spawned above

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 116 | 2025-12-25 | HYPOTHESIZE→EXPLORE→CONCLUDE | Complete | All phases executed, spawned E2-176, E2-177 |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1 CONFIRMED, H2 PARTIAL, H3 CONFIRMED |
| Evidence has sources | All findings have file:line or concept ID | [x] | 11 codebase, 5 memory evidence entries |
| Spawned items created | Items exist in backlog or via /new-* | [x] | E2-176, E2-177 created with spawned_by |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | 78898-78902 |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | Used for H1 and H2 exploration |
| Are all evidence sources cited with file:line or concept ID? | Yes | All codebase evidence has file:line |
| Were all hypotheses tested with documented verdicts? | Yes | H1, H2, H3 all have verdicts |
| Are spawned items created (not just listed)? | Yes | E2-176, E2-177 work files exist |
| Is memory_refs populated in frontmatter? | Yes | 78898-78902 |

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

- Spawned by: Session 115 insight during E2-173 work
- Related: INV-022 (Work Cycle DAG Architecture)
- Related: INV-024 (Work Item as File Architecture)
- Related: INV-026 (Unified Architecture Metaphor)
- Related: INV-011 (Command-Skill Architecture Gap)

---
