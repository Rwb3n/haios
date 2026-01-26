---
id: CH-010
arc: configuration
name: DeadCodeCleanup
status: Active
created: 2026-01-26
spawned_from:
- obs-212-001
generated: '2026-01-26'
last_updated: '2026-01-26T19:29:27'
---
# Chapter: Dead Code Cleanup in Hooks

## Purpose

Remove disabled code from user_prompt_submit.py.

## Context

obs-212-001 documented disabled code blocks in `.claude/hooks/hooks/user_prompt_submit.py`:
- Lines 71-76: `_check_context_threshold()` disabled Session 179
- Lines 79-87: Vitals injection disabled Session 179

## Deliverables

1. Remove `_check_context_threshold()` function and its disabled call
2. Remove vitals injection code (now superseded by statusLine)
3. Clean up any related imports

## Success Criteria

- [ ] Dead code removed
- [ ] No functionality changes (code was already disabled)
- [ ] Tests still pass

## References

- obs-212-001: Disabled code in hooks
- user_prompt_submit.py
