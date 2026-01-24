---
template: work_item
id: WORK-011
title: Coldstart Orchestrator - Wire Loaders into Unified Coldstart
type: feature
status: complete
owner: Hephaestus
created: 2026-01-24
spawned_by: null
chapter: CH-007
arc: configuration
closed: '2026-01-24'
priority: medium
effort: medium
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-24 20:19:51
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82334
- 82335
- 82336
- 82337
- 82338
- 82339
extensions: {}
version: '2.0'
generated: 2026-01-24
last_updated: '2026-01-24T20:55:15'
---
# WORK-011: Coldstart Orchestrator - Wire Loaders into Unified Coldstart

@docs/README.md
@docs/epistemic_state.md

---

## Context

Coldstart currently requires the agent to make 15+ Read tool calls following a markdown procedure. Three loaders now exist (IdentityLoader, SessionLoader, WorkLoader) but they are invoked separately via different recipes (`just coldstart` for identity, `just session-context` for session, `just work-options` for work).

**Problem:** No unified orchestrator wires these loaders together with breathing room between phases.

**Root Cause:** CH-004, CH-005, CH-006 built individual loaders. CH-007 is the integration chapter that composes them.

**Goal:** Single `just coldstart` invocation that:
1. Runs all three loaders in sequence
2. Injects `[BREATHE]` markers between phases
3. Outputs formatted context for agent consumption
4. Eliminates need for manual Read tool calls during coldstart

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

- [x] `config/coldstart.yaml` - Phase orchestration config defining loader sequence
- [x] `ColdstartOrchestrator` class in `.claude/haios/lib/coldstart_orchestrator.py`
- [x] Updated `just coldstart` recipe to use orchestrator (added `coldstart-orchestrator` recipe)
- [x] `[BREATHE]` markers between phases in output
- [x] Content parity verification (same information as current multi-step coldstart)
- [x] Tests for orchestrator in `tests/test_coldstart_orchestrator.py` (7 tests)
- [x] Updated `/coldstart` skill to invoke single recipe (no manual Read calls)

---

## History

### 2026-01-24 - Implemented (Session 233)
- ColdstartOrchestrator implemented with TDD (7 tests)
- coldstart.yaml config created
- cli.py cmd_coldstart() added
- justfile coldstart-orchestrator recipe added
- /coldstart skill updated to use orchestrator
- READMEs updated (lib, config)
- Memory refs: 82334, 82335, 82336, 82337

### 2026-01-24 - Created (Session 232)
- Initial creation
- Plan authored and approved

---

## References

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-007-coldstart-orchestrator.md
- @.claude/haios/epochs/E2_3/arcs/configuration/ARC.md
- @.claude/haios/lib/identity_loader.py
- @.claude/haios/lib/session_loader.py
- @.claude/haios/lib/work_loader.py
