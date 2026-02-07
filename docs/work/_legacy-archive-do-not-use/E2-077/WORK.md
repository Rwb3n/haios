---
template: work_item
id: E2-077
title: Schema-Verifier Skill Wrapper
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: small
category: implementation
spawned_by: Session 76
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-23 19:06:12
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-28T20:50:42'
---
# WORK-E2-077: Schema-Verifier Skill Wrapper

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Schema-verifier subagent works but agents don't know correct column names before querying. Example: queried `content_type='bridge_insight'` when actual schema is `type='SynthesizedInsight'`.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Create `.claude/skills/schema-query/SKILL.md`
- [ ] Skill loads schema summary (table→columns→types)
- [ ] Skill invokes schema-verifier subagent
- [ ] Skill formats response with "for future reference" schema hints

**Solution:** Wrap schema-verifier in a skill that:
1. Injects schema vocabulary hints before query
2. Shows common column name mappings (content_type vs type)
3. Returns query results WITH schema context for future queries

**Pattern:** "Make right way easy" - agent learns schema vocabulary through use

**Related:** E2-020 (Schema Discovery), schema-verifier subagent

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

### 2025-12-28 - Closed as Superseded (Session 139)
- Problem statement: "agents don't know correct column names before querying"
- Current solution already provides this:
  1. `/schema` command for quick lookups
  2. `schema-verifier` agent (REQUIRED for SQL queries per PreToolUse governance)
  3. PreToolUse hook blocks direct SQL, forcing schema verification
- Skill wrapper would be redundant - existing infrastructure solves the problem
- Closed without implementation

---

## References

- Superseded by: `/schema` command + `schema-verifier` agent
- Related: E2-020 (Schema Discovery)
