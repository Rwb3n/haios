---
template: work_item
id: E2-086
title: Template RFC 2119 Normalization
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: medium
category: implementation
spawned_by: Session 64 observation
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-23 19:06:12
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-28T21:51:07'
---
# WORK-E2-086: Template RFC 2119 Normalization

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Templates should guide agents with explicit RFC 2119 governance signals. Currently templates have placeholders but lack MUST/SHOULD/MAY guidance sections.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

Add RFC 2119 governance sections to all document templates. Each template should have appropriate MUST/SHOULD/MAY guidance for agents creating documents.

### Template Updates

- [ ] `.claude/templates/checkpoint.md` - Add "Session Hygiene" section with SHOULD items (e.g., SHOULD review unblocked plans, SHOULD capture observations)
- [ ] `.claude/templates/implementation_plan.md` - Add "Pre-Implementation Checklist" section with MUST items (e.g., MUST have tests before code)
- [ ] `.claude/templates/investigation.md` - Add "Discovery Protocol" section with SHOULD items (e.g., SHOULD query memory first)
- [ ] `.claude/templates/report.md` - Add "Verification Requirements" section with MUST items (e.g., MUST include evidence)
- [ ] `.claude/templates/architecture_decision_record.md` - Add "Decision Criteria" section with MUST items (e.g., MUST document alternatives considered)

### Verification

- [ ] All 5 templates updated with RFC 2119 sections
- [ ] Sections use correct keywords (MUST/SHOULD/MAY per RFC 2119)
- [ ] Template validation (just validate) passes for each template

---

## History

### 2025-12-28 - Populated (Session 141)
- Cleaned up corrupted deliverables (copy-paste contamination from ~90 other items)
- Defined clear scope: 5 template updates with RFC 2119 sections
- Ready for implementation

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- ADR-035: RFC 2119 Governance Signaling
- E2-037: RFC 2119 Governance Signaling System (completed, provides pattern)
- CLAUDE.md: RFC 2119 Keywords section (reference for MUST/SHOULD/MAY usage)
