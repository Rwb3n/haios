# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T12:50:00
# Arc: Observability

## Definition

**Arc ID:** observability
**Epoch:** E2.6
**Theme:** System state visibility, epistemic discipline, agent capability cards, legacy cleanup
**Status:** Planning

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
| CH-041 | EpistemicReviewAndUXDoD | WORK-082, WORK-096 | REQ-CEREMONY-004, REQ-CEREMONY-003 | None |
| CH-042 | AgentCards | WORK-144 | REQ-DISCOVER-004 | None |
| CH-043 | LegacyCleanup | WORK-145 | REQ-CONFIG-003 | None |

---

## Exit Criteria

- [ ] Epistemic review ceremony designed (KNOWN/INFERRED/UNKNOWN at investigation boundary)
- [ ] Agent UX Test criterion added to dod-validation-cycle (optional)
- [ ] All 11 agents have structured capability cards
- [ ] Legacy duplication resolved (lib/ orphans, deprecated artifacts)

---

## Notes

- CH-041 merges WORK-082 (epistemic review investigation, medium) with WORK-096 (Agent UX DoD, small) — both ceremony-related observability
- WORK-082 is an investigation; spawned implementation (WORK-081) deferred per spawn-deferral policy unless it serves E2.6 exit criteria

---

## References

- @docs/work/active/WORK-082/WORK.md
- @docs/work/active/WORK-096/WORK.md
- @docs/work/active/WORK-144/WORK.md
- @docs/work/active/WORK-145/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-*, REQ-DISCOVER-004)
