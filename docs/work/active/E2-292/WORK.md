---
template: work_item
id: E2-292
title: Wire set-cycle Recipe Calls into Cycle Skills
status: dismissed
owner: Hephaestus
created: 2026-01-16
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-065
spawned_by_investigation: INV-065
blocked_by: []
blocks: []
enables:
- E2-293
- E2-294
- E2-295
related:
- E2-286
- E2-287
- E2-288
- E2-291
- E2-293
- E2-294
- E2-295
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-16 20:44:04
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
last_updated: '2026-01-18T21:56:50'
---
# WORK-E2-292: Wire set-cycle Recipe Calls into Cycle Skills

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Session state in haios-status-slim.json is dead code. E2-286/287/288 built the schema and recipes but nothing actually calls them. This causes:
1. Queue context lost - survey-cycle picks queue but routing-gate doesn't know which
2. Phase observability missing - can't see what cycle/phase agent is in
3. work_cycle shows stale data

**Root cause:** INV-065 discovered that PostToolUse CANNOT intercept Skill() invocations - skills are markdown files, not hookable tool events. The cascade mechanism MUST be explicit recipe calls in skill prose.

**Solution:** Add `just set-cycle`, `just set-queue`, and `just clear-cycle` calls to cycle skill prose at:
- Skill entry (set active_cycle + initial phase)
- Phase transitions (update current_phase)
- Skill exit (clear-cycle or chain)

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

- [ ] Add `just set-queue` recipe (new - sets active_queue in session_state)
- [ ] Extend session_state schema with active_queue and phase_history fields
- [ ] Wire implementation-cycle with set-cycle at PLAN/DO/CHECK/DONE transitions
- [ ] Wire investigation-cycle with set-cycle at HYPOTHESIZE/EXPLORE/CONCLUDE transitions
- [ ] Wire survey-cycle with set-queue after queue selection
- [ ] Wire close-work-cycle with set-cycle and clear-cycle
- [ ] Wire work-creation-cycle with set-cycle at VERIFY/POPULATE/READY transitions
- [ ] Test: UserPromptSubmit displays current cycle/phase/queue context

---

## History

### 2026-01-16 - Created (Session 194)
- Initial creation

### 2026-01-16 - Deferred (Session 195)
- Scope exceeded 3-file threshold (7 files)
- Operator requested split into smaller PRs
- Split into: E2-293 (schema), E2-294 (impl+inv cycles), E2-295 (survey+close+work cycles)

---

## References

- @docs/work/active/INV-065/investigations/001-session-state-cascade-architecture.md (source investigation)
- @docs/work/archive/E2-286/WORK.md (session_state schema)
- @docs/work/archive/E2-288/WORK.md (set-cycle/clear-cycle recipes)
- justfile:244-245 (existing set-cycle recipe)
