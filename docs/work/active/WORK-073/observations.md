---
template: observations
work_id: WORK-073
captured_session: '281'
generated: '2026-02-02'
last_updated: '2026-02-02T00:08:52'
---
# Observations: WORK-073

## What surprised you?

**The first-pass audit claims were 100% accurate.** I expected to find at least one overclaim or underclaim during verification, but all major findings matched reality exactly: pytest showed exactly 14 failures (not 13, not 15), memory refs 83050-83071 contained specific findings that matched the audit assertions, and the 95% backlog-stuck claim was verified through evidence of the TRD/GovernanceLayer vocabulary mismatch.

**The three-vocabulary conflict was worse than documented.** The first pass noted TRD vs GovernanceLayer mismatch, but didn't discover L5-execution.md also defines a third vocabulary (`backlog|ready|in_progress|blocked|complete`). Three documents, three different sets of current_node values, none aligned. This is obs-276-01 (TRD vs GovernanceLayer) plus obs-276-02 (L5-execution.md) combined into a three-way conflict.

## What's missing?

**Observation auto-triage threshold.** 4 of 5 E2.4 observations are pending triage. The observation-capture-cycle creates observations but doesn't trigger triage. There's no "pending observation count" threshold that forces triage before new work. The threshold exists in haios.yaml (observation_pending.max_count: 10) but observations/ has only 5 files so threshold not reached.

**Test-to-feature traceability.** When tests fail, there's no clear way to determine if the test expects: (a) a feature that was designed but never implemented, (b) an old policy that was superseded, or (c) actual implementation bugs. The 6 checkpoint-cycle VERIFY phase tests are testing a feature that never existed - they expect a VERIFY phase with anti-pattern-checker integration that was designed but never built. No one caught this until the verification pass. Consider adding a test metadata field like `feature_status: implemented|designed|deprecated`.

## What should we remember?

**Second-pass audits are valuable.** The first pass (WORK-072) was comprehensive but missed: the observations directory content (5 files, 4 pending triage), the three-vocabulary conflict (first pass only found two of three), and the root cause analysis of test failures (documentation drift vs implementation bugs). A verification pass should be standard for audits.

**Test failures can indicate design debt, not bugs.** The 8 tests that fail due to policy/documentation drift are not implementation bugs - they're tests that were written for features that were never built or policies that changed. The checkpoint-cycle VERIFY phase was designed (tests written) but never implemented. The routing-gate INV- prefix routing was superseded by WORK-030 type field policy. This is a specific category ("phantom feature tests") that needs its own remediation pattern: either delete the tests or implement the feature.

## What drift did you notice?

**Activities arc ARC.md status drift (obs-271-1).** The ARC.md for activities arc shows CH-001-004 as "Planned" in the chapters table, but per WORK-042 closure message, all chapters are complete. Arc documentation didn't update when chapters closed. This suggests the epoch artifact reconciliation step in investigation-cycle CONCLUDE phase isn't being followed, or chapters are being closed without updating parent arc.

**TRD-WORK-ITEM-UNIVERSAL vs implementation (obs-276-01).** The approved TRD (Session 218) defines current_node values as `backlog|planning|in_progress|review|complete`. The GovernanceLayer implementation uses `backlog|discovery|plan|implement|close|complete`. These are completely different vocabularies. The TRD was approved but implementation diverged - no one caught this during implementation.
