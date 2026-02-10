---
id: obs-314-01
session: 314
date: 2026-02-05
dimension: architecture
triage_status: pending
potential_action: investigation
parked_for: E2.6
discovered_during: Session-314-review
generated: '2026-02-05'
last_updated: '2026-02-10T22:10:00'
---
# Observation: Missing Ceremony for Operator-Initiated System Evolution

## What Was Observed

Session 314 process review revealed an incomplete ceremony chain:

1. Session Review ("what went well / could've gone better") - produces learnings
2. Process Review ("keep / should / stop") - produces proposed L3/L4 changes
3. **???** - no ceremony governs how proposed upstream changes get approved and applied

The feedback arc assumes bottom-up flow (work -> chapter -> arc -> epoch -> requirements). Session 314 demonstrated top-down flow (operator reflection -> requirements change -> trickle down). No ceremony exists for this pattern.

## Why It Matters

Without a governed path for operator-initiated system evolution:
- Decisions about L3/L4 changes happen ad-hoc in conversation
- No threshold criteria for: memory note vs observation vs work item vs immediate L3/L4 mod
- No audit trail for why system rules changed
- Next agent has no context about what governance path was followed

## Additional Finding (Session 339)

Session 339 observation review surfaced a fourth gap in the ceremony chain:

4. **Batch Scope Triage** - no ceremony for reviewing accumulated themes across observations and deciding epoch scope (E2.5 vs park E2.6)

This is distinct from `observation-triage` (individual item SCAN/TRIAGE/PROMOTE) and `epoch-review` (is the epoch on track?). It operates at a different granularity: operator reviews patterns across many observations and memory entries, then makes batch scoping decisions about what fits current epoch vs next.

The full missing chain is now:
1. Session Review -> learnings
2. Process Review -> proposed behavioral changes (K/S/D)
3. Batch Scope Triage -> epoch scoping decisions
4. System Evolution -> governed application of upstream changes

All four are operator-initiated, top-down ceremonies with no existing skill or registry entry.

## Recommendation

E2.6 investigation scope:
- Define "System Evolution" ceremony with input/output contract
- Define threshold criteria for routing Process Review findings
- Define batch scope triage ceremony (distinct from observation-triage)
- Consider: should L3/L4 modifications require ADR?
- Related: WORK-101 (proportional governance), WORK-102 (review ceremonies)

## Links

- related_work: [WORK-101, WORK-102]
- related_requirement: REQ-FEEDBACK-004, REQ-CEREMONY-002
- epoch_context: E2.5 Independent Lifecycles (out of scope, parked for E2.6)
