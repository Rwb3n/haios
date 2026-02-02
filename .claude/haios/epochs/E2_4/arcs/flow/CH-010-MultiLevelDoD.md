# generated: 2026-02-02
# System Auto: last updated on: 2026-02-02T12:49:13
# Chapter: MultiLevelDoD

## Definition

**Chapter ID:** CH-010
**Arc:** flow
**Status:** Active
**implements_decisions:** [D8]
**Depends:** CH-009

---

## Problem

How do we verify that completing all work items actually achieves chapter/arc/epoch objectives?

Current state: Only work items have DoD (ADR-033). Chapters, arcs, and epochs can be declared "done" without verification.

**Gap:** Work item completion does not guarantee hierarchy-level completion. "Sum of parts != whole."

---

## Solution: Multi-Level DoD Ceremonies

Three new ceremonies verify completeness at each hierarchy level:

| Level | Ceremony | DoD Criteria |
|-------|----------|--------------|
| Chapter | close-chapter-ceremony | All work complete + implements_decisions verified |
| Arc | close-arc-ceremony | All chapters complete + no orphan decisions |
| Epoch | close-epoch-ceremony | All arcs complete + all decisions implemented |

### Ceremony Pattern

Each ceremony follows VALIDATE -> MARK -> REPORT cycle:

1. **VALIDATE** - Check DoD criteria for the level
2. **MARK** - Update status to Complete
3. **REPORT** - Summarize closure

### L4 Requirements

| Requirement | Ceremony | Criteria |
|-------------|----------|----------|
| REQ-DOD-001 | close-chapter-ceremony | All work items complete + implements_decisions match |
| REQ-DOD-002 | close-arc-ceremony | All chapters complete + no orphan decisions |

### DoD Cascade

```
Work Item (ADR-033)
    |
    v
Chapter (REQ-DOD-001)
    |
    v
Arc (REQ-DOD-002)
    |
    v
Epoch (close-epoch-ceremony)
```

Lower level must complete before higher level can close.

---

## Exit Criteria

- [x] REQ-DOD-001 and REQ-DOD-002 created (Session 285)
- [x] close-chapter-ceremony skill implemented (WORK-076, Session 286)
- [ ] close-arc-ceremony skill implemented (WORK-077)
- [ ] close-epoch-ceremony skill implemented (WORK-078)
- [x] Tests pass (6/6 - Session 285)

---

## Memory Refs

Session 279: 83018-83029 (multi-level governance investigation)
Session 285: [to be added on closure]

---

## References

- @docs/work/active/WORK-055/WORK.md (source investigation)
- @docs/work/active/WORK-070/WORK.md (this implementation)
- @.claude/haios/epochs/E2_4/arcs/flow/CH-009-DecisionTraceability.md (dependency)
- @docs/ADR/ADR-033-work-item-lifecycle.md (work item DoD)
