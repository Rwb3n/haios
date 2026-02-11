---
template: observations
work_id: 'WORK-123'
captured_session: '346'
generated: '2026-02-11'
last_updated: '2026-02-11T21:18:34'
---
# Observations: WORK-123

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

The fix was exactly 2 edits in a single markdown file. The skill author assumed work items reference chapters with an arc prefix (`ceremonies/CH-015`) but the actual frontmatter convention is just `chapter: CH-015`. The close-arc-ceremony was clean — it uses a completely different approach (Glob on chapter files rather than grep on work item `chapter:` field), so the two ceremony skills don't share this pattern despite being siblings in the closure category.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

There's no automated test that verifies skill file grep/glob patterns match actual data formats. Skill files are pure markdown instructions — they're never executed programmatically, so pattern mismatches only surface when a human or agent follows the instructions and gets wrong results. A "skill linter" that validates patterns in skill files against sample data would catch this class of bug proactively.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

When writing skill instructions that include grep/glob patterns referencing frontmatter fields, always verify the pattern against actual data in the codebase. The S345 critique-agent caught assumption A1 (status format) but this grep pattern bug was found by manual observation during WORK-122. Pattern: verify data format assumptions in ceremony/skill files before shipping.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

The WORK-123 WORK.md reference says "line 85" but after the fix the grep pattern is on line 84. This is a trivial drift from the original observation — line numbers shift as files are edited. Not actionable, just noting the fragility of line-number references in observations and work item descriptions.
