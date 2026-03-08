# WORK-287 Findings: Session-Boundary Decoupling

## Objective
Investigate how to decouple plan-authoring from implementation across session boundaries to address the 104% ceremony budget problem.

## Summary

A **tiered session architecture** that matches session strategy to work complexity using the existing governance tier (trivial/small/standard/architectural). Small items stay single-session; standard+ items split into plan-session and build-session with clean context boundaries.

## Hypothesis Verdicts

| # | Hypothesis | Verdict | Confidence |
|---|-----------|---------|------------|
| H1 | Tiered Session Architecture | Confirmed | 0.9 |
| H2 | Sub-agent Delegation is Complementary | Confirmed | 0.85 |
| H3 | Handoff as Checkpoint Extension | Confirmed (modified) | 0.75 |
| H4 | Context Reset > Context Compact | Confirmed | 0.9 |

## Tiered Session Architecture

| Tier | Session Strategy | PLAN Phase | DO Phase | Handoff |
|------|-----------------|------------|----------|---------|
| **trivial** | Single session | Skipped | Inline | N/A |
| **small** | Single session | Inline or sub-agent | Inline | N/A |
| **standard** | Two sessions | Session N: sub-agent plan, approve, checkpoint | Session N+1: coldstart, read plan, DO | Plan on disk + checkpoint pending |
| **architectural** | Two+ sessions | Session N: plan, critique loop, operator approval, checkpoint | Session N+1: coldstart, read plan, operator re-confirm, DO | Plan on disk + checkpoint pending + operator gate |

## Key Decisions

### 1. Handoff is NOT a new artifact
The handoff between plan-session and build-session uses existing mechanisms:
- Plan file at `docs/work/active/{id}/plans/PLAN.md` (already on disk, status: approved)
- Checkpoint `pending` field (already populated by plan-authoring-cycle CHAIN)
- Work item `cycle_phase` field (set by cycle_set)

### 2. Build-session starts clean
New session -> coldstart -> survey detects pending item with approved plan -> skip PLAN -> enter DO.
No `/compact` of plan-session state. CALLSHEET Phase 2.9 validates: "/clear not /compact — you can't verify what it kept."

### 3. Sub-agent delegation and session boundaries are complementary
- Sub-agents reduce cost WITHIN a session (plan-authoring-agent saves ~15% main context)
- Session boundaries prevent cumulative taint and give each phase a fresh window
- Both should be used for standard+ items

### 4. Changes are surgical
No new infrastructure needed. Modifications to existing skills:
1. **survey-cycle**: Detect pending work item with approved plan -> route to DO
2. **implementation-cycle PLAN phase**: Tier-aware yield after plan approval for standard+
3. **implementation-cycle**: Support direct DO-phase entry when plan is approved

## Evidence Base

| Evidence | Source | Finding |
|----------|--------|---------|
| 104% ceremony budget | mem:85390, 85606 | Full governed lifecycle cannot complete in one session |
| PLAN phase ~70% cost | mem:87482 | Single worst offender for context consumption |
| Plan round-tripping 30% | mem:89507 | 15% to author + 15% to re-read |
| S468 single-session success | mem:89508 | Small items complete efficiently without split |
| CALLSHEET slice-drafter | slice-drafter/skill.md:188-206 | Context reset between phases works in production |
| Plan-authoring-agent | mem:88086, 88277 | Sonnet delegation produces complete plans |
| Tier detection exists | PLAN.md:74-84 | Already determines trivial/small/standard/architectural |

## Epistemic Review

| Category | Finding | Citation |
|----------|---------|---------|
| KNOWN | 104% ceremony chain exceeds single-session budget | mem:85390, 85606 |
| KNOWN | Plan-authoring-agent produces complete plans via delegation | mem:88086, 88277 |
| KNOWN | CALLSHEET uses context reset between phases successfully | slice-drafter:188-206 |
| KNOWN | Tier detection already exists in PLAN.md exit gates | PLAN.md:74-84 |
| KNOWN | Checkpoint pending field already populated by plan-authoring CHAIN | SKILL.md:260-265 |
| INFERRED | Build-session minimal context load is under 20% budget | WORK.md + PLAN.md + specs + coldstart |
| INFERRED | Survey-cycle can detect approved-plan state and skip PLAN | cycle_phase + plan status queryable |
| UNKNOWN | Exact token cost per session type | Non-blocking; WORK-279 can measure |
| UNKNOWN | Operator experience with session splits | Non-blocking; operator initiated this |

**Verdict: PROCEED** — No blocking unknowns.

## Work Disposition

| Finding | Disposition | ID/Rationale |
|---------|------------|--------------|
| Tiered session architecture implementation | SPAWNED | WORK-289 |
| Token measurement for verification | DEFERRED | WORK-279 already covers |
| Operator experience evaluation | DEFERRED | Evaluate after first split |

## Cross-System Validation

CALLSHEET's `slice-drafter` skill already implements this pattern:
- Phase 2.9 (context reset): `/clear` then re-read key files
- Context limit resilience: if >70% consumed, launch next phase as background sub-agent
- Plan written to disk survives session boundaries
- Early context budget warnings for large items

This provides real-world evidence that the approach works. The HAIOS implementation is simpler (two sessions, not 12 sub-agents) but follows the same principle: **clean context per phase, plan artifacts on disk, deterministic load**.
