# generated: 2026-01-18
# System Auto: last updated on: 2026-01-18T20:20:28
# Arc: Observations

## Arc Definition

**Arc ID:** Observations
**Epoch:** E2.3 (The Pipeline)
**Name:** Observation Lifecycle Rewiring
**Status:** Active
**Pressure:** [volumous] - thematic exploration

---

## Theme

Rewire observation lifecycle for three-phase flow and new file structure.

**Current:**
- CAPTURE + TRIAGE (two phases compressed)
- Work observations in `docs/work/active/{id}/observations.md`
- Triage has `memory` action (that's promotion, not triage)

**Target:**
- CAPTURE → PROMOTE → TRIAGE (three phases)
- Work observations in `epochs/E2_3/work/{id}/observations.md`
- Atomic promoted obs at `epochs/E2_3/observations/obs-{session}-{seq}.md`
- Triage acts on promoted obs, not raw captures

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | ObservationPromoteCycle | Planned | New skill: filter raw → atomic obs files |
| CH-002 | CapturePathUpdate | Planned | Update observation-capture to write to epoch work dir |
| CH-003 | TriageRefactor | Planned | Remove `memory` action, scan epoch obs dir |
| CH-004 | AtomicObsTemplate | Planned | Template for obs-{session}-{seq}.md |
| CH-005 | ObservationsLibUpdate | Planned | Update observations.py paths and functions |

---

## Three-Phase Flow

```
CAPTURE → PROMOTE → TRIAGE
   │          │         │
   │          │         └→ spawn:WORK, discuss, dismiss
   │          │
   │          └→ atomic obs file + memory with provenance
   │
   └→ raw notes in work/{id}/observations.md
```

**CAPTURE** (observation-capture-cycle)
- When: Work close
- Input: 3 questions
- Output: `epochs/E2_3/work/{id}/observations.md`

**PROMOTE** (observation-promote-cycle - NEW)
- When: After capture
- Input: Raw observations from work
- Output: `epochs/E2_3/observations/obs-{session}-{seq}.md` + memory

**TRIAGE** (observation-triage-cycle - REFACTORED)
- When: Periodically or threshold
- Input: Epoch obs files
- Output: spawn:WORK, discuss, dismiss

---

## Exit Criteria

- [ ] Three-phase flow implemented
- [ ] Observations in epochs, not docs/
- [ ] Atomic obs files created by promote cycle
- [ ] Triage scans epoch obs dir

---

## References

- @obs-206-009.md (three-phase insight)
- @obs-206-008.md (work in epochs)
- @.claude/skills/observation-capture-cycle/SKILL.md
- @.claude/skills/observation-triage-cycle/SKILL.md
