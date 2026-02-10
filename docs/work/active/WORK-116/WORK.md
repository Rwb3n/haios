---
template: work_item
id: WORK-116
title: Adopt ceremony_context() in Ceremony Skills (CH-012)
type: implementation
status: active
owner: Hephaestus
created: 2026-02-10
spawned_by: WORK-115
chapter: CH-012
arc: ceremonies
closed: null
priority: medium
effort: medium
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/modules/governance_layer.py
- .claude/skills/close-work-cycle/SKILL.md
- .claude/skills/queue-intake/SKILL.md
- .claude/skills/session-start-ceremony/SKILL.md
- .claude/skills/spawn-work-ceremony/SKILL.md
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: working
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-10 20:51:26
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-10
last_updated: '2026-02-10T20:55:41.193639'
---
# WORK-116: Adopt ceremony_context() in Ceremony Skills (CH-012)

---

## Context

WORK-115 implemented `ceremony_context()` infrastructure in governance_layer.py: context manager, `check_ceremony_required()` guards on 5 WorkEngine methods (create_work, transition, close, archive, set_queue_position), and the `ceremony_context_enforcement` toggle. However, no ceremony skills actually invoke `ceremony_context()` yet. Without adoption, warn-mode enforcement is a no-op — all state changes trigger warnings because they occur outside ceremony boundaries, producing identical noise for every operation.

This work item wires `ceremony_context()` into ceremony skills that perform state changes, making the enforcement meaningful. When a skill wraps its state-changing operations in `ceremony_context("skill-name")`, the guards see an active context and stay silent. Only truly ungoverned mutations trigger warnings/blocks.

**Naming drift:** CH-012 spec references `update_work()` but WorkEngine has no such method. Actual guarded methods: `create_work()`, `transition()`, `close()`, `archive()`, `set_queue_position()`. Spec should be updated to match.

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

- [ ] Identify all ceremony skills that perform state-changing operations (WorkEngine calls or `just` commands that mutate work state)
- [ ] Add `ceremony_context()` wrapping to queue ceremony Python module: `queue_ceremonies.execute_queue_transition()` — covers queue-intake, queue-prioritize, queue-commit, queue-unpark
- [ ] Add `ceremony_context()` wrapping to closure ceremony Python path: `cli.py cmd_close()`, `cmd_archive()`, `cmd_transition()` — covers close-work-cycle (close-chapter/arc/epoch use same cli.py path)
- [ ] Verify session ceremony skills (session-start, session-end, checkpoint) — N/A if they don't call guarded WorkEngine methods
- [ ] Verify memory ceremony skills (observation-capture, observation-triage, memory-commit) — N/A if they don't call guarded WorkEngine methods
- [ ] Verify spawn-work-ceremony — N/A if it uses scaffold_template() (not WorkEngine.create_work())
- [ ] Update CH-012 spec to fix naming drift: replace `update_work()` references with actual WorkEngine API methods
- [ ] Tests: verify ceremony operations produce CeremonyStart/CeremonyEnd events in governance-events.jsonl
- [ ] Tests: verify warn-mode is silent when state changes occur inside ceremony_context()

---

## History

### 2026-02-10 - Created (Session 337)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-012-SideEffectBoundaries.md
- @docs/work/active/WORK-115/WORK.md (infrastructure — ceremony_context() implementation)
- @.claude/haios/modules/governance_layer.py (ceremony_context, check_ceremony_required)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001)
