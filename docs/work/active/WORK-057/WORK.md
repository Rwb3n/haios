---
template: work_item
id: WORK-057
title: Claude Code Hook Enhancements - additionalContext, skill hooks, once:true
type: investigation
status: backlog
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-056
chapter: null
arc: activities
closed: null
priority: high
effort: medium
traces_to:
- REQ-GOVERN-001
requirement_refs: []
source_files:
- .claude/hooks/hooks/pre_tool_use.py
- .claude/hooks/hooks/post_tool_use.py
acceptance_criteria:
- additionalContext capability documented and evaluated
- Skill-level hooks evaluated for governance use
- once:true pattern evaluated for session initialization
- Adoption recommendation with implementation plan
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 15:18:13
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T15:20:24'
---
# WORK-057: Claude Code Hook Enhancements - additionalContext, skill hooks, once:true

---

## Context

Claude Code 2.1.x introduced several hook enhancements that could strengthen HAIOS governance:

**Features to Investigate:**

| Feature | Version | Potential Use |
|---------|---------|---------------|
| **PreToolUse `additionalContext`** | 2.1.9 | Inject activity state, memory hints into context |
| **Hooks in skill frontmatter** | 2.1.0 | Per-skill validation without global hook complexity |
| **`once: true` config** | 2.1.0 | Run initialization hooks exactly once per session |
| **YAML-style lists in `allowed-tools`** | 2.1.0 | Cleaner skill tool restrictions |

**Current State:**
- HAIOS uses PreToolUse for governance (activity matrix, SQL blocking, path governance)
- Hooks are global in `.claude/hooks/` - no per-skill hooks
- No `additionalContext` injection currently

**Questions:**
1. Can `additionalContext` inject governed activity state into tool responses?
2. Can skill-level hooks replace or augment global PreToolUse?
3. Can `once:true` simplify coldstart initialization?

---

## Deliverables

- [ ] **additionalContext capability doc** - What can be injected, format, limitations
- [ ] **Skill hooks feasibility** - Can they gate specific cycles (e.g., implementation-cycle)?
- [ ] **once:true evaluation** - Benefits for session initialization vs current approach
- [ ] **Adoption recommendation** - Which features to adopt, in what order

---

## History

### 2026-02-01 - Created (Session 271)
- Spawned from WORK-056 parent investigation
- Linked to activities arc (governance enhancement)

---

## References

- @docs/work/active/WORK-056/WORK.md (parent investigation)
- @.claude/hooks/hooks/pre_tool_use.py (current implementation)
- @.claude/haios/config/activity_matrix.yaml (governance rules)
