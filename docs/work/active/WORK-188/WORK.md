---
template: work_item
id: WORK-188
title: "Hook Auto-Injection for Phase Contracts"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-163
spawned_children: []
chapter: CH-062
arc: query
closed: null
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
- "PostToolUse injects phase contract after advance_cycle_phase fires"
- "UserPromptSubmit injects current phase contract on every prompt"
- "Injection reads from .claude/skills/{cycle}/phases/{phase}.md"
- "Graceful degradation if phase file missing (fall-permissive)"
- "Existing tests still pass"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T10:15:14
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 85815
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T10:15:14
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

- [ ] PostToolUse extension: inject phase contract after advance_cycle_phase
- [ ] UserPromptSubmit extension: inject current phase contract on every prompt
- [ ] Phase contract reader function in lib/ (shared by both hooks)
- [ ] Tests for injection logic
- [ ] All existing tests pass

---

## History

### 2026-02-22 - Created (Session 420)
- Spawned from WORK-163 (Progressive Contracts design)
- ADR-048 specifies dual hook injection (belt and suspenders)

---

## References

- @docs/ADR/ADR-048-progressive-contracts-phase-per-file-skill-fracturing.md
- @docs/work/active/WORK-163/WORK.md
- @docs/work/active/WORK-187/WORK.md
- Memory: 85815 (context-switching token cost)
