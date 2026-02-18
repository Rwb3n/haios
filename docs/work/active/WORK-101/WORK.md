---
template: work_item
id: WORK-101
title: Proportional Governance Design
type: design
status: complete
owner: Hephaestus
created: 2026-02-05
spawned_by: Session-314-review
chapter: CH-058
arc: call
closed: '2026-02-18'
priority: high
effort: medium
traces_to:
- REQ-LIFECYCLE-001
- REQ-CEREMONY-001
- REQ-LIFECYCLE-005
- REQ-CEREMONY-005
requirement_refs: []
source_files:
- .claude/haios/manifesto/L3-requirements.md
- .claude/haios/manifesto/L4/functional_requirements.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/skills/investigation-cycle/SKILL.md
- .claude/skills/retro-cycle/SKILL.md
acceptance_criteria:
- L3.20 Proportional Governance principle defined (L3.8 was placeholder, L3.8 is No
  Autonomous Irreversibility)
- REQ-LIFECYCLE-005 fast-path requirement defined
- REQ-CEREMONY-005 proportional depth requirement defined (REQ-CEREMONY-004 is Epistemic
  review)
- Close-work-cycle updated with pytest hard gate for code work items
- Complexity threshold criteria documented
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 18:52:04
  exited: '2026-02-18T23:56:02.728897'
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.8
  unparked_session: 394
  unparked_reason: E2.8 Arc 1 (call) — CH-058 ProportionalGovernanceDesign
  previously_parked_for: E2.6
  cross_cuts:
  - lifecycles
  - ceremonies
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-18T23:56:02.732892'
queue_history:
- position: done
  entered: '2026-02-18T23:56:02.728897'
  exited: null
---
# WORK-101: Proportional Governance Design

---

## Context

Session 314 review surfaced that governance overhead is uniform regardless of work complexity. A 15-minute focused investigation (WORK-098) went through the same 8-skill ceremony chain as a multi-session architecture redesign. The ceremony-to-substance ratio was too high for small work.

**Core insight:** Governance should scale with blast radius, not be uniform.

**Proposed changes (from Session 314 discussion):**

| Level | Action | What |
|-------|--------|------|
| L3 | ADD | `[L3.20] Proportional Governance` - overhead scales with risk |
| L4 | ADD | `REQ-LIFECYCLE-005` - fast-path for effort=small work items |
| L4 | ADD | `REQ-CEREMONY-005` - proportional ceremony depth |
| L4 | MODIFY | Close-work ceremony contract to include pytest hard gate |
| Memory | STORE | Inline fix threshold: < 5 lines, no architecture = fix inline |

**Fast-path examples (lightweight phases, not skipped — REQ-FLOW-001 invariant):**
- Investigation: All 4 phases execute. HYPOTHESIZE/VALIDATE lightweight: inline reasoning, no separate doc.
- Implementation: All 4 phases execute. PLAN lightweight: CycleTransition event + inline note (no separate PLAN.md).
- Close: retro(trivial via Phase 0) → VALIDATE(lightweight) → ARCHIVE → CHAIN

**Threshold criteria (proposed):** effort=small AND source_files <= 3 AND no architectural decisions

---

## Deliverables

- [ ] L3.20 Proportional Governance principle authored in L3-requirements.md
- [ ] REQ-LIFECYCLE-005 fast-path lifecycle requirement authored in functional_requirements.md
- [ ] REQ-CEREMONY-005 proportional ceremony depth requirement authored in functional_requirements.md
- [ ] Close-work-cycle SKILL.md updated with pytest hard gate for code work items
- [ ] Complexity threshold criteria defined and documented
- [ ] Assigned to CH-058 (call arc, E2.8)

---

## History

### 2026-02-17 - Unparked (Session 394)
- Unparked for E2.8 Arc 1 (call) — assigned to CH-058 ProportionalGovernanceDesign
- Priority raised to high (prerequisite for WORK-160 CeremonyAutomation)
- Arc changed from lifecycles to call

### 2026-02-05 - Created (Session 314)
- Surfaced during session review discussion with operator
- Operator directed: capture as work item, prioritize against queue

---

## References

- @.claude/haios/manifesto/L3-requirements.md
- @.claude/haios/manifesto/L4/functional_requirements.md
- @.claude/skills/close-work-cycle/SKILL.md
- @.claude/skills/investigation-cycle/SKILL.md
- @.claude/skills/retro-cycle/SKILL.md
- @.claude/haios/epochs/E2_8/EPOCH.md
