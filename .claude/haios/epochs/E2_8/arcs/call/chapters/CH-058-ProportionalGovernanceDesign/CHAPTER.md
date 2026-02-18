# generated: 2026-02-18
# System Auto: last updated on: 2026-02-18T23:30:00
# Chapter: ProportionalGovernanceDesign

## Chapter Definition

**Chapter ID:** CH-058
**Arc:** call
**Epoch:** E2.8
**Name:** Proportional Governance Design
**Status:** Planning

---

## Purpose

Define the L3 principle and L4 requirements for proportional governance — governance overhead that scales with blast radius instead of being uniform. This is the design foundation that CH-059 (CeremonyAutomation) implements.

**Core insight:** Full ceremony chain consumes ~104% of 200k context budget (mem:85390). A 15-minute investigation goes through the same 8-skill chain as a multi-session redesign. Governance must scale with risk, not be uniform.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-101 | Proportional Governance Design | Active | design |

---

## Exit Criteria

- [ ] L3.20 Proportional Governance principle defined
- [ ] REQ-LIFECYCLE-005 fast-path requirement defined
- [ ] REQ-CEREMONY-005 proportional depth requirement defined
- [ ] Close-work-cycle updated with pytest hard gate
- [ ] Complexity threshold criteria documented

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| Blocks | CH-059 (CeremonyAutomation) | CH-059 implements what CH-058 designs |
| None | - | No inbound dependencies |

---

## References

- @.claude/haios/epochs/E2_8/arcs/call/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- @docs/work/active/WORK-101/WORK.md (work item)
- @.claude/haios/manifesto/L3-requirements.md (target: L3.20)
- @.claude/haios/manifesto/L4/functional_requirements.md (target: REQ-LIFECYCLE-005, REQ-CEREMONY-005)
- Memory: 85390 (104% problem), 85607/85363 (retro Phase 0 prototype), 84332 (40% overhead)
