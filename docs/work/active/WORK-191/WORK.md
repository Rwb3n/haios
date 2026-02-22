---
template: work_item
id: WORK-191
title: queue-commit Ceremony Contract Missing work_id Field
type: bug
status: complete
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-189
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-22'
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- queue-commit ceremony contract does not fire missing work_id warnings on valid invocations
- Contract validation correctly receives work_id from invocation path
- Existing tests still pass
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 15:20:16
  exited: '2026-02-22T16:05:25.781012'
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-22T16:05:25.784101'
queue_history:
- position: ready
  entered: '2026-02-22T15:46:41.719646'
  exited: '2026-02-22T15:46:59.422507'
- position: working
  entered: '2026-02-22T15:46:59.422507'
  exited: '2026-02-22T16:05:25.781012'
- position: done
  entered: '2026-02-22T16:05:25.781012'
  exited: null
---
# WORK-191: queue-commit Ceremony Contract Missing work_id Field

---

## Context

The `queue-commit` ceremony contract fires false "Required field 'work_id' is missing" warnings and blocks during implementation-cycle. The ceremony contract expects a `work_id` field that is not provided by the current invocation path.

Evidence: governance-events.jsonl:12009-12011 — 3 events (2 warn, 1 block) during WORK-189 implementation (S423). Related to WORK-179 (Queue Commit Cycle Phase Auto-Advance Investigation) but distinct: WORK-179 investigates auto-advance, this fixes the contract validation.

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

- [x] queue-commit ceremony contract receives work_id from invocation path
- [x] No false missing-field warnings on valid queue-commit calls
- [x] Existing tests pass

---

## History

### 2026-02-22 - Completed (Session 424)
- Root cause: _extract_ceremony_inputs() returned {} because Skill tool_input args is free-text string
- Fix: Parse args string with re.search(r'(WORK-\d{3,})', args) to extract work_id
- 4 new tests, 10 total pass. Full suite: 1609 passed, 0 regressions.
- Note: Fix is in pre_tool_use.py (hook layer), not queue_ceremonies.py (lib layer). Critique A2 confirmed: contract enforcement happens in hook, not in lib.

### 2026-02-22 - Created (Session 423)
- Extracted from WORK-189 retro-cycle (BUG-2)
- Related to WORK-179 (Queue Commit investigation) but distinct scope

---

## References

- @docs/work/active/WORK-189/WORK.md (source retro extraction)
- @docs/work/active/WORK-179/WORK.md (related investigation)
- Memory: 87512-87516 (S423 retro-extract)
