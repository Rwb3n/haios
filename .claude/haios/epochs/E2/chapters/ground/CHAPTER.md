# generated: 2026-01-06
# System Auto: last updated on: 2026-01-12T01:13:28
# Chapter: Ground

## Chapter Definition

**Chapter ID:** Ground
**Epoch:** E2.2 (The Refinement)
**Name:** Context Loading
**Status:** Active
**Pressure:** [volumous] - thematic exploration
**Memory Refs:** 81222-81247 (checkpoint as manifest)

---

## Theme

Load architectural context before cognitive work begins.

**Three-tier context model:**
- Session-level: Checkpoint manifest (load_principles, load_memory_refs)
- Boot-level: ContextLoader.GroundedContext (L0-L4 manifesto)
- Work-level: ground-cycle.GroundedContext (epoch/chapter/arc/provenance)

**Session handoff contract (E2-281/E2-282):**
```
/close → /new-checkpoint → /clear → /coldstart
           ↓                           ↓
    Creates manifest              Loads manifest
```

**Portal system:** Work items are self-contained universes with portals to other universes (references/REFS.md).

---

## REQUIRED READING

| Document | Why Required |
|----------|--------------|
| `../../EPOCH.md` | Epoch-level architecture |
| `../../architecture/S14-bootstrap-architecture.md` | Session-level context |
| `../../architecture/S2C-work-item-directory.md` | Portal system |

---

## Arcs

| Arc | Name | Status | Purpose |
|-----|------|--------|---------|
| ARC-001 | GroundCycle | Complete | Design ground-cycle skill (E2-276 complete) |
| ARC-002 | PortalSystem | Complete | Implement portals in work items (E2-277 complete, S179) |
| ARC-003 | SessionManifest | **Complete** | E2-281/E2-282: Checkpoint as loading manifest |
| TBD | CycleWiring | Planned | Wire ground-cycle to calling cycles |

---

## Chapter Completion Criteria

- [x] ground-cycle designed and implemented (E2-276)
- [x] Portal system (references/REFS.md) in work items (E2-277, S179)
- [x] Session manifest contract (E2-281, E2-282)
- [ ] Calling cycles invoke ground-cycle before cognitive work
- [ ] E2-271 can be correctly planned with grounded context

**Session 188 Note:** Better context loading = agent more likely to follow skills. Context is soft enforcement - grounds agent in architecture before work. Within Claude Code this is the best available lever. SDK harness (Epoch 4) will use same context patterns with hard enforcement.

---

## References

- S14: Bootstrap Architecture
- S25: SDK Path to Autonomy (context patterns carry forward)
- S2C: Work Item Directory (now notes "Implemented in WorkEngine E2-277")
- E2-276: Design ground-cycle skill (complete)
- E2-277: Implement Portal System (complete, S179)
- E2-281: Checkpoint Loading Manifest Redesign (complete)
- E2-282: Coldstart Hook Manifest Loading (complete)
- INV-062: Session State Tracking (context as soft enforcement)
- Memory 81222-81247: Checkpoint redesign
