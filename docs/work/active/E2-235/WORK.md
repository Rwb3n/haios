---
template: work_item
id: E2-235
title: Earlier Context Warning Thresholds
status: complete
owner: Hephaestus
created: 2025-12-30
closed: '2026-01-19'
milestone: M7b-WorkInfra
priority: high
effort: low
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-30 20:19:17
  exited: null
cycle_docs: {}
memory_refs:
- 82159
- 82160
- 82161
- 82162
- 82163
- 82164
- 82165
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-30
last_updated: '2026-01-19T20:27:59'
---
# WORK-E2-235: Earlier Context Warning Thresholds

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Current context warning threshold is 94%, which leaves insufficient runway (~6%) to complete checkpoint-cycle (SCAFFOLD + FILL + VERIFY + CAPTURE + COMMIT needs ~10% context).

**Root cause:** Threshold was set high to avoid premature warnings, but this backfires during complex sessions where context exhaustion happens abruptly.

**Source:** INV-052 Issue 3 (Context Warning Too Late)

---

## Current State

**RESOLVED via statusLine feature (Session 212).**

The original approach (hook-based warnings) was blocked by a technical constraint: context_window data is only passed to statusLine commands, not to hooks. The UserPromptSubmit hook only receives session_id, transcript_path, cwd, and prompt.

**Resolution:** Claude Code's statusLine feature now provides real-time context window visibility:
```
Claude 3.5 Sonnet | haios | Context: 42.3% used (57.7% free) | Total: 85k in / 43k out
```

This achieves the original goal (earlier awareness of context consumption) through a different mechanism that uses actual API data rather than file-size heuristics.

---

## Deliverables

- [x] ~~Update `.claude/hooks/hooks/user_prompt_submit.py` warning threshold from 94% to 85%~~ N/A - hooks don't receive context_window data
- [x] ~~Add escalating warnings: 85% (suggest checkpoint), 90% (MUST checkpoint), 94% (critical)~~ Replaced by continuous statusLine visibility
- [x] ~~Configure thresholds in `.claude/config/thresholds.yaml` for easy adjustment~~ N/A - statusLine shows actual % directly
- [x] Test with sessions approaching context limit - statusLine confirmed working

**Actual deliverable:** Configured `.claude/settings.json` statusLine to display context_window.used_percentage in real-time.

---

## History

### 2025-12-30 - Created (Session 150)
- Initial creation

### 2026-01-19 - Resolved (Session 212)
- Discovered hooks don't receive context_window data (only statusLine does)
- Configured statusLine in `.claude/settings.json` to show real-time context usage
- Original file-size heuristic in user_prompt_submit.py was disabled Session 179 due to unreliability
- Resolution: statusLine provides continuous visibility using actual API data

---

## References

- `.claude/settings.json` - statusLine configuration
- `.claude/hooks/hooks/user_prompt_submit.py` - disabled heuristic (lines 71-76)
- INV-052 Issue 3 - original problem statement
