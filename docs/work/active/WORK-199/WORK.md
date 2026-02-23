---
template: work_item
id: WORK-199
title: "Proportional Close Ceremony Investigation"
type: investigation
status: active
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-198
spawned_children: []
chapter: CH-058
arc: call
closed: null
priority: medium
effort: small
traces_to:
  - REQ-LIFECYCLE-005
  - REQ-CEREMONY-005
requirement_refs: []
source_files:
  - .claude/skills/close-work-cycle/SKILL.md
  - .claude/skills/retro-cycle/SKILL.md
acceptance_criteria:
  - "Decision documented: which close phases scale with effort tier"
  - "Lightweight close path defined for effort=small items"
  - "Full close path preserved for effort=standard+ items"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-23T10:49:50
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-23
last_updated: 2026-02-23T10:49:50
---
# WORK-199: Proportional Close Ceremony Investigation

---

## Context

The close ceremony pipeline (retro-cycle → dod-validation-cycle → close-work-cycle VALIDATE → ARCHIVE → CHAIN with checkpoint-cycle) is the same for all work items regardless of effort tier. For effort=small items like WORK-198 (1-function change, 2 new tests), the full pipeline consumed ~40% of context on ceremony vs ~10% on actual work.

Memory evidence: mem:85811 documents the delta — full pipeline ~12 ceremonies for substantial work, ~3 for small cleanup. mem:85053, mem:85394 propose lightweight close paths. REQ-LIFECYCLE-005 and REQ-CEREMONY-005 already define proportional governance tiers but close ceremony doesn't implement them yet.

**Question:** Which close phases can be scaled down or skipped for effort=small items while preserving the governance value (DoD validation, WHY capture, unblock cascade)?

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

- [ ] Decision: which close phases scale with effort tier
- [ ] Lightweight close path specification for effort=small
- [ ] Full close path preserved for effort=standard+
- [ ] Spawned implementation work item(s) if applicable

---

## History

### 2026-02-23 - Created (Session 427)
- Spawned from WORK-198 close experience — full ceremony pipeline for effort=small item
- Related prior work: mem:85811 (ceremony delta), mem:85053 (lightweight close proposal), mem:85394 (proportional governance), mem:86323 (synthesis on lightweight ceremonies)

---

## References

- @.claude/skills/close-work-cycle/SKILL.md (current close pipeline)
- @.claude/skills/retro-cycle/SKILL.md (retro pipeline)
- @docs/ADR/ADR-033.md (DoD governance)
- WORK-101 (Proportional Governance Design — closed S398)
