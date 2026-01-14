---
template: investigation
status: active
date: 2026-01-03
backlog_id: INV-055
title: Agent-Usability-Requirements-Detailing
author: Hephaestus
session: 161
lifecycle_phase: hypothesize
spawned_by: null
related: []
memory_refs:
- 80589
- 80590
- 80591
- 80592
- 80593
- 80594
- 80595
- 80596
- 80597
- 80598
- 80599
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-03T19:03:10'
---
# Investigation: Agent-Usability-Requirements-Detailing

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

**Trigger:** Session 161 operator question: "do we need AI-agent-as-user requirements?" Added draft section to L3-requirements.md, spawned this investigation for validation.

**Problem Statement:** L3-requirements.md has a new "Agent Usability Requirements" section (lines 76-113) that needs validation against actual HAIOS components.

**Prior Observations:**
- 6 L1 anti-patterns exist but need positive usability counterparts
- Draft section inverts anti-patterns to requirements but lacks grounding
- The Agent UX Test (4 questions) needs verification against real components

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "agent usability requirements anti-patterns LLM nature verification affordances ceremonial completion"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 77216 | Agent "designed for completion" creates emergent anti-patterns | Confirms bias is architectural |
| 79890 | "Bias toward completion" - requires mechanical gates, not prompting | Validates L3 gate requirements |
| 79075 | 6 evergreen anti-patterns documented in epistemic_state.md | Source of L3 inversions |
| 80243 | Design agent to verify claims against 6 L1 anti-patterns | Supports anti-pattern-checker |
| 79895 | Prevent "Ceremonial completion" anti-pattern | Validates observation gates |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-052 (HAIOS Architecture Reference), INV-053 (Modular Architecture Review)

---

## Objective

<!-- One clear question this investigation will answer -->

Do existing HAIOS components pass the Agent UX Test, and what gaps exist that require implementation?

---

## Scope

### In Scope
- Audit HAIOS components (modules, skills, agents, commands, hooks) against Agent UX Test
- Identify gaps in discoverability, verification, recovery, and token efficiency
- Propose DoD integration for Agent UX Test
- Create backlog items for discovered gaps

### Out of Scope
- Implementing fixes (spawn work items instead)
- External tools/APIs outside HAIOS control

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | ~50 | .claude/haios/modules/, skills/, agents/, hooks/, lib/ |
| Hypotheses to test | 3 | H1-H3 below |
| Expected evidence sources | 3 | Codebase / Memory / haios-status |
| Estimated complexity | Medium | Known component inventory |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Most HAIOS components PASS the Agent UX Test | High | Audit components against 4 questions | 1st |
| **H2** | Gaps exist primarily in error messaging and recovery | Medium | Check error handlers for actionable messages | 2nd |
| **H3** | Agent UX Test should be added to DoD criteria | High | Evaluate if test prevents anti-pattern gaps | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic
2. [x] Inventory components from haios-status-slim.json
3. [x] Check README.md coverage in each directory

### Phase 2: Hypothesis Testing
4. [x] Test H1: Audit modules, skills, agents, commands against 4 Agent UX Test questions
5. [x] Test H2: Check error handlers in hooks and modules for actionable messages
6. [x] Test H3: Evaluate if Agent UX Test would catch gaps in current DoD

### Phase 3: Synthesis
7. [x] Compile audit results table
8. [x] Determine verdict for each hypothesis
9. [x] Identify spawned work items for gaps

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| All major dirs have README.md | `.claude/lib/README.md`, `.claude/agents/README.md`, `.claude/haios/modules/README.md` | H1 | Discoverability PASS |
| haios-status-slim.json lists all infrastructure | `.claude/haios-status-slim.json:28-84` | H1 | 18 commands, 15 skills, 7 agents discoverable |
| `just --list` shows 40+ recipes with descriptions | `justfile` | H1 | Discoverability PASS |
| PreToolUse hook has BLOCKED messages with alternatives | `.claude/hooks/hooks/pre_tool_use.py:160,195,226,301-319` | H2 | Actionable error messages |
| WorkEngine has typed exceptions with clear messages | `.claude/haios/modules/work_engine.py:55-64,205,211,263` | H2 | Good recovery pattern |
| GovernanceLayer catches exceptions silently | `.claude/haios/modules/governance_layer.py:187,211` | H2 | GAP: Silent failures |
| MemoryBridge degrades gracefully with warnings | `.claude/haios/modules/memory_bridge.py:100-101` | H1 | Good degradation pattern |
| Agents lack individual README.md files | `.claude/agents/*.md` (no subdirs) | H1 | Minor gap: flat structure |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 79890 | Bias toward completion requires mechanical gates | H3 | DoD needs Agent UX enforcement |
| 80243 | Design agent to verify against anti-patterns | H3 | anti-pattern-checker exists |
| 79895 | Prevent ceremonial completion | H1 | Observation gates implemented |

### External Evidence (if applicable)

**SKIPPED:** No external sources needed - internal audit only.

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | READMEs in all major dirs, haios-status-slim.json discovers 40+ components, just recipes documented | High |
| H2 | **PARTIALLY CONFIRMED** | Most hooks have actionable BLOCKED messages, but GovernanceLayer silently catches exceptions | Medium |
| H3 | **CONFIRMED** | Current DoD lacks Agent UX Test; adding it would catch silent failure gaps like GovernanceLayer | High |

### Agent UX Test Audit Results

| Component Category | Q1: Discover? | Q2: Verify? | Q3: Recover? | Q4: Token? | Overall |
|-------------------|---------------|-------------|--------------|------------|---------|
| **Modules** (3) | PASS | PASS | PARTIAL | PASS | PARTIAL |
| **Skills** (15) | PASS | PASS | PASS | PASS | PASS |
| **Agents** (7) | PASS | PASS | PASS | PASS | PASS |
| **Commands** (18) | PASS | PASS | PASS | PASS | PASS |
| **Hooks** (4) | PASS | PASS | PASS | PASS | PASS |
| **Just Recipes** (40+) | PASS | PARTIAL | PASS | PASS | PARTIAL |

### Detailed Findings

#### Finding 1: GovernanceLayer Silent Failure

**Evidence:**
```python
# .claude/haios/modules/governance_layer.py:187,211
except Exception:
    # Log but don't fail on handler errors
    pass
```

**Analysis:** GovernanceLayer catches all exceptions and continues silently. An agent would not know if a handler failed.

**Implication:** Add logging or return a degraded status so agents know when governance is impaired.

#### Finding 2: Just Recipes Lack Success Verification

**Evidence:**
```bash
# Example: `just ready` returns list but no exit code verification
# Agent can't programmatically confirm if result is "no ready items" vs "error"
```

**Analysis:** Some just recipes return prose output without clear success indicators.

**Implication:** Add structured output option or consistent exit codes for machine parsing.

#### Finding 3: Strong Discoverability Infrastructure

**Evidence:**
- haios-status-slim.json lists all 18 commands, 15 skills, 7 agents, 2 MCPs
- Each major directory has README.md with component tables
- `just --list` shows 40+ recipes with descriptions

**Analysis:** HAIOS already implements strong discoverability per L3 requirements.

**Implication:** This is a strength to maintain and extend.

---

## Design Outputs

### DoD Integration Proposal

Add Agent UX Test as optional DoD criterion in ADR-033:

```markdown
### Optional DoD Criteria (for new components)

| Criterion | Verification Method |
|-----------|---------------------|
| Agent UX Test passed | Ask: Can discover? Can verify? Can recover? Token-efficient? |
```

**Trigger:** When creating new commands, skills, agents, modules.
**Not required for:** Bug fixes, documentation, internal refactors.

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Make Agent UX Test optional | Not required for all work | Would add friction to small changes; only matters for new interfaces |
| Focus on recovery gaps | Priority over discoverability | Discoverability already strong; recovery has gaps (GovernanceLayer) |
| Don't create massive backlog | 2 work items max | Most components pass; only fix actual gaps |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-248: GovernanceLayer Error Visibility**
  - Description: Add logging/return value for handler exceptions so agents know when governance is degraded
  - Fixes: Finding 1 (silent failure anti-pattern)
  - Spawned via: `/new-work E2-248 "GovernanceLayer Error Visibility"`

- [x] **E2-249: Agent UX Test in DoD (Optional Gate)**
  - Description: Add optional Agent UX Test criterion to dod-validation-cycle for new components
  - Fixes: H3 (DoD lacks agent usability check)
  - Spawned via: `/new-work E2-249 "Agent UX Test in DoD"`

### Future (Requires more work first)

- [ ] **Structured Just Recipe Output** (deferred)
  - Description: Add JSON output option to key recipes for machine parsing
  - Blocked by: Need to identify which recipes agents use most
  - **Note:** Low priority - current output is usable, just not optimal

### Not Spawned Rationale (if no items)

**N/A** - Two work items spawned for identified gaps.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 161 | 2026-01-03 | HYPOTHESIZE | Started | Initial context and hypotheses |
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
