---
template: observations
work_id: WORK-023
captured_session: '247'
generated: '2026-01-26'
last_updated: '2026-01-26T23:53:08'
---
# Observations: WORK-023

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] **Agent re-verified injected context (token waste).** The coldstart orchestrator had already extracted and presented the pending work list from the checkpoint, but I searched for checkpoint files to "verify" what was already injected. This revealed that agents don't trust injected context and waste tokens re-verifying it. The root cause is that REQ-CONTEXT-001 says "inject" but doesn't say "agent MUST NOT re-verify."

- [x] **Agent bypassed routing for "simple" work.** Survey-cycle has explicit routing rules (backlog node → work-creation-cycle), but I rationalized skipping because the bug fix "seemed simple with clear deliverables." This revealed that routing is governance, not agent discretion, but it's not codified as such in L4 requirements.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] **L4 requirement for "trust injected context."** REQ-CONTEXT-001 says "Coldstart MUST inject prior session context" but doesn't say agents must USE it without re-verification. Proposed: REQ-CONTEXT-00X requiring agents to trust injected context.

- [x] **L4 requirement for "routing is governance."** The functional_requirements.md covers transitions and gates, but doesn't explicitly state that cycle routing (survey-cycle → work-creation-cycle) IS a governance gate. Agent can currently bypass routing by rationalizing work is "simple."

- [x] **Survey-cycle auto-continue not codified.** The pattern (checkpoint pending → auto-continue first item) exists in skill prose but isn't a formal REQ-ROUTE-XXX requirement in functional_requirements.md.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] **Pattern: Terminal status filtering must happen at multiple layers.** Memory concept 79660 documented this: "Archive filtering must happen at multiple layers - both the status generator and the tree viewer." This bug (scan_incomplete_work not filtering) is another instance. The terminal_statuses set `{complete, archived, dismissed, invalid, deferred}` is authoritative at WorkEngine.get_ready() line 300.

- [x] **Pattern: Same bug recurs across components.** Memory concepts 82156 (queue filtering) and 82422 (plan_tree.py) show the same bug pattern - filtering only `complete` instead of all terminal statuses. When fixing one, grep for similar patterns.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] **Test imports from deprecated .claude/lib/.** The test file `tests/test_governance_events.py` has `sys.path.insert(0, ".claude/lib")` but `scan_incomplete_work` is in `.claude/haios/lib/`. Had to add second path entry. This is the drift noted in session 247 checkpoint: ".claude/lib/ marked DEPRECATED but test_governance_events.py still imports from it."

- [x] **Two governance_events.py files exist.** `.claude/lib/governance_events.py` and `.claude/haios/lib/governance_events.py` both exist. The haios one has `scan_incomplete_work`, the lib one doesn't. This causes import confusion and is part of the WORK-024 lib pruning investigation.
