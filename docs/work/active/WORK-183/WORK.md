---
template: work_item
id: WORK-183
title: Fix 13 Pre-Existing Test Failures
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-21
spawned_by: WORK-181
spawned_children: []
chapter: CH-065
arc: infrastructure
closed: '2026-02-22'
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- tests/test_agent_capability_cards.py
- tests/test_ceremony_retrofit.py
- tests/test_coldstart_orchestrator.py
- tests/test_epoch_validator.py
- tests/test_hooks.py
- tests/test_lib_migration.py
- tests/test_lib_status.py
- tests/test_manifest.py
- tests/test_routing_gate.py
- tests/test_survey_cycle.py
- tests/test_template_rfc2119.py
acceptance_criteria:
- All 13 test failures fixed or retired with documented rationale
- Zero new test failures introduced
- Full test suite passes (1565+ pass, 0 fail)
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-21 23:53:40
  exited: '2026-02-22T00:42:10.435255'
artifacts: []
cycle_docs: {}
memory_refs:
- 87296
- 87297
- 87298
- 87329
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-21
last_updated: '2026-02-22T00:42:10.439331'
queue_history:
- position: done
  entered: '2026-02-22T00:42:10.435255'
  exited: null
---
# WORK-183: Fix 13 Pre-Existing Test Failures

---

## Context

WORK-181 investigation found all 13 pre-existing test failures are test drift — zero genuine regressions. Three categories:

**Category 1: Stale assertions (3 tests)** — Hardcoded counts/lists not updated after artifact changes.
- `test_agent_count`: expects 12, now 13 (S416 added design-review-validation-agent)
- `test_stub_has_stub_marker[spawn-work-ceremony]`: skill was implemented but left in STUB list
- `test_component_counts_match_file_system`: open-epoch-ceremony on disk but not in manifest

**Category 2: Deprecated functionality (6 tests)** — Tests for intentionally removed features.
- `test_posttooluse_adds_timestamp`: timestamp injection disabled S327
- `test_old_location_has_deprecation_init`: .claude/lib/ removed after migration
- `test_route_investigation_by_prefix`: INV- prefix routing removed per WORK-030
- `test_route_legacy_inv_prefix_without_type`: same as above
- `test_survey_cycle_has_pressure_annotations`: pressure annotations removed from survey-cycle
- `test_checkpoint_template_has_rfc2119_section`: template simplified to pure YAML frontmatter

**Category 3: Environment-dependent (4 tests)** — Inadequate mocking of real disk state.
- `test_breathe_markers_between_phases`: doesn't mock _check_for_orphans()
- `test_coldstart_runs_epoch_validation`: __new__ bypass + real disk interaction
- `test_discover_milestones_finds_real_milestones`: M7d-Plumbing moved to legacy archive
- `test_discover_milestones_deduplicates`: depends on M7d-Plumbing being found

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

- [x] Category 1: Update 3 stale assertions (agent count, stub list, manifest)
- [x] Category 2: Retire or update 6 deprecated-functionality tests
- [x] Category 3: Fix 4 environment-dependent tests with proper mocking
- [x] Full pytest suite passes with 0 failures (1571 passed, 0 failed, S418)

---

## History

### 2026-02-21 - Created (Session 417)
- Spawned from WORK-181 investigation findings. All 13 failures classified as test drift.

---

## References

- WORK-181: Investigation that produced these findings
- Memory: 85721 (breathe test root cause), 85369 (16 pre-existing failures), 84816 (re-triage directive)
- @tests/ (all 11 affected test files listed in source_files)
