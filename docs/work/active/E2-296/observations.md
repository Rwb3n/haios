---
template: observations
work_id: E2-296
captured_session: '199'
generated: '2026-01-17'
last_updated: '2026-01-17T14:55:40'
---
# Observations: E2-296

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- [x] **Actual count higher than stated:** WORK.md said "15 observations" but scan found 35 across 12 files. INV-067 focused on Chariot-specific items but triage covered all arcs.
- [x] **Most already resolved:** 25/35 (71%) were dismissable - E2-293/294/295 session state wiring had already addressed them. Observation capture works; triage execution was the gap.

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- [x] **Triage log in observations.md:** Files get `triage_status: triaged` but no structured log of what decision was made. Future triage would benefit from "Triage Log" section.
- [x] **Batch triage automation:** Processing 35 observations manually is time-consuming. A triage assist tool that pre-classifies based on patterns would accelerate future batches.

## What should we remember?

<!-- Learnings, patterns, warnings -->

- [x] **"Re-discovery" signals process gaps:** When investigation "finds" existing things (like INV-067 found untriaged observations), the real finding is underutilized infrastructure.
- [x] **Triage should follow capture:** observation-triage-cycle exists but has no trigger. Consider routing threshold or session-end triage.
