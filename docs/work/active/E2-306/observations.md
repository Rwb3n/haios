---
template: observations
work_id: E2-306
captured_session: '247'
generated: '2026-01-26'
last_updated: '2026-01-26T23:16:51'
---
# Observations: E2-306

## What surprised you?

**The coldstart false positives bug (INV-073) surfaced during routine coldstart.** I expected a clean context load but instead saw 80+ work items reported as "stuck" when many were actually `status: complete`. This revealed that `scan_incomplete_work()` in `governance_events.py:191-241` checks `exited: null` in node_history but ignores the `status` field entirely. Every work item has `exited: null` on its current node by design - that's how you know which node is current. The function was answering "which node are you on?" not "is this work incomplete?". This is a design conflation of two independent axes: node position vs. completion status. Created INV-073 to track.

**The critique-agent found a library path conflict I would have missed.** The plan specified `.claude/haios/lib` but justfile convention (11+ recipes) uses `.claude/lib`. The session functions only exist in `.claude/haios/lib/governance_events.py`. Without the critique, implementation would have failed on ImportError. Operator decision: accept temporary inconsistency since `.claude/lib` is deprecated.

## What's missing?

**Node transition automation when plans are approved.** I discovered 22 work items with `plan: complete` but `current_node: backlog`. The plan-authoring workflow writes `status: approved` to PLAN.md but doesn't call `just node {id} plan`. This means checkpoint says "plan approved, ready for DO" but WORK.md says "backlog". I had to manually fix E2-306's node before implementation. This should be automatic.

**No validation that WORK.md node matches plan status.** The coldstart orchestrator could check: if plan exists with `status: approved/complete` but WORK.md has `current_node: backlog`, warn about desync.

## What should we remember?

**Critique-agent is valuable for catching assumption errors.** The SPEC_ALIGN phase found a path assumption that would have caused ImportError. This validates the defense-in-depth gating strategy from E2-072.

**Two library locations exist: `.claude/lib/` (deprecated) and `.claude/haios/lib/` (current).** Functions may exist in one but not the other. Always verify import path against actual file location, not just pattern matching.

**Pattern: `sys.path.insert(0,'.claude/haios/lib')` for justfile recipes importing governance_events session functions.** This is the correct path for session functions (`log_session_start`, `log_session_end`).

## What drift did you notice?

**Drift warning from Session 245 still valid:** `.claude/lib/` marked DEPRECATED but `test_governance_events.py` still imports from it. The duplication between `.claude/lib/governance_events.py` and `.claude/haios/lib/governance_events.py` is technical debt.

**Coldstart "INCOMPLETE WORK" output is misleading.** It reports completed work as "stuck". The terminology implies something is wrong when items are actually done. This erodes trust in coldstart output. See INV-073.
