---
template: work_item
id: INV-055
title: Agent Usability Requirements Detailing
status: complete
owner: Hephaestus
created: 2026-01-03
closed: 2026-01-03
milestone: M7b-WorkInfra
priority: medium
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related:
- L3-requirements.md
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 17:22:18
  exited: null
cycle_docs: {}
memory_refs:
- 80544
- 80545
- 80546
- 80547
- 80548
- 80549
- 80550
- 80551
- 80552
- 80553
- 80554
- 80555
- 80556
- 80557
- 80558
- 80559
- 80560
- 80561
- 80562
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T17:25:54'
---
# WORK-INV-055: Agent Usability Requirements Detailing

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** L3-requirements.md now has an "Agent Usability Requirements" section (added S161), but it's a draft that flips anti-patterns into requirements without deep analysis. The section needs:
1. Validation against existing HAIOS components (do they pass the Agent UX Test?)
2. Gap analysis (which components fail which requirements?)
3. Concrete actionable items for gaps discovered
4. Integration with DoD criteria (should Agent UX Test be part of DoD?)

**Root cause:** Session 161 discussion identified that while we have anti-patterns documented, we lacked a positive statement of what agents need to succeed. The draft section inverts anti-patterns but needs detailing.

---

## Current State

Draft section added to L3-requirements.md (lines 76-113). Contains:
- Anti-Pattern Inversion table (6 rows)
- Design Principles table (6 rows)
- Agent UX Test (4 questions)

Needs investigation to validate and expand.

---

## Deliverables

- [ ] Audit existing HAIOS components against Agent UX Test
- [ ] Document gaps discovered (which components fail which tests)
- [ ] Propose integration with DoD criteria
- [ ] Expand L3 section with findings
- [ ] Create backlog items for gaps requiring implementation

---

## History

### 2026-01-03 - Created (Session 161)
- Spawned from operator question: "do we need AI-agent-as-user requirements?"
- Draft section added to L3-requirements.md
- Created INV-055 for detailing in next session

---

## References

- `.claude/haios/manifesto/L3-requirements.md` (lines 76-113)
- `.claude/config/invariants.md` (L1 anti-patterns)
- `docs/epistemic_state.md` (L2 implementation patterns)
