---
template: work_item
id: WORK-236
title: 'Investigation: context_pct Governance Event Consumer Design'
type: investigation
status: complete
owner: Hephaestus
created: '2026-02-25'
closed: '2026-02-26'
priority: medium
effort: small
chapter: CH-059
arc: call
traces_to:
- REQ-CEREMONY-002
spawned_by: WORK-233
spawned_children:
- WORK-237
blocked_by: []
blocks: []
enables:
- WORK-233
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-02-25T22:58:17.052301'
  exited: '2026-02-26T01:03:02.432219'
queue_history:
- position: backlog
  entered: '2026-02-25T22:58:17.052301'
  exited: '2026-02-26T00:50:21.504644'
- position: ready
  entered: '2026-02-26T00:50:21.504644'
  exited: '2026-02-26T00:50:28.056255'
- position: working
  entered: '2026-02-26T00:50:28.056255'
  exited: '2026-02-26T01:03:02.432219'
- position: done
  entered: '2026-02-26T01:03:02.432219'
  exited: null
memory_refs:
- 89083
- 89084
- 89085
- 89086
- 89087
- 89109
- 89110
- 89111
- 89112
- 89113
- 89109
- 89114
- 89115
requirement_refs: []
source_files:
- .claude/haios/lib/governance_events.py
- .claude/hooks/hooks/user_prompt_submit.py
- .claude/hooks/hooks/post_tool_use.py
acceptance_criteria:
- Identify which hook(s) should populate context_pct when calling governance event
  log functions
- 'Design proposal: where _estimate_context_usage() should be called and how context_pct
  flows to log_* functions'
- Determine if PostToolUse hook or UserPromptSubmit hook is the right injection point
artifacts: []
extensions: {}
version: '2.0'
generated: '2026-02-25'
last_updated: '2026-02-26T01:03:02.437755'
---
# WORK-236: Investigation: context_pct Governance Event Consumer Design

---

## Context

WORK-233 (S459) added optional `context_pct` parameter to all governance event log functions. However, no caller currently populates this field — it's dead infrastructure. ADR-033 requires runtime consumers exist before closure.

This investigation determines HOW and WHERE context_pct should be populated:
- `_estimate_context_usage()` in `user_prompt_submit.py` can calculate context percentage from transcript
- PostToolUse hook fires after every tool call and has access to transcript_path
- UserPromptSubmit hook already injects `[CONTEXT: X% remaining]` into the prompt

Questions:
1. Which hook should call governance event functions with context_pct?
2. Should context_pct be injected at every event or only at phase transitions?
3. What's the token cost of calculating context_pct per-event vs per-session?

---

## References

- @.claude/haios/lib/governance_events.py (WORK-233 plumbing)
- @.claude/hooks/hooks/user_prompt_submit.py (_estimate_context_usage source)
- @.claude/hooks/hooks/post_tool_use.py (candidate injection point)
- @docs/work/active/WORK-233/WORK.md (parent — dead infrastructure)
