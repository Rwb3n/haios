---
template: work_item
id: WORK-097
title: Plan Decomposition Traceability Pattern
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: WORK-095
chapter: CH-038
arc: traceability
closed: '2026-02-14'
priority: medium
effort: medium
traces_to:
- REQ-ASSET-003
- REQ-ASSET-004
requirement_refs: []
source_files:
- docs/work/active/
acceptance_criteria:
- E2-292 decomposition documented as case study
- WORK.md frontmatter field designed (spawn_type replaces decomposed_into/from)
- plan.md decomposition_map section designed for step-to-child mapping
- Decomposition trigger thresholds defined (computable predicates)
- Spawned ADR work item for formal documentation
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 20:39:18
  exited: '2026-02-14T14:51:52.180033'
artifacts: []
cycle_docs: {}
memory_refs:
- 81399
- 81400
- 81401
- 85031
- 85032
- 85325
- 85331
extensions:
  epoch: E2.6
  lifecycle_type: investigation
  supersedes: INV-066
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-14T14:51:52.183548'
queue_history:
- position: ready
  entered: '2026-02-14T14:42:18.324999'
  exited: '2026-02-14T14:42:18.350224'
- position: working
  entered: '2026-02-14T14:42:18.350224'
  exited: '2026-02-14T14:51:52.180033'
- position: done
  entered: '2026-02-14T14:51:52.180033'
  exited: null
queue_position: done
cycle_phase: done
---
# WORK-097: Plan Decomposition Traceability Pattern

---

## Context

**Problem:** When a plan is decomposed into smaller work items (due to scope exceeding threshold), the relationship between parent and children is not clearly traceable.

**Evidence:** In Session 195, E2-292 was split into E2-293/294/295, but:
1. No standard pattern exists for marking the parent as "decomposed"
2. Child items lack clear link back to parent plan
3. WORK.md files and plans lack consistent fields for this relationship
4. Future sessions may not understand the decomposition history

**Goal:** Investigate and design a pattern for traceable plan decomposition.

**Supersedes:** INV-066 (archived - same concept, fresh E2.5 structure)

---

## Deliverables

- [x] Document current E2-292 decomposition as case study
- [x] Design WORK.md frontmatter fields for decomposition (spawn_type field)
- [x] Design plan.md decomposition_map section for step-to-child mapping
- [x] Define when decomposition is triggered (computable predicates)
- [ ] Create ADR (spawned as WORK-150)

---

## Hypotheses

| ID | Hypothesis | Verdict | Confidence |
|----|-----------|---------|------------|
| H1 | Decomposition = spawning + type tag | **Confirmed** | 0.85 |
| H2 | Plan is the decomposition anchor | **Confirmed** | 0.80 |
| H3 | Computable trigger predicates | **Partially Confirmed** | 0.65 |
| H4 | `enables` replaces `blocks` | **Partially Confirmed** | 0.55 |

---

## Findings

### 1. Case Study: E2-292 Decomposition (Session 195)

E2-292 "Wire set-cycle Recipe Calls into Cycle Skills" was decomposed when scope exceeded the 3-file threshold (7 files identified in plan).

**How it was split:**
| Parent Plan Steps | Child Work Item | Scope |
|---|---|---|
| Steps 1-2 (set-queue recipe, schema extension) | E2-293 | Foundation infrastructure |
| Steps 3-4 (wire impl-cycle, investigation-cycle) | E2-294 | Core cycle wiring |
| Steps 5-7 (wire survey, close, work-creation) | E2-295 | Remaining cycle wiring |
| Steps 8-9 (integration test, consumer verification) | E2-292 (parent, post-children) | Verification |

**Relationship tracking used:**
- Parent: `enables: [E2-293, E2-294, E2-295]`
- Children: `spawned_by: E2-292`
- Sequencing: E2-293 `blocks: [E2-294, E2-295]`
- Plan reference: Children reference `@docs/work/active/E2-292/plans/PLAN.md`

**What was missing:**
- No `spawn_type` to distinguish decomposition from investigation spawn
- No plan section mapping steps to children
- Decomposition history only in prose (E2-292 History section)
- Threshold was informal ("Scope exceeded 3-file threshold")

### 2. Design: WORK.md Frontmatter — `spawn_type` Field

**Decision: Decomposition IS spawning with a type tag.** No new `decomposed_into`/`decomposed_from` fields needed.

**New field for child work items:**
```yaml
spawned_by: WORK-XXX
spawn_type: decomposition  # NEW: decomposition | investigation | observation | follow-up
```

**spawn_type values:**
| Value | When Used | Example |
|---|---|---|
| `decomposition` | Plan scope exceeded threshold, split into sub-items | E2-292 → E2-293/294/295 |
| `investigation` | Investigation findings spawn implementation work | INV-065 → E2-292 |
| `observation` | Observation triage spawns new work | obs-222-001 → WORK-020 |
| `follow-up` | Work completion reveals follow-up needs | WORK-067 → WORK-147 |

**Rationale:** `spawned_by` already carries the parent link. `spawn_type` classifies WHY. SpawnTree already traverses `spawned_by`. No new traversal infrastructure needed. Memory 85031 confirms this direction: "Reused spawned_by field for parent work item IDs."

### 3. Design: Plan Template — `decomposition_map` Section

**New section added to plan when decomposition occurs:**
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
- Parent work item completes after verification (Steps 8-9 in E2-292 case)

### 4. Design: Decomposition Trigger Thresholds

**Current state:** >3 file threshold hardcoded in preflight-checker agent prose (line 79-81). Triggers at DO phase (after plan written).

**Proposed computable predicates (for plan-validation-cycle):**

| Trigger | Threshold | Level | When Checked |
|---|---|---|---|
| Files to modify | > 5 | SHOULD decompose | plan-validation-cycle |
| Implementation steps | > 5 | SHOULD decompose | plan-validation-cycle |
| Independent modules | > 2 | MAY decompose | plan-validation-cycle |
| Estimated effort | > 2 hours | MAY decompose | plan-validation-cycle |

**Key change:** Move decomposition check from preflight-checker (DO phase, too late) to plan-validation-cycle (end of PLAN phase, before DO approved). This gives the agent a chance to decompose before starting implementation.

**Implementation approach (deferred to E2.7):**
1. Add `decomposition_thresholds` section to `haios.yaml`
2. plan-validation-cycle checks plan metrics against thresholds
3. If SHOULD-level trigger fires: warn and suggest decomposition
4. Agent can accept or override with rationale

### 5. Dependency Field Status

| Field | In Template | In WorkState | Used by Engine | Recommendation |
|---|---|---|---|---|
| `spawned_by` | Yes | No | Yes (SpawnTree) | Keep — primary link |
| `spawned_children` | Yes | No | Yes (get_work_lineage) | Keep — denormalized cache |
| `blocked_by` | Yes | Yes | Yes (get_ready) | Keep — authoritative dependency |
| `blocks` | Yes | No | No | Keep as documentation, don't add to WorkState |
| `enables` | Yes | No | No | Keep as documentation, don't add to WorkState |
| `spawn_type` | **No (NEW)** | No | No (future) | **Add to template** |

---

## Spawned Work Items

| ID | Title | Type | Arc | Deferred To |
|----|-------|------|-----|-------------|
| WORK-150 | Plan Decomposition Traceability ADR | design | traceability | E2.6 |

---

## History

### 2026-02-14 - Investigation Complete (Session 368)
- E2-292 case study documented with step-to-child mapping
- spawn_type field designed (replaces proposed decomposed_into/from)
- Plan decomposition_map section designed
- Trigger thresholds defined (computable predicates for plan-validation-cycle)
- H1/H2 confirmed, H3/H4 partially confirmed
- WORK-150 spawned for ADR

### 2026-02-03 - Created (Session 299)
- Supersedes INV-066 from E2.5 Legacy Assimilation Triage (WORK-095)
- Mapped to assets arc (REQ-ASSET-003: provenance, REQ-ASSET-004: versioning)

---

## References

- @docs/work/active/E2-292/WORK.md (case study — parent that was decomposed)
- @docs/work/active/E2-293/WORK.md (child 1 — schema)
- @docs/work/active/E2-294/WORK.md (child 2 — core wiring)
- @docs/work/active/E2-295/WORK.md (child 3 — remaining wiring)
- @docs/work/active/E2-292/plans/PLAN.md (plan that was decomposed)
- @.claude/agents/preflight-checker.md (current >3 file threshold)
- Memory: 81399, 81400, 81401 (prior critique)
- Memory: 85031, 85032 (spawned_by reuse decision)
