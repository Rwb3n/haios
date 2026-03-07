---
template: work_item
id: WORK-248
title: "Hook Infrastructure Cleanup \u2014 Dead Code and Stale Gates"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-060
arc: call
closed: null
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
- .claude/hooks/hooks/pre_tool_use.py
- .claude/hooks/hooks/post_tool_use.py
- .claude/hooks/memory_retrieval.py
- .claude/hooks/reasoning_extraction.py
acceptance_criteria:
- Retire _extract_context_pct, _get_context_usage, _estimate_context_usage from user_prompt_submit.py
  (superseded by statusLine native data)
- Remove disabled vitals code (lines 101-127 user_prompt_submit.py, disabled since
  S179/S259)
- Remove .batch_work_bypass dead code from pre_tool_use.py (lines 331-334, 436-439)
- 'Resolve or delete orphaned hook scripts: memory_retrieval.py, reasoning_extraction.py'
- Process review gate scoped to current session (pre_tool_use.py lines 930-946)
- 3 pre-existing test failures fixed (test_lib_status, test_manifest, test_plan_authoring_agent)
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T13:54:21.470332'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T13:54:21.470332'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T13:54:21.470332'
---
# WORK-248: Hook Infrastructure Cleanup — Dead Code and Stale Gates
