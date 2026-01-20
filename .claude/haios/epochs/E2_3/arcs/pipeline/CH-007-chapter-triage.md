# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:14:20
# Chapter: Chapter Triage

## Definition

**Chapter ID:** CH-007
**Arc:** pipeline
**Status:** Planned
**Depends:** None

---

## Problem

No defined process for turning design (chapters) into implementation (work items).

Current state:
```
Chapter exists
    │
    └── ??? → Work items somehow created
```

Agent creates work items ad-hoc. No traceability. No approval gate.

---

## Agent Need

> "Given an approved chapter, I need to know how to decompose it into work items."

---

## Requirements

### R1: Chapter Approval Gate

Chapter must be explicitly approved before triage.

```
Chapter status: Planned → Approved → In Progress → Complete
```

Only `Approved` chapters can spawn work items.

### R2: Requirement → Work Item Mapping

Each chapter requirement (R1, R2, ...) maps to one or more work items.

```
CH-002 Session Simplify
├── R1: Single value file      → WORK-NNN
├── R2: Read is trivial        → (same work item)
├── R3: Increment is trivial   → WORK-NNN
└── R4: Discoverable           → WORK-NNN
```

### R3: Work Item Chapter Reference

Work item frontmatter includes chapter:

```yaml
chapter: CH-002
arc: configuration
requirement_refs: [R1, R2]
```

### R4: Triage Output

Triage produces:
1. List of work items to create
2. Dependency graph (blocked_by)
3. Suggested order

```
Triage Result:
  WORK-NNN: Create .claude/session (R1)
  WORK-NNN: Update just session-start (R3)
    blocked_by: [WORK-NNN]
  WORK-NNN: Update coldstart (R4)
    blocked_by: [WORK-NNN]
```

### R5: Operator Confirmation

Agent proposes triage. Operator confirms or adjusts.

```
Agent: "I propose 3 work items for CH-002. [details]"
Operator: "Approved" or "Combine WORK-2 and WORK-3"
```

---

## Interface

```
Input: Approved chapter file
Output: Work item creation commands or proposals

Process:
1. Read chapter requirements
2. Group requirements by implementation unit
3. Identify dependencies
4. Propose work items
5. Await operator confirmation
6. Create work items with chapter reference
```

---

## Success Criteria

- [ ] Chapters have approval status field
- [ ] Work items have chapter reference field
- [ ] Triage process documented
- [ ] Agent can propose work items from chapter
- [ ] Operator approval required before creation

---

## Non-Goals

- Automatic work item creation (always needs operator)
- Requirement tracking beyond chapter reference
- Test generation from requirements
