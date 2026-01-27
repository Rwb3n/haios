---
template: observations
work_id: E2-305
captured_session: '252'
generated: '2026-01-27'
last_updated: '2026-01-27T22:38:01'
---
# Observations: E2-305

## What surprised you?

The critique agent caught a real regex bug before implementation. The pattern `\bjust\s+scaffold\b` would have matched `just scaffold-observations` because hyphen is a non-word character, creating a word boundary after "scaffold". This was marked as "verify in implementation" in the initial plan — exactly the anti-pattern critique is designed to catch. The fix was simple: `(?:\s|$)` instead of `\b` for the trailing boundary. Critique-as-gate proved its value on a concrete, provable bug.

## What's missing?

No guard exists for `just adr` or `just checkpoint` scaffold recipes. The current implementation covers `work`, `plan`, `inv`, `scaffold`, and `new-investigation` — the recipes identified by INV-070. If other scaffold recipes exist in the justfile, they bypass governance. A more comprehensive approach would grep the justfile for all scaffold-type recipes and block them all. This is a scope gap, not a bug — the work item deliverables only specified the five patterns from INV-070.

## What should we remember?

Word boundary `\b` in Python regex matches between `\w` (alphanumeric + underscore) and `\W` (everything else, including hyphens). When guarding commands like `just scaffold` where hyphenated variants exist (`scaffold-observations`), use `(?:\s|$)` instead of `\b` for the trailing anchor. This is a reusable pattern for any command-matching regex in hooks. File: `.claude/hooks/hooks/pre_tool_use.py:215`.

## What drift did you notice?

The scaffold recipes (`just plan`, `just work`, `just inv`) still exist in the justfile and work at the shell level. The PreToolUse hook intercepts at the Bash tool level before execution reaches the shell. This is defense-in-depth: recipes exist for potential manual/operator use but agents are blocked. No documentation describes this layered blocking pattern — the hook docstring was updated (line 9) but no architectural doc captures the "recipes exist but are agent-blocked" design.
