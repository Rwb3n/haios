---
template: observations
work_id: 'WORK-137'
captured_session: '357'
generated: '2026-02-12'
last_updated: '2026-02-12T21:54:32'
---
# Observations: WORK-137

## What surprised you?

The `scaffold_template` and `get_next_work_id` functions are tightly coupled to `PROJECT_ROOT` (resolved from scaffold.py's file location via `Path(__file__).parent.parent.parent.parent`). This means any test using `tmp_path` for isolated work engines cannot use scaffold's ID generation or output path resolution without workarounds. I had to add `_override_work_id` parameter to `execute_spawn()` and pass absolute paths through `engine._base_path` to achieve test isolation. This wasn't anticipated in the plan — the critique agent flagged ceremony context patterns and portal creation, but not the test isolation issue with `PROJECT_ROOT`. The first run produced 6 failures from a single root cause (both spawns getting the same WORK-XXX ID because `get_next_work_id()` scans the real project, not `tmp_path`).

## What's missing?

A `base_path`-aware version of `get_next_work_id()` and `scaffold_template()` that accepts a base path parameter instead of always using `PROJECT_ROOT`. This would eliminate the `_override_work_id` hack and make the scaffold system fully testable in isolation. This is directly related to the portability arc (REQ-PORTABLE-001: all paths configurable via haios.yaml) and CH-028 (PathConfigMigration). The 17 hardcoded paths identified in WORK-094 include scaffold.py — this observation reinforces that finding.

## What should we remember?

The "ceremony-as-wrapper" pattern is now proven across two ceremony categories: `queue_ceremonies.py` (CH-010, WORK-110) and `spawn_ceremonies.py` (CH-017, WORK-137). The pattern is: validate inputs → `_ceremony_context_safe()` → engine operations with `ctx.log_side_effect()` → event logging via `_append_event()` → return `{success, ...}` or `{success: False, error}` dict. Future ceremony implementations should follow this exact structure. The critique-agent was genuinely valuable — it caught the missing REFS.md portal creation (A8) and ceremony context side-effect logging (A5) which would have been real bugs in production. Both were non-obvious from reading the plan alone.

## What drift did you notice?

The ceremony overhead concern (obs-314, mem 85027) is measurable but lower than feared for this work item. Plan validation + critique + preflight added ~15 minutes to what would have been a ~45 minute implementation (~33% overhead). This is below the ~40% reported in the S339 retro, possibly because the work was well-scoped from a clear chapter spec (CH-017 had explicit requirements R1-R4 and success criteria). The overhead may scale better with clear specs.
