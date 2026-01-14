# generated: 2026-01-06
# System Auto: last updated on: 2026-01-06T21:36:05
# Section 19: Skill and Work Item Unification

Generated: 2026-01-06 (Session 179)
Purpose: Consolidate emerging architectural decisions about skill isolation and work item taxonomy
Status: DRAFT (decisions accumulating from operator sessions)

---

## 19.1 Observation Capture Isolation

**Source:** Session 179, E2-276 closure review

### Problem

Observation capture is buried as OBSERVE phase inside close-work-cycle (between VALIDATE and ARCHIVE). This causes:
1. Agents treat it as checkbox step, not genuine reflection
2. Cognitive context is wrong - agent is in "completion mode"
3. Mechanical gate passes even without actual reflection

### Evidence

Session 179: Agent checked all "None observed" boxes without reflecting. Only caught real observations (dual GroundedContext schema gap, runtime consumer ambiguity) when operator challenged.

### Decision

**Extract observation capture into standalone `observation-capture-cycle` skill.**

Current flow:
```
/close {id}
  └── close-work-cycle
        ├── VALIDATE (DoD)
        ├── OBSERVE   <-- buried here, rushed
        ├── ARCHIVE
        └── MEMORY
```

Target flow:
```
/close {id}
  ├── observation-capture-cycle  <-- dedicated focus, FIRST
  │     ├── RECALL (what happened?)
  │     ├── CATEGORIZE (unexpected/gap/future)
  │     └── VALIDATE (gate)
  │
  └── close-work-cycle
        ├── VALIDATE (DoD)
        ├── ARCHIVE
        └── MEMORY
```

### Rationale

- Isolated skill = dedicated cognitive context
- Called BEFORE close-work-cycle, not sandwiched inside
- Harder to skip when it's a separate invocation

### Investigation

INV-059: Observation Capture Skill Isolation

---

## 19.2 Work Item Taxonomy Unification

**Source:** Session 179, operator observation

### Problem

Current system conflates ID prefix with work type:
- `INV-*` = investigation
- `E2-*` = implementation
- But both are work items with same lifecycle

This creates friction:
1. `/new-investigation` creates WORK.md AND investigation doc (why two?)
2. `INV-*` items get special DoD checks based on prefix
3. work-creation-cycle routes based on ID prefix, not category
4. ID prefix encodes epoch (`E2-`) but investigations don't (`INV-`) - inconsistent

### Insight

> "All investigation is work, but not all work is investigation."

Investigation is a *type* of work, not a separate entity.

### Current State

```
Work Items
├── INV-* (investigation prefix)
│     └── category: investigation (redundant)
├── E2-* (epoch prefix)
│     └── category: implementation|design|bug|...
└── TD-* (tech debt prefix)
      └── category: ???
```

Routing logic checks ID prefix:
```python
if id.startswith("INV-"):
    # investigation path
else:
    # implementation path
```

### Target State

```
Work Items (all use {epoch}-{seq} pattern)
├── E2-301: category: investigation
├── E2-302: category: implementation
├── E2-303: category: design
├── E2-304: category: bug
└── E2-305: category: tech-debt
```

Routing logic checks category field:
```python
match work_item.category:
    case "investigation": investigation-cycle
    case "implementation": implementation-cycle
    case "design": design-cycle (or implementation-cycle)
    case "bug": bug-cycle (or implementation-cycle)
    case _: default handling
```

### Benefits

1. **Single creation flow:** `/new-work` → populate category → appropriate cycle
2. **Consistent ID scheme:** All work is `{epoch}-{seq}`
3. **Category drives behavior:** Not magic prefix parsing
4. **Cleaner routing:** `category` field is explicit, not inferred

### Migration Considerations

- Existing `INV-*` items continue to work (category already set)
- New investigations use `E2-*` with `category: investigation`
- Routing logic updated to check category first, prefix as fallback
- ID prefix becomes cosmetic (human readability), not semantic

### Open Questions

1. Should existing `INV-*` items be migrated? (probably not worth it)
2. What categories should exist? (investigation, implementation, design, bug, tech-debt, ?)
3. Should category determine which cycle skills are available?

### Investigation

To be created: Work Item Category-Driven Routing

---

## 19.3 Dual GroundedContext Schemas

**Source:** Session 179, E2-276 implementation

### Problem

Two different GroundedContext structures exist:
1. S17.3 ContextLoader.GroundedContext (session-level)
2. ground-cycle GroundedContext (work-level)

Relationship undocumented - could confuse future agents.

### Decision

Both are needed and serve different purposes:

| Context | Scope | When Loaded | Contains |
|---------|-------|-------------|----------|
| ContextLoader.GroundedContext | Session | /coldstart | L0-L4 manifesto, session number, strategies |
| ground-cycle.GroundedContext | Work Item | Before cognitive work | epoch/chapter/arc, provenance chain, memory refs |

### Formalization

Session-level context (ContextLoader):
```yaml
GroundedContext:
  session_number: int
  prior_session: int | null
  l0_north_star: str
  l1_invariants: str
  l2_operational: dict
  l3_session: dict
  strategies: list[Strategy]
  ready_work: list[WorkItem]
```

Work-level context (ground-cycle):
```yaml
GroundedContext:
  epoch: str
  chapter: str | null
  arc: str | null
  provenance_chain: list[str]
  architectural_refs: list[str]
  memory_concepts: list[int]
  required_reading_loaded: bool
```

### Recommendation

Consider renaming to avoid confusion:
- `SessionContext` (ContextLoader output)
- `WorkContext` (ground-cycle output)

Or keep both as GroundedContext with qualifier:
- `GroundedContext.session`
- `GroundedContext.work`

---

## Related

- S17: Modular Architecture (module definitions)
- S2C: Work Item Directory (portal system)
- INV-059: Observation Capture Skill Isolation
- E2-276: Design ground-cycle Skill
- ADR-039: Work Item as File Architecture

---

*This document accumulates architectural decisions as they emerge from operator sessions. Decisions here are DRAFT until formalized into ADRs or implemented.*
