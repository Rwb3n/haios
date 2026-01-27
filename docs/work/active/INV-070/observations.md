---
template: observations
work_id: INV-070
captured_session: '251'
generated: '2026-01-27'
last_updated: '2026-01-27T22:14:02'
---
# Observations: INV-070

## What surprised you?

The investigation itself became a live demonstration of the problem it was investigating. When scaffolding E2-305 and E2-306 via `just work`, both produced `type: {{TYPE}}` — exactly the placeholder bug INV-070 documents. This confirms the finding is not theoretical; it occurs on every direct scaffold recipe call. The governance gap is reliably reproducible and affects every agent session that uses `just work` directly.

## What's missing?

The PreToolUse hook has no Bash-command pattern matching for scaffold recipes. It guards Write/Edit tool calls to governed paths (`pre_tool_use.py` lines 266-319) but treats all Bash calls as opaque. There is no infrastructure for "this Bash command invokes a governed operation" detection. E2-305 (the spawned fix) will be the first Bash-level governance guard, which may establish a reusable pattern for future Bash guards beyond scaffolding.

## What should we remember?

The scaffold recipes (`just work`, `just plan`, `just inv`) are necessary infrastructure — they are the low-level file creation layer called by `/new-*` commands. They cannot simply be removed. The fix must be a governance guard that blocks direct agent invocation while allowing commands/skills to call them. This means the guard needs to distinguish "agent called this directly" from "command chain called this" — or the commands should call `cli.py scaffold` directly, bypassing `just` entirely.

## What drift did you notice?

The `scaffold-observations` recipe produces files with `captured_session: '247'` but current session is 251. The scaffold template hardcodes or incorrectly derives the session number. This is a secondary instance of the same root problem: scaffold recipes produce files with wrong metadata. The session number should come from `.claude/session` at scaffold time, but the template appears to use a stale or default value.
