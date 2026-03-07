---
template: work_item
id: WORK-279
title: "Lightweight Token Counter \u2014 Character-Based Ceremony Cost Measurement"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-270
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/
acceptance_criteria:
- Build approximate token counter using character/word ratio heuristic (~4 chars/token)
- 'Measure token cost of: skill file loading, additionalContext injection, coldstart
  output, subagent prompts'
- 'Provide lib function: estimate_tokens(text) -> int and estimate_file_tokens(path)
  -> int'
- Enable data-driven ceremony optimization decisions (mem:89324)
- 'Evidence: S477 WORK-270 finding P5, mem:89322 (no token measurement tooling exists),
  mem:85987'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T20:21:16.406998'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T20:21:16.406998'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T20:21:16.406998'
---
# WORK-279: Lightweight Token Counter — Character-Based Ceremony Cost Measurement
