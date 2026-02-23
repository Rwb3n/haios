---
template: work_item
id: WORK-195
title: UserPromptSubmit Slim-Read-Once Refactor
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-194
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-23'
priority: medium
effort: small
traces_to:
- REQ-OBSERVE-002
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
acceptance_criteria:
- haios-status-slim.json read and parsed exactly once per handle() invocation
- Parsed slim dict passed to all functions that need it (_get_session_state_warning,
  _get_phase_contract)
- Existing tests pass with no behavior change
blocked_by: []
blocks:
- WORK-196
enables:
- WORK-196
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 16:24:41
  exited: '2026-02-23T10:23:57.272960'
artifacts: []
cycle_docs: {}
memory_refs:
- 87635
- 87636
- 87637
- 87638
- 87639
- 87674
- 87675
extensions: {}
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-23T10:23:57.275312'
queue_history:
- position: ready
  entered: '2026-02-22T16:33:08.872071'
  exited: '2026-02-22T16:33:08.900033'
- position: working
  entered: '2026-02-22T16:33:08.900033'
  exited: '2026-02-23T10:23:57.272960'
- position: done
  entered: '2026-02-23T10:23:57.272960'
  exited: null
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

- [x] `handle()` reads slim JSON once and passes parsed dict to consumers
- [x] `_get_session_state_warning` accepts slim dict parameter
- [x] `_get_phase_contract` accepts slim dict parameter
- [x] Disabled functions (`_get_vitals`, `_get_thresholds`) updated for consistency
- [x] Existing tests pass with no behavior change

---

## History

### 2026-02-22 - Created (Session 425)
- Spawned from WORK-194 investigation finding: slim JSON parsed 4x per handle() call
- Prerequisite for WORK-196 (new hook injections)

---

## References

- @docs/work/active/WORK-194/WORK.md (parent investigation)
- @.claude/hooks/hooks/user_prompt_submit.py (target file)
