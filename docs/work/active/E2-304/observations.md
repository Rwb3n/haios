---
template: observations
work_id: E2-304
captured_session: '253'
generated: '2026-01-28'
last_updated: '2026-01-28T21:32:17'
---
# Observations: E2-304

## What surprised you?

**E2-305 scaffold guard blocking legitimate command flows (Session 253 discovery):**
The E2-305 scaffold guard was implemented to prevent agents from calling bare scaffold recipes (which produce placeholder files). However, the guard pattern was too broad - it blocked ALL `just plan`, `just inv`, `just scaffold` calls. This broke `/new-plan` and `/new-investigation` commands which legitimately call these recipes internally and then chain to authoring cycles that fill placeholders.

This revealed a circular dependency in governance design: hooks that block "bad patterns" must consider the full call chain. The `/new-plan` command calls `just plan`, which is correct behavior - the command orchestrates the cycle that fills placeholders. The fix (Session 253) was to narrow the guard to only block `just work` and `just scaffold work_item`, since work items have the most complex placeholder requirements and require the full work-creation-cycle.

**Plan authoring was faster than expected:**
The work item had clear deliverables directly from INV-072's Design Outputs section. All 6 deliverables mapped 1:1 to investigation findings. This validated the pattern: investigations that produce clear Design Outputs accelerate downstream implementation planning.

## What's missing?

**No pytest test for scaffold.py validation:**
Added `_get_work_status()` helper (line 142) and validation check (line 478) to scaffold.py, but no dedicated pytest test was added. The manual test passed (verified E2-072 and E2-179 are blocked), but this should have a regression test in `tests/test_lib_scaffold.py`.

**Pre-existing test failure in test_lib_scaffold.py:**
`TestGenerateOutputPath::test_implementation_plan_path` fails because it assumes E2-212 work directory exists, but that item was archived. This is pre-existing technical debt (not caused by E2-304) but should be tracked.

## What should we remember?

**Defense in depth for entry point validation:**
Validation was added at BOTH entry points for work creation:
1. `WorkEngine.create_work()` - programmatic entry (line 246)
2. `scaffold.scaffold_template()` - CLI entry via `just work` (line 478)

This pattern ensures protection regardless of how work items are created. Future validation requirements should follow this pattern: identify all entry points and validate at each.

**Terminal status definition:**
Per INV-072 design, only `complete` and `archived` are terminal statuses that block ID reuse. Active, draft, and other statuses explicitly allow overwriting for backward compatibility. This was a conscious design decision, not an oversight.

**WorkIDUnavailableError distinct from WorkNotFoundError:**
Created new exception class (line 80) rather than reusing existing exceptions. Clear error types help agents understand what went wrong: "unavailable" means exists-but-terminal, "not found" means doesn't exist.

## What drift did you notice?

**WORK.md source_files path incorrect:**
The work item's `source_files` field lists `.claude/lib/scaffold.py` but the actual path is `.claude/haios/lib/scaffold.py`. This is a metadata drift from when scaffold.py was migrated to the haios/ subdirectory. Minor impact but shows work item metadata can go stale.
