---
template: observations
work_id: WORK-032
captured_session: '260'
generated: '2026-01-29'
last_updated: '2026-01-29T21:34:12'
---
# Observations: WORK-032

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**Critique-agent caught real issues:** The critique-agent (E2-072) surfaced 5 actionable assumptions during plan validation. Two were particularly valuable: (1) A3 flagged that malformed IDs like "REQ-001" (missing domain segment) had no test coverage - this led to Test 3.5 which caught real edge cases. (2) A10 noted CLI dispatch referenced "line 425" which would drift as code evolves - changing to pattern-based ("after extract-requirements") is more maintainable.

**TDD worked smoothly:** All 10 tests written before implementation, all failed initially (RED), implementation made them pass (GREEN). No refactoring needed. The plan's test definitions were concrete enough to translate directly to pytest.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**No runtime integration yet:** PlannerAgent produces WorkPlan but nothing consumes it to actually create work items. The plan explicitly scoped this as "interface documentation only" (A9 clarification), but the gap remains. CH-006 (Orchestrator) is the planned consumer.

**Corpus config lacks deduplication:** The haios-requirements.yaml corpus produces a GENERAL group with many duplicate R0-R8 entries because TRDParser extracts from multiple files. A deduplication or grouping refinement would improve output quality.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Pattern: Domain extraction fallback:** The `_extract_domain()` method uses regex `^REQ-([A-Z]+)-\d+$` with GENERAL fallback. This pattern should be reused if other components need to parse requirement IDs. Location: `planner_agent.py:169-178`.

**Pattern: Kahn's algorithm for cycle-safe topological sort:** `DependencyGraph.topological_sort()` handles cycles gracefully by logging warning and appending remaining nodes. This is safer than crashing on cyclic dependencies. Location: `planner_agent.py:104-142`.

**Pattern: WORK-PXXX prefix:** Planned work items use WORK-P### to distinguish from actual WORK-XXX items. This prevents confusion during operator review before WorkEngine creates real items.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**None observed.** The implementation matched CH-003 and S26 specifications exactly. The critique-agent's A5 concern about `loader._parsed.name` being a protected attribute is valid, but this follows the existing pattern in requirement_extractor.py (line 342), so it's consistent drift rather than new drift.
