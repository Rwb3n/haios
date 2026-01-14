# generated: 2026-01-06
# System Auto: last updated on: 2026-01-06T19:46:48
# Chapter: WorkInfra

## Chapter Definition

**Chapter ID:** C3-WorkInfra
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

## Arcs

| Arc | Name | Status | Work Items |
|-----|------|--------|------------|
| ARC-001 | GroundCycle | Active | TBD |
| ARC-002 | PortalSystem | Planned | TBD |
| ARC-003 | ChariotWiring | Planned | TBD |

---

## Chapter Completion Criteria

- [ ] ground-cycle designed and implemented
- [ ] Portal system (references/REFS.md) in all work items
- [ ] Chariot modules wired with runtime consumers
- [ ] ContextLoader loads chapter context
- [ ] E2-271 (and similar) can be correctly planned

---

## Key Decisions Made

| Decision | Choice | Arc/Work Item |
|----------|--------|---------------|
| Hierarchy naming | Epoch → Chapter → Arc → Work Item | Session 177 |
| Context loading | ground-cycle as standalone cycle | Session 177 |

---

## References

- @.claude/haios/epochs/E2/EPOCH.md
- @docs/work/archive/INV-052/
