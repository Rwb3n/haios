# generated: 2026-01-30
# System Auto: last updated on: 2026-02-01T16:55:32
# Arc: WorkUniversal (Carried from E2.3)

## Arc Definition

**Arc ID:** workuniversal
**Epoch:** E2.4 (The Activity Layer)
**Name:** Universal Work Item Structure
**Status:** Active (carried from E2.3)
**Pressure:** [volumous]

---

## Theme

Universal work item structure for pipeline portability.

**Carried from E2.3** - See @.claude/haios/epochs/E2_3/arcs/workuniversal/ARC.md for full context.

---

## E2.4 Additions

### Add `mode` Field

Per Session 265 L4 decision, work items need a `mode` field:

```yaml
mode: volumous | tight
```

Mode determines pressure/breath. Type determines routing.

**Two-axis model:**
- `mode`: volumous | tight
- `type`: investigate | design | implement | validate | triage

---

## Chapters (E2.3 status + E2.4 additions)

| Chapter | Status | Notes |
|---------|--------|-------|
| CH-001 | Complete | Schema Design (TRD approved) |
| CH-002 | Complete | Template Update |
| CH-003 | Complete | WorkEngine Adapt |
| CH-004 | Complete | Scaffold Update |
| CH-005 | Active | Validation Rules |
| CH-006 | **NEW** | Mode Field Addition |

---

## Related Investigation: WORK-059 (Session 274)

**Finding:** Two-Layer Work Tracking Model

| Layer | System | Scope | Persistence |
|-------|--------|-------|-------------|
| **Strategic** | HAIOS WorkEngine | Work items (WORK-XXX) | Disk (WORK.md) |
| **Tactical** | CC Task System | Sub-tasks within DO phase | Ephemeral (session) |

**Key Insight:** CC Tasks and WorkEngine are COMPLEMENTARY, not competing.
- WorkEngine: Governed, traceable, cross-session
- CC Tasks: Fast, UX-focused (activeForm spinner), auto-cleanup

**Recommendation:** Agent SHOULD use CC Tasks for DO phase micro-tracking (L2 RECOMMENDED).
No integration between systems needed - intentional separation of concerns.

**Memory Refs:** 82904-82914

---

## Memory Refs

Session 265 two-axis model: 82693-82705

---

## References

- @.claude/haios/epochs/E2_3/arcs/workuniversal/ARC.md (source)
- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md
