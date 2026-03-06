---
template: work_item
id: WORK-243
title: "Clean /close command: remove stale Steps 2-3 duplicate documentation"
type: implementation
status: active
owner: Hephaestus
created: 2026-03-06
spawned_by: WORK-238
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: low
effort: small
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/commands/close.md
acceptance_criteria:
- "Steps 2-3 (DoD validation + closure execution) removed from close.md"
- "close.md retains: Step 1 (lookup), Step 1.1 (tier detect), retro chain, retro-enrichment chain, close-work chain"
- "Reference note added: 'See close-work-cycle SKILL.md for VALIDATE/ARCHIVE/CHAIN details'"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-03-06T23:42:12
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89334
- 89342
extensions: {}
version: "2.0"
generated: 2026-03-06
last_updated: 2026-03-06T23:42:12
---
# WORK-243: Clean /close command: remove stale Steps 2-3 duplicate documentation

---

## Context

WORK-238 investigation (S465) found that `/close` command (close.md) Steps 2-3 duplicate close-work-cycle SKILL.md content. close.md:118 explicitly notes "The remaining steps below document the skill's phases for reference." This reference documentation creates a maintenance burden — when close-work-cycle changes, close.md becomes stale.

The command should be the orchestrator (find work -> retro -> enrichment -> close-work skill) and delegate phase details to the skill definition.

---

## Deliverables

- [ ] Remove Steps 2 and 3 from close.md (lines ~196-293)
- [ ] Remove Step 4 "Report Closure" (owned by close-work-cycle CHAIN)
- [ ] Remove "Verification Checklist" and "Example Usage" stale sections
- [ ] Add reference note after "Chain to Close Work Cycle" section pointing to SKILL.md
- [ ] Verify close.md still correctly chains: lookup -> tier detect -> retro -> enrichment -> close-work

---

## References

- @docs/work/active/WORK-238/investigations/001-done-chain-duplication.md
- @.claude/commands/close.md
- @.claude/skills/close-work-cycle/SKILL.md
