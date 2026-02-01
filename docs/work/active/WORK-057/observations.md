---
template: observations
work_id: WORK-057
captured_session: '275'
generated: '2026-02-01'
last_updated: '2026-02-01T19:39:09'
---
# Observations: WORK-057

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**GovernanceLayer already does state-aware blocking, but agent doesn't see the state.** I assumed investigating "skill hooks" would reveal a governance gap, but the existing architecture (GovernanceLayer.get_activity_state() + activity_matrix.yaml) already provides comprehensive state-aware blocking. The gap isn't in enforcement - it's in visibility. The agent can't see the current state until AFTER a tool is blocked. This was the key insight: the problem isn't "we need skill hooks" but "we need additionalContext to surface what we already track."

**WORK-057 source_files in frontmatter had wrong paths.** The spawned work item referenced `.claude/hooks/hooks/pre_tool_use.py` but the actual path is `.claude/hooks/hooks/pre_tool_use.py` (with nested hooks/ directory). This caused initial Read failures and required Glob to find the actual location. Minor drift but highlights that spawn-time paths can become stale.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**No centralized "blocked primitives per state" query.** The activity_matrix.yaml defines rules but there's no helper function to answer "what's blocked in DO state?" You have to iterate through all primitives and check each one. For additionalContext injection, we'll need a new helper like `get_blocked_primitives(state: str) -> List[str]` in governance_layer.py. This would also be useful for debugging and documentation.

**Claude Code Guide agent was essential.** Without the specialized claude-code-guide subagent, finding documentation for CC 2.1.x features would have required extensive web searching. The agent returned structured information about additionalContext, skill hooks, once:true with confidence. This pattern (specialized guide agents for specific domains) should be used more widely.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**"Visibility before enforcement" principle.** When investigating governance features, distinguish between enforcement (blocking bad actions) and visibility (showing state before decisions). HAIOS had strong enforcement but weak visibility. The additionalContext feature addresses the visibility gap without changing enforcement. This principle applies broadly: showing the user/agent what they CAN'T do before they try is better than blocking and explaining why.

**Feature adoption requires layer analysis.** When evaluating new platform features (like CC skill hooks vs HAIOS GovernanceLayer), the key question is: "What layer does this operate at, and do we already have coverage there?" Skill hooks operate at permission-prompt layer; GovernanceLayer operates at tool-execution layer. They're not redundant - they're different layers. But we don't need both if one layer is sufficient.

**Investigation EXPLORE-FIRST worked well.** Starting with broad evidence gathering (8 sources) before forming hypotheses led to the key insight about visibility vs enforcement. If I'd started with "skill hooks will help governance" hypothesis, I might have missed the additionalContext opportunity.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**WORK-057 source_files referenced wrong path structure.** The frontmatter listed `.claude/hooks/hooks/pre_tool_use.py` but then also mentioned a different path pattern earlier in the Context section. The actual structure is `.claude/hooks/hooks/` (nested hooks directory under hooks). This suggests work items spawned from parent investigations may inherit incorrect path assumptions.

**activity_matrix.yaml phase_to_state mapping is comprehensive but not fully utilized.** The mapping exists (lines 179-241) but PreToolUse doesn't surface this to the agent. The state is tracked internally by GovernanceLayer but never exposed. This is the core drift: we built state tracking infrastructure but didn't complete the visibility loop.
