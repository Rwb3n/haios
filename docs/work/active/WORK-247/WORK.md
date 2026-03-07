---
template: work_item
id: WORK-247
title: "Context Budget Gate \u2014 Wire Prototype to Production"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-060
arc: call
closed: null
priority: high
effort: medium
traces_to:
- REQ-CEREMONY-003
requirement_refs: []
source_files:
- .claude/hooks/statusline.py
- .claude/hooks/hooks/pre_tool_use.py
- .claude/hooks/hooks/user_prompt_submit.py
- .claude/settings.json
acceptance_criteria:
- statusline.py writes .claude/context_remaining with Claude Code native context_window.remaining_percentage
  on every refresh
- PreToolUse _check_context_budget reads .claude/context_remaining and injects [CONTEXT
  LOW] at <=20% and [CONTEXT CRITICAL] at <=10%
- Retire transcript-based _extract_context_pct and _get_context_usage from user_prompt_submit.py
- Update _write_context_pct_to_slim to read from .claude/context_remaining instead
  of transcript parsing
- Tests for _check_context_budget and _inject_context_warning
- Governance events use fresh context_pct from .claude/context_remaining instead of
  stale slim relay
- .claude/context_remaining is gitignored
- 'Verified: warning appears in additionalContext when context drops below 20%'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T13:42:19.874074'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T13:42:19.874074'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T13:42:19.874074'
---
# WORK-247: Context Budget Gate — Wire Prototype to Production

## Context

Session 468 exhausted context during CHAIN phase — no retro, no checkpoint, no /close.
Root cause: context_pct was only updated on UserPromptSubmit (rarely fires during autonomous work),
so the agent had no warning that context was running low.

## Prototype (S469 — already in working tree)

The following changes are already implemented and tested but not yet committed:

1. **statusline.py** (NEW): Python replacement for jq-based statusLine. Reads Claude Code native
   `context_window.remaining_percentage`, writes float to `.claude/context_remaining`.
   Also fixed: old jq-based statusLine was silently failing (jq not installed).

2. **pre_tool_use.py**: Added `_check_context_budget()` and `_inject_context_warning()`.
   Reads `.claude/context_remaining`, injects `[CONTEXT LOW]` at <=20% or
   `[CONTEXT CRITICAL]` at <=10% into every PreToolUse response's `additionalContext`.

3. **settings.json**: statusLine command changed to `python .claude/hooks/statusline.py`.

4. **.gitignore**: `.claude/context_remaining` added.

## Remaining Work

1. **Retire transcript parsing**: Remove `_extract_context_pct()` and `_get_context_usage()`
   from `user_prompt_submit.py`. These are inaccurate (hardcoded 200K limit, dubious token math)
   and redundant with the native context_window data.

2. **Update slim relay**: `_write_context_pct_to_slim()` should read from
   `.claude/context_remaining` file instead of transcript parsing. Or remove entirely
   if governance events can read from the file directly.

3. **Governance event freshness**: `_append_event()` in governance_events.py reads context_pct
   from slim. Verify it now gets fresh values (statusLine updates the file frequently).

4. **Tests**: Unit tests for `_check_context_budget`, `_inject_context_warning`,
   and `statusline.py` main function.

5. **Integration verification**: Confirm warning appears in agent context when remaining drops
   below 20% during a real session.

## Memory Refs

- 89534-89542 (S469 context budget implementation details)
- 89493-89533 (S468 retro — context exhaustion root cause analysis)
