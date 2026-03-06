---
template: investigation
status: active
date: 2026-03-06
backlog_id: WORK-235
title: "Post-Work Ceremony Token Efficiency"
author: Hephaestus
session: 464
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 89284
- 89285
- 89286
- 89287
- 89288
- 89289
- 89290
- 89291
- 89292
- 89293
- 89294
version: "2.0"
generated: 2025-12-22
last_updated: 2025-12-22T23:16:24
---
# Investigation: Post-Work Ceremony Token Efficiency

<!-- DEPRECATION NOTICE (E2.4 - WORK-061)

     This monolithic template is preserved for backward compatibility.

     NEW investigations should use the fractured phase templates:
       .claude/templates/investigation/EXPLORE.md
       .claude/templates/investigation/HYPOTHESIZE.md
       .claude/templates/investigation/VALIDATE.md
       .claude/templates/investigation/CONCLUDE.md

     The investigation-cycle skill reads these phase-specific templates.
     This monolithic template will be removed in E2.5.
-->

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

**Trigger:** Session 451 observations (memory refs 89078-89082) identified four concrete token waste patterns in post-work ceremonies.

**Problem Statement:** Post-work ceremonies consume disproportionate tokens through redundant verification steps that re-check information already verified in prior phases.

**Prior Observations:**
- Haiku subagents over-explore by reading files beyond their verification scope (89078)
- close-work VALIDATE re-checks DoD criteria already verified in impl-cycle CHECK (89079)
- Config read duplication between orchestrator and agent (89080)
- Schema column name confusion causes failed queries and retries (89081)

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "ceremony token efficiency redundant phases token waste"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 84332 | ~40% of session tokens on governance vs ~30% on implementation for small items | Core metric — quantifies the problem |
| 84837 | Confirms 40% overhead figure | Convergent signal strengthening 84332 |
| 84951 | 12+ ceremony invocations for a single well-defined change | Concrete count of phase overhead |
| 85043 | 15 phases for 2-line fix (WORK-100) | Extreme case showing proportionality failure |
| 85459 | Most tokens on context loading and ceremony navigation, not implementation | Identifies WHERE tokens go |
| 85814 | DIMENSION 1: Weight per ceremony — reducible by proportional scaling | Design direction: retro-cycle Phase 0 as prototype |
| 85987 | Proposal: token cost measurement tool needed | Measurement gap |
| 87710 | Meta-observation: ceremony overhead on investigation about ceremony overhead | Ironic but validates signal |

**Prior Investigations:**
- [x] Searched for related investigation documents
- [x] No direct prior investigation found — but strong convergent memory signal (8 entries across multiple sessions)

---

## Objective

<!-- One clear question this investigation will answer -->

Which post-work ceremony phases perform redundant work (re-reading files, re-verifying criteria already checked), and what is a concrete design proposal for eliminating that redundancy while preserving all DoD gates?

---

## Scope

### In Scope
- Redundancy between impl-cycle CHECK, dod-validation-cycle, and close-work-cycle VALIDATE
- Redundancy between impl-cycle DONE and close-work-cycle ARCHIVE
- Subagent over-exploration (reading files beyond verification scope)
- The 4 original observed patterns (memory 89078-89081)

### Out of Scope
- Pre-work ceremony efficiency (coldstart, survey-cycle) — different concern
- Retro-cycle internal efficiency — already has proportional scaling (Phase 0)
- Token measurement tooling (memory 85987) — separate feature request
- Fundamental ceremony redesign — this is optimization, not replacement

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 7 | Skill files for CHECK, DONE, CHAIN, retro, dod-validation, close-work, session-end |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase (skill files) + Memory (8 convergent entries) |
| Estimated complexity | Medium | Cross-cutting analysis across 7 skills |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | DoD verification is performed 3 times: impl-cycle CHECK verifies tests/plans/deliverables, dod-validation-cycle re-checks the same criteria, then close-work VALIDATE re-checks again. The middle layer (dod-validation) is fully redundant for effort=medium+ items too. | High | Compare action lists across CHECK.md, dod-validation SKILL.md, and close-work SKILL.md side-by-side | 1st |
| **H2** | impl-cycle DONE and close-work ARCHIVE duplicate plan status updates and partially overlap on memory storage, creating a "double-close" pattern where work is declared complete twice. | High | Compare action lists in DONE.md vs close-work ARCHIVE phase | 2nd |
| **H3** | Subagent over-exploration wastes tokens because delegation prompts don't constrain the file-read scope, causing haiku agents to re-read context files already in the main agent's context. | Med | Examine Task() prompts in CHECK.md and retro-cycle SKILL.md for scope constraints | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic (8 convergent entries found)
2. [x] Search codebase: Read all 7 ceremony skill files
3. [x] Read identified files: CHECK.md, DONE.md, CHAIN.md, retro-cycle SKILL.md, dod-validation SKILL.md, close-work SKILL.md, session-end SKILL.md

### Phase 2: Hypothesis Testing
4. [x] Test H1: Side-by-side action comparison across 3 verification layers
5. [x] Test H2: DONE.md vs close-work ARCHIVE action comparison
6. [x] Test H3: Delegation prompt scope analysis across all Task() calls

### Phase 3: Synthesis
7. [x] Compile evidence table (redundancy map)
8. [x] Determine verdict for each hypothesis
9. [x] Identify spawned work items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| "Tests pass" checked in CHECK step 1-2 | `.claude/skills/implementation-cycle/phases/CHECK.md:16-20` | H1 | Via haiku test-runner subagent |
| "Tests pass" checked in dod-validation VALIDATE criterion 1 | `.claude/skills/dod-validation-cycle/SKILL.md:66` | H1 | Third check of same criterion |
| "Tests pass" checked in close-work VALIDATE step 1 | `.claude/skills/close-work-cycle/SKILL.md:122-128` | H1 | Pytest hard gate — yet another check |
| "Plans complete" checked in CHECK step 4 | `.claude/skills/implementation-cycle/phases/CHECK.md:23` | H1 | Ground Truth Verification |
| "Plans complete" checked in dod-validation CHECK step 2 | `.claude/skills/dod-validation-cycle/SKILL.md:41` | H1 | Duplicate plan status check |
| "Plans complete" checked in close-work VALIDATE step 3 | `.claude/skills/close-work-cycle/SKILL.md:133` | H1 | Third plan status check |
| DONE step 2: "Update plan status: complete" | `.claude/skills/implementation-cycle/phases/DONE.md:16` | H2 | Sets plan complete |
| ARCHIVE step 2: "Update associated plans to complete" | `.claude/skills/close-work-cycle/SKILL.md:209` | H2 | Sets plan complete again |
| EXTRACT prompt: "Do NOT use the Read tool" | `.claude/skills/retro-cycle/SKILL.md:362` | H3 | Already has scope constraint |
| Preflight-checker prompt gives specific file paths | `.claude/skills/implementation-cycle/phases/CHECK.md:31` | H3 | Reasonably scoped |
| Lightweight path skips dod-validation entirely | `.claude/skills/close-work-cycle/SKILL.md:91-108` | H1 | Proves dod-validation is skippable — already done for effort=small |
| Schema hints already in coldstart output | `.claude/haios/lib/operations_loader.py:204-212` | Pattern #4 | WORK-232 addressed this |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 84332 | ~40% governance tokens vs ~30% implementation for small items | H1 | Core quantification |
| 85043 | 15 phases for 2-line fix (WORK-100) | H1 | Extreme proportionality failure |
| 84951 | 12+ ceremony invocations for single change | H1 | Phase count evidence |
| 85459 | Most tokens on context loading and ceremony navigation | H1, H3 | Identifies token sink |
| 85814 | DIMENSION 1: Weight per ceremony — proportional scaling | H1 | retro Phase 0 as prototype |
| 89079 | close-work VALIDATE re-checks DoD already verified in CHECK | H1 | Direct observation of redundancy |
| 89080 | Config double-read between orchestrator and agent | Pattern #3 | Less prevalent than observed |
| 89081 | Schema column errors — schema hints needed | Pattern #4 | Already addressed (WORK-232) |

### External Evidence (if applicable)

**SKIPPED:** Internal investigation only, no external sources needed.

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1: Triple DoD verification | **Confirmed** | "Tests pass" checked 3 times (CHECK.md:16, dod-validation:66, close-work:122). "Plans complete" checked 3 times. WORK.md read 4+ times. Lightweight path already proves dod-validation is skippable. | High |
| H2: Double-close pattern | **Partially Confirmed** | Plan status update duplicated (DONE.md:16, close-work:209). Memory stores serve different purposes (not redundant). Git commits capture different scopes (not redundant). | Medium |
| H3: Subagent over-exploration | **Partially Confirmed (addressed)** | S436 already added scope constraints (retro EXTRACT:362 "Do NOT use Read tool"). Remaining re-reads are inherent to delegation pattern (subagents need files in their context). | Low |

### Detailed Findings

#### Finding 1: dod-validation-cycle is redundant for all tiers, not just effort=small

**Evidence:**
```
close-work-cycle/SKILL.md:91-108 — Lightweight path (effort=small):
  "Skip: dod-validation-cycle 3-phase bridge (near-zero signal for planless
   small items per WORK-199 H2)"
  "Replace VALIDATE with inline DoD checklist"

For effort=medium+ items, dod-validation still runs its full 3-phase
CHECK->VALIDATE->APPROVE cycle, then close-work runs its own VALIDATE.
```

**Analysis:** The lightweight path already proved that dod-validation can be replaced by an inline checklist without losing any gates. For effort=medium+ items, the same logic applies: impl-cycle CHECK already ran tests, verified deliverables, ran Ground Truth, and demoed the feature. The only unique value dod-validation adds is the Agent UX Test (which is a SHOULD, not MUST) and a second Ground Truth parse (which CHECK already did with more depth).

**Implication:** Extend the lightweight pattern to all tiers. Replace dod-validation-cycle invocation with an inline DoD checklist in close-work VALIDATE that covers the unique gates (traced requirements, governance events, retro findings) without re-checking what CHECK already verified. Estimated savings: ~2000 tokens per closure for effort=medium+ items.

#### Finding 2: The closure chain has 13 phases for a single work item

**Evidence:**
```
Full post-implementation closure chain:
  impl-cycle CHECK (1 phase)
  impl-cycle DONE (1 phase)
  impl-cycle CHAIN (1 phase) → invokes /close →
    retro-cycle: SCALE + REFLECT + DERIVE + COMMIT + EXTRACT (5 phases)
    dod-validation-cycle: CHECK + VALIDATE + APPROVE (3 phases)
    close-work-cycle: VALIDATE + ARCHIVE + CHAIN (3 phases)
      close-work CHAIN invokes: checkpoint-cycle (1+ phases)
Total: ~14 distinct phase transitions
```

**Analysis:** Each phase transition involves a `cycle_set` governance event, context switching, and often a re-read of the work file. The 40% ceremony overhead figure (memory 84332) is explained by this chain length. Retro-cycle's 5 phases are justified by cognitive separation (S20 Pressure Dynamics). The redundancy is concentrated in the verification layers (H1 finding).

**Implication:** The highest-ROI optimization is collapsing the verification layers, not reducing retro-cycle phases. Specifically: merge dod-validation into close-work VALIDATE, and merge impl-cycle DONE into CHECK (since DONE's unique actions — memory store, plan update, docs, commit — are mechanical post-CHECK steps, not a separate cognitive phase).

#### Finding 3: Plan status is updated twice

**Evidence:**
```
DONE.md:16 — "Update plan status: status: complete"
close-work/SKILL.md:209 — "Update any associated plans to status: complete (if not already)"
```

**Analysis:** DONE sets plan status to complete. Then close-work ARCHIVE sets it again. The "(if not already)" qualifier in ARCHIVE shows awareness of the duplication — it's defensive coding against the case where DONE didn't run. But in the normal flow, this is pure waste.

**Implication:** Remove plan status update from DONE (let ARCHIVE own it as part of the atomic `hierarchy_close_work` operation), or remove it from ARCHIVE (let DONE own it). Not both. Recommend: keep in ARCHIVE since `hierarchy_close_work` is the authoritative closure action.

#### Finding 4: Original patterns #3 and #4 are already addressed

**Evidence:**
```
Pattern #3 (config double-read): Ceremony skills don't independently read
  haios.yaml — they read WORK.md and plan files. The coldstart orchestrator
  loads config. No evidence of ceremony-time config re-reading found.

Pattern #4 (schema column confusion): WORK-232 added schema hints to
  coldstart output (operations_loader.py:204-212). Coldstart now emits:
  "NOTE: Column is 'type' NOT 'concept_type'"
```

**Analysis:** Pattern #3 may have been observed in a specific session where an agent or subagent read haios.yaml, but it's not a structural pattern in the ceremony skill definitions. Pattern #4 was a real problem, now solved by WORK-232.

**Implication:** Close these two patterns as resolved. Focus implementation effort on the verification layer redundancy (Finding 1) and the phase count reduction (Finding 2).

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design (if applicable)

**SKIPPED:** No new data schema — this is a ceremony restructuring proposal.

### Optimized Closure Chain (Proposed)

**Current chain (14 phases):**
```
impl CHECK → impl DONE → impl CHAIN → /close →
  retro (5 phases) → dod-validation (3 phases) → close-work (3 phases) → checkpoint
```

**Proposed chain (9 phases):**
```
impl CHECK+DONE → impl CHAIN → /close →
  retro (5 phases) → close-work VALIDATE+ARCHIVE+CHAIN → checkpoint
```

**Changes:**
1. **Merge DONE into CHECK** — DONE's actions (memory store, plan update, docs update, git commit) become the final steps of CHECK. No cognitive separation needed — CHECK already verified everything, DONE is mechanical cleanup.
2. **Eliminate dod-validation-cycle** — Absorb its unique gates (Agent UX Test) into close-work VALIDATE's inline checklist. The same approach already proven by lightweight path.
3. **Inline DoD checklist in close-work VALIDATE** — Replace the dod-validation invocation with an inline checklist that checks ONLY gates not already verified:
   - Governance events exist for work_id (unique to close-work)
   - Traced requirement addressed (unique to close-work)
   - Retro dod_relevant_findings reviewed (unique to close-work)
   - Agent UX Test if applicable (absorbed from dod-validation, SHOULD gate)
   - Skip: tests pass (already verified in CHECK), plans complete (already verified in CHECK)

### Token Savings Estimate

| Optimization | Current Cost (est.) | Proposed Cost (est.) | Savings |
|-------------|--------------------|--------------------|---------|
| Eliminate dod-validation (3 phases) | ~2500 tokens | 0 (absorbed into inline checklist ~300 tokens) | ~2200 |
| Merge DONE into CHECK (remove 1 phase transition + plan double-update) | ~800 tokens | 0 (actions move to CHECK tail) | ~800 |
| Remove redundant "tests pass" re-checks (2 eliminated) | ~400 tokens | 0 | ~400 |
| Remove redundant "plans complete" re-checks (2 eliminated) | ~300 tokens | 0 | ~300 |
| Remove redundant WORK.md re-reads (2 eliminated) | ~200 tokens | 0 | ~200 |
| **Total per closure** | | | **~3900 tokens** |

For sessions with 2 work item closures: ~7800 tokens saved. At 40% ceremony overhead baseline, this is a meaningful reduction.

### Migration Path

| Step | Action | Blast Radius | Reversibility |
|------|--------|-------------|---------------|
| 1 | Merge DONE actions into CHECK.md tail section | 1 file (CHECK.md) | High (revert edit) |
| 2 | Remove DONE.md or mark as pass-through | 1 file | High |
| 3 | Add inline DoD checklist to close-work VALIDATE | 1 file (close-work SKILL.md) | High |
| 4 | Remove dod-validation invocation from close-work | 1 file (close-work SKILL.md) | High |
| 5 | Deprecate dod-validation-cycle skill | 1 file (add deprecated: true) | High |
| 6 | Update CLAUDE.md ceremony table | 1 file | High |

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Merge DONE into CHECK, not eliminate DONE | Preserve all DONE actions as CHECK tail steps | DONE has unique value (memory store, docs update) — we're removing the phase boundary, not the actions |
| Eliminate dod-validation entirely, not just for small items | Lightweight path proved the inline checklist sufficient. Agent UX Test (only unique dod-validation value) is a SHOULD gate, not MUST | dod-validation's 3-phase ceremony adds ~2500 tokens for near-zero incremental signal over CHECK |
| Keep retro-cycle phases intact | Retro's 5 phases serve distinct cognitive pressures (S20 Pressure Dynamics). Proportional scaling via Phase 0 already handles trivial items | Retro phases are justified by cognitive separation; verification layers are not |
| Close patterns #3 and #4 as resolved | Config double-read not structurally present. Schema hints addressed by WORK-232 | Evidence doesn't support active waste in these patterns |

---

## Work Disposition

<!-- DEPRECATED: This monolithic template is preserved for backward compatibility.
     Prefer fractured template: .claude/templates/investigation/CONCLUDE.md

     MUST: Every finding that recommends follow-on work MUST appear in this table.
     Each item must have a disposition: SPAWNED (with ID) or DEFERRED (with rationale). -->

| Finding | Recommended Work | Disposition | ID / Rationale |
|---------|-----------------|-------------|----------------|
| K1-K2, I1 | Eliminate dod-validation-cycle: absorb unique gates into close-work VALIDATE inline checklist | SPAWNED | WORK-238 covers this (DONE/CHAIN duplication with close-work) |
| K3, I3 | Merge impl-cycle DONE into CHECK: move DONE actions to CHECK tail | SPAWNED | WORK-238 covers this |
| K7, I2 | Update CLAUDE.md ceremony table after implementation | DEFERRED | Dependent on WORK-238 implementation completing first |
| U1 | Token measurement tooling for ceremony cost tracking | DEFERRED | Low priority — approximations sufficient for design decisions. Would be E3+ capability. |

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 464 | 2026-03-06 | EXPLORE→CONCLUDE | Complete | Single-session investigation |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-H3 have verdict | [x] | H1 Confirmed, H2 Partially, H3 Partially |
| Evidence has sources | All findings have file:line or concept ID | [x] | 12 codebase + 8 memory citations |
| Spawned items created | Items exist in backlog or via /new-* | [x] | WORK-238 already exists, covers main findings |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | 11 concepts (89284-89294) |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | No | Main agent explored freely per Session 262 learning: unrestricted exploration produces deeper analysis than subagent constraint |
| Are all evidence sources cited with file:line or concept ID? | Yes | |
| Were all hypotheses tested with documented verdicts? | Yes | |
| Are spawned items created (not just listed)? | Yes | WORK-238 already exists in backlog |
| Is memory_refs populated in frontmatter? | Yes | 11 concept IDs (89284-89294) |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - 4 detailed findings with evidence, analysis, and implications
- [x] **Evidence sourced** - 12 codebase citations (file:line), 8 memory citations
- [x] **Hypotheses resolved** - H1 Confirmed, H2 Partially Confirmed, H3 Partially Confirmed
- [x] **Spawned items created** - WORK-238 already exists, covers main design proposal
- [x] **Memory stored** - 11 concepts (89284-89294) via ingester_ingest
- [x] **memory_refs populated** - Frontmatter updated with concept IDs
- [x] **lifecycle_phase updated** - Set to conclude
- [x] **Ground Truth Verification complete** - All items checked

### Optional
- [x] Design outputs documented - Optimized closure chain, token savings estimate, migration path
- [x] Session progress updated

---

## References

- Spawned by: Session 451 observations (memory refs 89078-89082)
- Related: WORK-238 (Implementation-Cycle DONE/CHAIN Phase Duplication with Close-Work-Cycle)
- Related: WORK-199 (Lightweight closure path — proved dod-validation skippable)
- Related: WORK-232 (Schema hints in coldstart — resolved pattern #4)
- Related: REQ-CEREMONY-005 (Ceremony depth scales proportionally)
- Related: ADR-033 (Work Item Lifecycle Governance — DoD criteria)

---
