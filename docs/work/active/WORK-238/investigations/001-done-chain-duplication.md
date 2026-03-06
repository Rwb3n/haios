---
template: investigation
status: complete
date: 2026-03-06
backlog_id: WORK-238
title: "Implementation-Cycle DONE/CHAIN Phase Duplication with Close-Work-Cycle"
author: Hephaestus
session: 465
lifecycle_phase: conclude
spawned_by: WORK-237
related:
- WORK-235
memory_refs: []
version: "2.0"
generated: 2026-03-06
last_updated: 2026-03-06T23:45:00
---
# Investigation: Implementation-Cycle DONE/CHAIN Phase Duplication with Close-Work-Cycle

## Context

**Trigger:** WORK-237 retro (S461) found retro-cycle was silently skipped because impl-cycle CHAIN used `work_close()` directly instead of `/close`. WORK-235 (S464) confirmed triple DoD verification redundancy and proposed ceremony consolidation.

**Problem Statement:** The post-implementation closure chain runs 14+ distinct phase transitions. Redundant verification layers (impl-cycle CHECK, dod-validation-cycle, close-work VALIDATE) re-check the same DoD criteria. impl-cycle DONE duplicates plan status updates with close-work ARCHIVE. This investigation maps all duplication and produces a design proposal for unified closure.

---

## Prior Work Query

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 89284 | H1 CONFIRMED: DoD verification performed 3 times across closure chain | Core finding from WORK-235 |
| 89285 | H2 PARTIALLY CONFIRMED: Plan status update duplicated | Direct evidence |
| 89290 | Proposed 9 phases (CHECK+DONE -> CHAIN -> retro 5 -> close-work 3) | Prior design proposal |
| 89291 | Changes: merge DONE into CHECK, eliminate dod-validation, inline DoD | Actionable proposals |
| 89292 | Estimated savings: ~3900 tokens per closure | Quantification |
| 89164 | Retro was skipped in DONE->CHAIN transition | Original trigger |
| 89180 | Stop using work_close() directly — use /close instead | Directive from WORK-237 retro |
| 89191 | CHAIN phase bypasses retro-cycle by using work_close() directly | Evidence of bypass pattern |

---

## Objective

Map all duplicated actions between lifecycle DONE/CHAIN phases and the `/close` chain (retro-cycle, dod-validation-cycle, close-work-cycle), then produce actionable design proposals for eliminating redundancy while preserving all DoD gates.

---

## Scope

### In Scope
- impl-cycle DONE/CHAIN vs close-work-cycle action overlap
- dod-validation-cycle redundancy assessment for ALL tiers
- Investigation-cycle CONCLUDE/CHAIN duplication patterns
- `/close` command documentation staleness
- Impact assessment across all lifecycle skills

### Out of Scope
- Retro-cycle internal efficiency (already has proportional scaling via Phase 0)
- Pre-work ceremonies (coldstart, survey-cycle)
- Token measurement tooling (memory 85987)
- Fundamental ceremony redesign

---

## Hypotheses

| # | Hypothesis | Confidence | Test Method |
|---|------------|------------|-------------|
| H1 | dod-validation-cycle is fully redundant for ALL tiers, not just effort=small | High | Map each dod-validation action to equivalent in CHECK or close-work VALIDATE |
| H2 | impl-cycle DONE has exactly 2 duplicated actions with close-work ARCHIVE, but 2 unique actions worth preserving | High | Side-by-side action table DONE vs ARCHIVE vs retro COMMIT |
| H3 | Investigation-cycle CONCLUDE+CHAIN have same duplication pattern as impl-cycle DONE+CHAIN | Med-High | Map CONCLUDE actions against `/close` chain |
| H4 | `/close` command Steps 2-3 duplicate close-work-cycle skill (documentation, not execution) | Medium | Check whether Steps 2-3 are executed or reference docs |

---

## Evidence Collection

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis |
|---------|-------------------|---------------------|
| "Tests pass" checked in CHECK step 1-2 via haiku test-runner | `.claude/skills/implementation-cycle/phases/CHECK.md:15-20` | H1 |
| "Tests pass" checked in dod-validation VALIDATE criterion 1 | `.claude/skills/dod-validation-cycle/SKILL.md:66` | H1 |
| "Tests pass" checked in close-work VALIDATE pytest hard gate | `.claude/skills/close-work-cycle/SKILL.md:122-128` | H1 |
| "Plans complete" checked in CHECK step 4 (Ground Truth) | `.claude/skills/implementation-cycle/phases/CHECK.md:22` | H1 |
| "Plans complete" checked in dod-validation CHECK step 2 | `.claude/skills/dod-validation-cycle/SKILL.md:41` | H1 |
| "Plans complete" checked in close-work VALIDATE step 3 | `.claude/skills/close-work-cycle/SKILL.md:133` | H1 |
| Lightweight path already skips dod-validation for effort=small | `.claude/skills/close-work-cycle/SKILL.md:91-108` | H1 |
| Agent UX Test is SHOULD gate, only unique dod-validation value | `.claude/skills/dod-validation-cycle/SKILL.md:71-93` | H1 |
| DONE step 2: "Update plan status: complete" | `.claude/skills/implementation-cycle/phases/DONE.md:16` | H2 |
| ARCHIVE step 2: "Update associated plans to complete (if not already)" | `.claude/skills/close-work-cycle/SKILL.md:209` | H2 |
| DONE step 1: WHY capture via ingester_ingest | `.claude/skills/implementation-cycle/phases/DONE.md:15` | H2 |
| retro COMMIT: closure summary via ingester_ingest | `.claude/skills/retro-cycle/SKILL.md:311-319` | H2 |
| Investigation-cycle CONCLUDE stores memory + updates status | `.claude/skills/investigation-cycle/SKILL.md:174-285` | H3 |
| Investigation-cycle has no fractured phases directory | Glob: no files in investigation-cycle/phases/ | H3 |
| No design-cycle/validation-cycle/triage-cycle phase dirs exist | Glob: no files found | H3 |
| `/close` Steps 2-3 noted as "document the skill's phases for reference" | `.claude/commands/close.md:118` | H4 |
| impl-cycle CHAIN now calls `/close` (not work_close directly) | `.claude/skills/implementation-cycle/phases/CHAIN.md:15` | Context |

### Memory Evidence

| Concept ID | Content | Supports |
|------------|---------|----------|
| 89284-89295 | WORK-235 findings: triple DoD, double-close, subagent scope | H1, H2 |
| 89164-89165 | Retro skipped in DONE->CHAIN transition | Original trigger |
| 89180-89183 | K/S/S directives: use /close, enforce retro-before-close | Context |
| 85043 | 15 phases for 2-line fix (WORK-100) | H1 quantification |
| 84332 | ~40% governance tokens vs ~30% implementation | H1 quantification |

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1: dod-validation fully redundant | **Confirmed** | Every MUST gate covered by CHECK + close-work VALIDATE. Only unique value (Agent UX Test) is a SHOULD gate. | High |
| H2: DONE has 2 duplicated + 2 unique actions | **Confirmed** | Plan status exact duplicate (DONE:16, close-work:209). WHY capture NOT duplicate (different content from retro COMMIT). Docs update + git commit unique to DONE. | High |
| H3: Investigation CONCLUDE has same pattern | **Confirmed** | Status update overlaps with ARCHIVE. Memory storage has partial content overlap with retro COMMIT. But CONCLUDE has significant unique value (epistemic review, epoch reconciliation, spawning). | Medium-High |
| H4: `/close` Steps 2-3 are reference docs | **Partially Confirmed** | close.md:118 says "for reference." Not execution duplication, but maintenance/staleness risk. | Medium |

### Detailed Findings

#### Finding 1: Complete duplication map

| Action | impl CHECK | impl DONE | dod-validation | close-work VALIDATE | close-work ARCHIVE |
|--------|-----------|-----------|----------------|--------------------|--------------------|
| Pytest run | YES | — | YES (re-check) | YES (re-check) | — |
| Plans complete | YES | — | YES (re-check) | YES (re-check) | — |
| Ground Truth | YES | — | YES (re-check) | — | — |
| Deliverables verified | YES | — | — | — | — |
| WHY captured | — | YES | YES (re-check) | YES (re-check) | — |
| Docs updated | — | YES | YES (re-check) | YES (re-check) | — |
| Plan status -> complete | — | YES | — | — | YES (duplicate) |
| Agent UX Test | — | — | YES (unique, SHOULD) | — | — |
| Traced requirement | — | — | — | YES (unique) | — |
| Governance events | — | — | — | YES (unique) | — |
| Retro findings review | — | — | — | YES (unique) | — |
| hierarchy_close_work | — | — | — | — | YES (unique) |
| Status propagation | — | — | — | — | YES (unique) |

**Summary:** 5 actions are performed 2-3 times (pytest, plans complete, Ground Truth, WHY captured, docs updated). Plan status update performed twice (DONE + ARCHIVE).

#### Finding 2: dod-validation-cycle has exactly 1 unique contribution

Agent UX Test (dod-validation SKILL.md:71-93) is the ONLY gate not covered elsewhere. It's a SHOULD gate (failure warns, doesn't block). Can be absorbed as an optional checklist item in close-work VALIDATE.

#### Finding 3: DONE's WHY capture is NOT redundant with retro COMMIT

DONE's ingester_ingest captures "what was built and why" — implementation rationale. Retro COMMIT captures structured reflection (WWW, WCBB, WSY, WDN, WMI) — process observations. Different cognitive purpose. However, DONE's WHY capture could be deferred to retro COMMIT with a modified prompt that includes implementation rationale. This is a design choice, not a redundancy.

#### Finding 4: No other lifecycle skills have this problem

Design-cycle, validation-cycle, and triage-cycle don't have fractured DONE/CHAIN phases. Investigation-cycle has CONCLUDE+CHAIN in its monolithic SKILL.md but with minimal duplication (status update only). The impl-cycle DONE/CHAIN + dod-validation redundancy is the concentrated problem.

---

## Epistemic Review

| Category | Finding | Citation |
|----------|---------|---------|
| KNOWN | dod-validation CHECK/VALIDATE/APPROVE re-checks every criterion already verified by impl-cycle CHECK | dod-validation SKILL.md:34-141 vs CHECK.md:15-31 |
| KNOWN | Plan status update duplicated between DONE.md:16 and close-work SKILL.md:209 | Direct file evidence |
| KNOWN | Lightweight path already skips dod-validation for effort=small | close-work SKILL.md:91-108 |
| KNOWN | Agent UX Test is the only unique dod-validation contribution, SHOULD gate | dod-validation SKILL.md:71-93 |
| KNOWN | Investigation-cycle has no fractured phases — CONCLUDE+CHAIN in monolithic SKILL.md | Glob confirmed |
| KNOWN | No design/validation/triage-cycle phase directories exist | Glob confirmed |
| KNOWN | impl-cycle CHAIN now correctly calls `/close` (not work_close directly) | CHAIN.md:15 |
| INFERRED | Removing dod-validation saves ~2200 tokens per closure | WORK-235: 2500 cost - 300 inline = 2200 |
| INFERRED | Total savings ~3200 tokens per closure | Revised: dod-validation (2200) + plan double-update (200) + re-check elimination (800) |
| UNKNOWN | Whether Agent UX Test has ever caught a real issue | No evidence either way — non-blocking |

**Verdict: PROCEED** — No blocking unknowns.

---

## Work Disposition

| Finding | Recommended Work | Disposition | ID / Rationale |
|---------|-----------------|-------------|----------------|
| dod-validation-cycle fully redundant for all tiers | Eliminate dod-validation-cycle, absorb Agent UX Test into close-work VALIDATE | TO SPAWN | Implementation item |
| Plan status double-update in DONE + ARCHIVE | Remove plan status update from DONE.md, let ARCHIVE own it | TO SPAWN | Implementation item |
| `/close` command Steps 2-3 stale documentation | Remove duplicate docs from close.md, keep only skill invocation chain | TO SPAWN | Implementation item |
| Investigation CONCLUDE status overlap with ARCHIVE | DEFERRED | Minimal duplication, CONCLUDE has significant unique cognitive value |

---

## Design Proposal: Unified Closure Flow

### Current chain (14+ phases):
```
impl CHECK -> impl DONE -> impl CHAIN -> /close ->
  retro (5 phases) -> dod-validation (3 phases) -> close-work (3 phases) -> checkpoint
```

### Proposed chain (10 phases):
```
impl CHECK -> impl DONE -> impl CHAIN -> /close ->
  retro (5 phases) -> close-work VALIDATE+ARCHIVE+CHAIN -> checkpoint
```

### Changes:
1. **Eliminate dod-validation-cycle** — absorb Agent UX Test into close-work VALIDATE inline checklist
2. **Remove plan status update from DONE** — ARCHIVE owns it via hierarchy_close_work
3. **Clean /close command** — remove Steps 2-3 duplicate documentation

### Estimated savings: ~3200 tokens per closure

---

## References

- @.claude/skills/implementation-cycle/phases/CHECK.md
- @.claude/skills/implementation-cycle/phases/DONE.md
- @.claude/skills/implementation-cycle/phases/CHAIN.md
- @.claude/skills/close-work-cycle/SKILL.md
- @.claude/skills/retro-cycle/SKILL.md
- @.claude/skills/dod-validation-cycle/SKILL.md
- @.claude/commands/close.md
- @docs/work/active/WORK-235/investigations/001-post-work-ceremony-token-efficiency.md
- WORK-237 retro findings (memory 89161-89165, 89180-89183)
