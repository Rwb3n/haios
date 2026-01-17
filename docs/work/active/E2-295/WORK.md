---
template: work_item
id: E2-295
title: Wire survey, close, and work-creation cycles with set-cycle
status: active
owner: Hephaestus
created: 2026-01-16
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: E2-292
spawned_by_investigation: INV-065
blocked_by:
- E2-293
blocks: []
enables: []
related:
- E2-292
- E2-293
- E2-294
current_node: complete
node_history:
- node: backlog
  entered: 2026-01-16 21:10:30
  exited: '2026-01-17T12:01:22.154038'
- node: plan
  entered: '2026-01-17T12:01:22.154038'
  exited: '2026-01-17T12:01:22.179579'
- node: implement
  entered: '2026-01-17T12:01:22.179579'
  exited: '2026-01-17T12:01:22.206290'
- node: close
  entered: '2026-01-17T12:01:22.206290'
  exited: '2026-01-17T12:01:22.230958'
- node: complete
  entered: '2026-01-17T12:01:22.230958'
  exited: null
cycle_docs: {}
memory_refs: []
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-16
last_updated: '2026-01-17T12:01:08'
---
# WORK-E2-295: Wire survey, close, and work-creation cycles with set-cycle

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Part C of E2-292 split. The remaining cycle skills need recipe calls wired in.

**Solution:** Add `just set-cycle` and `just set-queue` calls to survey-cycle, close-work-cycle, and work-creation-cycle.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

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
-->

- [x] Wire survey-cycle with `just set-queue` after queue selection
- [x] Wire close-work-cycle with `just set-cycle` at VALIDATE/ARCHIVE/MEMORY phase entries
- [x] Wire close-work-cycle with `just clear-cycle` at end
- [x] Wire work-creation-cycle with `just set-cycle` at VERIFY/POPULATE/READY phase entries
- [x] Test: UserPromptSubmit displays queue context from survey-cycle

---

## History

### 2026-01-17 - Completed (Session 196)
- Wired survey-cycle with set-queue after queue selection
- Wired close-work-cycle with set-cycle at all 4 phases + clear-cycle
- Wired work-creation-cycle with set-cycle at all 4 phases
- Manual test verified active_queue updates correctly

### 2026-01-16 - Created (Session 195)
- Initial creation

---

## References

- @docs/work/active/E2-292/plans/PLAN.md (original plan with wiring pattern)
- @docs/work/active/INV-065/investigations/001-session-state-cascade-architecture.md
- @.claude/skills/survey-cycle/SKILL.md
- @.claude/skills/close-work-cycle/SKILL.md
- @.claude/skills/work-creation-cycle/SKILL.md
