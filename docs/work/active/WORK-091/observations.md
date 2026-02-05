---
template: observations
work_id: WORK-091
captured_session: '316'
generated: '2026-02-05'
last_updated: '2026-02-05T20:32:46'
---
# Observations: WORK-091

## What surprised you?

Both WORK-091 and WORK-092 had `blocked_by: WORK-088` in their frontmatter, but WORK-088 was already `status: complete` (closed 2026-02-04). The queue engine still showed them as blocked. This reveals that the queue does not dynamically resolve `blocked_by` against actual work item status - it relies on the static frontmatter field. A queue refresh mechanism or dynamic blocker resolution would prevent items from appearing stuck when their blockers are already done. The implementation itself was straightforward because the reference pattern from investigation/design/implementation templates was clean and consistent - the fracturing pattern proved highly replicable.

## What's missing?

The `activity_matrix.yaml` (lines 179-241) has no phase-to-state mappings for `validation-cycle` or `triage-cycle`. It only covers implementation-cycle, investigation-cycle, close-work-cycle, observation-triage-cycle, work-creation-cycle, plan-authoring-cycle, checkpoint-cycle, survey-cycle, ground-cycle, and plan-validation-cycle. When validation and triage cycles are implemented as skills, corresponding `phase_to_state` entries will be needed (e.g., `validation-cycle/VERIFY: CHECK`, `triage-cycle/SCAN: EXPLORE`). Also, WORK-092 had no formal plan - the WORK.md deliverables and WORK-091's plan pattern were sufficient for a small CREATE_NEW item, but the governance gap is noted.

## What should we remember?

Template fracturing is now complete across all 5 lifecycles (investigation, design, implementation, validation, triage). The state mapping convention was an operator decision from Session 313: validation phases all map to CHECK (validation is fundamentally a checking activity); triage phases distribute across EXPLORE (SCAN/ASSESS for gathering), DESIGN (RANK for deciding), DONE (COMMIT for acting). The test pattern in `tests/test_validation_templates.py` covers both WORK-091 and WORK-092 in one file with parametrized tests - this is efficient for related template sets and should be reused for similar batch template work. Writing both work items' tests together in one file (with clear section comments) reduced overhead without sacrificing clarity.

## What drift did you notice?

WORK-091 frontmatter had `current_node: backlog` and `queue_position: backlog` despite being actively worked in this session. The close-work-cycle should update these to reflect the actual state transition. Also, the WORK-091 deliverables specify "Unit test: load validation/JUDGE.md contains only JUDGE phase" as a single test, but the actual implementation uses parametrized tests across all phases (which is better coverage). Minor positive spec-to-implementation drift. The `scaffold-observations` command still generates `captured_session: '247'` (stale SESSION variable from governance-events.jsonl) instead of the actual current session number - same drift warning flagged during coldstart.
