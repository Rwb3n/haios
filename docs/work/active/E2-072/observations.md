---
template: observations
work_id: E2-072
captured_session: '236'
generated: '2026-01-25'
last_updated: '2026-01-25T01:59:11'
---
# Observations: E2-072

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] **Agent registration gap:** The critique-agent.md file exists and is well-defined, but `Task(subagent_type='critique-agent')` fails because HAIOS-defined agents aren't automatically registered with Claude Code's Task tool. Only Claude Code plugin-registered agents work. Assumption: file existence = runtime availability. Reality: separate registration required.
- [x] **Framework effectiveness:** The assumption_surfacing.yaml framework with 5 categories surfaced meaningful assumptions across all 3 test artifacts. All returned REVISE verdicts with actionable blocking assumptions.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] **Agent registration mechanism:** Need a way to make HAIOS-defined agents (.claude/agents/*.md) available to the Task tool. Currently they're prompt-based definitions requiring manual invocation.
- [x] **Coldstart config injection:** Coldstart reads haios.yaml but doesn't inject relevant config outputs (like agents.critique settings). Orchestrator could surface agent configurations.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] **Framework-as-config pattern:** Storing critique categories and verdict rules in YAML enables extensibility without code changes. Can add pre_mortem.yaml, red_team.yaml later.
- [x] **Phase-as-gate pattern:** CRITIQUE phase uses BLOCK/REVISE/PROCEED verdicts to control flow. Operator can override REVISE but not BLOCK.
- [x] **Agent invocation workaround:** Until registration solved, invoke HAIOS agents via `Task(subagent_type='general-purpose', prompt='Follow the agent definition at .claude/agents/{agent}.md...')`.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] **Deliverable naming:** WORK.md says "Create `.claude/agents/critic.md`" but implementation uses `critique-agent.md`. Minor drift - follows naming convention of other agents (validation-agent, investigation-agent).
