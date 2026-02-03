# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:12:17
# Critique Report: Queue Arc (CH-007 through CH-010)

## Executive Summary

The Queue arc chapters define a clear separation between queue position and lifecycle phase, addressing the WORK-065 finding where 94% of items were stuck at backlog due to conflation. The design is sound but contains several implicit assumptions and potential conflicts that need resolution.

**Overall Verdict: REVISE**

---

## Assumptions Registry

| ID | Chapter | Statement | Confidence | Risk if Wrong |
|----|---------|-----------|------------|---------------|
| A1 | CH-007 | WorkState dataclass exists and is authoritative | medium | Field may not propagate consistently |
| A2 | CH-007 | WORK.md frontmatter is single source of truth | high | Low risk - established |
| A3 | CH-007 | Migration of existing WORK.md files safe | medium | Could corrupt edge cases |
| A4 | CH-007 | Four dimensions are truly orthogonal | medium | Hidden constraints cause errors |
| A5 | CH-007 | status and queue_position don't overlap semantically | low | done/complete and active/active collision |
| A6 | CH-008 | close-work-cycle currently requires spawn_next | high | If allows null, chapter redundant |
| A7 | CH-008 | Governance rules requiring spawn are discoverable | medium | Some may be missed |
| A8 | CH-008 | "Store output" is a defined operation | low | No storage mechanism defined |
| A9 | CH-008 | DoD validation independent of spawn | high | DoD verifies deliverables |
| A10 | CH-009 | Four phases are sufficient | medium | May need intermediate states |
| A11 | CH-009 | Rollback only valid ready→backlog | medium | May need active→ready |
| A12 | CH-009 | "done" is truly terminal | high | Reopen problematic |
| A13 | CH-009 | Governance can enforce transitions | medium | Integration assumed |
| A14 | CH-010 | Skills infrastructure exists | medium | Ceremony skills blocked |
| A15 | CH-010 | governance-events.jsonl handles QueueCeremony | medium | Schema may need update |
| A16 | CH-010 | Ceremony contracts sufficient for implementation | medium | May need more detail |
| A17 | CH-010 | CH-011-CeremonyContracts.md exists | low | Pattern undefined |

---

## Blocking Assumptions

- **A5** (Low confidence): "active" terminology collision
- **A8** (Low confidence): Storage contract undefined
- **A17** (Low confidence): CH-011 dependency unverified

---

## Chapter-Specific Issues

### CH-007: Queue Position Field

**Gaps:**
- Initial value policy undefined (default queue_position?)
- Archived items: what queue_position?
- Blocked items: can queue_position be active?
- Forbidden state combinations undefined

**Terminology Issue:**
- `status: active` = work not blocked
- `queue_position: active` = being worked
- Same word, different meanings

### CH-008: Complete Without Spawn

**Gaps:**
- Where is output stored when not spawning?
- Relationship to Release ceremony unclear
- spawn_next field type (work ID or lifecycle reference?)

**Conflict:**
- CH-004 says lifecycle returns output, caller decides
- CH-008 says close_work accepts spawn_next=None
- Interaction unclear

### CH-009: Queue Lifecycle

**Gaps:**
- Concurrent active items policy undefined
- Transition triggers (who/what) unclear
- Error recovery on failed transitions
- Reopen scenario handling
- Priority within phases undefined

**Interface Concern:**
```python
QUEUE_TRANSITIONS = {...}  # Hardcoded
```
Should be configurable via YAML per REQ-CONFIG-002.

### CH-010: Queue Ceremonies

**Gaps:**
- Prioritize batch partial failure handling
- "Work session" definition unclear
- Release vs close_work DoD overlap
- Ceremony idempotency undefined
- Ceremony rollback undefined

**Critical Conflict:**
Release ceremony and close-work-cycle both:
- Verify DoD
- Update status to complete
- Update queue_position to done

Must clarify relationship.

---

## Cross-Chapter Conflicts

### Conflict 1: Release vs close_work()

Both CH-008 close_work() and CH-010 Release ceremony:
- Validate DoD
- Update status to complete
- Set queue_position to done

**Resolution Options:**
- A: close_work() IS Release ceremony
- B: close_work() invokes Release ceremony
- C: Different operations (needs clarification)

### Conflict 2: Terminology Collision

| Term | CH-007 meaning | Alternative |
|------|----------------|-------------|
| active (queue) | Being worked | `working` |
| active (status) | Not blocked | Keep |

**Recommendation:** Rename queue_position: active → working

---

## Recommendations

### High Priority (Blocking)

1. Clarify Release vs close_work() relationship
2. Define forbidden state combinations
3. Add storage contract for non-spawn completion

### Medium Priority

4. Rename queue_position: active → working
5. Make QUEUE_TRANSITIONS configurable
6. Add partial batch failure handling
7. Verify CH-011 exists

### Low Priority

8. Add concurrency policy
9. Add glossary for shared terms
10. Add error recovery paths

---

*Critique generated: 2026-02-03*
*Verdict: REVISE*
