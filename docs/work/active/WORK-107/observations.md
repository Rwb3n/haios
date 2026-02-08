---
template: observations
work_id: WORK-107
captured_session: '324'
generated: '2026-02-08'
last_updated: '2026-02-08T23:11:04'
---
# Observations: WORK-107

## What surprised you?

- [x] WorkEngine.close() had a latent bug: it set `status=complete` but left `queue_position` unchanged. Since WORK-105 added forbidden state combinations including `complete+working`, calling close() on an item with `queue_position: working` would actually **raise ValueError**. The "complete without spawn" feature wasn't just missing UX — it was broken at the engine level for working items. The fix was 1 line (`work.queue_position = "done"`), but it also fixed a real runtime error. This validates the WORK-105 forbidden-state design — it caught a real inconsistency.

## What's missing?

- [x] **Ceremony overhead for small-effort items.** This 1-line code change went through: work-creation-cycle (4 phases), plan-authoring-cycle (4 phases), critique-agent, plan-validation-cycle, preflight-checker, implementation-cycle (5 phases), observation-capture-cycle, and close-work-cycle — approximately 12 ceremony invocations total. The S323 observation about ceremony overhead (~40% of session time) is confirmed. A "plan-lite" or "fast-track" path for items with `effort: small` and clear specs would reduce this significantly without losing governance value.

## What should we remember?

- [x] **Atomic multi-field updates pattern:** For WorkEngine operations that change multiple related fields (like close: status + queue_position), assign all fields directly on the WorkState object, then call `_write_work_file()` once. Do NOT use individual setter methods like `set_queue_position()` which each call `_write_work_file()` — this creates intermediate invalid states that `_validate_state_combination()` rejects. The `_write_work_file()` path validates the final combined state (line 929), so validation still runs.

## What drift did you notice?

- [x] **Scaffold session hardcoding confirmed (persistent).** Both `scaffold-observations` and `scaffold implementation_plan` still hardcode `session: 247` instead of reading `.claude/session`. This was noted in S323 checkpoint as pending fix. Observed again: WORK-107 observations scaffolded with `captured_session: '247'`, manually corrected to 324. This is the third session noting this drift.
