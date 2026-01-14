# generated: 2026-01-06
# System Auto: last updated on: 2026-01-12T01:12:58
# Chapter: Form

## Chapter Definition

**Chapter ID:** Form
**Epoch:** E2.2 (The Refinement)
**Name:** Skill Decomposition
**Status:** Active
**Pressure:** [volumous] - thematic exploration
**Memory Refs:** 81211-81221 (skills as procedural theater), 81248-81266 (drift diagnosis)

---

## Theme

Smaller containers, harder boundaries. Each skill does ONE thing.

**From monoliths to atoms:**

| Now | Should be | Work Item |
|-----|-----------|-----------|
| ~~survey-cycle (5 phases, 241 lines)~~ | Minimal routing (42 lines) | **E2-283 DONE** |
| ~~observation-capture-cycle (3 phases, 134 lines)~~ | 3 questions, hard gate (41 lines) | **E2-284 DONE** |
| skill template (phases default) | Single-phase default | E2-285 |
| checkpoint template (112 lines) | Loading manifest (24 lines) | **E2-281 DONE** |

**Session 186 Drift Diagnosis:**
> "We agreed on the philosophy ('smaller containers') and built the opposite ('more phases')."

Skills became procedural scripts. Agent pattern-matches through phases without thinking differently. Exit criteria checklists are self-validated ceremony.

**What works:** Templates (structure output), Hooks (block actions)
**What doesn't:** Skills with phases (guide process)

**Session 188 Reality Check (INV-062):**
> "Skill simplification without enforcement is cosmetic - shorter theater is still theater."

Within Claude Code, Skill() is not hookable. Hard enforcement requires SDK migration (Epoch 4). Simplification still provides value:
- Marginally better compliance (less to pattern-match through)
- Easier to port to SDK custom tools later
- Better observability when combined with soft enforcement (E2-286/287/288)

---

## REQUIRED READING

| Document | Why Required |
|----------|--------------|
| `../../EPOCH.md` | Epoch-level architecture |
| `../../architecture/S20-pressure-dynamics.md` | **PRIMARY** - Lines 92-107 define the target |
| `../../architecture/S22-skill-patterns.md` | Composable skill patterns |

---

## Arcs

| Arc | Name | Status | Purpose |
|-----|------|--------|---------|
| ARC-001 | ConfigDrivenGeneration | Planned | haios.yaml is source of truth; plumbing regenerates from config |
| ARC-002 | CategoryRouting | Planned | Route by category, not prefix |
| ARC-003 | TemplateSimplification | **Complete** | E2-281: Checkpoint 112→24, E2-284: Observations 105→26 |
| ARC-004 | SkillAtomization | **Active** | ~~E2-283~~, ~~E2-284~~, E2-285: Prune verbose skills |
| ARC-005 | SoftEnforcement | **Active** | E2-286/287/288: Observability + warnings (INV-062 spawned) |

---

## Chapter Completion Criteria

- [ ] Category field drives routing (not ID prefix)
- [x] Templates simplified (checkpoint 112→24 lines, observations 105→26 lines)
- [x] Skills decomposed into single-responsibility units (E2-283 DONE, E2-284 DONE, E2-285 pending)
- [ ] UNIX philosophy applied: each skill does one thing well
- [ ] Skill template defaults to single-phase (E2-285)
- [ ] Soft enforcement operational (E2-286/287/288)

---

## References

- S20: Pressure Dynamics (lines 92-107: "smaller containers, harder boundaries")
- S22: Skill Patterns (composable)
- S25: SDK Path to Autonomy (hard enforcement requires Epoch 4)
- E2-281: Checkpoint Loading Manifest Redesign (DONE)
- E2-283: Survey-Cycle Prune to Minimal Routing (DONE)
- E2-284: Observation-Capture Simplify to 3 Questions (DONE)
- E2-285: Skill Template Single-Phase Default
- E2-286/287/288: Soft Enforcement (session_state, warnings, set-cycle)
- INV-062: Session State Tracking investigation (SDK discovery)
- Memory 81211-81266: Session 186 architecture correction
- Memory 81299-81333: Session 188 enforcement gap + SDK discovery
