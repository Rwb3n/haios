---
template: observations
work_id: WORK-005
captured_session: '221'
generated: '2026-01-21'
last_updated: '2026-01-21T21:06:42'
---
# Observations: WORK-005

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] **Regex complexity for section extraction** - The initial `extract_all_h3` implementation failed because regex patterns for finding consecutive H3 headings didn't properly separate them. Required switching to line-by-line iteration. Regex is brittle for structured document parsing.
- [x] **Path resolution inconsistency across modules** - Sibling modules have different path patterns due to WORK-006 migration. Old modules use `.parent.parent / "haios" / "config"`, new modules use `.parent.parent.parent.parent`. Could cause confusion.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] **No runtime consumer yet** - Loader is complete but nothing uses it. Per E2-250: "Tests pass" does not equal "Code is used". ContextLoader should be first consumer (CH-004).
- [x] **Config validation** - No schema validation for loader config YAML. Invalid configs fail at runtime with unclear errors rather than validation messages.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] **TDD worked well** - 24 tests before implementation made verification easy. When H3 extraction failed, the test clearly showed what was wrong.
- [x] **Module-level functions for testability** - Extraction functions as module-level (not class methods) was the right call. Each can be tested without Loader instantiation.
- [x] **Graceful degradation is essential** - Return empty strings for missing sections instead of raising exceptions. Makes Loader robust for optional content.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] **ARC.md path drift** - Configuration arc's "Files to Create" references `.claude/lib/loader.py` but implementation is at `.claude/haios/lib/loader.py` (post WORK-006 migration). ARC.md should be updated.
