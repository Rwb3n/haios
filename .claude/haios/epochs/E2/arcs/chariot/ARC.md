# generated: 2026-01-06
# System Auto: last updated on: 2026-01-17T12:06:50
# Arc: Chariot

## Arc Definition

**Arc ID:** Chariot
**Epoch:** E2.2 (The Refinement)
**Name:** Module Architecture
**Status:** Active
**Pressure:** [volumous] - thematic exploration
**Memory Refs:** 81194-81198 (E2-279 decomposition), 81199-81210 (closure), 81351-81365 (S190 arc discussion)

---

## Theme

The 9 Chariot modules that make HAIOS portable and LLM-agnostic:

| Module | Breath | Function | Lines |
|--------|--------|----------|-------|
| ContextLoader | Inhale | Take in context (L0-L4) | ~300 |
| MemoryBridge | Inhale | Take in prior knowledge | ~450 |
| CycleRunner | Rhythm | Enforce inhale/exhale pattern | ~350 |
| GovernanceLayer | Exhale | Gates, verification, commitment | ~350 |
| WorkEngine | Exhale | Commit state to truth (core CRUD) | ~585 |
| CascadeEngine | Exhale | Completion cascade, unblock | ~387 |
| PortalManager | Exhale | REFS.md management | ~230 |
| SpawnTree | Exhale | Spawn tree traversal | ~170 |
| BackfillEngine | Exhale | Backlog content backfill | ~220 |

*E2-279 (Session 186): WorkEngine decomposed 1197→585 lines. 4 satellites extracted with lazy delegation.*

---

## REQUIRED READING

| Document | Why Required |
|----------|--------------|
| `../../EPOCH.md` | Epoch-level architecture |
| `../../architecture/S17-modular-architecture.md` | Module interfaces |
| `../../architecture/S20-pressure-dynamics.md` | Module ↔ breath mapping |
| `../../architecture/S25-sdk-path-to-autonomy.md` | Epoch 4 migration path (SDK enables hard enforcement) |

---

## Arcs

| Arc | Name | Status | Purpose |
|-----|------|--------|---------|
| ARC-001 | ModuleWiring | **Complete** | E2-279: WorkEngine delegates to satellites |
| ARC-002 | BoundaryEnforcement | Planned | Enforce module boundaries (hooks?) |
| ARC-003 | SDKMigration | Vision | Claude Agent SDK enables hard enforcement (S25, Epoch 4) |
| ARC-004 | PathAuthority | Planned | Recipes own paths - agent doesn't hardcode (S190) - **INV-041 exists** |
| ARC-005 | FileTypeLocking | Planned | PreToolUse enforces what file types go where (S190) |

---

## Chapter Completion Criteria

- [x] All 9 modules have runtime consumers (E2-279)
- [ ] Module boundaries enforced (no cross-boundary calls)
- [ ] Portable plugin structure works

---

## References

- S17: Modular Architecture
- S20: Pressure Dynamics (breath mapping)
- S25: SDK Path to Autonomy (Epoch 4 migration)
- E2-279: WorkEngine Decomposition (Session 185-186)
- E2-293: session_state schema extension (active_queue, phase_history)
- INV-065: Session State Cascade Architecture (Session 194)
- INV-062: Session State Tracking (enforcement gaps)
- Memory 81194-81210: Decomposition learnings
- Memory 81309-81324: SDK discovery
