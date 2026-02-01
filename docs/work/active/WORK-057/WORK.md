---
template: work_item
id: WORK-057
title: Claude Code Hook Enhancements - additionalContext, skill hooks, once:true
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-056
chapter: null
arc: activities
closed: '2026-02-01'
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
enables:
- WORK-064
current_node: close
node_history:
- node: backlog
  entered: 2026-02-01 15:18:13
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82928
- 82929
- 82930
- 82931
- 82932
- 82933
- 82934
- 82935
- 82936
- 82937
- 82938
- 82939
- 82940
- 82945
- 82946
- 82947
- 82948
- 82949
- 82950
- 82951
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T17:45:08'
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

- [x] **additionalContext capability doc** - What can be injected, format, limitations
- [x] **Skill hooks feasibility** - Can they gate specific cycles (e.g., implementation-cycle)?
- [x] **once:true evaluation** - Benefits for session initialization vs current approach
- [x] **Adoption recommendation** - Which features to adopt, in what order

---

## Findings (Session 275)

### Hypothesis Verdicts

| Feature | Verdict | Confidence | Action |
|---------|---------|------------|--------|
| **additionalContext** | ADOPT | 0.90 | WORK-064 spawned |
| **Skill hooks** | DEFER | 0.80 | GovernanceLayer sufficient |
| **once:true** | SKIP | 0.75 | Architecture handles differently |
| **allowed-tools** | EVALUATE | 0.55 | Low priority future work |

### Key Insight

**Visibility Gap:** Current PreToolUse returns `permissionDecisionReason` (shown AFTER attempt) but not `additionalContext` (shown BEFORE attempt). Agent wastes tokens on repeated blocked attempts.

**Solution:** Add `additionalContext: "[STATE: {state}] Blocked: {primitives}"` to hookSpecificOutput.

### Evidence Sources

| Source | Finding |
|--------|---------|
| pre_tool_use.py | Returns hookSpecificOutput but no additionalContext |
| governance_layer.py | get_activity_state() + check_activity() provide state |
| activity_matrix.yaml | Defines blocked primitives per state |
| CC Guide Agent | Confirmed additionalContext in v2.1.9 |

---

## History

### 2026-02-01 - Created (Session 271)
- Spawned from WORK-056 parent investigation
- Linked to activities arc (governance enhancement)

### 2026-02-01 - Completed (Session 275)
- EXPLORE: Gathered evidence from 8 sources
- HYPOTHESIZE: Formed 4 hypotheses with evidence citations
- VALIDATE: Confirmed H1-H3, H4 inconclusive
- CONCLUDE: Spawned WORK-064, stored findings to memory
- Memory refs: 82928-82940

---

## References

- @docs/work/active/WORK-056/WORK.md (parent investigation)
- @docs/work/active/WORK-064/WORK.md (spawned implementation)
- @.claude/hooks/hooks/pre_tool_use.py (current implementation)
- @.claude/haios/config/activity_matrix.yaml (governance rules)
