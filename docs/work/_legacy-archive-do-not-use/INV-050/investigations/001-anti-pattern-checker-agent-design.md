---
template: investigation
status: active
date: 2025-12-29
backlog_id: INV-050
title: Anti-Pattern Checker Agent Design
author: Hephaestus
session: 143
lifecycle_phase: conclude
spawned_by: Session-143
related:
- E2-232
memory_refs:
- 80243
- 80244
- 80245
- 80246
- 80247
- 80248
- 80249
- 80250
- 80251
- 80252
- 80253
- 80254
- 80255
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-29T11:15:13'
---
# Investigation: Anti-Pattern Checker Agent Design

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

**Trigger:** Session 143 roadmap review - agent (me) claimed "Epoch 2 exit criteria are essentially met" without evidence. Operator challenged: "why do you assess it that way?" - exposing Optimistic Confidence anti-pattern.

**Problem Statement:** No mechanical check challenges agent claims before acceptance, allowing self-assessed, lenient evaluations that conflate "infrastructure exists" with "behavior achieved."

**Prior Observations:**
- Agent claimed 5 exit criteria were met, but had no evidence for any
- When challenged, agent immediately recognized the error (anti-pattern is predictable)
- The 6 L1 anti-patterns in invariants.md describe this failure mode but aren't applied mechanically
- "Structured Mistrust" principle exists but isn't enforced

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "anti-pattern checker verification claims evidence optimistic confidence structured mistrust"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 51221 | "structured mistrust: we trust the process and evidence, not claims" | Core philosophy - this is what we're making mechanical |
| 79892 | "Optimistic confidence (L1 anti-pattern)" | The specific anti-pattern that triggered this investigation |
| 65698 | "Consistent Anti-Pattern Identification" synthesis | Prior work on detection patterns |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] No direct prior investigation on anti-pattern checker agent; related work in invariants.md and ADR-033 (DoD verification)

---

## Objective

<!-- One clear question this investigation will answer -->

How should an anti-pattern-checker agent be designed to mechanically verify claims against the 6 L1 anti-patterns before acceptance?

---

## Scope

### In Scope
- The 6 L1 anti-patterns from invariants.md as verification lenses
- Agent architecture (system prompt, tools, trigger conditions)
- Integration points (checkpoint-cycle, manual invocation, epoch/milestone claims)
- Evidence requirements for each anti-pattern lens

### Out of Scope
- Implementation of the agent (separate work item)
- Automated invocation via hooks (future enhancement)
- Integration with external validation systems

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 3-5 | invariants.md, existing agents, ADR-033 |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + Memory |
| Estimated complexity | Medium | Novel agent design, clear requirements |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Each L1 anti-pattern can be converted to a verification question with evidence requirement | High | Read invariants.md, define question + evidence for each | 1st |
| **H2** | Existing agent patterns (validation-agent, investigation-agent) provide reusable architecture | Med | Read existing agents, extract common patterns | 2nd |
| **H3** | checkpoint-cycle is the right automatic integration point (before finalizing summaries) | Med | Read checkpoint-cycle skill, identify claim-making steps | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Read invariants.md L1 anti-patterns section
2. [x] Read existing agents (validation-agent, investigation-agent)
3. [x] Read checkpoint-cycle skill for integration points

### Phase 2: Hypothesis Testing
4. [x] Test H1: Convert each anti-pattern to question + evidence requirement
5. [x] Test H2: Extract reusable patterns from existing agents
6. [x] Test H3: Identify where in checkpoint-cycle claims are made

### Phase 3: Synthesis
7. [x] Design agent specification (system prompt, tools, trigger)
8. [x] Define the 6 verification lenses
9. [x] Recommend integration approach
10. [ ] Spawn implementation work item

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| 6 L1 anti-patterns in table with Pattern/Truth/Mitigation | `.claude/config/invariants.md:83-95` | H1 | Ready to convert to verification questions |
| validation-agent has structured output format | `.claude/agents/validation-agent.md:27-51` | H2 | Reusable pattern for report |
| preflight-checker returns JSON with ready/blocked/issues | `.claude/agents/preflight-checker.md:48-57` | H2 | Machine-readable output |
| checkpoint-cycle FILL phase has claim sections | `.claude/skills/checkpoint-cycle/SKILL.md:47-66` | H3 | Integration point identified |
| Session Verification section in checkpoint template | `.claude/templates/checkpoint.md:82-92` | H3 | Existing claim verification |
| observations.md mentions Ceremonial Completion anti-pattern | `.claude/templates/observations.md:17-18` | H1/H3 | Pattern already referenced |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 51221 | "structured mistrust: we trust the process and evidence, not claims" | All | Core philosophy |
| 79892 | "Optimistic confidence (L1 anti-pattern)" | H1 | Triggering anti-pattern |
| 56664 | "AntiPattern Validation Gap (ACCEPTED RISK)" | All | Prior recognition of gap |

### External Evidence (if applicable)

**SKIPPED:** All evidence available in codebase and memory

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **Confirmed** | invariants.md:83-95 provides 6 anti-patterns with mitigations; each converts to verification question + evidence requirement | High |
| H2 | **Confirmed** | validation-agent, preflight-checker share patterns: frontmatter, structured output, edge cases, tools declaration | High |
| H3 | **Confirmed** | checkpoint-cycle FILL phase (lines 47-66) is where claims are made; add VERIFY step before CAPTURE | High |

### Detailed Findings

#### Finding 1: The 6 Verification Lenses

**Evidence:**
```markdown
# From invariants.md:83-95
| Pattern | Truth | Mitigation |
|---------|-------|------------|
| Assume over verify | LLMs predict likely values, don't verify | Gates force verification |
| Generate over retrieve | Creation is default mode | Glob/Read before Write |
| Move fast | No internal friction mechanism | Blockers > suggestions |
| Optimistic confidence | No episodic memory for failures | External memory systems |
| Pattern-match solutions | Edge cases underrepresented | DoD requires edge case testing |
| Ceremonial completion | Literal task, not integration | DoD requires integration test |
```

**Analysis:** Each anti-pattern has a corresponding mitigation. The checker agent converts these to verification questions.

**Verification Question Table:**

| Anti-Pattern | Question | Evidence Requirement | Failure Indicator |
|--------------|----------|---------------------|-------------------|
| Assume over verify | "What evidence was cited?" | File:line or concept ID | No evidence, declarative claim |
| Generate over retrieve | "Was memory consulted?" | memory_refs populated | Empty prior work section |
| Move fast | "Was this claim validated?" | Gate passage confirmed | Claims without verification |
| Optimistic confidence | "Is confidence supported?" | Quantitative evidence | High confidence, no support |
| Pattern-match solutions | "Were edge cases considered?" | Edge case table | Generic solution only |
| Ceremonial completion | "Does 'done' match ground truth?" | Checklist complete | Unchecked items |

#### Finding 2: Integration Point - VERIFY Phase

**Evidence:**
```
checkpoint-cycle phases (SKILL.md:22-24):
SCAFFOLD --> FILL --> CAPTURE --> COMMIT

Recommended change:
SCAFFOLD --> FILL --> **VERIFY** --> CAPTURE --> COMMIT
```

**Analysis:** Claims are made in FILL phase. VERIFY phase invokes anti-pattern-checker before memory capture.

**Implication:** Add new phase to checkpoint-cycle that gates on anti-pattern verification.

---

## Design Outputs

### Agent Specification

```yaml
# anti-pattern-checker agent
name: anti-pattern-checker
description: Verify claims against 6 L1 anti-patterns before acceptance
tools: [Read, Grep, Glob]
requirement_level: SHOULD (manual), MUST (for epoch/milestone claims)
```

### Mechanism Design

```
TRIGGER:
  - Manual: Agent invokes before major summary claim
  - Automatic: checkpoint-cycle VERIFY phase (future)

INPUT:
  - claim: string (the assertion to verify)
  - context: string (file path or section reference)

ACTION:
  For each of 6 lenses:
    1. Extract sub-claims from input
    2. Apply verification question
    3. Check for evidence requirement
    4. Flag if failure indicator present

OUTPUT:
  {
    "claim": "<original claim>",
    "verified": true/false,
    "lenses": {
      "assume_over_verify": { "pass": bool, "evidence": "..." },
      "generate_over_retrieve": { "pass": bool, "evidence": "..." },
      ...
    },
    "verdict": "SUPPORTED" | "UNSUPPORTED",
    "gaps": ["list of missing evidence"]
  }
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| 6 lenses from invariants.md | Use existing L1 anti-patterns | Already defined, tested in Session 143 |
| Structured JSON output | Match preflight-checker pattern | Machine-readable for gates |
| SHOULD for manual, MUST for epochs | Graduated enforcement | Avoid friction on small claims |
| Add VERIFY phase to checkpoint-cycle | Integrate at claim-making point | Catch errors before memory capture |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-232: Implement Anti-Pattern Checker Agent**
  - Description: Create `.claude/agents/anti-pattern-checker.md` with 6-lens verification
  - Fixes: Optimistic confidence anti-pattern - claims made without evidence
  - Spawned via: `/new-work E2-232 "Implement Anti-Pattern Checker Agent"`

### Future (Requires more work first)

- [ ] **E2-233: Add VERIFY Phase to Checkpoint Cycle**
  - Description: Integrate anti-pattern-checker into checkpoint-cycle VERIFY phase
  - Blocked by: E2-232 (agent must exist first)

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 143 | 2025-12-29 | HYPOTHESIZE | Complete | Context, hypotheses, scope defined |
| 143 | 2025-12-29 | EXPLORE | Complete | Evidence gathered, 6 lenses designed |
| 143 | 2025-12-29 | CONCLUDE | Complete | E2-232 spawned, design documented |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1/H2/H3 all Confirmed |
| Evidence has sources | All findings have file:line or concept ID | [x] | 6 codebase refs, 3 memory refs |
| Spawned items created | Items exist in backlog or via /new-* | [x] | E2-232 created |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | See below |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | Subagent gathered all evidence |
| Are all evidence sources cited with file:line or concept ID? | Yes | 6 codebase, 3 memory |
| Were all hypotheses tested with documented verdicts? | Yes | All Confirmed |
| Are spawned items created (not just listed)? | Yes | E2-232 in docs/work/active/ |
| Is memory_refs populated in frontmatter? | Yes | 13 concept IDs added |

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

- Spawned by: Session 143 roadmap review - operator challenged incorrect epoch claim
- Related: `.claude/config/invariants.md` - L1 anti-patterns source
- Related: ADR-033 - Work Item Lifecycle DoD (evidence verification model)

---
