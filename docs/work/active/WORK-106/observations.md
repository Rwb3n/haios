---
template: observations
work_id: WORK-106
captured_session: '320'
generated: '2026-02-07'
last_updated: '2026-02-07T15:38:18'
---
# Observations: WORK-106

## What surprised you?

The design drift was more structural than expected. I anticipated a simple terminology mismatch, but found that REQ-QUEUE-003 and REQ-QUEUE-005 had been updated in Session 314 after the chapter specs were written in Sessions 295-296, creating a 3-way disagreement (L4: 5 values with `active`, chapters: 4 values with `working`, implementation: 3 values with `in_progress`). The fact that WORK-066 shipped with a third terminology choice (`in_progress`) that matched neither L4 nor the chapters shows how drift compounds when upstream changes aren't propagated. Three independent authors (L4 writer, chapter writer, implementer) each made reasonable but different naming choices.

## What's missing?

There is no automated mechanism to detect when L4 requirements are updated after dependent chapters are written. The traceability chain (L4 -> Epoch -> Arc -> Chapter -> Work Item) is one-directional at creation time but has no "change notification" when upstream changes. A `traces_to` reference in chapters back to L4 exists conceptually but isn't machine-checked. When REQ-QUEUE-005 was added in Session 314, nothing flagged that CH-007 through CH-010 needed review. A potential solution: when L4 requirements are edited, a hook or audit could identify chapters that `traces_to` the modified requirement and flag them for review.

## What should we remember?

**Pattern: Amendment feedback loop works.** The investigation discovered that chapters (CH-007) had a better terminology choice (`working`) than L4 (`active`). Rather than forcing chapters to match a flawed L4 term, we amended L4 with a supersession log entry. This demonstrates the feedback loop: `Work Complete -> Chapter Review -> L4 Requirements Review` from REQ-FEEDBACK-004/005. This pattern should be repeated when downstream work reveals upstream improvements.

**Pattern: MVP-then-expand is valid.** WORK-066 shipped 3 values as an MVP and was correctly closed as complete. WORK-105 expands to 5 values. This validates the "complete without spawn" design (REQ-QUEUE-002) - an item can be genuinely done at its scoped level even if the full vision has more to implement.

## What drift did you notice?

CH-007 "Current State" section was stale - it described WorkState as if WORK-066 hadn't happened (said `queue_position` field "doesn't exist" when it has existed since Session 307). Updated during this investigation. This is a specific instance of the general "chapter specs drift from reality after implementation" pattern that the CONCLUDE phase's epoch artifact reconciliation step (Session 276) was designed to catch. The reconciliation step worked as intended here - it was the investigation that surfaced and fixed the stale chapter content.
