---
template: observations
work_id: WORK-088
captured_session: '247'
generated: '2026-02-04'
last_updated: '2026-02-04T22:34:46'
---
# Observations: WORK-088

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**WORK-084 archive files existed in git but were missing from working directory.** Git ls-tree showed the files at HEAD, but Glob returned empty. This was unexpected - I had to `git checkout HEAD -- path/` to restore them. Root cause unknown, possibly an incomplete checkout or filesystem sync issue. This highlights the importance of verifying file existence via git when Glob returns unexpected results.

**Critique agent surfaced real value (A4 integration gap).** The critique phase identified that the plan showed new validation methods but didn't show how they wired into existing check_phase_entry/exit. Without that catch, the methods would have been implemented but never called - dead code that tests pass but provides no runtime value.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**Field-to-section mapping for actual contract validation.** The MVP `_check_work_has_field` always returns True because there's no defined mapping between contract field names (like "work_context", "evidence_table") and actual sections in WORK.md files. This is acknowledged as deferred to CH-007, but the schema would be useful.

**No template path config.** Phase-to-template mapping is hardcoded in `_load_phase_template`. When other lifecycles (design, implementation) add templates, this dict must be manually extended. CH-006 should introduce config-based mapping.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Critique-agent is worth the extra cycle.** A4 (integration gap) would have resulted in orphan methods without the critique. Worth 80 seconds of runtime to catch issues that could waste hours of debugging.

**Contract schema pattern is extensible.** YAML frontmatter with field/type/required/description is portable across template types. Same pattern can apply to implementation, design, validation templates when fractured in CH-006.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**None observed.** Implementation matched plan, tests matched specification, templates already had human-readable contracts that mapped cleanly to machine-readable schema.
