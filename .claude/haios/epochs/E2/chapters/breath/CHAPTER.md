# generated: 2026-01-06
# System Auto: last updated on: 2026-01-15T00:18:07
# Chapter: Breath

## Chapter Definition

**Chapter ID:** Breath
**Epoch:** E2.2 (The Refinement)
**Name:** Pressure Dynamics
**Status:** Active
**Pressure:** [volumous] - thematic exploration
**Memory Refs:** 81222-81247 (checkpoint redesign), 81248-81266 (drift diagnosis), 81351-81365 (S190 arc discussion)

---

## Theme

The rhythm of agent cognition: inhale (explore) and exhale (commit).

```
[volumous] → [tight] → [volumous] → [tight]
   inhale     exhale      inhale     exhale
```

**The fractal pattern:**
- Epoch [tight] → Chapter [volumous] → Arc [tight] → Work Item [volumous] → Phases [tight]

---

## REQUIRED READING

| Document | Why Required |
|----------|--------------|
| `../../EPOCH.md` | Epoch-level architecture |
| `../../architecture/S20-pressure-dynamics.md` | **PRIMARY** - The theory |
| `../../architecture/S22-skill-patterns.md` | Composable skill patterns |

---

## Arcs

| Arc | Name | Status | Purpose |
|-----|------|--------|---------|
| ARC-001 | ObservationIsolation | **Complete** | observation-capture-cycle standalone (INV-059) |
| ARC-002 | SessionCeremony | **Complete** | E2-281/282: Checkpoint as loading manifest (24 lines) |
| ARC-003 | MemoryRefEnforcement | **Active** | Coldstart MUST query load_memory_refs |
| ARC-004 | PhaseAnnotation | Planned | Add [MAY]/[MUST] to all skill phases |
| ARC-005 | BatchCycleExecution | Planned | Related work items: plan all → review → implement all (S190) |

---

## Key Insight (Session 179, refined Session 186)

**Session is ephemeral. Work item is durable. Checkpoint is a loading manifest.**

Session 186 discovered checkpoints were write-only activity logs that didn't prevent drift. Solution:

```yaml
# Checkpoint as manifest (E2-281)
load_principles: [S20, S22]  # MUST read
load_memory_refs: [81222...]  # MUST query
pending: [E2-283...]          # Work options
drift_observed: [...]         # Warnings
```

**Contract:** `/close` → `/new-checkpoint` → `/clear` → `/coldstart`

Operator owns `/clear` and `/coldstart`. System handles the rest.

---

## Chapter Completion Criteria

- [x] Observation capture is standalone skill (E2-280)
- [x] Checkpoint thinned (24 lines, manifest not log) (E2-281)
- [x] memory_refs enforced via load_memory_refs (E2-282)
- [ ] All skills annotated with pressure ([MAY]/[MUST])
- [ ] Agent actually breathes (doesn't skip volumous phases)

---

## References

- S20: Pressure Dynamics (FOUNDATIONAL)
- S22: Skill Patterns (composable)
- E2-281: Checkpoint Loading Manifest Redesign
- E2-282: Coldstart Hook Manifest Loading
- Memory 81222-81266: Session 186 architecture correction
