---
template: observations
work_id: WORK-027
captured_session: '250'
generated: '2026-01-27'
last_updated: '2026-01-27T21:12:18'
---
# Observations: WORK-027

## What surprised you?

The PostToolUse linter hook (updating timestamps on file save) caused frequent "file modified since read" errors during batch edits. With 20 files to edit, nearly every parallel edit batch had 2-3 failures requiring re-reads. The mechanical nature of the task (search-and-replace) made this especially frustrating since the edits were trivially correct but tooling forced sequential re-reads. Also, `test_database.py` lacked `from pathlib import Path` at module level - switching its inline `sys.path.insert(0, '.claude/lib')` to the `Path(__file__)` pattern caused a NameError. Subtle dependency only caught by running tests.

## What's missing?

A bulk search-and-replace tool or script. This task was 100% mechanical - replace path string A with path string B across 20 files. A `just migrate-imports OLD NEW` recipe would have completed this in seconds instead of 30+ individual Edit calls with linter race conditions. Also, `conftest.py` doesn't centralize the lib path setup - each test file independently does `sys.path.insert`. A shared fixture or conftest entry would make future path migrations trivial.

## What should we remember?

- When editing `sys.path.insert` calls, verify the target file has `from pathlib import Path` imported if switching to `Path(__file__)` pattern
- `test_ground_truth_parser.py` contains `.claude/lib` strings as test fixture data (not actual imports) - these should NOT be migrated since they test the parser's ability to handle arbitrary paths
- `test_lib_migration.py` and `test_orphan_detection.py` intentionally reference the old path - preserve these
- 20 pre-existing test failures exist across the suite, none related to this work

## What drift did you notice?

- `test_routing_gate.py` tests a `work_type` parameter on `determine_route()` that doesn't exist in the actual function signature (`.claude/haios/lib/routing.py:28`). 4 tests permanently failing.
- `test_lib_retrieval.py` fails because `extraction.py` imports `preprocessors` which doesn't exist in `.claude/haios/lib/`. Import chain is broken.
- Multiple stale skill-structure tests (checkpoint_cycle_verify, survey_cycle, observation_capture_cycle) assert content that no longer matches actual skill files.
