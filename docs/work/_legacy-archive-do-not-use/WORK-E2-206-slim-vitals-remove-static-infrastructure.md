---
template: work_item
id: E2-206
title: Slim Vitals - Remove Static Infrastructure
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-27
milestone: M7d-Plumbing
priority: medium
effort: small
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-27 12:37:41
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T13:23:29'
---
# WORK-E2-206: Slim Vitals - Remove Static Infrastructure

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Vitals inject ~115 tokens per prompt, with ~65 tokens being static infrastructure lists (commands, skills, agents, MCPs) already documented in CLAUDE.md.

**Root Cause:** Vitals were designed before CLAUDE.md had infrastructure tables. Now redundant.

**Analysis (Session 125):**
- Commands/skills/agents/MCPs rarely change mid-session
- CLAUDE.md § "Governance Quick Reference" has authoritative lists
- Only dynamic data needs per-prompt injection: milestone progress, working context, blocked items

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Remove infrastructure section from `_get_vitals()` in `user_prompt_submit.py`
- [ ] Remove: Commands, Skills, Agents, MCPs, Recipes lines
- [ ] Keep: Milestone, Working, Blocked (if > 0)
- [ ] Verify vitals display correctly after change
- [ ] Token savings: ~115 → ~40 tokens (65% reduction)

---

## History

### 2025-12-27 - Created (Session 125)
- Initial creation

---

## References

- [Related documents]
