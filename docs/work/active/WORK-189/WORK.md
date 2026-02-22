---
template: work_item
id: WORK-189
title: Context Window Usage Injection via UserPromptSubmit Hook
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-163
spawned_children:
- WORK-190
- WORK-191
- WORK-192
chapter: CH-059
arc: call
closed: '2026-02-22'
priority: medium
effort: small
traces_to:
- REQ-OBSERVE-002
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
acceptance_criteria:
- UserPromptSubmit hook parses transcript JSONL for last assistant usage metadata
- 'Agent sees [CONTEXT: N% used] in hook output'
- Graceful degradation if transcript missing or no usage data found
- Existing tests still pass
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 10:27:49
  exited: '2026-02-22T15:18:58.757292'
artifacts: []
cycle_docs: {}
memory_refs:
- 87469
- 87470
- 87471
- 87472
- 87473
- 87474
- 87475
- 87476
- 87526
- 87527
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-22T15:18:58.760328'
queue_history:
- position: done
  entered: '2026-02-22T15:18:58.757292'
  exited: null
---
# WORK-189: Context Window Usage Injection via UserPromptSubmit Hook

---

## Context

Agents cannot see their current context window usage. Token estimation is done manually and is consistently inaccurate (S420: agent estimated 80-100K usage when actual was 150K). This leads to poor decisions about whether to chain to next work or end the session.

Claude Code exposes `context_window.used_percentage` and `context_window.remaining_percentage` via the status line JSON — but ONLY to `statusLine` commands, NOT to hooks. E2-235 discovered this constraint: UserPromptSubmit hooks receive only `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, and `prompt` (see obs-212-002).

**Pivot (S423):** Parse the transcript JSONL directly. The hook already receives `transcript_path`. Claude Code embeds API `usage` metadata (input_tokens, cache_creation_input_tokens, cache_read_input_tokens) in assistant messages in the JSONL. Scan to last assistant message, sum input token fields, calculate percentage against 200k context window. Proven pattern from github.com/harrymunro/nelson/scripts/count-tokens.py.

**Architecture:** UserPromptSubmit hook reads `transcript_path` JSONL → extracts last usage → calculates percentage → injects `[CONTEXT: N% used]`. Single-file change.

Assigned to CH-059 (CeremonyAutomation) because this is hook-based automation of a mechanical observability step, consistent with CH-059's scope of migrating mechanical operations to hooks/modules.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [ ] UserPromptSubmit hook extended to inject context window usage percentage
- [ ] Agent sees real usage on every prompt (e.g., "[CONTEXT: 75% used]")
- [ ] Graceful degradation if data unavailable
- [ ] Existing tests pass

---

## History

### 2026-02-22 - Pivot (Session 423)
- Critique (A4) confirmed E2-235 finding: hooks do NOT receive context_window data
- Initial pivot to statusLine sidecar approach (write JSON to file, hook reads it)
- Second pivot to transcript JSONL parsing after discovering nelson/count-tokens.py pattern
- Final approach: parse transcript_path JSONL for API usage metadata, single-file change
- Fixed traces_to from REQ-ASSET-001 to REQ-OBSERVE-002 (critique A1)
- Registered in CH-059 CHAPTER.md (critique A2)

### 2026-02-22 - Created (Session 420)
- Spawned from WORK-163 retro observation
- Agent token estimates consistently wrong — need real data injection

---

## References

- @docs/work/active/WORK-163/WORK.md
- Claude Code status line docs: context_window.used_percentage field
