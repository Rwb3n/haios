---
id: observability
epoch: E2.6
theme: System state visibility, epistemic discipline, agent capability cards, legacy
  cleanup
status: Complete
chapters:
- id: CH-041
  title: EpistemicReviewAndUXDoD
  work_items: []
  requirements:
  - WORK-082 (complete)
  - WORK-096
  - WORK-151 (spawned)
  dependencies:
  - REQ-CEREMONY-004
  - REQ-CEREMONY-003
  status: None
- id: CH-042
  title: AgentCards
  work_items: []
  requirements:
  - WORK-144
  dependencies:
  - REQ-DISCOVER-004
  status: None
- id: CH-043
  title: LegacyCleanup
  work_items: []
  requirements:
  - WORK-145
  dependencies:
  - REQ-CONFIG-003
  status: None
exit_criteria:
- text: 'Epistemic review ceremony designed (KNOWN/INFERRED/UNKNOWN at investigation
    boundary) — WORK-082 S372: inside CONCLUDE, three-level verdict, WORK-151 spawned
    for implementation'
  checked: true
- text: 'Agent UX Test criterion added to dod-validation-cycle (WORK-096 S380: agent
    UX test in DoD validation)'
  checked: true
- text: 'All 11 agents have structured capability cards (WORK-144: A2A-inspired agent
    cards)'
  checked: true
- text: 'Legacy duplication resolved (WORK-145 S377: lib/ orphans and deprecated artifacts
    cleaned up)'
  checked: true
---
# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T17:25:00
# Arc: Observability

## Definition

**Arc ID:** observability
**Epoch:** E2.6
**Theme:** System state visibility, epistemic discipline, agent capability cards, legacy cleanup
**Status:** Complete

---

## Purpose

The system must see itself. Epistemic state (KNOWN vs INFERRED vs UNKNOWN) is invisible at investigation boundaries. Agent capabilities are undocumented. Legacy duplication obscures what's real. This arc makes the system observable.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-CEREMONY-004 | Epistemic review ceremony at investigation->implementation boundary |
| REQ-CEREMONY-003 | Ceremonies distinct from lifecycles (WHEN vs WHAT) |
| REQ-DISCOVER-004 | All agents have capability cards |
| REQ-CONFIG-003 | Config follows single-source-of-truth principle |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies |
|-------|-------|------------|--------------|--------------|
| CH-041 | EpistemicReviewAndUXDoD | WORK-082 (complete), WORK-096, WORK-151 (spawned) | REQ-CEREMONY-004, REQ-CEREMONY-003 | None |
| CH-042 | AgentCards | WORK-144 | REQ-DISCOVER-004 | None |
| CH-043 | LegacyCleanup | WORK-145 | REQ-CONFIG-003 | None |

---

## Exit Criteria

- [x] Epistemic review ceremony designed (KNOWN/INFERRED/UNKNOWN at investigation boundary) — WORK-082 S372: inside CONCLUDE, three-level verdict, WORK-151 spawned for implementation
- [x] Agent UX Test criterion added to dod-validation-cycle (WORK-096 S380: agent UX test in DoD validation)
- [x] All 11 agents have structured capability cards (WORK-144: A2A-inspired agent cards)
- [x] Legacy duplication resolved (WORK-145 S377: lib/ orphans and deprecated artifacts cleaned up)

---

## Notes

- CH-041 merges WORK-082 (epistemic review investigation, medium) with WORK-096 (Agent UX DoD, small) — both ceremony-related observability
- WORK-082 complete (S372): Epistemic review is a CONCLUDE sub-step, not standalone ceremony. Spawned WORK-151 for implementation.
- WORK-151 (spawned by WORK-082): Implement K/I/U review + three-level verdict in investigation-cycle CONCLUDE phase

---

## References

- @docs/work/active/WORK-082/WORK.md
- @docs/work/active/WORK-096/WORK.md
- @docs/work/active/WORK-144/WORK.md
- @docs/work/active/WORK-145/WORK.md
- @docs/work/active/WORK-151/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-*, REQ-DISCOVER-004)
- Memory: 85419-85424 (WORK-082 findings)
