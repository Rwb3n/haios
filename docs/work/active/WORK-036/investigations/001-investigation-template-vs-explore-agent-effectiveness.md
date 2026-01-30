---
template: investigation
status: active
date: 2026-01-30
backlog_id: WORK-036
title: Investigation Template vs Explore Agent Effectiveness
author: Hephaestus
session: 263
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 82646
- 82647
- 82648
- 82649
- 82650
- 82651
- 82652
- 82653
- 82654
- 82655
- 82656
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-30T19:28:49'
---
# Investigation: Investigation Template vs Explore Agent Effectiveness

@docs/README.md
@docs/epistemic_state.md

<!-- FILE REFERENCE REQUIREMENTS (MUST - Session 171 Learning)

     1. MUST use full @ paths for prior work:
        CORRECT: @docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md
        WRONG:   INV-052, "See INV-052"

     2. MUST read ALL @ referenced files BEFORE starting EXPLORE phase:
        - Read each @path listed at document top
        - For directory references (@docs/work/active/INV-052/), MUST Glob to find all files
        - Document key findings in Prior Work Query section
        - Do NOT proceed to EXPLORE until references are read

     3. MUST Glob referenced directories:
        @docs/work/active/INV-052/ → Glob("docs/work/active/INV-052/**/*.md")
        Then read key files (SECTION-*.md, WORK.md, investigations/*.md)

     Rationale: Session 171 wasted ~15% context searching for INV-052 in wrong
     location because agent ignored @ references and guessed file locations.
-->

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

## Discovery Protocol (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic before starting |
| Document hypotheses | SHOULD | State what you expect to find before exploring |
| Use investigation-agent | MUST | Delegate EXPLORE phase to subagent for structured evidence |
| Capture findings | MUST | Fill Findings section with evidence, not assumptions |

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** Session 262 strategic review - Explore agent with open-ended prompt ("Is the pipeline ready to be a blackbox module?") produced comprehensive 12-part architectural analysis examining 45+ files, cataloguing patterns, and generating design recommendations. This exceeded typical investigation template outputs.

**Problem Statement:** Why does the Explore agent (built-in, unconstrained) produce deeper analysis than formal investigations using the investigation template + investigation-agent?

**Prior Observations:**
- Memory concept 77254: "The investigation template at 125 lines could not channel agents to produce detailed outputs. Session 101 proved this when agent bypassed subagent and wrote summaries instead of detailed evidence."
- Investigation template v2.0 is now 372 lines with extensive structure
- EXPLORE phase requires invoking investigation-agent subagent (MUST level)
- Explore agent has no template constraints - just tools and open prompt

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "investigation template effectiveness explore agent deep analysis structured output"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 77254 | Investigation template at 125 lines couldn't channel agents to produce detailed outputs. Session 101: agent bypassed subagent. | Direct prior evidence of template ineffectiveness |
| 77155 | Integration with investigation-cycle skill (E2-111) - Agent referenced in template v1.2 comment | History of investigation-agent integration |
| 82643 | investigation-agent (phase-aware subagent) | Current design proposal from Session 262 |
| 80046 | "MUST: Use investigation-agent, capture findings" | Current L3 requirement level |
| 77157 | investigation-agent completes infrastructure quartet: skill + DoD + events + agent | Architectural context |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] No directly related prior investigation found on this specific question

---

## Objective

<!-- One clear question this investigation will answer -->

**Primary Question:** What characteristics of the Explore agent's operation (prompt framing, tool access, lack of template constraints) enable deeper analysis than the investigation template + investigation-agent combination?

**Secondary Question:** Can investigation-cycle be improved to capture Explore agent's effectiveness while retaining governance benefits?

---

## Scope

### In Scope
- Explore agent definition and tool access (Claude Code built-in)
- Investigation template structure and constraints (v2.0, 372 lines)
- Investigation-agent definition and output formats
- Session 262 Explore agent prompt and output quality
- Session 101 investigation-agent bypass incident (memory 77254)
- Prompt framing differences (open-ended vs hypothesis-driven)

### Out of Scope
- Other investigation failures not related to template/agent design
- Performance optimization of agents
- Memory system effectiveness (separate concern)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 6 | Template, agent definitions, skill, Session 262 checkpoint |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + Memory |
| Estimated complexity | Medium | Comparative analysis with clear artifacts |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | **Template overhead constrains depth** - The 372-line investigation template creates cognitive overhead that diverts agent attention from actual exploration to template compliance. Explore agent has no such overhead. | High | Compare template line count vs investigation-agent output format. Count "MUST" requirements in template. Analyze Session 101 bypass. | 1st |
| **H2** | **Prompt framing enables depth** - Open-ended questions ("Is X ready?") allow exploratory breadth, while hypothesis-driven prompts ("Test H1") narrow focus prematurely. Explore agent gets open prompts by default. | Medium | Compare Session 262 Explore prompt vs investigation-agent invocation patterns. Analyze prompt structure in skill. | 2nd |
| **H3** | **Tool access is equivalent but usage differs** - Both agents have similar tools (Glob, Grep, Read), but Explore agent uses them more extensively because it isn't constrained by template checkboxes. | Medium | Compare tool lists. Analyze Explore agent behavior description. Check if investigation-agent has tool restrictions. | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior investigation effectiveness learnings
2. [x] Read investigation template (`.claude/templates/investigation.md`) - count MUST requirements
3. [x] Read investigation-agent definition (`.claude/agents/investigation-agent.md`) - analyze output constraints
4. [x] Examine Explore agent definition from Claude Code Task tool system (built-in, no file)

### Phase 2: Hypothesis Testing
5. [x] Test H1: Count template MUST requirements. Measure cognitive load indicators. Review Session 101 bypass evidence.
6. [x] Test H2: Compare prompt structures between Explore invocation vs investigation-agent invocation patterns.
7. [x] Test H3: Compare tool access lists. Check for usage pattern differences.

### Phase 3: Synthesis
8. [x] Compile evidence table with sources
9. [x] Determine verdict for each hypothesis
10. [x] Identify recommendations for investigation-cycle improvements
11. [x] Document spawned work items (rationale: operator decision needed)

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| Investigation template contains **18 MUST requirements** | `.claude/templates/investigation.md:22-349` | H1 | Grep count of "MUST" keyword |
| Template is **372 lines** (197% growth from original 125) | `.claude/templates/investigation.md` | H1 | Line count |
| Template has **27 checkbox items** requiring tracking | `.claude/templates/investigation.md` | H1 | Grep count of `[ ]` |
| Investigation-cycle skill adds **7 more MUST requirements** | `.claude/skills/investigation-cycle/SKILL.md:62-163` | H1 | Skill MUST gates |
| Investigation-agent output format is rigidly specified: 12-line evidence table | `.claude/agents/investigation-agent.md:55-65` | H2 | Output format constraint |
| Investigation-agent lacks Bash tool - cannot run tests or use `just` | `.claude/agents/investigation-agent.md:4` | H3 | Tool list comparison |
| Session 262 CH-004 Explore output: **271 lines** with code examples, interfaces, data classes | `.claude/haios/epochs/E2_3/arcs/pipeline/CH-004-builder-interface.md` | H2 | Open prompt = deep output |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 77254 | "investigation template at 125 lines could not channel agents to produce detailed outputs. Session 101 proved this when agent bypassed subagent" | H1 | Prior evidence of template ineffectiveness |
| 77253 | "META-FAILURE: Agent did not invoke investigation-agent subagent as documented, proving H2 in real-time" | H1 | Even L3 enforcement fails |
| 77430 | "Agent *will* follow templates if they're the only path" | H1 | Constraint causes compliance, not depth |

### External Evidence (if applicable)

**SKIPPED:** Investigation is internal architecture analysis, no external sources needed.

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1: Template overhead constrains depth | **Confirmed** | 25 MUST gates + 27 checkboxes + Session 101 bypass evidence (concept 77254) | High |
| H2: Prompt framing enables depth | **Confirmed** | Open prompt produced 271-line CH-004 design vs 12-line evidence table format | High |
| H3: Tool access equivalent but usage differs | **Partial** | Investigation-agent lacks Bash; primary constraint is output format, not tools | Medium |

### Detailed Findings

#### Finding 1: The Template Tax

**Evidence:**
```
Investigation Template: 18 MUST requirements, 27 checkboxes, 372 lines
Investigation-Cycle Skill: 7 additional MUST requirements
Investigation-Agent: Rigid 12-line output format
-------------------------------------------------
Total: 25 MUST gates + 27 checkboxes + format constraint
Explore Agent: 0 MUST, 0 checkboxes, no format constraint
```

**Analysis:** The investigation infrastructure imposes a "Template Tax" - cognitive overhead that diverts agent attention from actual exploration to governance compliance. The tax grows with each refinement (template v1.0 was 125 lines, v2.0 is 372 lines - 197% growth).

**Implication:** Depth and compliance are inversely correlated. Reducing template burden should increase output quality.

#### Finding 2: Output Format as Primary Constraint

**Evidence:**
```
Investigation-agent output format (investigation-agent.md:55-65):
| Hypothesis | Evidence | Source | Supports? |
|------------|----------|--------|-----------|

Session 262 Explore agent output (CH-004-builder-interface.md):
271 lines including:
- 5 interface proposals with code
- Data class definitions
- State machine design
- Integration patterns
```

**Analysis:** The investigation-agent's prescribed table format explicitly limits depth. There is no room for code examples, design rationale, or multi-paragraph analysis. The Explore agent's open format allowed comprehensive expression.

**Implication:** Remove or relax output format constraints. Allow narrative + evidence, not just evidence tables.

#### Finding 3: Open vs Directed Prompts

**Evidence:**
```
Session 262 Explore prompt: "Is the pipeline ready to be a blackbox module?"
Investigation-agent prompt: "EXPLORE: Test hypothesis H1 - strategy extraction specificity"
```

**Analysis:** Open-ended questions ("Is X ready?") enable exploratory breadth - the agent examined 45+ files and produced 12-part analysis. Hypothesis-directed prompts ("Test H1") narrow focus prematurely, producing single-hypothesis evidence.

**Implication:** Consider using open exploration phase before hypothesis testing, not after.

---

## Design Outputs

### Recommendations for Investigation-Cycle Improvements

Based on findings, three architectural improvements to consider:

#### R1: Two-Phase Investigation (EXPLORE-FIRST Pattern)

```
Current:  HYPOTHESIZE → EXPLORE → CONCLUDE
Proposed: EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE
```

**Rationale:** Session 262 showed open exploration produces depth. Use Explore agent FIRST to understand landscape, THEN form hypotheses from evidence, THEN validate. This inverts the current scientific method assumption.

#### R2: Template Slimming (Reduce Template Tax)

| Current | Proposed |
|---------|----------|
| 372 lines, 25 MUST gates | ~100 lines, 5 MUST gates |
| 27 checkboxes | ~8 checkboxes (essential only) |
| Rigid output format | Flexible narrative + evidence |

**Essential gates to retain:**
1. Memory query before starting
2. Evidence with sources
3. Spawned items or rationale
4. Memory storage at end
5. Findings synthesis

**Gates to remove:** Detailed hypothesis tables, scope metrics, multiple verification checklists, section skip rationale.

#### R3: Relaxed Output Format for Investigation-Agent

```yaml
# Current (investigation-agent.md:55-65):
### EXPLORE Output
| Hypothesis | Evidence | Source | Supports? |

# Proposed:
### EXPLORE Output
Narrative analysis with embedded evidence citations.
Code examples where relevant.
No table format requirement.
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Template overhead causes shallow output | Reduce template to essential gates only | Evidence: 25 MUST gates + Session 101 bypass prove overhead diverts from depth |
| Output format constrains expression | Allow narrative + evidence instead of table-only | Evidence: 271-line CH-004 output vs 12-line table format |
| Hypothesis-first is premature | Consider EXPLORE-FIRST pattern | Evidence: Open prompts enable 45+ file exploration vs narrow hypothesis testing |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Spawned

- [x] **WORK-037: Investigation Cycle Redesign - EXPLORE-FIRST Pattern**
  - Description: Further design exploration of Option C (EXPLORE-FIRST) and/or Option D (Hybrid)
  - Type: investigation
  - Priority: low (for later triage per operator direction)
  - Spawned via: `/new-work WORK-037 "Investigation Cycle Redesign - EXPLORE-FIRST Pattern"`

### Operator Direction (Session 263)

Operator selected: "spawn a work item to further discuss & design option C and/or D if logical. not sure if it fits this epoch so leave for later triage."

WORK-037 created with low priority for future triage.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 262 | 2026-01-30 | Created | Scaffold | Investigation created, template instantiated |
| 263 | 2026-01-30 | HYPOTHESIZE | Complete | Context, hypotheses, exploration plan populated |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1 Confirmed, H2 Confirmed, H3 Partial |
| Evidence has sources | All findings have file:line or concept ID | [x] | 7 codebase + 3 memory sources |
| Spawned items created | Items exist in backlog or via /new-* | [x] | WORK-037 created |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | Concepts 82646-82656 |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | Task tool with subagent_type='investigation-agent' |
| Are all evidence sources cited with file:line or concept ID? | Yes | All evidence in tables has sources |
| Were all hypotheses tested with documented verdicts? | Yes | H1 Confirmed, H2 Confirmed, H3 Partial |
| Are spawned items created (not just listed)? | Yes | WORK-037 created for further design exploration |
| Is memory_refs populated in frontmatter? | Yes | [82646-82656] |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - Answer to objective documented in Findings section
- [x] **Evidence sourced** - All findings have file:line or concept ID citations
- [x] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [x] **Spawned items created** - Rationale provided: operator direction needed for A/B/C/D options
- [x] **Memory stored** - `ingester_ingest` called with findings summary
- [x] **memory_refs populated** - Frontmatter updated with concept IDs 82646-82656
- [x] **lifecycle_phase updated** - Set to `conclude`
- [x] **Ground Truth Verification complete** - All items checked above

### Optional
- [x] Design outputs documented (if applicable)
- [x] Session progress updated (if multi-session)

---

## References

- Spawned by: Session 262 strategic review (observation: Explore agent output quality)
- @.claude/templates/investigation.md (v2.0, 372 lines)
- @.claude/agents/investigation-agent.md
- @.claude/skills/investigation-cycle/SKILL.md
- @docs/checkpoints/2026-01-30-01-SESSION-262-title-plan-validation-with-critique-a9-fix.md
- Memory concept 77254 (Session 101 template bypass)
- Memory concepts 82646-82656 (this investigation's findings)

---
