---
template: work_item
id: INV-070
title: Legacy Scaffold Recipe Audit
type: investigation
status: active
owner: Hephaestus
created: 2026-01-27
spawned_by: WORK-027
chapter: CH-004
arc: migration
closed: null
priority: high
effort: medium
traces_to:
- REQ-TRACE-005
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-27 21:49:18
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T21:50:02'
---
# INV-070: Legacy Scaffold Recipe Audit

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Legacy `just` scaffold recipes (`just work`, `just inv`, `just scaffold`) produce WORK.md files with unfilled placeholders (`type: {{TYPE}}`, wrong session numbers, generic deliverables). These recipes predate the work-creation-cycle skill that properly populates fields. An agent calling `just work` directly (as happened in Session 250) creates a malformed artifact that appears syntactically valid but has garbage values.

**Risk:** Malformed work items can pass governance gates because YAML is structurally valid. The `{{TYPE}}` placeholder isn't caught by any hook. This violates the Module-First Principle (Session 218) and the traceability chain (REQ-TRACE-005).

**Scope:**
- Audit all `just` recipes that scaffold governed documents
- Identify which recipes bypass cycle skills
- Determine which should be removed, gated, or redirected to cycle skills
- Assess whether PreToolUse hook should block direct scaffold calls

---

## Deliverables

- [ ] Inventory of all scaffold-related recipes in justfile
- [ ] Classification: safe (used by skills) vs unsafe (bypasses skills)
- [ ] Recommendation per recipe: keep / remove / gate / redirect
- [ ] If gate: spawn work item for PreToolUse hook enhancement
- [ ] If remove: spawn cleanup work item

---

## History

### 2026-01-27 - Created (Session 250)
- Spawned after agent called `just work` directly, producing malformed WORK.md
- Traced to migration arc, CH-004 (RecipeAudit)

---

## References

- @.claude/haios/epochs/E2_3/arcs/migration/CH-004-recipe-audit.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TRACE-005)
- Session 218: Module-First Principle
