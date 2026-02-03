# generated: 2026-01-30
# System Auto: last updated on: 2026-02-03T00:32:06
# Epoch 2.4: The Activity Layer

## L4 Object Definition

**Epoch ID:** E2.4
**Name:** The Activity Layer
**Status:** Design-Complete
**Started:** 2026-01-30 (Session 265)
**Closed:** 2026-02-03 (Session 295)
**Prior:** E2.3 (The Pipeline)
**Next:** E2.5 (Independent Lifecycles)

---

## Purpose

Implement the five-layer hierarchy and governed activities paradigm.

**The Mission:**
```
Principles → Ways of Working → Ceremonies → Activities → Assets
```

**The Paradigm Shift:**
- From: Pipeline stages as modules
- To: Governed activities as Primitive × State × Governance Rules

---

## What We Learned (E2.3)

### What Works

| Component | Evidence | Reuse |
|-----------|----------|-------|
| Pipeline stages (INGEST, PLAN) | CH-001-003, CH-006 complete | Foundation valid |
| Universal work item structure | WORK-XXX format adopted | Keep, add `mode` field |
| Configuration arc | Loaders, haios.yaml | Keep |
| Critique agent pattern | Surfaces assumptions pre-DO | Elevate to hard gate |

### What Doesn't Work

| Problem | Evidence | Fix |
|---------|----------|-----|
| Monolithic templates | 372-line investigation.md, Template Tax | Fracture to phase templates |
| Investigation HYPOTHESIZE-FIRST | WORK-036: premature hypothesis constrains depth | Invert to EXPLORE-FIRST |
| DO phase leaky | Design decisions during implementation | Black-box with governed activities |
| Critique optional | Agent skips when rushing | Make hard gate |

---

## Core Decisions (Session 265)

### Decision 1: Five-Layer Hierarchy

```
PRINCIPLES       (WHY)
WAYS OF WORKING  (HOW - functions/transformations)
CEREMONIES       (WHEN - side-effect boundaries)
ACTIVITIES       (WHAT - governed primitives)
ASSETS           (OUTPUT - immutable artifacts)
```

### Decision 2: Work Classification (Two-Axis)

| Axis | Values |
|------|--------|
| **Mode** | volumous, tight |
| **Type** | investigate, design, implement, validate, triage |

Type as function signature:
- investigate: Question → Findings
- design: Requirements → Specification
- implement: Specification → Artifact
- validate: Artifact × Spec → Verdict
- triage: [Items] → [PrioritizedItems]

### Decision 3: Governed Activities

```
Governed Activity = Primitive × State × Governance Rules
```

Same primitive, different governance per state.

### Decision 4: Critique as Hard Gate

- DESIGN → PLAN: Critique verdict must = PROCEED
- PLAN → DO: Critique verdict must = PROCEED
- Revise until no critique

### Decision 5: Universal Flow

```
EXPLORE → DESIGN → PLAN → DO → CHECK → DONE
```

Investigation variant:
```
EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE
```

### Decision 6: Fractured Templates

One template per phase with:
- Input contract
- Output contract
- Governed activities
- ~30-50 lines each

---

## Arcs

| Arc | Theme | Status |
|-----|-------|--------|
| **Activities** | Define governed activities per state | Planned |
| **Templates** | Fracture templates to phase contracts | Planned |
| **Flow** | Implement universal flow with gates | Planned |
| **Configuration** | (Carried from E2.3) Loader system | Active |
| **WorkUniversal** | (Carried from E2.3) Add mode + queue_position fields | Active |

---

## Session 276 Additions

### Decision 7: Four-Dimensional Work Item State (WORK-065)

Work items have four orthogonal state dimensions:

| Dimension | Field | Values | Purpose |
|-----------|-------|--------|---------|
| Lifecycle | `status` | active/blocked/complete/archived | ADR-041 authoritative |
| Queue | `queue_position` | backlog/todo/in_progress/done | **NEW** - selection pipeline |
| Cycle | `cycle_phase` | discovery/plan/implement/close | RENAME current_node |
| Activity | `activity_state` | EXPLORE/DESIGN/.../DONE | E2.4 derived |

**Key Finding:** `current_node` conflated queue and cycle dimensions. 94% stuck at backlog.

**Implementation:** WORK-066 (queue_position field + cycle wiring)

---

## Session 279 Additions

### Decision 8: Multi-Level Governance (WORK-055)

assigned_to:
  - arc: flow
    chapters: [CH-009, CH-010, CH-011]

Governance must exist at branch nodes (chapters, arcs, epochs), not just leaf nodes (work items).

**Gap Identified:**
1. Epoch decisions have no traceability to chapters (no `assigned_to` field)
2. REQ-TRACE-005 traces hierarchy but not decision coverage
3. DoD exists only at work item level (no Chapter/Arc/Epoch DoD)

**Patterns:**
1. **Decision Traceability Schema:** Add `assigned_to` field to decisions, `implements_decisions` to chapters
2. **Multi-Level DoD Cascade:** Work → Chapter → Arc → Epoch DoD verification
3. **Pre-Decomposition Review Gate:** Arc-level critique before chapter work begins

**Implementation:** WORK-069, WORK-070, WORK-071

**Memory Refs:** 83018-83029

---

## Exit Criteria

- [ ] Governed activities matrix implemented
- [ ] Phase templates fractured with contracts
- [ ] Universal flow with critique hard gates
- [x] Investigation cycle uses EXPLORE-FIRST (Session 276 - WORK-065 demonstrated)
- [ ] DO phase enforces black-box constraints
- [ ] Queue position field implemented (WORK-066)

---

## Session 280: Full System Audit (WORK-072)

**Audit File:** `.claude/haios/epochs/E2_4/SYSTEM-AUDIT.md`

Key findings:
- 78% ceremonies implemented (26 total: 12 cycle skills, 2 bridges, 4 utilities, 8 agents)
- 71% work items orphaned (96/135 lack chapter assignment)
- 95% items stuck at backlog node (confirms WORK-065 finding)
- ActivityMatrix: 76 rules across 21 primitives
- Memory: 82,860 concepts, 96.8% embedding coverage
- 14 failing tests (documentation drift)

---

## Session 292: Breath Model Discovery (S27)

**Architecture File:** `.claude/haios/epochs/E2_4/architecture/S27-breath-model.md`

Key insight: Work phases follow inhale/exhale rhythm in pairs:

```
EXPLORE    [inhale] → INVESTIGATE [exhale] → [pause: epistemic review]
EPISTEMY   [inhale] → DESIGN      [exhale] → [pause: critique]
PLAN       [inhale] → IMPLEMENT   [exhale] → [pause: validate] → DONE
```

**Reframes Decision 5 (Universal Flow):**
- Pauses between breaths are ceremonies (not just gates)
- Pauses are safe return points (no pressure forward)
- Each phase has input/output data contracts validated at pause

**Spawned:**
- WORK-081: Cycle-as-Subagent (needs DESIGN phase per S27)
- WORK-082: Epistemic Review Ceremony investigation

---

## Memory Refs

Session 265 L4 decisions: 82688-82744
Session 276 work item state model: 82952-82954, 82963-82973
Session 279 multi-level governance: 83018-83029
Session 280 system audit: 83050-83058
Session 292 breath model: 83240-83249

---

## Closure Summary (Session 295)

**Status:** Design-Complete (not Implementation-Complete)

E2.4 was a **design epoch**. It produced architecture and requirements, not running code.

### What E2.4 Achieved

| Deliverable | Evidence |
|-------------|----------|
| Five-layer hierarchy | Documented in EPOCH.md, referenced in L4 |
| Governed activities paradigm | ActivityMatrix (76 rules, 21 primitives) |
| Four-dimensional work state model | WORK-065 finding, REQ-WORK-001 |
| Breath Model (S27) | architecture/S27-breath-model.md |
| Lifecycle independence principle | Session 294, REQ-LIFECYCLE-001 to 004 |
| Queue orthogonality | Session 294, REQ-QUEUE-001 to 004 |
| 20 ceremony definitions | Session 294, REQ-CEREMONY-001 to 003 |
| Asset typing (Unix pipe) | Session 294, REQ-ASSET-001 to 005 |
| Feedback loops | Session 294, REQ-FEEDBACK-001 to 005 |

### What E2.4 Did NOT Implement

| Design | Carried To |
|--------|------------|
| CycleRunner lifecycle mode | E2.5 lifecycles arc |
| Queue ceremonies | E2.5 queue arc |
| Review ceremonies | E2.5 feedback arc |
| Asset versioning | E2.5 assets arc |
| Fractured templates | E2.5 (TBD) |

### Exit Criteria Status

- [ ] Governed activities matrix implemented → **Designed, not implemented**
- [ ] Phase templates fractured with contracts → **Designed, not implemented**
- [ ] Universal flow with critique hard gates → **Superseded by lifecycle independence**
- [x] Investigation cycle uses EXPLORE-FIRST → **Demonstrated Session 276**
- [ ] DO phase enforces black-box constraints → **Designed, not implemented**
- [ ] Queue position field implemented → **Designed (WORK-066), not implemented**

**Verdict:** E2.4 exit criteria were for implementation. E2.4 pivoted to design-only after discovering lifecycle independence principle (Session 294). Implementation deferred to E2.5.

---

## References

- @.claude/haios/epochs/E2_3/EPOCH.md (prior epoch)
- @.claude/haios/epochs/E2_4/architecture/S27-breath-model.md (breath model)
- @.claude/haios/manifesto/L4-implementation.md (to update)
- @docs/work/active/WORK-036/ (Template Tax investigation)
- @docs/work/active/WORK-037/ (EXPLORE-FIRST design)
