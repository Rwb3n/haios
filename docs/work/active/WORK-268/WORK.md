---
template: work_item
id: WORK-268
title: E2E Integration Test for Context Budget Gate Chain
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/hooks/statusline.py
- .claude/hooks/hooks/pre_tool_use.py
- .claude/hooks/hooks/user_prompt_submit.py
acceptance_criteria:
- Integration test covering statusLine -> context_remaining file -> PreToolUse warning
  injection -> UserPromptSubmit relay
- 'Tests context budget thresholds: >20% (no warning), <=20% (LOW), <=15% (SESSION-END),
  <=10% (CRITICAL)'
- Verifies full gate chain from native context_window data to agent-visible warnings
  (mem:89622)
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T17:05:26.632093'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T17:05:26.632093'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T17:05:26.632093'
---
# WORK-268: E2E Integration Test for Context Budget Gate Chain
