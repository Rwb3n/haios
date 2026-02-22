---
template: work_item
id: WORK-184
title: "Parallel Hypothesis Validation in Investigation Cycle"
type: investigation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: null
spawned_children: []
chapter: null
arc: call
closed: null
priority: low
effort: medium
traces_to:
  - REQ-LIFECYCLE-005
requirement_refs: []
source_files:
  - .claude/skills/investigation-cycle/SKILL.md
acceptance_criteria:
  - "Design for parallel VALIDATE phase documented"
  - "Threshold predicate defined (when to parallelize vs sequential)"
  - "Input/output contract for hypothesis-validator subagent specified"
  - "Spawned implementation work item if design is viable"
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-22T00:04:39
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T00:04:39
---
# WORK-184: Parallel Hypothesis Validation in Investigation Cycle

---

## Context

Investigation-cycle VALIDATE phase runs hypotheses sequentially. When 3+ independent hypotheses exist, each requiring separate evidence review, parallel validation could reduce wall-clock time and token waste from sequential context carrying.

**Pattern (from WORK-181 S417 discussion with operator):**
1. EXPLORE — single agent, unrestricted (unchanged)
2. HYPOTHESIZE — single agent, forms N hypotheses from evidence (unchanged)
3. **VALIDATE in parallel** — spawn N subagents, one per hypothesis, each with evidence corpus and assigned hypothesis. Render verdict independently.
4. CONCLUDE — single agent, synthesizes all verdicts (unchanged)

**Key design questions:**
- Threshold predicate: when is parallel worthwhile? (3+ hypotheses? evidence corpus size?)
- Subagent model: haiku (structural verdict) or sonnet (judgment required)?
- Evidence passing: full corpus to each agent, or hypothesis-scoped subset?
- Failure mode: if one validator fails, do others still complete?

**Prior art:** WORK-176 (plan-authoring delegation), WORK-178 (CHECK phase delegation), WORK-181 (investigation that surfaced this pattern). E2.8 theme: "agents spend tokens on work, not bookkeeping."

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

- [ ] Design document with parallel VALIDATE architecture
- [ ] Threshold predicate (computable: when to parallelize)
- [ ] hypothesis-validator subagent input/output contract
- [ ] Spawned implementation work (if viable)

---

## History

### 2026-02-22 - Created (Session 417)
- Operator-initiated during WORK-181 closure discussion. Parallel hypothesis validation pattern identified as E2.8 scope (agent UX, subagent delegation).
- Parked — lower priority than WORK-183 (test fixes).

---

## References

- WORK-181: Investigation that surfaced this pattern (S417)
- WORK-176: Plan-authoring delegation (prior art)
- WORK-178: CHECK phase delegation (prior art)
- .claude/skills/investigation-cycle/SKILL.md (VALIDATE phase spec)
- Memory: 87259 (WORK-181 findings), 85109 (EXPLORE-FIRST validation)
