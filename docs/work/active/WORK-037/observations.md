---
template: observations
work_id: WORK-037
captured_session: '271'
generated: '2026-02-01'
last_updated: '2026-02-01T15:22:56'
---
# Observations: WORK-037

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**The L4 decision already existed.** When I started WORK-037, I expected to evaluate Options C (EXPLORE-FIRST) and D (Hybrid) as the work item scope indicated. But querying memory revealed that Session 265 had already made the L4 decision approving EXPLORE-FIRST (concepts 82721-82723). The work item was created before that decision was made, so its scope was outdated. This required a pivot from "evaluate options" to "design implementation." Implication: Work items can become stale if strategic decisions are made between creation and execution.

**The activity_matrix.yaml already partially supports the new flow.** The phase-to-state mapping (lines 186-189) shows investigation-cycle phases mapped to states, and the EXPLORE state already has the right governed activities (allow web-fetch, memory-search, warn on writes). The Template Tax problem came from the template's 27 checkboxes and the investigation-agent's rigid output format, not from activity restrictions. Implication: Governed activities infrastructure is sound; the overhead is in template structure.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**No automatic work item scope refresh.** When L4 decisions supersede work item scope, there's no mechanism to flag or update affected work items. WORK-037 sat in backlog with outdated scope until I manually discovered the L4 decision through memory query. Implication: A "decision impact" check could query memory for L4 decisions affecting backlog items.

**Investigation-agent output format is still rigid.** The design spec calls for relaxing the 12-line evidence table format (`.claude/agents/investigation-agent.md:55-65`), but this requires a separate work item. The agent design is coupled to the old flow. Implication: WORK-061 spawned; investigation-agent update should be separate follow-on work.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Always query memory for L4 decisions before starting work.** Work items can become stale if created before strategic decisions are made. Memory concepts 82721-82723 captured the decision that made the original WORK-037 scope obsolete. Pattern: `memory_search_with_experience` for "L4 Decision" + work topic early in HYPOTHESIZE phase.

**Template Tax reduction is significant.** Going from 368 lines/18 MUST/27 checkboxes to ~140 lines/9 MUST/~12 checkboxes is a 62%/50%/56% reduction respectively. This pattern (fracturing monolithic templates into phase-specific contracts) should apply to implementation templates too. See Templates arc CH-002 (ImplementationFracture).

**Fractured templates align with governed activities.** Each phase template (~30 lines) maps to one state in activity_matrix.yaml. This creates a clean contract: template defines structure, activity matrix defines allowed primitives. Pattern worth naming: "Phase-Contract-Activity Triple" - every phase has template + contract + activity rules.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**Activities arc ARC.md shows chapters as "Planned" but they're complete.** The ARC.md for the activities arc (`.claude/haios/epochs/E2_4/arcs/activities/ARC.md`) shows CH-001 through CH-004 all as "Planned" in the table, but per the session opening message, WORK-042 (CH-004 PreToolUseIntegration) was just closed and the arc is complete. The ARC.md needs updating to reflect actual status. File: `.claude/haios/epochs/E2_4/arcs/activities/ARC.md:29-33`

**Investigation-cycle skill says "MUST invoke investigation-agent" but EXPLORE-FIRST removes this.** The current skill (`.claude/skills/investigation-cycle/SKILL.md:89`) has a MUST requirement that will become incorrect once WORK-061 implements the new flow. The new flow has main agent do open exploration without investigation-agent constraint.
