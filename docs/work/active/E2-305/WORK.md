---
template: work_item
id: E2-305
title: Add PreToolUse Bash Guard for Scaffold Recipes
type: implementation
status: active
owner: Hephaestus
created: 2026-01-27
spawned_by: INV-070
chapter: CH-004
arc: migration
closed: null
priority: high
effort: small
traces_to:
- REQ-GOVERN-002
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-27 22:12:16
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T22:12:53'
---
# E2-305: Add PreToolUse Bash Guard for Scaffold Recipes

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** The PreToolUse hook blocks raw Write/Edit to governed paths but has NO guard for Bash calls to scaffold recipes (`just work`, `just plan`, `just inv`, `just scaffold`, `just new-investigation`). Agents can bypass governance by calling these recipes directly, producing files with unfilled template placeholders like `type: {{TYPE}}`.

**Root cause:** Scaffold recipes predate cycle skills. The PreToolUse hook was designed to guard file writes, not Bash recipe invocations.

**Fix:** Add a pattern match in the PreToolUse Bash handler that detects scaffold recipe calls and blocks them with a message redirecting to `/new-*` commands.

---

## Deliverables

- [ ] PreToolUse Bash guard pattern matching `just (work|plan|inv|scaffold|new-investigation)` calls
- [ ] Block message redirecting to appropriate `/new-*` command
- [ ] Test coverage for the new guard

---

## History

### 2026-01-27 - Created (Session 251)
- Spawned from INV-070 Legacy Scaffold Recipe Audit

---

## References

- @docs/work/active/INV-070/WORK.md (parent investigation)
- @.claude/hooks/pre_tool_use.py (target file)
- @.claude/haios/epochs/E2_3/arcs/migration/CH-004-recipe-audit.md
