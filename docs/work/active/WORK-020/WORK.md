---
template: work_item
id: WORK-020
title: Discoverability Architecture
type: investigation
status: active
owner: Hephaestus
created: 2026-01-26
spawned_by: obs-222-001
chapter: CH-009
arc: configuration
closed: null
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 19:31:51
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-26
last_updated: '2026-01-28T23:54:36'
---
# WORK-020: Discoverability Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** HAIOS has 125 entry points spread across 4 systems with no unified discovery:
- 77 justfile recipes
- 19 skills
- 20 commands
- 9 agents

**Friction points:**
1. Agent doesn't know when to use `just X` vs `/command` vs `Skill(skill="X")`
2. Some recipes wrap skills, some call cli.py, some are standalone
3. No `just help` or categorized listing
4. Checkpoint scaffolding: tried `just scaffold-checkpoint`, `just new-checkpoint` before finding `just scaffold checkpoint`
5. Skills are in agent's system prompt but recipes require discovery
6. Commands and skills overlap (e.g., `/close` invokes `close-work-cycle` skill)

**Root cause:** Organic growth without unified discovery layer. Each system was added to solve specific problems but the aggregate creates cognitive overhead.

---

## Hypotheses

**H1: Three-tier model can simplify**
```
User-facing: /commands (10-15 total)
Agent-facing: Skills via Skill() (18 total)
Runtime: just recipes (consolidate to ~30 core)
```

**H2: Just recipes should be implementation details**
Agent shouldn't need to know `just scaffold checkpoint` - the `/new-checkpoint` command should handle it.

**H3: Discovery needs a single entry point**
`/haios help` or `just help` that shows categorized capabilities.

---

## Scope

**In Scope:**
- Inventory all entry points
- Identify overlap/redundancy
- Design unified discovery pattern
- Recommend consolidation strategy

**Out of Scope:**
- Implementing all consolidation (spawn follow-up work)
- Removing working infrastructure

---

## Deliverables

- [ ] Complete inventory of all entry points (recipes, skills, commands, agents)
- [ ] Friction map showing overlaps and gaps
- [ ] Proposed three-tier architecture
- [ ] Discovery mechanism design (`/haios help` or equivalent)
- [ ] Spawn implementation work items

---

## Exploration Plan

- [ ] Inventory all 77 just recipes by category
- [ ] Map skill→recipe dependencies
- [ ] Map command→skill→recipe chains
- [ ] Identify redundant paths
- [ ] Design discovery mechanism
- [ ] Draft consolidation proposal

---

## Findings

(To be populated during EXPLORE phase)

---

## History

### 2026-01-28 - Populated (Session 256)
- Filled in context with friction analysis
- Defined hypotheses and scope
- Created exploration plan

### 2026-01-26 - Created (Session 244)
- Initial creation from obs-222-001

---

## References

- @.claude/haios/epochs/E2_3/observations/obs-222-001.md (spawn source)
- Memory: 71797, 81378, 82201, 82302 (recipe architecture)
