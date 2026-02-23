---
template: work_item
id: WORK-212
title: "Mechanical Phase Delegation to Haiku Subagents"
type: refactor
status: open
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-209
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: medium
traces_to:
  - REQ-CEREMONY-005
requirement_refs: []
source_files:
  - .claude/skills/implementation-cycle/phases/DO.md
  - .claude/skills/implementation-cycle/phases/CHECK.md
acceptance_criteria:
  - "pytest runs delegated to haiku test-runner subagent in DO and CHECK phases"
  - "Git commits delegated to haiku subagent in DONE/CHAIN phases"
  - "Grep verifications and README updates delegated to haiku subagent"
  - "Main agent context savings measurable (fewer tool calls inline)"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-23T19:08:11
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-23
last_updated: 2026-02-23T19:08:11
---
# WORK-212: Mechanical Phase Delegation to Haiku Subagents

---

## Context

S436 operator observation: pytest, git commits, grep verifications, README updates are all mechanical — they consume main agent context tokens for zero-judgment work. These should be delegated to haiku subagents (test-runner already exists but is underused). DO phase dispatches tests inline; CHECK phase runs full suite inline. Both could delegate to haiku and receive pass/fail summary. Memory: 88078.

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

- [ ] DO phase: pytest delegation to test-runner subagent (haiku)
- [ ] CHECK phase: full suite delegation to test-runner subagent
- [ ] DONE/CHAIN: git commit delegation to haiku subagent
- [ ] Updated phase contracts (DO.md, CHECK.md) reflecting delegation

---

## History

### 2026-02-23 - Created (Session 436)
- Initial creation

---

## References

- [Related documents]
