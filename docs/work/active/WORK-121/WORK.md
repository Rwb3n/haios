---
template: work_item
id: WORK-121
title: Enforce Critique Gate Before DO Phase
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-11
spawned_by: null
chapter: null
arc: null
closed: '2026-02-11'
priority: medium
effort: medium
traces_to:
- REQ-CRITIQUE-001
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/SKILL.md
- .claude/skills/plan-validation-cycle/SKILL.md
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-11 20:02:07
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84884
- 65046
- 84885
- 84886
- 84887
- 82309
- 84888
- 84889
- 84890
- 84891
- 84892
- 84893
- 84894
- 84895
extensions: {}
version: '2.0'
generated: 2026-02-11
last_updated: '2026-02-11T20:36:44.342523'
---
# WORK-121: Enforce Critique Gate Before DO Phase

---

## Context

The implementation-cycle skill's PLAN phase exit gate currently goes: plan complete → plan-validation-cycle → preflight-checker → DO. The critique-agent is listed in CLAUDE.md as required for pre-implementation assumption surfacing, but there is no enforcement in the implementation-cycle skill. Session 343 skipped critique entirely on WORK-120 — no issues arose, but that's survivorship bias. The critique agent should run after plan completion in a revise loop: critique → revise if needed → re-critique until clean → then validate. This ensures implicit assumptions are surfaced before committing to implementation.

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

- [ ] implementation-cycle SKILL.md PLAN phase exit gate updated: critique-agent invoked after plan complete, before plan-validation-cycle
- [ ] Critique-revise loop documented: critique → revise if flagged → re-critique → until clean → validate
- [ ] PLAN phase exit criteria checklist updated to include critique step as MUST
- [ ] plan-validation-cycle SKILL.md CRITIQUE phase removed (moved to implementation-cycle); cycle becomes CHECK → SPEC_ALIGN → VALIDATE → APPROVE
- [ ] Test verifying implementation-cycle skill references critique-agent in PLAN phase
- [ ] Test verifying plan-validation-cycle no longer has CRITIQUE phase

---

## History

### 2026-02-11 - Created (Session 343)
- Initial creation

---

## References

- @.claude/skills/implementation-cycle/SKILL.md
- @.claude/agents/critique-agent/AGENT.md
- @CLAUDE.md (critique-agent listed as required)
