---
template: work_item
id: CH-005
title: Session Loader - Build session context loader for coldstart Phase 2
type: feature
status: complete
owner: Hephaestus
created: 2026-01-24
spawned_by: null
chapter: CH-005
arc: configuration
closed: '2026-01-24'
priority: medium
effort: medium
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by:
- WORK-008
- WORK-009
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-24 18:24:50
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82322
- 82323
- 82324
- 82325
- 82326
- 82327
extensions: {}
version: '2.0'
generated: 2026-01-24
last_updated: '2026-01-24T19:08:56'
---
# CH-005: Session Loader - Build session context loader for coldstart Phase 2

@docs/README.md
@docs/epistemic_state.md

---

## Context

Agent manually reads checkpoint, parses frontmatter, queries memory IDs individually during coldstart. This is a 6-step fragile process:

1. Find latest checkpoint (ls + sort)
2. Read checkpoint file
3. Parse frontmatter for load_memory_refs
4. For each ID, query memory
5. Parse frontmatter for drift_observed
6. Parse frontmatter for pending

**Agent Need:** "What happened last session? What should I know? What's drifting?"

**Root Cause:** No SessionLoader exists. IdentityLoader (WORK-008/009) established the pattern; now apply it to session context.

**Source:** CH-005-session-loader.md (Configuration arc)

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

- [x] **R1: session.yaml config** - `config/loaders/session.yaml` with extraction rules for checkpoint frontmatter
- [x] **R2: SessionLoader class** - `.claude/haios/lib/session_loader.py` following IdentityLoader pattern
- [x] **R3: Memory integration** - Loader queries memory_refs IDs and formats inline (not file references)
- [x] **R4: Drift prominence** - Drift warnings appear clearly in output (agent cannot miss them)
- [x] **R5: just session-context recipe** - Single command outputs formatted session context
- [x] **R6: Coldstart Phase 2 wiring** - coldstart.md uses `just session-context` for Phase 2
- [x] **Tests** - Unit tests for SessionLoader (test_session_loader.py)

---

## History

### 2026-01-24 - Created (Session 229)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-005-session-loader.md (chapter spec)
- @.claude/haios/epochs/E2_3/arcs/configuration/ARC.md (arc definition)
- @.claude/haios/modules/context_loader.py (IdentityLoader pattern)
- @.claude/haios/config/loaders/identity.yaml (config pattern)
- @docs/work/active/WORK-008/WORK.md (ContextLoader Identity Integration - prior work)
- @docs/work/active/WORK-009/WORK.md (Coldstart Orchestrator - prior work)
