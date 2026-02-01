# generated: 2026-01-30
# System Auto: last updated on: 2026-02-01T21:04:52
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
| CH-006 | **Complete** | Node Transitions Investigation (Session 276) |
| CH-007 | Planned | Mode Field Addition |
| CH-008 | **NEW** | Queue Position Field (WORK-066) |

---

## Related Investigation: WORK-065 (Session 276)

**Finding:** Four-Dimensional Work Item State Model

| Dimension | Field | Values | Purpose |
|-----------|-------|--------|---------|
| 1. Lifecycle | `status` | active/blocked/complete/archived | ADR-041 authoritative |
| 2. Queue | `queue_position` | backlog/todo/in_progress/done | **NEW** - work selection pipeline |
| 3. Cycle | `cycle_phase` | discovery/plan/implement/close | RENAME from current_node |
| 4. Activity | `activity_state` | EXPLORE/DESIGN/PLAN/DO/CHECK/DONE | E2.4 (derived) |

**Key Insight:** `current_node` conflated queue position and cycle phase. 94% of work items stuck at `backlog` because cycles never called transitions.

**Decision:** Add `queue_position` field, wire cycles to update it.

**Implementation:** WORK-066

**Memory Refs:** 82952-82954, 82963-82973

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
