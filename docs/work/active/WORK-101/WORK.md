---
template: work_item
id: WORK-101
title: Proportional Governance Design
type: design
status: blocked
owner: Hephaestus
created: 2026-02-05
spawned_by: Session-314-review
chapter: null
arc: lifecycles
closed: null
priority: medium
effort: medium
traces_to:
- REQ-LIFECYCLE-001
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/manifesto/L3/principles.md
- .claude/haios/manifesto/L4/functional_requirements.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/skills/investigation-cycle/SKILL.md
acceptance_criteria:
- L3.8 Proportional Governance principle defined
- REQ-LIFECYCLE-005 fast-path requirement defined
- REQ-CEREMONY-004 proportional depth requirement defined
- Close-work-cycle updated with pytest hard gate for code work items
- Complexity threshold criteria documented
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 18:52:04
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.6
  parked_for: E2.6
  parked_reason: New design work, not E2.5 implementation scope
  cross_cuts:
  - lifecycles
  - ceremonies
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-05T19:00:27'
---
# WORK-101: Proportional Governance Design

---

## Context

Session 314 review surfaced that governance overhead is uniform regardless of work complexity. A 15-minute focused investigation (WORK-098) went through the same 8-skill ceremony chain as a multi-session architecture redesign. The ceremony-to-substance ratio was too high for small work.

**Core insight:** Governance should scale with blast radius, not be uniform.

**Proposed changes (from Session 314 discussion):**

| Level | Action | What |
|-------|--------|------|
| L3 | ADD | `[L3.8] Proportional Governance` - overhead scales with risk |
| L4 | ADD | `REQ-LIFECYCLE-005` - fast-path for effort=small work items |
| L4 | ADD | `REQ-CEREMONY-004` - proportional ceremony depth |
| L4 | MODIFY | Close-work ceremony contract to include pytest hard gate |
| Memory | STORE | Inline fix threshold: < 5 lines, no architecture = fix inline |

**Fast-path examples:**
- Investigation: EXPLORE -> CONCLUDE (skip HYPOTHESIZE/VALIDATE when self-evident)
- Implementation: DO -> DONE (skip PLAN/CHECK when < 20 lines with existing tests)
- Close: commit directly (skip checkpoint for effort=small)

**Threshold criteria (proposed):** effort=small AND source_files <= 3 AND no architectural decisions

---

## Deliverables

- [ ] L3.8 Proportional Governance principle authored
- [ ] REQ-LIFECYCLE-005 fast-path lifecycle requirement authored
- [ ] REQ-CEREMONY-004 proportional ceremony depth requirement authored
- [ ] Close-work-cycle SKILL.md updated with pytest gate
- [ ] Complexity threshold criteria defined and documented
- [ ] Chapter added to lifecycles or ceremonies arc

---

## History

### 2026-02-05 - Created (Session 314)
- Surfaced during session review discussion with operator
- Operator directed: capture as work item, prioritize against queue

---

## References

- @.claude/haios/manifesto/L3/principles.md
- @.claude/haios/manifesto/L4/functional_requirements.md
- @.claude/skills/close-work-cycle/SKILL.md
- @.claude/skills/investigation-cycle/SKILL.md
