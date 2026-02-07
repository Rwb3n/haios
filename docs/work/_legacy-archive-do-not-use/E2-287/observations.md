---
template: observations
work_id: E2-287
captured_session: '190'
generated: '2026-01-14'
last_updated: '2026-01-14T22:13:00'
---
# Observations: E2-287

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- Existing `test_vitals_injection_with_slim_json` test was stale - expected "HAIOS Vitals" but vitals disabled in Session 179. Fixed by updating test.
- Backward compatibility needed explicit `"session_state" in slim` check - using `.get()` with default `{}` triggered warning for old format too.

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- E2-288 not implemented yet - warning fires on every prompt because `session_state.active_cycle` is always null
- No "skip warning" mechanism like other governance reminders have - may want to add if warning becomes noisy

## What should we remember?

<!-- Learnings, patterns, warnings -->

- Pattern: `_get_X_warning(cwd)` functions in UserPromptSubmit follow consistent pattern (read slim JSON, check condition, return formatted warning or None)
- Soft enforcement chain: E2-286 (schema) → E2-287 (warning) → E2-288 (set-cycle) - all three needed for complete solution
- Reuse existing formats: RFC2119 reminder format (`--- X ---\n...\n---`) for consistency
