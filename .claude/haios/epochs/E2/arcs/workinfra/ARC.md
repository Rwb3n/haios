# generated: 2026-01-06
# System Auto: last updated on: 2026-01-18T15:30:36
# Arc: WorkInfra

## Arc Definition

**Arc ID:** workinfra
**Epoch:** E2
**Name:** Work Infrastructure
**Status:** Active
**Milestone ID:** M7b-WorkInfra (legacy reference)

---

## Purpose

Complete the work item lifecycle infrastructure. Wire Chariot modules to have runtime consumers. Implement portal system. Create ground-cycle for architectural context loading.

---

## REQUIRED READING

All work in this chapter MUST load these before planning:

| Document | Why Required |
|----------|--------------|
| `../../EPOCH.md` | Epoch-level architecture |
| `../../architecture/S17-modular-architecture.md` | Module interfaces |
| `../../architecture/S2C-work-item-directory.md` | Portal system design |

---

## Chapters

| Chapter | Name | Status | Work Items |
|---------|------|--------|------------|
| CH-001 | GroundCycle | Active | TBD |
| CH-002 | PortalSystem | Planned | TBD |
| CH-003 | ChariotWiring | Planned | TBD |

---

## Arc Completion Criteria

- [ ] ground-cycle designed and implemented
- [ ] Portal system (references/REFS.md) in all work items
- [ ] Chariot modules wired with runtime consumers
- [ ] ContextLoader loads chapter context
- [ ] E2-271 (and similar) can be correctly planned

---

## Key Decisions Made

| Decision | Choice | Arc/Work Item |
|----------|--------|---------------|
| Hierarchy naming | Epoch → Arc → Chapter → Work Item | ADR-042 (Session 191) |
| Context loading | ground-cycle as standalone cycle | Session 177 |

---

## References

- @.claude/haios/epochs/E2/EPOCH.md
- @docs/work/archive/INV-052/
