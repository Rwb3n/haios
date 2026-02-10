---
template: observations
work_id: 'WORK-113'
captured_session: '334'
generated: '2026-02-10'
last_updated: '2026-02-10T00:10:10'
---
# Observations: WORK-113

## What surprised you?

The critique agent caught a genuine scope gap (A5: governance gate) that the preflight checker missed entirely. The preflight checker said "READY FOR IMPLEMENTATION" with all checks passed, but the critique agent identified that the WORK.md acceptance criterion "Governance gate blocks ceremony start if input contract fails" was NOT addressed by the plan - the plan delivered validation functions and a toggle but no actual gate function that calls them. This validated the plan-validation-cycle's CRITIQUE phase as a MUST gate, not optional. The plan was revised to add `enforce_ceremony_contract()` before any code was written, catching the gap at design time rather than during CHECK phase verification. This is a concrete example of the critique agent preventing a "deliverable gap" - code that works but doesn't satisfy the acceptance criteria.

## What's missing?

No runtime caller of `enforce_ceremony_contract()` exists yet. The function is tested and works (Tests 13-15), but no ceremony skill or hook actually invokes it during execution. The governance toggle `ceremony_contract_enforcement: warn` in `haios.yaml` is set but passive. This is by design (enforcement wiring is a separate concern from validation logic), but it means ceremony contracts are still not enforced at runtime - they're just enforceable. A future work item should wire `enforce_ceremony_contract()` into either a PreToolUse hook or a CeremonyRunner wrapper that reads skill frontmatter and calls the gate before executing ceremony steps.

## What should we remember?

- **Critique catches what preflight misses:** Preflight validates plan structure (sections present, no placeholders, scope reasonable). Critique validates plan semantics (does the design actually satisfy the acceptance criteria?). Both are needed and they catch different classes of errors. Demonstrated concretely in WORK-113: preflight returned PASSED, critique returned REVISE with 3 actionable items (A5 governance gate, A3 missing success warning, A8 documented coupling). The A5 item would have been caught in CHECK phase but at much higher cost (code already written, needs rework). Catching it in CRITIQUE cost zero implementation effort.
- **Vocabulary grep before `__post_init__`:** Before adding construction-time validators to dataclasses (`ContractField.__post_init__`, `OutputField.__post_init__`), always verify all existing instantiations use valid values. We ran a Python script grepping all 19 SKILL.md files for `type:` and `guaranteed:` values and confirmed all are in the canonical vocabulary (`{string, boolean, list, path, integer}` and `{always, on_success, on_failure}`). This prevented a potential 87-test regression in `test_ceremony_retrofit.py::TestContractsParseable`.
- **A3 warning pattern for silent degradation:** When output validation has conditional semantics (`on_success`/`on_failure`), add a structural warning if the prerequisite field (`success:always`) is missing from the contract. The `validate_ceremony_output()` function now warns when a contract has conditional fields but no `success` field with `guaranteed=always`. Without this, validation silently degrades to a no-op for affected ceremonies (like `queue-intake`).

## What drift did you notice?

The agent (me) initially skipped the plan-validation-cycle MUST gate, heading straight from plan authoring to DO phase. I rationalized this as "plan was authored and validated in the same session with full context" - but the operator caught it and required correction. Running the critique phase then surfaced 3 genuine issues (A5, A3, A8) that would not have been caught otherwise. This reinforces that MUST gates in skills should not be optimized away by the agent even when the context "feels sufficient." The governance system exists precisely because agents make judgment calls about what to skip, and those judgment calls are sometimes wrong. The irony of skipping a governance gate while implementing governance enforcement is noted.
