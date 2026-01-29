---
template: work_item
id: WORK-033
title: Pipeline Orchestrator Module (CH-006)
type: implementation
status: active
owner: Hephaestus
created: 2026-01-29
spawned_by: null
chapter: CH-006
arc: pipeline
closed: null
priority: high
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-29 22:39:10
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-29
last_updated: '2026-01-29T22:40:02'
---
# WORK-033: Pipeline Orchestrator Module (CH-006)

@docs/README.md
@docs/epistemic_state.md

---

## Context

The Pipeline arc has three complete modules with no runtime consumer:
- CH-001 CorpusLoader (WORK-031) - YAML-configurable file discovery
- CH-002 RequirementExtractor (WORK-015) - Multi-parser requirement extraction
- CH-003 PlannerAgent (WORK-032) - Requirement → work item decomposition

The Orchestrator (CH-006) is the state machine that wires these stages together into a functional pipeline.

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

- [ ] `PipelineOrchestrator` class in `modules/pipeline_orchestrator.py`
- [ ] State machine with INGEST → PLAN → BUILD → VALIDATE transitions
- [ ] INGEST stage: CorpusLoader → RequirementExtractor integration
- [ ] PLAN stage: PlannerAgent integration
- [ ] CLI command: `just pipeline-run <corpus_config>`
- [ ] Tests: 8+ covering state transitions and stage execution
- [ ] Pipeline ARC.md updated with CH-006 complete

---

## History

### 2026-01-29 - Created (Session 247)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_3/arcs/pipeline/ARC.md
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md
- @.claude/haios/modules/corpus_loader.py
- @.claude/haios/modules/requirement_extractor.py
- @.claude/haios/modules/planner_agent.py
