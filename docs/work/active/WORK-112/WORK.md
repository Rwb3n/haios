---
template: work_item
id: WORK-112
title: "Retrofit Ceremony Skills with Contracts"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-09
spawned_by: null
chapter: ceremonies/CH-011
arc: ceremonies
closed: null
priority: high
effort: medium
traces_to: [REQ-CEREMONY-002]
requirement_refs: []
source_files: []
acceptance_criteria:
  - "All 11 existing ceremony skills have YAML frontmatter contracts (category, input_contract, output_contract, side_effects)"
  - "8 missing ceremony skills have stub SKILL.md files with contracts"
  - "Ceremony registry updated to reflect 19/19 contract coverage"
blocked_by: [WORK-111]
blocks: [WORK-113]
enables: [WORK-113]
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-09T22:19:48
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: [84249]
extensions:
  epoch: E2.5
version: "2.0"
generated: 2026-02-09
last_updated: 2026-02-09T22:19:48
---
# WORK-112: Retrofit Ceremony Skills with Contracts

---

## Context

After WORK-111 defines the contract schema, this work item applies it to all 19 ceremonies. 11 ceremonies already have skill files that need frontmatter retrofit. 8 ceremonies need new stub skill files created.

**Existing skills to retrofit (11):**
- Queue: queue-intake, queue-prioritize, queue-commit, queue-unpark
- Closure: close-work-cycle, close-chapter-ceremony, close-arc-ceremony, close-epoch-ceremony
- Memory: observation-capture-cycle, observation-triage-cycle
- Session: checkpoint-cycle

**Missing skills to create stubs (8):**
- Session: session-start-ceremony, session-end-ceremony
- Memory: memory-commit-ceremony
- Spawn: spawn-work-ceremony
- Feedback: chapter-review, arc-review, epoch-review, requirements-review

**Scope:** Frontmatter edits + stub creation. No validation code. No behavior changes.

---

## Deliverables

- [ ] 11 existing ceremony skills retrofitted with YAML contract frontmatter
- [ ] 8 new ceremony skill stubs created with contracts
- [ ] Ceremony registry updated: 19/19 skills with contracts
- [ ] No behavioral regressions (existing skill content unchanged)

---

## History

### 2026-02-09 - Created (Session 332)
- Spawned from ceremonies arc survey (CH-011 decomposition)
- 2 of 3 work items for CH-011: schema → retrofit → validation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-002, ceremony definitions table)
- @docs/work/active/WORK-111/WORK.md (schema dependency)
