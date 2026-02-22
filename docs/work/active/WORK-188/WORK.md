---
template: work_item
id: WORK-188
title: Hook Auto-Injection for Phase Contracts
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-163
spawned_children: []
chapter: CH-062
arc: query
closed: '2026-02-22'
priority: medium
effort: small
traces_to:
- REQ-ASSET-001
requirement_refs: []
source_files:
- .claude/hooks/hooks/post_tool_use.py
- .claude/hooks/hooks/user_prompt_submit.py
- .claude/haios/lib/cycle_state.py
acceptance_criteria:
- PostToolUse injects phase contract after advance_cycle_phase fires
- UserPromptSubmit injects current phase contract on every prompt
- Injection reads from .claude/skills/{cycle}/phases/{phase}.md
- Graceful degradation if phase file missing (fall-permissive)
- Existing tests still pass
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 10:15:14
  exited: '2026-02-22T12:09:00.077480'
artifacts: []
cycle_docs: {}
memory_refs:
- 85815
- 72314
- 87437
- 87438
- 87439
- 87440
- 87441
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-22T12:09:00.079988'
queue_history:
- position: done
  entered: '2026-02-22T12:09:00.077480'
  exited: null
---
# WORK-188: Hook Auto-Injection for Phase Contracts

---

## Context

ADR-048 specifies dual hook-based auto-injection for phase contracts: PostToolUse injects on phase transition, UserPromptSubmit injects on every prompt as fallback. This work item implements both injection points.

Depends on WORK-187 (phase files must exist before hooks can inject them).

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

- [x] PostToolUse extension: inject phase contract after advance_cycle_phase
- [x] UserPromptSubmit extension: inject current phase contract on every prompt
- [x] Phase contract reader function in lib/ (shared by both hooks)
- [x] Tests for injection logic (8 tests, all green)
- [x] All existing tests pass (1597 passed, 0 failed)

---

## History

### 2026-02-22 - Created (Session 420)
- Spawned from WORK-163 (Progressive Contracts design)
- ADR-048 specifies dual hook injection (belt and suspenders)
- Dependency: WORK-187 (phase files must exist) — completed S421, dependency resolved

---

## References

- @docs/ADR/ADR-048-progressive-contracts-phase-per-file-skill-fracturing.md
- @docs/work/active/WORK-163/WORK.md
- @docs/work/active/WORK-187/WORK.md
- Memory: 85815 (context-switching token cost)
