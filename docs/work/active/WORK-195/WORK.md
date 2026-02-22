---
template: work_item
id: WORK-195
title: "UserPromptSubmit Slim-Read-Once Refactor"
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
- "haios-status-slim.json read and parsed exactly once per handle() invocation"
- "Parsed slim dict passed to all functions that need it (_get_session_state_warning, _get_phase_contract)"
- "Existing tests pass with no behavior change"
blocked_by: []
blocks:
- WORK-196
enables:
- WORK-196
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T16:24:41
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T16:24:41
---
# WORK-195: UserPromptSubmit Slim-Read-Once Refactor

---

## Context

WORK-194 investigation found that `user_prompt_submit.py` reads and parses `haios-status-slim.json` up to 4 times per `handle()` call (lines 151, 199, 299, 394). Each call does `json.loads(slim_path.read_text(encoding="utf-8-sig"))` independently. Two of these are in active code paths (`_get_session_state_warning`, `_get_phase_contract`), two in disabled functions (`_get_vitals`, `_get_thresholds`).

Refactor `handle()` to read slim JSON once at the top and pass the parsed dict as a parameter to all functions that need it. This is a prerequisite for WORK-196 (new hook injections that also need slim data).

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

- [ ] `handle()` reads slim JSON once and passes parsed dict to consumers
- [ ] `_get_session_state_warning` accepts slim dict parameter
- [ ] `_get_phase_contract` accepts slim dict parameter
- [ ] Disabled functions (`_get_vitals`, `_get_thresholds`) updated for consistency
- [ ] Existing tests pass with no behavior change

---

## History

### 2026-02-22 - Created (Session 425)
- Spawned from WORK-194 investigation finding: slim JSON parsed 4x per handle() call
- Prerequisite for WORK-196 (new hook injections)

---

## References

- @docs/work/active/WORK-194/WORK.md (parent investigation)
- @.claude/hooks/hooks/user_prompt_submit.py (target file)
