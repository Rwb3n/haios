---
template: observations
work_id: INV-071
captured_session: '234'
generated: '2026-01-25'
last_updated: '2026-01-25T00:24:15'
---
# Observations: INV-071

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] **The triage was already done.** Discovered WORK-002 (Session 208) had completed comprehensive triage 26 sessions ago. MANIFEST.md contains 59 items across 4 categories with documented rationale. Memory system worked - prior work was discoverable via `memory_search_with_experience` (concept 81592).

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] **Coldstart warning lacks manifest reference.** The warning "Queue contains 3 items from prior epochs" doesn't reference MANIFEST.md or indicate triage is complete. Creates operator friction - warning implies action needed when queue is correct per manifest.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] **Query memory before creating new work.** This investigation could have been avoided by checking memory during survey-cycle. Pattern: When operator requests something that sounds like "should already exist," query memory first before spawning new work.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] **epistemic_state.md is stale.** Shows "Epoch: 2.2" but we're in E2.3. Last updated Session 190, now Session 234. Should reflect current epoch.
