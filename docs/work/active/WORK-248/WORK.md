---
template: work_item
id: WORK-248
title: Hook Infrastructure Cleanup — Dead Code and Stale Gates
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
- .claude/hooks/hooks/pre_tool_use.py
- .claude/hooks/memory_retrieval.py
- .claude/hooks/reasoning_extraction.py
acceptance_criteria:
- Remove disabled vitals code (lines 98-104 user_prompt_submit.py, disabled S179)
  and disabled thresholds code (lines 119-123, disabled S259), plus dead _get_vitals
  function body and any unreferenced helper functions from the vitals/context_pct
  era
- Remove .batch_work_bypass dead code from pre_tool_use.py (lines 331-334, 436-439)
- 'Resolve orphaned hook scripts: memory_retrieval.py deleted (zero callers); reasoning_extraction.py
  kept (live consumer in memory_bridge.py:extract_learnings)'
- Process review gate scoped to current session (pre_tool_use.py lines 930-946)
- 3 pre-existing test failures fixed (test_lib_status, test_manifest, test_plan_authoring_agent)
blocked_by: []
blocks: []
enables: []
queue_position: working
cycle_phase: DONE
current_node: DONE
node_history:
- node: backlog
  entered: '2026-03-07T13:54:21.470332'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T13:54:21.470332'
  exited: '2026-03-07T16:18:37.133971'
- position: ready
  entered: '2026-03-07T16:18:37.133971'
  exited: '2026-03-07T16:18:39.725212'
- position: working
  entered: '2026-03-07T16:18:39.725212'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89703
- 89704
- 89705
- 89706
- 89707
- 89708
- 89709
- 89710
- 89731
- 89732
- 89733
- 89734
- 89735
- 89736
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T16:53:39.035424'
---
# WORK-248: Hook Infrastructure Cleanup — Dead Code and Stale Gates
