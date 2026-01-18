# generated: 2026-01-06
# System Auto: last updated on: 2026-01-18T15:34:14
# Arc: Breath

## Arc Definition

**Arc ID:** Breath
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
- Epoch [tight] → Arc [volumous] → Chapter [tight] → Work Item [volumous] → Phases [tight]

---

## REQUIRED READING

| Document | Why Required |
|----------|--------------|
| `../../EPOCH.md` | Epoch-level architecture |
| `../../architecture/S20-pressure-dynamics.md` | **PRIMARY** - The theory |
| `../../architecture/S22-skill-patterns.md` | Composable skill patterns |

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | ObservationIsolation | **Complete** | observation-capture-cycle standalone (INV-059) |
| CH-002 | SessionCeremony | **Complete** | E2-281/282: Checkpoint as loading manifest (24 lines) |
| CH-003 | MemoryRefEnforcement | **Active** | Coldstart MUST query load_memory_refs |
| CH-004 | PhaseAnnotation | Planned | Add [MAY]/[MUST] to all skill phases |
| CH-005 | BatchCycleExecution | Planned | Related work items: plan all → review → implement all (S190) |
| CH-006 | SessionStateWiring | **Complete** | E2-293/294/295: All skills call set-cycle/clear-cycle (S196) |
| CH-007 | ObservationTriageOperationalization | **Active** | E2-296: Triage happens but isn't triggered (INV-067 S198) |

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

## Arc Completion Criteria

- [x] Observation capture is standalone skill (E2-280)
- [x] Checkpoint thinned (24 lines, manifest not log) (E2-281)
- [x] memory_refs enforced via load_memory_refs (E2-282)
- [x] Session state wiring complete - all skills update session_state (E2-293/294/295)
- [ ] All skills annotated with pressure ([MAY]/[MUST])
- [ ] Agent actually breathes (doesn't skip volumous phases)

---

## Session 198 Insight (INV-067)

**Observation capture works. Observation triage doesn't happen.**

INV-067 discovered that Session 197's observation extraction "re-discovered" 15 observations already captured in `docs/work/archive/*/observations.md`. The capture mechanism (close-work-cycle OBSERVE phase) works correctly. The gap is:

1. **No trigger** - observation-triage-cycle exists (E2-218) but nothing invokes it
2. **No schedule** - no session-end prompt or threshold routing to triage
3. **Accumulation** - observations pile up without review

**Pattern learned:** "Re-discovery" investigations reveal process gaps, not content gaps. When investigation "finds" existing things, the real finding is underutilized infrastructure.

**Spawned work:** E2-296 (Observation Triage Batch)

---

## Session 205 Observations (triaged from E2-296, E2-299)

**CH-007 (ObservationTriageOperationalization) gaps identified:**
- Gap: Triage log missing in observations.md - files get `triage_status: triaged` but no structured log of decisions (E2-296)
- Gap: Batch triage automation needed - processing 35 observations manually is time-consuming (E2-296)
- Gap: Triage should follow capture - observation-triage-cycle exists but has no trigger (E2-296)

**Insight validated:**
- The observation->triage->fix pipeline WORKS when exercised: typo caught during E2-253 -> documented in observations.md -> triaged by INV-067 -> spawned as E2-299 -> fixed in S200 (E2-299)

---

## References

- S20: Pressure Dynamics (FOUNDATIONAL)
- S22: Skill Patterns (composable)
- E2-281: Checkpoint Loading Manifest Redesign
- E2-282: Coldstart Hook Manifest Loading
- E2-293/294/295: Session State Cascade Wiring (Session 196)
- E2-296: Observation Triage Batch (Session 198, spawned by INV-067)
- INV-065: Session State Cascade Architecture (Session 194)
- INV-067: Observation Backlog Verification and Triage (Session 197-198)
- Memory 81222-81266: Session 186 architecture correction
- Memory 81396-81401: Session 195 plan decomposition learnings
- Memory 81412-81418: INV-067 closure learnings (S198)
