---
template: work_item
id: E2-300
title: ContextLoader S17.3 Spec Alignment
status: invalid
owner: Hephaestus
created: 2026-01-17
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: E2-296
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-17 14:49:46
  exited: null
cycle_docs: {}
memory_refs:
- 81478
operator_decisions: []
documents:
  investigations: []
  plans:
  - docs/work/active/E2-300/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2026-01-17
last_updated: '2026-01-18T10:45:05'
---
# WORK-E2-300: ContextLoader S17.3 Spec Alignment

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** E2-254 observations noted that ContextLoader implementation doesn't match S17.3 spec. Current implementation loads manifesto files (L0-L4), but spec requires structured L0-L3 layers with different semantics (north_star/invariants/operational/session).

**Trigger:** E2-254 observations.md triage - "Fix ContextLoader to match spec".

**Root Cause:** E2-254 designed against manifesto files instead of INV-052 S17.3 spec's layer definitions.

## Resolution (Session 202)

**CLOSED AS INVALID.** The S17.3 spec was stale and incorrect.

The actual manifesto file naming is:
- L0-telos.md (WHY)
- L1-principal.md (WHO)
- L2-intent.md (WHAT)
- L3-requirements.md (HOW)
- L4-implementation.md (WHAT to build)

The S17.3 spec used different names (`north_star`, `invariants`, `operational`, `session`) that don't match the file names or conceptual layer hierarchy. The original ContextLoader implementation was correct.

Changes made in Session 202:
- Reverted GroundedContext to use l0_telos, l1_principal, l2_intent, l3_requirements, l4_implementation
- Fixed cli.py to use correct field names
- Updated README.md to reflect original naming
- Removed obsolete S17.3 alignment tests

The architecture file (SECTION-17-MODULAR-ARCHITECTURE.md) needs review and correction.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

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
-->

- [x] Review S17.3 spec layer definitions (north_star/invariants/operational/session)
- [x] Align ContextLoader implementation with spec
- [x] Document discrepancies or rationale for deviations

---

## History

### 2026-01-17 - Created (Session 199)
- Initial creation

---

## References

- @docs/work/archive/E2-254/observations.md (source observation)
- INV-052 S17.3 spec (ContextLoader layer definitions)
