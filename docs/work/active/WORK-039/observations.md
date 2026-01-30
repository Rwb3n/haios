---
template: observations
work_id: WORK-039
captured_session: '266'
generated: '2026-01-30'
last_updated: '2026-01-30T22:38:42'
---
# Observations: WORK-039

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**Critique value was higher than anticipated.** The critique-agent surfaced 10 implicit assumptions in the ActivityMatrix design, with 2 being blocking (A3: phase-to-state mapping, A6: redirect behavior). Without critique, implementation would have hit these gaps during PreToolUse hook integration - requiring backtracking. The critique loop (invoke → verdict → revise → re-verify) proved its worth as a hard gate (REQ-CRITIQUE-001).

**Full matrix enumeration scope was larger than expected.** Operator requested "full matrix enumeration" which expanded the design from the Arc's 5-state summary table to 17 primitives × 6 states = 102 cells. This required discovering the complete Claude Code tool taxonomy (via Explore agent), not just mapping the Session 265 decisions. The resulting chapter is comprehensive but implementation-heavy.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**`just get-cycle` recipe does not exist yet.** The chapter references `just get-cycle` for state detection, but this recipe hasn't been implemented. The ActivityMatrix implementation will need this recipe to query current cycle state. Should be added to CycleRunner module (WORK-047 scope or new work item).

**Activity matrix YAML schema not defined.** The chapter specifies the matrix should be stored in `.claude/haios/config/activity_matrix.yaml` but no schema exists. The 102-cell matrix needs a data format for GovernanceLayer to consume. This is implementation detail but should be captured in CH-003 (GovernanceRules) or a separate schema spec.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Design chapters benefit from full Explore-first.** When Operator said "Explore first" before implementation, querying memory + reviewing existing code (PreToolUse hook) + enumerating primitives (via Explore agent) produced a more grounded design than jumping straight to scaffolding. The exploration discovered that the PreToolUse hook already has 8 governance checks - the ActivityMatrix will integrate with, not replace, these.

**Critique-revise pattern should be standard for design work.** This work item demonstrated the full pattern: design → critique → verdict REVISE → address blocking assumptions → re-critique → verdict PROCEED. This pattern aligns with REQ-CRITIQUE-001 (critique as hard gate) and should be the default for all `type: design` work items. The critique agent's structured output (assumptions list with BLOCKING/non-blocking categorization) made revision tractable.

**Phase-to-state mapping is non-obvious.** The critique revealed that mapping existing cycle phases (HYPOTHESIZE, VALIDATE, OBSERVE, etc.) to the 6 ActivityMatrix states requires explicit tables. Future state-machine designs should include this mapping upfront, not assume it's self-evident.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**Work-creation-cycle CHAIN phase routing is inconsistent.** The skill says "If HIGH confidence: auto-chain to /new-plan" but for `type: design` work items where the deliverable is a chapter file, there's no plan - the chapter IS the design artifact. The ChapterFlow pattern (CH-006) documents this but the skill doesn't account for it. The skill should recognize `type: design` + chapter scaffolding scope = skip plan, implement directly.

**Session number in scaffolded observations.md was stale.** The `just scaffold-observations` created a file with `captured_session: '247'` but current session is 266. The scaffold template doesn't read `.claude/session` for the current session number. Minor but causes inaccurate provenance.
