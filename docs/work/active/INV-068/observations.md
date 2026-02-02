---
template: observations
work_id: INV-068
captured_session: '292'
generated: '2026-02-02'
last_updated: '2026-02-02T19:34:44'
---
# Observations: INV-068

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**INV-065 findings were directly applicable.** The prior investigation (INV-065 - Session State Cascade Architecture) had already proven that Skill() is fundamentally unhookable - hooks cannot intercept skill invocations because they're markdown file reads, not distinct tool events. This meant I could skip re-investigating the hook-based approach and focus directly on Task tool delegation. The architectural groundwork from Session 193-194 saved significant exploration time. This demonstrates the value of the `related:` field in work items - INV-068 correctly linked to INV-062 and INV-065, and those findings were immediately actionable.

**The 70-90% context reduction estimate is high.** I initially expected ~60-80% reduction based on the problem statement. After analyzing the actual mechanics - subagent gets fresh context, executes full cycle, returns only summary - the reduction is closer to 70-90%. A 390-line skill with 5 phases accumulating thousands of tokens in tool results compresses to a ~100 token summary. This is better than expected.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**No "cycle-agent" pattern exists yet.** The existing agents (preflight-checker, validation-agent, test-runner) are all single-purpose point checks. There's no precedent for a "full cycle execution" agent that runs PLAN→DO→CHECK→DONE autonomously. WORK-081 will need to establish this pattern - including how the agent loads cycle skill content, how it reports phase transitions, and what the structured return format looks like. The agents/README.md categories (Required Gates, Verification Agents, Utility Agents) will need a new category: "Cycle Agents."

**No context consumption metrics exist.** The 70-90% reduction estimate is based on reasoning, not measurement. There's no mechanism to actually measure how many tokens a cycle consumes vs. its subagent alternative. This would be valuable for validating the architectural decision.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Task tool delegation is the E2.4 bridge to SDK.** The patterns developed now (cycle-as-subagent) will port directly to SDK custom tools in Epoch 4. The Task tool's `subagent_type` parameter maps conceptually to SDK's custom tool registration. The structured return format maps to SDK tool response. Investment now pays forward.

**Phase-as-Subagent vs Full-Cycle: start simple.** H4 was inconclusive between decomposing to 5 single-phase agents vs. 1 full-cycle agent. The recommendation is to start with full-cycle delegation (simpler, lower overhead) and decompose later if gate enforcement becomes an issue. This follows YAGNI - don't over-engineer until the problem manifests.

**S20 pressure dynamics applies to agent architecture.** Main track should be [volumous] - routing, survey, orchestration. Subagents should be [tight] - focused execution with clear inputs/outputs. This is fractal with the phase structure: volumous phases for exploration, tight phases for gates.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**CycleRunner is validator-only, not orchestrator.** The module docstring says "Stateless phase gate validator... Does NOT execute skill content (Claude interprets markdown)." This is correct behavior per L4 invariant. However, INV-068's problem statement implied we might change CycleRunner to delegate - that would violate the invariant. The solution (Task subagents) correctly avoids touching CycleRunner. The "cycle delegation" happens at the skill invocation level, not within CycleRunner.

**Investigation-cycle uses EXPLORE-FIRST, not HYPOTHESIZE-FIRST.** The cycle skill was already updated (WORK-037, E2.4 Decision 5). CYCLE_PHASES in cycle_runner.py still shows `["HYPOTHESIZE", "EXPLORE", "CONCLUDE", "CHAIN"]` but the skill markdown shows EXPLORE first. Minor drift - the module constant doesn't affect behavior since skills are markdown-interpreted.
