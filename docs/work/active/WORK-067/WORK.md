---
template: work_item
id: WORK-067
title: HAIOS Portable Schema Architecture Investigation
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-065
chapter: CH-035
arc: referenceability
closed: '2026-02-14'
priority: high
effort: medium
traces_to:
- REQ-REFERENCE-001
- REQ-REFERENCE-002
acceptance_criteria:
- Schema location strategy defined (where do portable schemas live?)
- Template reference pattern defined (how do templates consume schemas?)
- Project bootstrap pattern defined (how does new project get HAIOS schemas?)
- Core vs project-specific boundary defined
blocked_by: []
blocks:
- WORK-066
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 21:19:30
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82952
- 85286
- 85287
- 85288
- 85289
- 85290
extensions:
  epoch: E2.6
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-14T13:58:30.288467'
queue_history:
- position: ready
  entered: '2026-02-14T13:58:24.327269'
  exited: '2026-02-14T13:58:30.285962'
- position: working
  entered: '2026-02-14T13:58:30.285962'
  exited: null
queue_position: done
cycle_phase: done
---
# WORK-067: HAIOS Portable Schema Architecture Investigation

@docs/work/active/WORK-065/WORK.md
@docs/work/active/WORK-066/WORK.md

---

## Context

**Problem:** HAIOS must be portable to other projects, but schemas are scattered and inconsistent.

**Evidence (WORK-065 finding):**
- `current_node` enum defined in 3 places with 3 different values:
  - TRD-WORK-ITEM-UNIVERSAL: `backlog|planning|in_progress|review|complete`
  - GovernanceLayer: `backlog|discovery|plan|implement|close|complete`
  - L5-execution.md: `backlog|ready|in_progress|blocked|complete`
- Chapter status defined inline in template: `Planned | Approved | In Progress | Complete`
- No central schema registry
- No portability consideration

**Why it matters:**
- New project adopting HAIOS wouldn't know which enums are authoritative
- Schema drift causes bugs (94% of work items stuck at `backlog`)
- Adding new enum values (e.g., `Implemented-Deficient`) requires updating multiple files

**Questions to investigate:**
1. Where should portable schemas live? (haios.yaml? Separate schema file? In-code?)
2. How do templates reference schemas without hardcoding paths?
3. How does a new project bootstrap HAIOS schemas?
4. What's the boundary between "core HAIOS" (portable) and "project-specific"?
5. Should schemas be YAML, JSON Schema, or prose markdown?

---

## Deliverables

- [x] **Schema location strategy** - Central registry at `.claude/haios/schemas/` with core/ and project/ subdirectories
- [x] **Template reference pattern** - `{{schema:domain.key}}` syntax resolved at scaffold time
- [x] **Bootstrap pattern** - Copy schemas/core/, create empty schemas/project/, haios.yaml schemas: path is discovery root
- [x] **Core/project boundary** - Core = TRD-WORK-ITEM-UNIVERSAL enums (~10), Project = HAIOS-specific (~35)
- [x] **Schema format recommendation** - YAML with lightweight convention (values/default/version/source)

---

## Investigation (Session 367)

### Evidence Gathered (EXPLORE Phase)

**Schema Scatter Quantified:** 46 distinct enum/schema definitions across 8 file categories with no centralized registry.

| Category | Count | Locations |
|----------|-------|-----------|
| Python enum-like defs | 19 | governance_layer, cycle_runner, work_engine, observations, ceremony_contracts, routing, memory_bridge, requirement_extractor, pipeline_orchestrator |
| Python dataclass schemas | 3 | work_engine (WorkState, QueueConfig), requirement_extractor |
| Validation schemas | 11 | validate.py template registry |
| YAML config schemas | 5 | haios.yaml, work_queues.yaml, ceremony_registry.yaml, activity_matrix.yaml |
| Template inline enums | 4 | chapter.md, work_item.md, phase template contracts |
| Spec definitions | 1 | TRD-WORK-ITEM-UNIVERSAL.md |

**Key Drift Evidence:**
- `type` field: TRD defines 5 values, actual data has 9 distinct values (implementation, design, bugfix, task, cleanup not in spec)
- `queue_position`: TRD says `backlog|in_progress|done`, implementation says `parked|backlog|ready|working|done`
- `effort`: schema says `small|medium|large|unknown`, data has `trivial`, `low`
- `cycle_phase` vs VALID_TRANSITIONS: two different state machines with different vocabularies

**Sources Examined:**
- WORK-065 (queue position investigation, complete)
- WORK-066 (queue position implementation, complete)
- TRD-WORK-ITEM-UNIVERSAL.md (approved spec)
- governance_layer.py:59-68 (VALID_TRANSITIONS)
- work_engine.py (WorkState, VALID_QUEUE_POSITIONS, QUEUE_TRANSITIONS, TYPE_TO_LIFECYCLE)
- cycle_runner.py (CYCLE_PHASES, PAUSE_PHASES, VALID_LIFECYCLES)
- ceremony_contracts.py, observations.py, routing.py, memory_bridge.py
- requirement_extractor.py (4 Enum classes)
- validate.py (11 template schemas)
- activity_matrix.yaml, work_queues.yaml, ceremony_registry.yaml
- chapter.md template, work_item.md template
- L4 functional_requirements.md (REQ-REFERENCE-001, REQ-REFERENCE-002)
- ConfigLoader (config.py) — proven pattern for centralized path resolution
- scaffold.py — substitute_variables() extensible for schema references
- Memory: 82952, 84110, 84343, 85282

### Hypotheses (HYPOTHESIZE Phase)

| ID | Hypothesis | Evidence | Test Method | Confidence |
|----|-----------|----------|-------------|------------|
| H1 | Central YAML schema registry at `.claude/haios/schemas/` | ConfigLoader pattern proven; 46 enums scattered; REQ-REFERENCE-001 says "discoverable from haios.yaml root" | Can haios.yaml gain schemas: section? Can consumers resolve from registry? | High |
| H2 | Templates reference schemas by key, not inline values | REQ-REFERENCE-002: "zero duplicated schema definitions"; chapter.md hardcodes status enum; scaffold.py substitute_variables() extensible | Does scaffold.py have extension point? Migration cost? | Medium |
| H3 | Core/project boundary: TRD enums = core, HAIOS enums = project | TRD design principle: "Portable"; extensions block exists; 9 types in data vs 5 in schema | Which enums are universal vs HAIOS-specific? | Medium |
| H4 | YAML convention over JSON Schema | All config is YAML; no JSON Schema tooling; 38/46 are simple value lists | Any schemas need cross-field constraints? | High |

### Hypothesis Verdicts (VALIDATE Phase)

| ID | Hypothesis | Verdict | Confidence | Evidence |
|----|-----------|---------|------------|----------|
| H1 | Central YAML schema registry | **CONFIRMED** | High | ConfigLoader extensible (singleton, _load() method); haios.yaml paths section is the model; 46 enums need centralization |
| H2 | Template schema references | **CONFIRMED** (with caveat) | Medium | substitute_variables() trivially extensible for `{{schema:X}}` syntax; migration touches every template with inline enums |
| H3 | Core/project boundary | **CONFIRMED** | Medium | ~10 core enums (status, type, priority, effort, queue_position, cycle_phase, lifecycles, RFC 2119); ~35 HAIOS-specific (activities, ceremonies, observations, pipelines) |
| H4 | YAML over JSON Schema | **CONFIRMED** | High | 38/46 simple value lists; 3 transition maps; 0 cross-field constraints; JSON Schema adds dependency with no benefit |

### Findings (CONCLUDE Phase)

**Answer to Investigation Objective:**

Portable schemas should live in `.claude/haios/schemas/` with a two-tier structure:

```
.claude/haios/schemas/
  core/                     # Portable to any project
    work_item.yaml          # status, type, priority, effort
    queue.yaml              # queue_position, queue_types, transitions
    lifecycle.yaml          # cycle_phase, lifecycles, transitions
    requirements.yaml       # RFC 2119 strengths
  project/                  # HAIOS-specific
    activity.yaml           # E2.4 activity states, phase_to_state
    ceremony.yaml           # categories, contract types, guarantees
    observation.yaml        # categories, actions, priorities
    pipeline.yaml           # pipeline states
    validation.yaml         # template-specific allowed statuses
```

**Schema File Convention (YAML):**

```yaml
# Example: core/work_item.yaml
version: "2.0"
source: TRD-WORK-ITEM-UNIVERSAL

enums:
  status:
    values: [active, blocked, complete, archived]
    default: active

  type:
    values: [feature, investigation, bug, chore, spike]
    default: feature

  priority:
    values: [critical, high, medium, low]
    default: medium

  effort:
    values: [small, medium, large, unknown]
    default: medium

transitions:
  cycle_phase:
    backlog: [plan]
    plan: [backlog, implement]
    implement: [plan, check]
    check: [implement, done]
    done: []
```

**Template Reference Pattern:**

Templates use `{{schema:core.work_item.type}}` which scaffold.py resolves to `feature|investigation|bug|chore|spike` at scaffold time.

**Bootstrap Pattern:**

1. New project copies `schemas/core/` directory
2. Creates empty `schemas/project/` directory
3. Adds `schemas: ".claude/haios/schemas"` to `haios.yaml` paths section
4. ConfigLoader discovers schemas from that root

**Core/Project Boundary:**

| Layer | Content | Portable? |
|-------|---------|-----------|
| `schemas/core/` | TRD-defined enums, queue positions, lifecycle phases, RFC 2119 | Yes |
| `schemas/project/` | Activity states, ceremony types, observation categories, pipeline states | No — HAIOS-specific |
| `extensions:` block | Per-item custom fields | Project decision |

---

## Spawned Work

| ID | Title | spawned_by |
|----|-------|------------|
| WORK-147 | Implement Schema Registry and ConfigLoader Extension | WORK-067 |

**Spawn rationale:** Investigation satisfies REQ-REFERENCE-001 (strategy defined). Implementation needed for REQ-REFERENCE-002 (templates consume schemas via reference). Serves E2.6 exit criteria for referenceability.

**Deferred to E2.7+:**
- Migrating all 46 Python enum definitions to YAML-driven (composability concern)
- Data cleanup of work items with out-of-schema field values (maintenance)

---

## History

### 2026-02-14 - Investigation Complete (Session 367)
- EXPLORE: Quantified 46 enums across 8 file categories
- HYPOTHESIZE: 4 hypotheses formed from evidence
- VALIDATE: All 4 confirmed (2 High, 2 Medium confidence)
- CONCLUDE: Schema location strategy, template reference pattern, bootstrap pattern, core/project boundary, format recommendation all defined
- Spawning implementation work item

### 2026-02-01 - Created (Session 276)
- Spawned from discussion during E2.4 update
- WORK-065 revealed schema scatter problem
- Operator identified portability requirement
- Blocks WORK-066 (need schema decision before implementing queue_position)

---

## References

- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (current work item schema)
- @.claude/templates/chapter.md (inline status enum)
- @.claude/haios/modules/governance_layer.py:59-68 (VALID_TRANSITIONS)
- @.claude/haios/config/haios.yaml (current config approach)
- @.claude/haios/lib/config.py (ConfigLoader — pattern to follow)
- @.claude/haios/lib/scaffold.py (substitute_variables — extension point)
- @.claude/haios/manifesto/L4/functional_requirements.md:642-648 (REQ-REFERENCE-001/002)
