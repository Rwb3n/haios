---
template: work_item
id: WORK-143
title: "Retro-Triage Consumer Update for Memory-Based Provenance Tags"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-12
spawned_by: WORK-142
spawned_children: []
chapter: null
arc: null
closed: null
priority: high
effort: medium
traces_to: [REQ-CEREMONY-002, REQ-FEEDBACK-001]
requirement_refs: []  # DEPRECATED: use traces_to instead
source_files:
  - .claude/skills/observation-triage-cycle/SKILL.md
acceptance_criteria:
  - observation-triage-cycle updated to query memory by retro provenance tags
  - Triage can consume retro-reflect, retro-kss, retro-extract provenance entries
  - Frequency aggregation across K/S/S directives surfaces patterns
  - Bug candidates with confidence tags surfaced for operator disposition
  - Feature candidates with confidence tags surfaced for epoch-level triage
blocked_by: [WORK-142]
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-12T23:34:51
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-12
last_updated: 2026-02-12T23:34:51
---
# WORK-143: Retro-Triage Consumer Update for Memory-Based Provenance Tags

---

## Context

### Problem

WORK-142 (retro-cycle) stores typed outputs to memory with provenance tags (retro-reflect, retro-kss, retro-extract). The existing observation-triage-cycle scans for archived work items with `triage_status: pending` in file frontmatter. It has no awareness of memory-based provenance tags. Without updating the triage consumer, retro outputs are write-only memory — accumulating signal with no mechanism to act on it.

This is the same consumer-update pattern from CH-006 (template fracturing broke 8+ consumers, memory 83973/83974). Identified as blocking assumption A6 in WORK-142 critique round 2.

### Scope

Update observation-triage-cycle (or create a new retro-triage-cycle) to:
1. Query memory by retro provenance tags instead of scanning file frontmatter
2. Aggregate K/S/S directives across work items (frequency = pattern signal)
3. Surface bug candidates with confidence tags for operator disposition
4. Surface feature candidates for epoch-level triage (batch scope triage ceremony)

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

- [ ] Triage skill updated/created to query memory by retro-* provenance tags
- [ ] K/S/S frequency aggregation: count independent convergent directives, rank by frequency
- [ ] Bug candidate surfacing: query retro-extract entries, filter type=bug, present with confidence
- [ ] Feature candidate surfacing: query retro-extract entries, filter type=feature, present for epoch triage
- [ ] Integration test: retro-cycle outputs are consumable by triage ceremony

---

## History

### 2026-02-12 - Created (Session 359)
- Spawned from WORK-142 as companion work item
- Identified as blocking assumption A6 in critique round 2: triage consumer doesn't exist for new memory-based format
- CH-006 consumer-update pattern applies (memory 83973/83974)

---

## References

- WORK-142 (parent: retro-cycle design and implementation)
- .claude/skills/observation-triage-cycle/SKILL.md (current triage consumer)
- obs-314-operator-initiated-system-evolution.md (batch scope triage gap)
- REQ-CEREMONY-002 (explicit input/output contract per ceremony)
- REQ-FEEDBACK-001 (work completion triggers review)
