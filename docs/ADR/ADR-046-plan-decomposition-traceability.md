---
template: architecture_decision_record
status: accepted
date: 2026-02-15
adr_id: ADR-046
title: "Plan Decomposition Traceability"
author: Hephaestus
session: 379
lifecycle_phase: decide
decision: accepted
spawned_by: WORK-150
traces_to:
- REQ-ASSET-003
- REQ-ASSET-004
- REQ-ASSET-005
memory_refs: [85325, 85326, 85331, 85332, 85340]
version: "1.1"
generated: 2026-02-15
last_updated: 2026-02-15
---
# ADR-046: Plan Decomposition Traceability

@docs/work/active/WORK-097/WORK.md
@docs/work/active/WORK-150/WORK.md

> **Status:** Accepted
> **Date:** 2026-02-15
> **Decision:** Accepted

---

## Decision Criteria (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Document alternatives | MUST | 3 options documented in Considered Options |
| Explain WHY | MUST | Rationale in Decision section |
| Link to memory | SHOULD | Memory 85325, 85326, 85331, 85332, 85340 |
| Get operator approval | MUST | Update decision from "pending" to "accepted" |

---

## Context

When a plan's scope exceeds implementation thresholds, it must be decomposed into smaller work items. Currently, this decomposition loses traceability: the relationship between parent plan steps and child work items is captured only in prose, and the reason for spawning (decomposition vs investigation vs observation) is invisible in frontmatter.

**Evidence: E2-292 Case Study (Session 195)**

E2-292 "Wire set-cycle Recipe Calls into Cycle Skills" was decomposed when scope exceeded the 3-file threshold (7 files identified in plan). The split was:

| Parent Plan Steps | Child Work Item | Scope |
|---|---|---|
| Steps 1-2 (set-queue recipe, schema extension) | E2-293 | Foundation infrastructure |
| Steps 3-4 (wire impl-cycle, investigation-cycle) | E2-294 | Core cycle wiring |
| Steps 5-7 (wire survey, close, work-creation) | E2-295 | Remaining cycle wiring |
| Steps 8-9 (integration test, consumer verification) | E2-292 (parent, post-children) | Verification |

**Outcome:** All three children completed successfully (E2-293, E2-294, E2-295 all status: complete), validating that decomposition reduced scope to manageable units. Parent E2-292 completed post-children verification.

**What was missing:**
- No `spawn_type` field to distinguish decomposition from investigation spawn
- No plan section mapping steps to children
- Decomposition history only in prose (E2-292 History section)
- Threshold was informal ("Scope exceeded 3-file threshold")

This ADR formalizes three design decisions from the WORK-097 investigation to close these gaps.

---

## Decision Drivers

- **Traceability:** REQ-ASSET-003 requires assets to be pipeable to next lifecycle OR stored; decomposition is a form of asset piping
- **Provenance:** REQ-ASSET-005 requires assets have provenance (source lifecycle, timestamp, author); spawn_type provides classification provenance
- **Simplicity:** Reuse existing `spawned_by` field rather than introducing new fields (Memory 85325: "Decomposition is a specialization of spawning, not a separate concept")
- **Computable governance:** Thresholds should be checked automatically at plan-validation time, not informally during DO phase

---

## Considered Options

### Option A: Separate decomposed_into/from Fields

**Description:** Add new `decomposed_into` field to parent work items and `decomposed_from` field to child work items, creating a parallel relationship graph to `spawned_by`/`spawned_children`.

**Pros:**
- Explicit decomposition relationship separate from other spawn types
- Could support different traversal logic for decomposition vs spawning

**Cons:**
- Adds 2 new fields when `spawned_by` already carries the parent-child link
- Requires new SpawnTree traversal logic for the decomposition graph
- Increases template complexity with minimal information gain
- Rejected by WORK-097 investigation (Memory 85332: "Original acceptance criteria proposed decomposed_into/from fields — investigation proved spawn_type simpler")

### Option B: spawn_type + decomposition_map (Proposed)

**Description:** Extend the existing `spawned_by` field with a `spawn_type` classification tag on child work items, and add a `decomposition_map` section to parent plans when decomposition occurs. Check decomposition triggers at plan-validation time.

**Pros:**
- Minimal new infrastructure — reuses existing `spawned_by` and SpawnTree
- Single field (`spawn_type`) classifies WHY a work item was spawned
- `decomposition_map` in plan provides step-to-child traceability
- Computable triggers move decomposition check to plan-validation (before DO phase)

**Cons:**
- `spawn_type` is on the child, not the parent — parent doesn't directly declare decomposition (mitigated by `decomposed: true` flag in plan frontmatter)
- Trigger thresholds are SHOULD-level, not MUST — agent can override with rationale

### Option C: No Formal Pattern

**Description:** Continue with ad-hoc decomposition, relying on prose in History sections and informal conventions.

**Pros:**
- No new fields or infrastructure
- Maximum flexibility

**Cons:**
- Loses traceability (E2-292 evidence: decomposition history only in prose)
- Future sessions cannot programmatically identify decomposed work items
- No computable triggers — decomposition depends on agent judgment at DO phase (too late)

---

## Decision

**Option B: spawn_type + decomposition_map.** Three decisions formalized:

### Decision 1: spawn_type Field

Decomposition is spawning with a type tag, not a separate concept. Add `spawn_type` to child work item frontmatter alongside existing `spawned_by`:

```yaml
spawned_by: WORK-XXX
spawn_type: decomposition  # NEW field
```

**Enum values:**

| Value | When Used | Example |
|---|---|---|
| `decomposition` | Plan scope exceeded threshold, split into sub-items | E2-292 -> E2-293/294/295 |
| `investigation` | Investigation findings spawn implementation work | INV-065 -> E2-292 |
| `observation` | Observation triage spawns new work | obs-222-001 -> WORK-020 |
| `follow-up` | Work completion reveals follow-up needs | WORK-067 -> WORK-147 |

**Rationale:** `spawned_by` already carries the parent link. `spawn_type` classifies WHY. SpawnTree already traverses `spawned_by`. No new traversal infrastructure needed. (Memory 85325, 85340)

**Enforcement:** work-creation-cycle MUST validate: if `spawned_by` is set, `spawn_type` MUST also be set. This prevents spawn relationships without classification.

**Extension policy:** New `spawn_type` values require an ADR amendment or new ADR. Agents MUST NOT invent values outside the defined enum.

### Decision 2: decomposition_map Section

When a plan is decomposed, add a `decomposition_map` section and a frontmatter flag:

```yaml
# In plan frontmatter
decomposed: true
```

```markdown
## Decomposition Map

> Added when plan scope exceeds threshold and is split into sub-items.

| Steps | Child ID | Title | Rationale |
|-------|----------|-------|-----------|
| 1-2 | E2-293 | Schema and recipe foundation | Independent infrastructure |
| 3-4 | E2-294 | Core cycle wiring | Depends on E2-293 schema |
| 5-7 | E2-295 | Remaining cycle wiring | Parallel to E2-294 |

**Trigger:** Plan exceeded [threshold] at [phase].
**Parent status:** Decomposed — completes after all children done.
```

**Key design decisions:**
- `decomposed: true` flag in plan frontmatter (machine-parseable)
- Decomposition map is a markdown table (human-readable, grep-able)
- Parent plan stays intact — children reference it, don't duplicate it
- Parent work item completes after verification (post-children steps)

**Consistency enforcement:** When decomposition_map is present, plan-validation-cycle SHOULD verify that child IDs in the map match `spawned_children` in the parent WORK.md.

### Decision 3: Computable Trigger Thresholds

Decomposition triggers are checked at plan-validation-cycle (end of PLAN phase), not at DO phase where it's too late to decompose cleanly.

| Trigger | Threshold | Level | When Checked |
|---|---|---|---|
| Files to modify | > 5 | SHOULD decompose | plan-validation-cycle |
| Implementation steps | > 5 | SHOULD decompose | plan-validation-cycle |
| Independent modules | > 2 | MAY decompose | plan-validation-cycle |
| Estimated effort | > 2 hours | MAY decompose | plan-validation-cycle |

**Implementation approach (deferred to E2.7 Composability):**
1. Add `decomposition_thresholds` section to `haios.yaml`
2. plan-validation-cycle checks plan metrics against thresholds
3. If SHOULD-level trigger fires: warn and suggest decomposition
4. Agent can accept or override with rationale

**haios.yaml schema example:**
```yaml
decomposition_thresholds:
  files_to_modify:
    threshold: 5
    level: SHOULD
  implementation_steps:
    threshold: 5
    level: SHOULD
  independent_modules:
    threshold: 2
    level: MAY
  estimated_effort_hours:
    threshold: 2
    level: MAY
```

**Key change:** Move decomposition check from preflight-checker (DO phase, too late) to plan-validation-cycle (end of PLAN phase, before DO approved). This gives the agent a chance to decompose before starting implementation.

---

## Consequences

**Positive:**
- Spawn relationships are classifiable: `spawn_type` distinguishes decomposition from investigation, observation, and follow-up spawns
- Plan decomposition is traceable: `decomposition_map` links parent plan steps to child work items
- Decomposition is timely: computable triggers fire at plan-validation, not DO phase
- No new traversal infrastructure: SpawnTree continues using `spawned_by`
- Existing work items are unaffected: `spawn_type` is optional (defaults to unset for pre-existing items)

**Negative:**
- Template update required: work item template must add `spawn_type` field (E2.7 implementation)
- Plan template update required: implementation plan template must support `decomposition_map` section (E2.7 implementation)
- Trigger thresholds are advisory (SHOULD/MAY), not blocking — agent can still skip decomposition
- Backward compatibility: pre-E2.7 work items will not have `spawn_type`; queries filtering by spawn_type must treat null as "unclassified" (not error). No migration of existing items required — spawn_type is additive

**Neutral:**
- Dependency field status unchanged: `spawned_by`, `spawned_children`, `blocked_by`, `blocks`, `enables` all retain current semantics
- `spawn_type` only classifies the child's relationship to parent — parent doesn't explicitly declare "I was decomposed" (mitigated by `decomposed: true` in plan frontmatter)

---

## Implementation

Implementation is deferred to E2.7 (Composability epoch):

- [ ] Add `spawn_type` field to work item template (`.claude/templates/work_item.md`)
- [ ] Add `decomposition_map` section support to plan template
- [ ] Add `decomposition_thresholds` to `haios.yaml`
- [ ] Update plan-validation-cycle to check thresholds
- [ ] Update preflight-checker to reference plan-validation thresholds (not hardcoded >3 file check)
- [ ] Add spawn_type validation to work-creation-cycle (spawned_by set -> spawn_type MUST be set)
- [ ] Add decomposition_map consistency check to plan-validation-cycle (child IDs match spawned_children)

---

## References

- @docs/work/active/WORK-097/WORK.md (source investigation)
- @docs/work/active/WORK-150/WORK.md (ADR work item)
- @docs/work/active/E2-292/WORK.md (case study — parent that was decomposed)
- @docs/work/active/E2-293/WORK.md (child 1 — schema)
- @docs/work/active/E2-294/WORK.md (child 2 — core wiring)
- @docs/work/active/E2-295/WORK.md (child 3 — remaining wiring)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (ADR pattern)
- Memory: 85325 (decomposition is specialization of spawning)
- Memory: 85326 (spawn_type field design)
- Memory: 85331 (SHOULD decompose directive)
- Memory: 85332 (spawn_type simpler than decomposed_into/from)
- Memory: 85340 (reuse existing fields principle)

---
