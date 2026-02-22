---
template: work_item
id: WORK-189
title: "Context Window Usage Injection via UserPromptSubmit Hook"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-163
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-ASSET-001
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
acceptance_criteria:
- "UserPromptSubmit hook injects context_window.used_percentage on every prompt"
- "Agent sees [CONTEXT: N% used] in hook output"
- "Graceful degradation if status line data unavailable"
- "Existing tests still pass"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T10:27:49
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T10:27:49
---
# WORK-189: Context Window Usage Injection via UserPromptSubmit Hook

---

## Context

Agents cannot see their current context window usage. Token estimation is done manually and is consistently inaccurate (S420: agent estimated 80-100K usage when actual was 150K). This leads to poor decisions about whether to chain to next work or end the session.

Claude Code exposes `context_window.used_percentage` and `context_window.remaining_percentage` via the status line JSON. The UserPromptSubmit hook already runs on every prompt — extending it to inject context usage would give the agent real-time visibility with zero cognitive overhead.

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

### 2026-02-22 - Created (Session 420)
- Spawned from WORK-163 retro observation
- Agent token estimates consistently wrong — need real data injection

---

## References

- @docs/work/active/WORK-163/WORK.md
- Claude Code status line docs: context_window.used_percentage field
