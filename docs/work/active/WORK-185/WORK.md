---
template: work_item
id: WORK-185
title: External Audit Remediation Batch
type: implementation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: null
spawned_children: []
chapter: null
arc: infrastructure
closed: null
priority: low
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- haios_etl/quality.py
- haios_etl/health_checks.py
- haios_etl/job_registry.py
acceptance_criteria:
- Orphaned ETL modules removed or deprecated with explanation
- Usage tracking mechanism designed (hook-based skill/agent invocation logging)
- Similarity threshold in retrieval.py investigated and documented
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 09:17:54
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 87330
- 87331
- 87332
- 87333
- 87334
- 87335
- 87336
- 87337
- 87338
- 87339
- 87340
- 87341
- 87342
extensions: {}
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-22T09:20:00.396689'
queue_history:
- position: parked
  entered: '2026-02-22T09:20:00.394163'
  exited: null
---
# WORK-185: External Audit Remediation Batch

---

## Context

External auditor (S419) reviewed the full HAIOS architecture and identified several legitimate gaps alongside misreadings. This work item captures the actionable remediation items:

1. **Orphaned ETL modules**: quality.py, health_checks.py, job_registry.py are dead code from pre-E2.5 ETL design. No runtime imports, only test suite references marked deprecated.
2. **No usage tracking**: Skills, agents, and hooks have zero invocation evidence trail. The auditor misclassified all ceremony/queue/cycle skills as "Orphaned" because there's no usage data to verify they're active. A PostToolUse hook logging invocations would prevent future misreadings and provide operational metrics.
3. **Similarity threshold investigation**: Auditor flagged hardcoded 0.8 similarity cutoff in retrieval.py. Needs verification — may be accurate for ETL retrieval layer even though memory_search_with_experience uses dynamic modes.

Memory refs: 87330-87342 (audit ingestion S419)

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

- [ ] Remove or deprecate orphaned ETL modules (quality.py, health_checks.py, job_registry.py)
- [ ] Design usage tracking mechanism (PostToolUse hook for skill/agent invocation logging)
- [ ] Investigate and document similarity threshold in retrieval.py (hardcoded 0.8 vs dynamic)

---

## History

### 2026-02-22 - Created (Session 419)
- Initial creation

---

## References

- docs/architecture_diagrams/architectural_gaps_analysis.md
- docs/architecture_diagrams/orphan_analysis.md
- docs/architecture_diagrams/remediation_roadmap.md
- docs/architecture_diagrams/system_inventory.md
