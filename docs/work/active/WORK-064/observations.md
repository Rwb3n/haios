---
template: observations
work_id: WORK-064
captured_session: '277'
generated: '2026-02-01'
last_updated: '2026-02-01T22:15:46'
---
# Observations: WORK-064

## What surprised you?

**Hook flow control complexity:** The change from `return None` (silent allow) to `return _allow_with_context()` (explicit allow with context) broke the control flow in `handle()` at `.claude/hooks/hooks/pre_tool_use.py:68-134`. The original code pattern used `if result: return result` to short-circuit on any response from `_check_governed_activity()`. When we started returning context on every call, it exited before reaching other governance checks (SQL blocking, scaffold blocking, path governance).

The fix required:
1. Check `permissionDecision == "deny"` before early return (line 73-75)
2. Pass `activity_result` through to return at function end (lines 99, 135)

This coupling between "response means stop processing" and "response contains context" wasn't obvious from reading the code initially. The pattern is: None = no opinion, dict with deny = block, dict with allow = continue but remember context.

## What's missing?

**Test fixture for governance state mocking:** Tests in `test_hooks.py` use inline mocking of `subprocess.run` to control `GovernanceLayer.get_activity_state()`. Each test repeats:
```python
mock_result = mocker.Mock()
mock_result.stdout = "implementation-cycle/DO/WORK-064"
mock_result.returncode = 0
mocker.patch.object(subprocess, "run", return_value=mock_result)
```

A reusable fixture like `@pytest.fixture def with_governance_state(state)` would reduce boilerplate. The critique agent (A3) correctly identified this gap but it wasn't blocking for WORK-064.

## What should we remember?

**When adding always-present fields to hook responses, audit all callers that check `if result:`.** The PreToolUse handler uses early-return pattern where any non-None response exits the function. Adding context to all responses changes the semantics:

| Before | After |
|--------|-------|
| `None` = allow silently | `None` = governance unavailable |
| `dict` = block/warn | `dict with deny` = block |
| - | `dict with allow` = continue, use context at end |

This is a general pattern for hooks: distinguish between "continue processing" (allow, pass through result) vs "stop processing" (deny, return immediately).

## What drift did you notice?

**Scaffold blocking tests were outdated.** Tests in `TestPreToolUseScaffoldBlocking` expected `just plan`, `just inv`, and `just scaffold work` to be blocked, but Session 253/257 refined the blocking to only:
- `just work WORK-XXX` or `just work "title"`
- `just scaffold work_item`

The tests hadn't been updated to match the refined behavior. Fixed as part of WORK-064 test updates. This is spec/test drift that pre-existed WORK-064.
