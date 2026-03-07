---
id: Ground
name: Context Loading
epoch: E2.2 (The Refinement)
status: Active
chapters:
- id: CH-001
  title: GroundCycle
  work_items: []
  requirements: []
  dependencies: []
  status: Complete
- id: CH-002
  title: PortalSystem
  work_items: []
  requirements: []
  dependencies: []
  status: Complete
- id: CH-003
  title: SessionManifest
  work_items: []
  requirements: []
  dependencies: []
  status: Complete
- id: CH-004
  title: CycleWiring
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
- id: CH-005
  title: ObservationCentralization
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
exit_criteria:
- text: ground-cycle designed and implemented (E2-276)
  checked: true
- text: Portal system (references/REFS.md) in work items (E2-277, S179)
  checked: true
- text: Session manifest contract (E2-281, E2-282)
  checked: true
- text: Calling cycles invoke ground-cycle before cognitive work
  checked: false
- text: E2-271 can be correctly planned with grounded context
  checked: false
---
# generated: 2026-01-06
# System Auto: last updated on: 2026-01-18T15:30:12
# Arc: Ground

## Arc Definition

**Arc ID:** Ground
**Epoch:** E2.2 (The Refinement)
**Name:** Context Loading
**Status:** Active
**Pressure:** [volumous] - thematic exploration
**Memory Refs:** 81222-81247 (checkpoint as manifest), 81351-81365 (S190 arc discussion)

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

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | GroundCycle | Complete | Design ground-cycle skill (E2-276 complete) |
| CH-002 | PortalSystem | Complete | Implement portals in work items (E2-277 complete, S179) |
| CH-003 | SessionManifest | **Complete** | E2-281/E2-282: Checkpoint as loading manifest |
| CH-004 | CycleWiring | Planned | Wire ground-cycle to calling cycles |
| CH-005 | ObservationCentralization | Planned | Epoch-level observation location for pattern review (S190) |

---

## Arc Completion Criteria

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
