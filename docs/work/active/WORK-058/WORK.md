---
template: work_item
id: WORK-058
title: Claude Code Session/Context Management - SESSION_ID, agent_type, context:fork
type: investigation
status: backlog
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-056
chapter: null
arc: configuration
closed: null
priority: high
effort: medium
traces_to:
- REQ-CONTEXT-001
requirement_refs: []
source_files:
- .claude/session
- .claude/haios/modules/coldstart_orchestrator.py
acceptance_criteria:
- SESSION_ID substitution documented and evaluated
- agent_type in SessionStart hook evaluated for role-based loading
- context:fork pattern evaluated for isolated subagents
- Adoption recommendation with implementation plan
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 15:18:17
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T15:20:27'
---
# WORK-058: Claude Code Session/Context Management - SESSION_ID, agent_type, context:fork

---

## Context

Claude Code 2.1.x introduced session and context management features that could improve HAIOS continuity:

**Features to Investigate:**

| Feature | Version | Potential Use |
|---------|---------|---------------|
| **`${CLAUDE_SESSION_ID}`** | 2.1.9 | Skills can reference session ID - link checkpoints to sessions |
| **`agent_type` in SessionStart** | 2.1.2 | Know which agent type for role-based context loading |
| **`context: fork`** | 2.1.0 | Isolated context for subagents - cleaner validation agents |
| **`--from-pr` flag** | 2.1.27 | Resume sessions linked to GitHub PRs |

**Current State:**
- HAIOS tracks session via `.claude/session` file (manual increment)
- Coldstart orchestrator loads context but doesn't know agent type
- Subagents share full context (can be noisy)

**Questions:**
1. Can SESSION_ID replace our manual session tracking?
2. Can agent_type enable true role-based loading per haios.yaml config?
3. Can context:fork create cleaner isolated validators/investigators?
4. Is PR-linked resume useful for HAIOS workflows?

---

## Deliverables

- [ ] **SESSION_ID integration doc** - Replace or augment `.claude/session`
- [ ] **agent_type feasibility** - How to leverage for role-based loading
- [ ] **context:fork evaluation** - Benefits for validation-agent, investigation-agent
- [ ] **Adoption recommendation** - Which features to adopt, in what order

---

## History

### 2026-02-01 - Created (Session 271)
- Spawned from WORK-056 parent investigation
- Linked to configuration arc (context management)

---

## References

- @docs/work/active/WORK-056/WORK.md (parent investigation)
- @.claude/session (current session tracking)
- @.claude/haios/modules/coldstart_orchestrator.py (context loading)
