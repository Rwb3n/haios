# generated: 2026-02-17
# System Auto: last updated on: 2026-02-17T21:00:00
# Arc: Call

## Definition

**Arc ID:** call
**Epoch:** E2.8
**Theme:** The agent should not read what it can call
**Status:** Planning
**Started:** 2026-02-17 (Session 393)

---

## Purpose

Move mechanical ceremony phases from SKILL.md (agent reads) to hooks/modules (auto-execute). Proportional scaling for phases that require judgment. The agent should spend tokens on decisions, not on reading ceremony instructions.

**The Structural Problem:** Full ceremony chain consumes ~104% of 200k context budget (mem:85390). Ceremony skills are markdown — the agent is the runtime (mem:84857). Moving mechanical phases to hooks/modules eliminates token cost for judgment-free operations.

**The Three Governance Mechanisms:**
| Mechanism | Token Cost | Examples |
|-----------|-----------|----------|
| Hooks (PreToolUse, PostToolUse, UserPromptSubmit) | ~0 | Time injection, write blocks, SQL blocks |
| Python modules (lib/, modules/) | ~0 | queue_ceremonies.py, status_propagator.py |
| Ceremony skills (SKILL.md) | 100% agent tokens | implementation-cycle, retro-cycle |

This arc moves what it can from Tier 3 (SKILL.md) to Tier 1/2 (hooks/modules).

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-CEREMONY-001 | Ceremonies are side-effect boundaries |
| REQ-CEREMONY-002 | Ceremony overhead proportional to work complexity |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-058 | ProportionalGovernanceDesign | WORK-101 | REQ-CEREMONY-001 | None | Complete |
| CH-059 | CeremonyAutomation | New | REQ-CEREMONY-002 | CH-058 | Planning |
| CH-060 | SessionBoundaryFix | WORK-161 | REQ-CEREMONY-001 | None | Complete |

---

## Exit Criteria

- [ ] Governance overhead measurably reduced (target: perceptible improvement over E2.5 baseline)
- [ ] Trivial items skip heavy ceremony phases (computable predicates, extending retro-cycle Phase 0 pattern)
- [ ] Mechanical ceremony phases migrated to hooks/modules (session-end, checkpoint population, cycle_phase advancement)
- [x] Session boundary gap governed (post-closure transition runs reliably) (WORK-161, S396)

---

## Notes

- WORK-101 (Proportional Governance Design) unparked Session 394, assigned to CH-058. Plan approved S397.
- Retro-cycle Phase 0 (S393, mem:85607/85363) is the prototype: computable predicate skips retro for trivial items
- Session boundary gap (mem:85609, 85385, 85387): last 2-3 ceremonies in a session never run because context exhausted

---

## References

- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- @docs/work/active/WORK-101/WORK.md (proportional governance design)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-*)
- Memory: 85390 (104% problem), 85609 (session gap), 84857 (ceremony=markdown), 85607/85363 (retro Phase 0)
