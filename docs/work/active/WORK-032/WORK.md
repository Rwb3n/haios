---
template: work_item
id: WORK-032
title: PlannerAgent Module Implementation
type: feature
status: complete
owner: Hephaestus
created: 2026-01-29
spawned_by: null
chapter: CH-003
arc: pipeline
closed: '2026-01-29'
priority: medium
effort: large
traces_to:
- REQ-TRACE-004
- REQ-TRACE-005
requirement_refs: []
source_files:
- .claude/haios/modules/planner_agent.py
acceptance_criteria:
- WorkPlan schema defined
- PlannerAgent class implements plan() and suggest_groupings()
- Requirements grouped by domain/strength
- Dependencies estimated from derives_from links
- CLI command works
- Tests verify planning with sample requirements
blocked_by:
- WORK-031
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-29 18:33:41
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82556
- 82557
extensions: {}
version: '2.0'
generated: 2026-01-29
last_updated: '2026-01-29T18:34:45'
---
# WORK-032: PlannerAgent Module Implementation

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** RequirementExtractor produces `RequirementSet` with structured requirements, but there's no automated path from requirements to work items. Currently, an agent must manually read requirements and create work items.

**Root cause:** No PLAN stage component exists. The pipeline gap: `INGEST (done) → PLAN (missing) → BUILD → VALIDATE`.

**Solution:** Build PlannerAgent module that:
1. Takes RequirementSet as input
2. Groups requirements by domain and strength
3. Estimates dependencies from `derives_from` links
4. Suggests work item groupings for operator approval
5. Produces WorkPlan with work items ready for WorkEngine

This completes the PLAN stage interface: `plan(requirements: RequirementSet) → WorkPlan`

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

- [ ] `.claude/haios/modules/planner_agent.py` - PlannerAgent class
- [ ] WorkPlan schema definition (dataclass)
- [ ] `plan()` method produces WorkPlan from RequirementSet
- [ ] `suggest_groupings()` method for operator review
- [ ] `estimate_dependencies()` method using derives_from links
- [ ] Grouping heuristics (by domain, strength, dependencies)
- [ ] CLI command: `plan <requirements_file>`
- [ ] CLI command: `plan --from-corpus <corpus_config>`
- [ ] Unit tests: `tests/test_planner_agent.py`
- [ ] Integration with WorkEngine for work item creation

---

## History

### 2026-01-29 - Created (Session 257)
- Initial creation from L4/E2.3 gap analysis
- Chapter CH-003 created with requirements
- Blocked by WORK-031 (CorpusLoader)
- Completes PLAN stage for Pipeline arc

---

## References

- @.claude/haios/epochs/E2_3/arcs/pipeline/CH-003-planner-agent.md (chapter definition)
- @.claude/haios/modules/requirement_extractor.py (input source)
- @.claude/haios/modules/work_engine.py (work item creation)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (stage interface)
