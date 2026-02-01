---
template: observations
work_id: WORK-042
captured_session: '270'
generated: '2026-02-01'
last_updated: '2026-02-01T14:59:24'
---
# Observations: WORK-042

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**Critique agent caught a real infrastructure gap.** The plan assumed `just get-cycle` existed as a command to retrieve current cycle state, but this recipe was NOT defined in the justfile. Only `set-cycle` and `clear-cycle` existed. The critique phase (plan-validation-cycle) surfaced this blocking assumption with specific evidence (grep of justfile showed no match). This validates the CRITIQUE hard gate as more than ceremony - it actually prevented an implementation failure. Without critique, the agent would have implemented code that calls a non-existent command, discovered the error during testing, and wasted a full TDD cycle. Instead, we added the recipe BEFORE writing code.

**Test mocking patterns matter.** The first attempt at tests for `get_activity_state()` used `mocker.patch("governance_layer.subprocess.run")` which failed with "governance_layer is not a package". The correct pattern is `mocker.patch.object(subprocess, "run")` after importing subprocess. This is because the module uses `import subprocess` not `from subprocess import run`. The lesson: mock at the object level for modules, not the string path.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**No `just get-cycle` existed before this work.** The infrastructure to read session state was write-only (set-cycle, clear-cycle) but not read. The PreToolUse hook integration required reading state, which forced creation of the get-cycle recipe. This pattern (write infrastructure before read infrastructure) may recur - worth checking if other state-setting recipes have corresponding getters.

**Path classification logic was scoped out.** CH-003 defines `classify_path()` for validating file writes by classification (spec, artifact, notes, etc.). This was explicitly deferred to v2 in the plan. The current implementation enforces primitive-level governance but not path-level governance within those primitives. This means `file-write` is allowed in DO but ANY path can be written, not just artifact paths.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Critique-as-hard-gate works.** This is the first real validation of E2.4's decision to make critique a hard gate. The assumption surfacing framework found a dependency assumption (A1: just get-cycle exists) that would have caused runtime failure. The pattern: critique before implementation, not after.

**Instance attribute caching is preferable to global cache.** The plan used `global _activity_matrix_cache` but implementation used `self._activity_matrix_cache` (instance attribute). This allows test isolation - each test gets a fresh GovernanceLayer instance without cross-test pollution from global state. Pattern: prefer instance attributes for caching in classes that may be instantiated in tests.

**Module-first imports from hooks.** The pattern established in E2-264 (Strangler Fig) continues to work. Hooks import from `.claude/haios/modules/` not directly from `.claude/lib/`. This keeps the dependency direction clean: hooks → modules → lib.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**CH-002 phase-to-state mapping had placeholder phases.** The plan-validation-cycle mapping in CH-002 (lines 362-366) used placeholders like `GATE1`, `GATE2`, `GATE3`, `GATE4` instead of actual phase names (CHECK, SPEC_ALIGN, CRITIQUE, VALIDATE, APPROVE). This was noted in obs-267-1.md but the activity_matrix.yaml now has the correct mapping. The CH-002 document should be updated to match.

**22 pre-existing test failures.** The full test suite shows 22 failures unrelated to this work - mostly YAML template placeholder parsing issues (`{{TYPE}}` in frontmatter) and checkpoint cycle tests. These represent tech debt in the test suite that should be addressed in a separate cleanup work item.
