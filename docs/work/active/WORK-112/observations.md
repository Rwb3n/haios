---
template: observations
work_id: 'WORK-112'
captured_session: '334'
generated: '2026-02-09'
last_updated: '2026-02-09T23:47:11'
---
# Observations: WORK-112

## What surprised you?

The retrofit of all 19 ceremony skills was completed in a single session (S333), covering 11 existing skill retrofits and 8 new stub creations. The work was largely mechanical (YAML frontmatter addition), but the critique agent surfaced 10 assumptions - 3 addressed in-session (A7: `stub: true` marker to prevent agents treating stubs as functional, A1: registry cross-validation test ensuring declared count matches actual skill files, A8: git diff body preservation check). The remaining 7 were triaged into deferred (A5/A6/A10 forwarded to WORK-113 acceptance criteria) vs accepted risk. This demonstrates the critique agent delivers genuine value even on "mechanical" tasks by catching structural gaps that would otherwise compound.

## What's missing?

No automated validation exists yet for ceremony contracts - they are documentation-only until WORK-113 implements `validate_ceremony_input()` and `validate_ceremony_output()` in `lib/ceremony_contracts.py`. The 8 stub skills have `stub: true` frontmatter but no behavioral implementation. The gap between "all 19 have contracts" and "contracts are enforced" is exactly WORK-113's scope. Additionally, there is no tooling to detect when a ceremony skill's actual behavior drifts from its declared contract - this would require runtime introspection beyond static validation.

## What should we remember?

- **`stub: true` pattern (memory 84288):** Any skill that describes future behavior MUST have `stub: true` in its frontmatter. This prevents agents from executing aspirational workflow steps as if they were functional. Applied to all 8 new ceremony stubs in this work item. Should become a standard practice for any scaffolded-but-not-yet-implemented skill.
- **Critique deferred-items pattern:** When the critique agent surfaces assumptions, address what you can in-session and explicitly defer the rest by writing them into the next work item's acceptance criteria. WORK-112 addressed A7/A1/A8 in-session, deferred A5 (OutputField.guaranteed validation), A6 (ContractField.type vocabulary validation), and A10 (registry self-verification) to WORK-113. This avoids scope creep while maintaining full traceability from critique to resolution.
- **Registry as single source of truth:** `ceremony_registry.yaml` now declares all 19 ceremonies with `has_contract: true` and `has_skill: true`. The cross-validation test (`test_ceremony_contracts.py`) ensures the registry count matches actual skill file count. This pattern of "registry + cross-validation test" is reusable for any enumerable system component.

## What drift did you notice?

WORK-112 was completed functionally in S333 (all tests passing, all deliverables checked) but was never formally closed via `/close`. The session worked outside the governance cycle entirely - the coldstart drift warning confirms "no /coldstart or /implement invoked" in S333. This is the recurring pattern of "work gets done but ceremony doesn't happen," which is precisely the problem the ceremonies arc (and this work item's contract system) is designed to solve. The irony of a ceremony-contract work item skipping its own closure ceremony highlights the gap between having ceremonies defined and having them enforced - exactly WORK-113's mission.
