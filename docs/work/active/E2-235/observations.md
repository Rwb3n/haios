---
template: observations
work_id: E2-235
captured_session: '212'
generated: '2026-01-19'
last_updated: '2026-01-19T20:29:33'
---
# Observations: E2-235

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] **Context window data architecture:** UserPromptSubmit hook receives minimal payload (session_id, transcript_path, cwd, prompt) while statusLine receives full model context including `context_window.used_percentage`. Intentional split: hooks for governance, statusLine for metrics.
- [x] **Problem was already solved:** statusLine could provide real-time context visibility. E2-235 framed as "fix hook warnings" when goal was "context visibility." Different solution, same outcome.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] **Hook input schema documentation:** No authoritative doc listing what data each hook type receives. Had to discover through code inspection.
- [x] **statusLine discoverability:** Not mentioned in CLAUDE.md or agent bootstrap. Agent wouldn't know to use it without operator guidance.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] **"What data does X receive?" is critical.** Before implementing hook-based solutions, verify the hook receives the data you need.
- [x] **statusLine = real-time model metrics.** When you need actual API data (context usage, model info), statusLine has it. Hooks don't.
- [x] **Reframe problems before implementing.** E2-235 assumed "hook-based warnings" was the solution. Stepping back to "context visibility" revealed statusLine was the answer.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] **E2-235 deliverables were obsolete.** Written when file-size heuristic was the only option. statusLine capability (ground truth) wasn't considered.
- [x] **user_prompt_submit.py has disabled code.** Lines 71-76 and 79-87 show disabled vitals and context threshold. Accumulated disabled features should be removed or re-enabled with proper data sources.
