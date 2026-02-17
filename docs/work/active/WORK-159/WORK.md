---
template: work_item
id: WORK-159
title: Recipe Rationalization
type: feature
status: complete
owner: Hephaestus
created: 2026-02-17
spawned_by: null
spawned_children: []
chapter: CH-048
arc: composability
closed: '2026-02-17'
priority: high
effort: medium
traces_to:
- REQ-CONFIG-004
- REQ-DISCOVER-002
- REQ-DISCOVER-003
requirement_refs: []
source_files:
- justfile
- .claude/skills
- .claude/commands
acceptance_criteria:
- 5 stub/deprecated skills removed or fixed (4 stubs + 1 deprecated)
- 18 unwrapped recipes documented with tier assignment
- Justfile recipes grouped by category with section headers
- docs/README.md updated with accurate entry point count
- No regressions in existing test suite
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-17 19:58:38
  exited: '2026-02-17T20:05:42.044966'
artifacts: []
cycle_docs: {}
memory_refs:
- 85302
- 85303
- 85307
extensions:
  epoch: E2.7
version: '2.0'
generated: 2026-02-17
last_updated: '2026-02-17T20:05:42.049090'
queue_history:
- position: ready
  entered: '2026-02-17T19:59:37.919227'
  exited: '2026-02-17T19:59:37.953314'
- position: working
  entered: '2026-02-17T19:59:37.953314'
  exited: '2026-02-17T20:05:42.044966'
- position: done
  entered: '2026-02-17T20:05:42.044966'
  exited: null
---
# WORK-159: Recipe Rationalization

---

## Context

**Problem:** HAIOS has ~100 justfile recipes with no grouping, documentation, or category headers. ADR-045 (Three-Tier Entry Point Architecture) established the tier model but 18 recipes remain unwrapped (no Tier 2 skill wrappers), 5 stub/deprecated skills pollute the system prompt, and the justfile has no section organization.

**Root cause:** Recipes were added organically to solve specific problems. ADR-045 designed the rationalization but implementation was deferred to E2.7 CH-048.

**Evidence:** WORK-020 investigation (S368) identified 151 entry points, 8 friction points. ADR-045 accepted (S378). Memory: 85302 (agents never run just X directly), 85303 (decision space drops to ~40).

**Scope:**
1. Remove 5 stub/deprecated skills (4 stubs + 1 deprecated observation-capture-cycle)
2. Document all 18 unwrapped recipes with their tier assignment
3. Add category section headers to justfile for organization
4. Update docs/README.md with accurate entry point count

---

## Deliverables

- [ ] 5 stub/deprecated skills cleaned up
- [ ] 18 unwrapped recipes documented (tier assignment in justfile comments)
- [ ] Justfile organized with category section headers
- [ ] docs/README.md entry point count updated
- [ ] No regressions in existing test suite

---

## History

### 2026-02-17 - Created (Session 393)
- Spawned from CH-048 RecipeRationalization (composability arc, E2.7)
- REQ-CONFIG-004, REQ-DISCOVER-002, REQ-DISCOVER-003 traceability
- ADR-045 provides tier model, this implements it

---

## References

- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md
- @docs/work/active/WORK-020/WORK.md (investigation source)
- @.claude/haios/epochs/E2_7/arcs/composability/ARC.md
- @.claude/haios/manifesto/L4/functional_requirements.md
