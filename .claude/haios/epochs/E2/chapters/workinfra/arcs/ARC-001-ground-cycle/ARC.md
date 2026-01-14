# generated: 2026-01-06
# System Auto: last updated on: 2026-01-06T21:21:25
# Arc: ground-cycle

## Arc Definition

**Arc ID:** ARC-001
**Chapter:** C3-WorkInfra
**Epoch:** E2
**Name:** ground-cycle Implementation
**Status:** Active

---

## Purpose

Design and implement ground-cycle - the standalone cycle that loads architectural context before any cognitive work. This is the missing piece that ensures agents know the Epoch 2.2 architecture before planning or implementing.

---

## REQUIRED READING

**MUST load before ANY work in this arc:**

| Document | Location | Why Required |
|----------|----------|--------------|
| Epoch Definition | `../../../EPOCH.md` | Epoch-level architecture decisions |
| Modular Architecture | `../../../architecture/S17-modular-architecture.md` | Module interfaces ground-cycle must respect |
| Work Item Directory | `../../../architecture/S2C-work-item-directory.md` | Portal system ground-cycle traverses |
| Bootstrap Architecture | `../../../architecture/S14-bootstrap-architecture.md` | Context loading hierarchy |
| Information Architecture | `../../../architecture/S15-information-architecture.md` | Token budgets for grounded context |
| Chapter Definition | `../../CHAPTER.md` | Chapter-level context |

---

## Problem Statement

E2-271 plan was authored referencing `.claude/lib/` as correct module location. INV-052 specifies `.claude/haios/modules/`. The architectural decision was LOST because:
1. Nothing traverses `spawned_by_investigation` to load source investigation
2. plan-authoring-cycle has "MUST query memory" but doesn't traverse provenance
3. No mechanism builds context map before cognitive work

---

## Design

### ground-cycle Phases

```
PROVENANCE → ARCHITECTURE → MEMORY → CONTEXT MAP
```

**PROVENANCE Phase:**
- Read work item's `spawned_by_investigation`
- Traverse chain: E2-271 → INV-057 → INV-052
- Load each investigation's key findings

**ARCHITECTURE Phase:**
- Read work item's `epoch` field
- Load epoch's architectural sections
- Load chapter's REQUIRED READING
- Load arc's REQUIRED READING (if applicable)

**MEMORY Phase:**
- Query memory for epoch ID: `"Epoch 2.2 architecture"`
- Query memory for investigation chain
- Query memory for related work items
- Collect strategies and anti-patterns

**CONTEXT MAP Phase:**
- Output GroundedContext object
- Pass to downstream cycle (plan-authoring, investigation, etc.)

### Interface

```
Input:
  work_id: str
  cycle_type: str  # which cycle is calling

Output:
  GroundedContext:
    epoch: str
    chapter: str
    arc: str | null
    provenance_chain: list[str]
    architectural_refs: list[str]
    memory_concepts: list[int]
    required_reading_loaded: bool
```

---

## Work Items

| ID | Title | Status | Dependencies |
|----|-------|--------|--------------|
| E2-276 | Design ground-cycle skill | **Complete (S179)** | None |
| E2-277 | Implement Portal System | Plan approved (S178) | E2-276 |
| E2-280 | Wire ground-cycle to plan-authoring-cycle | Not created | E2-276, E2-277 |
| E2-281 | Wire ground-cycle to investigation-cycle | Not created | E2-280 |
| E2-282 | Wire ground-cycle to implementation-cycle | Not created | E2-280 |

> **Session 178 Note:** E2-278/E2-279 removed. PROVENANCE/ARCHITECTURE/MEMORY/CONTEXT MAP phases are internal to ground-cycle SKILL.md (E2-276), not separate work items. E2-277 renamed to "Portal System" - portals enable provenance traversal.

---

## Arc Completion Criteria

- [ ] ground-cycle skill exists and is tested
- [ ] All 4 phases implemented
- [ ] plan-authoring-cycle calls ground-cycle
- [ ] investigation-cycle calls ground-cycle
- [ ] implementation-cycle calls ground-cycle
- [ ] E2-271 can be re-planned correctly with grounded context

---

## References

- @session:177:ground-cycle-discovery (memory concepts 80858-80874)
- @session:177:hierarchy-design-final (memory concepts 80910-80917)
- @docs/work/archive/INV-052/README.md
