---
template: observations
work_id: INV-067
captured_session: '198'
generated: '2026-01-17'
last_updated: '2026-01-17T13:49:51'
---
# Observations: INV-067

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- [x] **Observations weren't new gaps - already captured but never triaged.** The Session 197 extraction re-discovered 15 observations already in `docs/work/archive/*/observations.md`. Observation capture works; triage doesn't happen.
- [x] **E2-293/294/295 resolved more than expected.** All three session state observations (E2-288, E2-283, E2-291) fully addressed. 17 set-cycle calls across 4 cycle skills.

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- [x] **Observation triage not operationalized.** Skill exists (E2-218), no trigger or schedule. Observations accumulate without review. Need threshold routing or session-end prompt.
- [x] **No automated observation listing.** Manual table building. A `just observations` recipe would accelerate triage.

## What should we remember?

<!-- Learnings, patterns, warnings -->

- [x] **Pattern: "Re-discovery" investigations reveal process gaps, not content gaps.** When investigation "finds" existing things, the real finding is underutilized infrastructure.
- [x] **Investigation-agent subagent effective for hypothesis testing.** Three invocations, each returned focused evidence with citations. Reuse this pattern.
- [x] **E3/E4 classification verified against L3:187-188 and S25:54-59.** These are authoritative sources for epoch boundaries.
