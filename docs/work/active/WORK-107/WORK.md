---
template: work_item
id: WORK-107
title: Implement Complete Without Spawn (CH-008)
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-08
spawned_by: null
chapter: CH-008
arc: queue
closed: '2026-02-08'
priority: high
effort: small
traces_to:
- REQ-QUEUE-002
requirement_refs: []
source_files:
- .claude/haios/epochs/E2_5/arcs/queue/CH-008-CompleteWithoutSpawn.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- AC1: close-work-cycle accepts spawn_next=None without warnings
- AC2: WORK.md template supports null spawn_next field
- AC3: No governance rules block no-spawn closure
- AC4: Unit tests verify close-without-spawn succeeds
- AC5: Integration test - close work item with no spawn produces status complete +
    queue_position done
blocked_by: []
blocks: []
enables:
- CH-009
queue_position: done
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-08 22:57:40
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84094
- 84095
- 84096
- 84100
- 84101
extensions: {}
version: '2.0'
generated: 2026-02-08
last_updated: '2026-02-08T23:12:06.320297'
---
# WORK-107: Implement Complete Without Spawn (CH-008)

---

## Context

close-work-cycle currently has a "no spawn" path via `await_operator`, but it's a fallback when no unblocked work exists — not an explicit user choice. Per REQ-QUEUE-002, "Complete without spawn" must be a valid terminal state: a deliberate option, not a side-effect.

**What exists:** `await_operator` path in CHAIN phase when `next_work_id` is None.
**What's missing:** Explicit "Store output, no spawn" choice in close-work-cycle UX; no warnings on null spawn_next; governance acceptance of no-spawn closure.

**Source:** CH-008-CompleteWithoutSpawn spec (queue arc, E2.5).

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

- [ ] close-work-cycle SKILL.md updated: explicit "Store output, no spawn" option in CHAIN phase prompt
- [ ] close-work-cycle accepts spawn_next=None without warnings or blocks
- [ ] WorkEngine.close_work() (or equivalent) sets status=complete + queue_position=done when spawn_next is null
- [ ] No governance hooks warn or block on empty spawn_next
- [ ] Unit tests: close without spawn returns success
- [ ] Integration test: work item closes with null spawn_next, verified complete + done state

---

## History

### 2026-02-08 - Created (Session 324)
- Scaffolded from CH-008-CompleteWithoutSpawn spec
- Populated via work-creation-cycle

---

## References

- @.claude/haios/epochs/E2_5/arcs/queue/CH-008-CompleteWithoutSpawn.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-002)
- @.claude/skills/close-work-cycle/SKILL.md
- @docs/work/active/WORK-106/WORK.md (design alignment review - confirmed CH-008 aligned)
