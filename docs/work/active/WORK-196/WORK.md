---
template: work_item
id: WORK-196
title: "UserPromptSubmit Hook Injection Batch (Session, Working, Duration)"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-194
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-OBSERVE-002
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
acceptance_criteria:
- "Hook injects [SESSION: N] on every prompt from .claude/session file"
- "Hook injects [WORKING: WORK-XXX] when active cycle has work_id (from slim JSON)"
- "Hook injects [DURATION: Nm] calculated from .claude/session file mtime"
- "Each injection is <5 tokens, total <20 tokens"
- "Graceful degradation if any data source unavailable"
- "Existing tests pass"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T16:24:53
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T16:24:53
---
# WORK-196: UserPromptSubmit Hook Injection Batch (Session, Working, Duration)

---

## Context

WORK-194 investigation evaluated 4 candidates for UserPromptSubmit hook injection. Three were approved for implementation:

1. **Session number** `[SESSION: 425]` — Read `.claude/session` file (3 lines, ~50 bytes), extract last line as integer. ~5 tokens.
2. **Working item** `[WORKING: WORK-194]` — Extract `session_state.work_id` from slim JSON (already parsed after WORK-195 refactor). ~5 tokens. Only inject when active cycle has work_id.
3. **Time-in-session** `[DURATION: 61m]` — Use `.claude/session` file mtime as session start timestamp, calculate elapsed minutes via `datetime.now() - mtime`. ~5 tokens. Candidates 1+3 share a single Path object.

Design constraint: each injection <20 tokens. Combined overhead: ~15 tokens per prompt.

Candidate 4 (pending count `[READY: N items]`) was deferred — requires WorkEngine import which is too heavy for per-prompt hook context.

Depends on WORK-195 (slim-read-once refactor) being complete first.

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

- [ ] `[SESSION: N]` injected on every prompt
- [ ] `[WORKING: WORK-XXX]` injected when active cycle has work_id
- [ ] `[DURATION: Nm]` injected from session file mtime
- [ ] Graceful degradation for each injection (None if data unavailable)
- [ ] Tests for each new injection function
- [ ] Existing tests pass

---

## History

### 2026-02-22 - Created (Session 425)
- Spawned from WORK-194 investigation: 3 of 4 candidates approved
- Candidate 4 (pending count) deferred — WorkEngine too heavy for per-prompt hook

---

## References

- @docs/work/active/WORK-194/WORK.md (parent investigation)
- @docs/work/active/WORK-195/WORK.md (prerequisite: slim refactor)
- @.claude/hooks/hooks/user_prompt_submit.py (target file)
