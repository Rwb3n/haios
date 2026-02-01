---
template: observations
work_id: WORK-072
captured_session: '280'
generated: '2026-02-01'
last_updated: '2026-02-01T23:54:05'
---
# Observations: WORK-072

## What surprised you?

The scale of work item orphaning - 71% (96/135) of active work items have no chapter assignment. This violates REQ-TRACE-005 (traceability chain) but the system has been operating for 280 sessions despite this. The governance hooks don't enforce chapter assignment, only block scaffold without /new-work. This reveals a gap: chapter assignment is a SHOULD requirement but no enforcement exists.

The ActivityMatrix is more comprehensive than documented in the epoch file - 76 rules across 21 primitives, not the smaller set implied by arc documentation. The matrix is functional and actively enforcing DO phase black-box constraints (I observed the [STATE: EXPLORE] blocking messages throughout this session).

## What's missing?

**Chapter Assignment Enforcement:** There's no hook or validation that prevents creating work items without chapter assignment. The `chapter: null` pattern is valid YAML but violates traceability principles. A soft gate (warn) in work-creation-cycle would catch this.

**Orphan Remediation Tool:** With 96 orphans, we need a bulk assignment mechanism. Something like `just assign-chapter WORK-XXX arc/CH-YYY` or a triage workflow for orphan assignment.

**Test-to-Documentation Sync:** 14 tests are failing because documentation drifted from implementation. No mechanism alerts when tests expect patterns that have evolved. The test files themselves could reference the documents they're testing.

## What should we remember?

**Investigation-as-Audit Pattern:** This audit demonstrated that investigations are effective for system-wide state capture. The EXPLORE phase naturally gathers evidence across many files. The resulting SYSTEM-AUDIT.md is both a deliverable and a reference document. Consider formalizing "system audit" as a work type.

**Memory Statistics Command:** `memory_stats` MCP tool provides quick health check without writing SQL. 82,860 concepts with 96.8% embedding coverage indicates healthy memory state. This should be part of coldstart or /status output.

**95% Backlog Node Problem:** The WORK-065 finding about current_node conflating queue and cycle is real and measured. Almost all items are stuck at backlog. The queue_position field (WORK-066) is critical to unblock this.

## What drift did you notice?

**Test Expectations vs Reality:** 14 tests fail because:
- `test_checkpoint_cycle_verify.py` expects VERIFY phase documentation that doesn't exist in current skill
- `test_routing_gate.py` expects INV- prefix routing but WORK-030 made type field authoritative
- `test_survey_cycle.py` expects pressure annotations that were removed

**Skill Categorization:** README says "10 cycle skills + 4 bridge skills" but actual count is "12 cycle skills + 2 bridge skills". Plan-validation and DoD-validation are cycle skills with phases, not bridges.

**Epoch Exit Criteria:** EPOCH.md says "DO phase enforces black-box constraints" but this is already implemented via ActivityMatrix. The exit criterion should be checked off, but the checkbox format doesn't match (it's `- [ ]` not a reference to evidence).
