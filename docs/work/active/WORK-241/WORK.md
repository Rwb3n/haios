---
template: work_item
id: WORK-241
title: "Eliminate dod-validation-cycle: absorb Agent UX Test into close-work VALIDATE"
type: implementation
status: active
owner: Hephaestus
created: 2026-03-06
spawned_by: WORK-238
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-002
- REQ-CEREMONY-005
requirement_refs: []
source_files:
- .claude/skills/dod-validation-cycle/SKILL.md
- .claude/skills/close-work-cycle/SKILL.md
acceptance_criteria:
- "dod-validation-cycle invocation removed from close-work-cycle SKILL.md"
- "Agent UX Test absorbed as optional inline checklist item in close-work VALIDATE"
- "dod-validation-cycle SKILL.md marked deprecated: true"
- "CLAUDE.md ceremony table updated to reflect removal"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-03-06T23:42:11
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89334
- 89335
- 89336
extensions: {}
version: "2.0"
generated: 2026-03-06
last_updated: 2026-03-06T23:42:11
---
# WORK-241: Eliminate dod-validation-cycle: absorb Agent UX Test into close-work VALIDATE

---

## Context

WORK-238 investigation (S465) confirmed dod-validation-cycle is fully redundant for ALL tiers. Every MUST gate (tests pass, plans complete, WHY captured, docs current, Ground Truth) is already verified by impl-cycle CHECK and close-work VALIDATE. The only unique contribution is Agent UX Test (SHOULD gate, not MUST).

The lightweight path (effort=small) already skips dod-validation. This work extends that pattern to all tiers.

**Estimated savings:** ~2200 tokens per closure for effort=medium+ items.

---

## Deliverables

- [ ] Remove `Skill(skill="dod-validation-cycle")` invocation from close-work-cycle SKILL.md
- [ ] Add Agent UX Test as optional inline checklist item in close-work VALIDATE
- [ ] Add `deprecated: true` to dod-validation-cycle SKILL.md frontmatter
- [ ] Update close-work-cycle diagram to remove dod-validation box
- [ ] Update CLAUDE.md ceremony table

---

## References

- @docs/work/active/WORK-238/investigations/001-done-chain-duplication.md
- @.claude/skills/dod-validation-cycle/SKILL.md
- @.claude/skills/close-work-cycle/SKILL.md
- WORK-235 investigation: Finding 1 (dod-validation redundant for all tiers)
