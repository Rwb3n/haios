---
template: work_item
id: INV-070
title: Legacy Scaffold Recipe Audit
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-27
spawned_by: WORK-027
chapter: CH-004
arc: migration
closed: '2026-01-27'
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
current_node: active
node_history:
- node: backlog
  entered: 2026-01-27 21:49:18
  exited: 2026-01-27 22:05:00
- node: active
  entered: 2026-01-27 22:05:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82537
- 82538
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T22:20:25'
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

- [x] Inventory of all scaffold-related recipes in justfile
- [x] Classification: safe (used by skills) vs unsafe (bypasses skills)
- [x] Recommendation per recipe: keep / remove / gate / redirect
- [x] If gate: spawn work item for PreToolUse hook enhancement
- [ ] If remove: spawn cleanup work item

---

## Findings

### Scaffold Recipe Inventory

| Recipe | Creates | Called By | Classification | Recommendation |
|--------|---------|----------|----------------|----------------|
| `scaffold` | Any governed doc via cli.py | All `/new-*` commands + aliases | **Safe** (gateway) | Keep |
| `work` | Work item WORK.md | `/new-work`, `new-investigation` recipe | **Unsafe** | Gate |
| `plan` | Implementation plan | `/new-plan` | **Unsafe** | Gate |
| `inv` | Investigation doc | `/new-investigation` | **Unsafe** | Gate |
| `new-investigation` | Work item + investigation (combo) | Not called by any skill/module | **Unsafe** | Remove or gate |
| `adr` | ADR | `/new-adr` | Marginal | Keep with caution |
| `checkpoint` | Session checkpoint | `/new-checkpoint` | Marginal | Keep |
| `scaffold-observations` | Observations.md | `observation-capture-cycle` | **Safe** | Keep |

### The Governance Gap

**Safe path:** `/new-work` command -> agent reads instructions -> `just work` -> work-creation-cycle populates fields

**Unsafe path:** Agent calls `just work` directly via Bash -> no cycle runs -> placeholders remain (`{{TYPE}}`, wrong session, generic deliverables)

**PreToolUse hook gap:** The hook blocks raw Write/Edit to governed paths (justfile L266-319) but does NOT block or warn on `just work/plan/inv/scaffold` Bash commands. No scaffold recipe guard exists.

### Root Cause

The recipes are **aliases to `scaffold`** which calls `cli.py scaffold` -> `scaffold.py`. The scaffold module uses template files with placeholders. These recipes were created before cycle skills existed. They remain necessary as the low-level file creation mechanism, but agents should never call them directly.

### Conclusion

**H1 Confirmed:** 4 unsafe scaffold recipes exist (work, plan, inv, new-investigation).
**H2 Confirmed:** Classification is clear — recipes called only by commands/skills are safe; directly-callable ones are unsafe.
**H3 Confirmed:** A PreToolUse Bash guard blocking `just (work|plan|inv|scaffold|new-investigation)` with a redirect message to `/new-*` commands is the recommended fix.

### Spawned Work

1. **E2-305** (to create): Add PreToolUse guard blocking direct scaffold recipe calls via Bash, redirecting to `/new-*` commands
2. **E2-306** (to create): Remove `new-investigation` compound recipe (redundant, `/new-investigation` command exists)

---

## History

### 2026-01-27 - Created (Session 250)
- Spawned after agent called `just work` directly, producing malformed WORK.md
- Traced to migration arc, CH-004 (RecipeAudit)

### 2026-01-27 - Investigated (Session 251)
- Full audit of justfile: 8 scaffold-related recipes identified
- 4 classified as unsafe, 2 as marginal, 2 as safe
- Governance gap confirmed: PreToolUse hook has no Bash guard for scaffold recipes
- Recommendation: Add PreToolUse Bash guard + remove compound `new-investigation` recipe

---

## References

- @.claude/haios/epochs/E2_3/arcs/migration/CH-004-recipe-audit.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TRACE-005)
- Session 218: Module-First Principle
- justfile lines 22-73: scaffold recipe definitions
- .claude/hooks/hooks/pre_tool_use.py lines 266-319: governed path Write/Edit blocks
