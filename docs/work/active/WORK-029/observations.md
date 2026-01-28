---
template: observations
work_id: WORK-029
captured_session: '255'
generated: '2026-01-28'
last_updated: '2026-01-28T23:25:46'
---
# Observations: WORK-029

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**Windows cmd vs bash confusion:** The `del` command appeared to succeed (printed "Deleted") but files weren't actually removed. This happened because the shell environment runs bash, not Windows cmd. Using `rm -f` worked correctly. This is a subtle trap on Windows when bash commands are dispatched through a compatibility layer - some Windows-native commands may silently fail or behave unexpectedly.

**synthesis.py was also broken:** The original WORK-029 context listed only mcp_server.py, extraction.py, and retrieval.py for deletion. Upon inspection, synthesis.py also had the same broken bare imports (`from database import DatabaseManager`). The scope organically expanded from 3 to 4 files during investigation. This shows the value of reading files rather than trusting external descriptions.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**Import health check tooling:** There's no automated way to detect "orphan" Python files with broken imports in `.claude/haios/lib/`. A simple lint rule could check that all imports in a file can be resolved. This would have prevented these broken files from lingering for months. Consider adding a `just lint-imports` recipe that runs `python -c "import sys; exec(open(f).read())"` on all Python files in the plugin.

**test_lib_migration.py tested existence, not usability:** The test `test_all_modules_importable_from_haios_lib` originally checked that etl_dependent_modules "files exist" (structural check) rather than that they can be imported. This is backwards - checking file existence without import capability gives false confidence. Tests should verify behavior, not just structure.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Bare imports vs relative imports pattern:** When copying code between directories, import style determines portability. `from database import X` (bare) only works when running from the same directory. `from .database import X` (relative) works from any location within the package. The haios_etl/ files use proper relative imports; the .claude/haios/lib/ copies used bare imports and broke immediately.

**"Real" code location for MCP:** The authoritative MCP server and related memory code lives in `haios_etl/`. The `.claude/haios/lib/` directory contains HAIOS governance code (scaffold, work_item, status, validate, etc.). These are separate concerns that were accidentally conflated during an earlier migration attempt.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**test_lib_retrieval.py was already broken:** This test file existed but was testing code that couldn't import due to the broken preprocessors dependency. The test was probably green only because pytest collects tests but may not have been running the import tests (or they were marked skip). Tests that can't run are worse than no tests - they create false confidence. Observation: there may be other "zombie tests" that silently fail or skip.
