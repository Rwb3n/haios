---
template: observations
work_id: WORK-003
captured_session: '216'
generated: '2026-01-21'
last_updated: '2026-01-21T12:14:09'
---
# Observations: WORK-003

## What surprised you?

Justfile doesn't support Python multiline strings with backslash continuation. Had to compress the entire recipe into a single line, reducing readability.

## What's missing?

- [x] Python script for complex recipes: When logic exceeds ~50 chars, should call `.claude/lib/` script instead of inline code
- [x] Session number ownership: Recipe still takes session as argument. "Trivial increment" (R3) not fully realized - caller computes increment.

## What should we remember?

- [x] Dual-write pattern: During transitions, write to both old and new locations for gradual migration
- [x] Justfile inline Python: Use semicolons, single quotes, `chr(10)` for newlines. Keep short or call external script.
- [x] Header preservation: When writing to files with PostToolUse headers, read and preserve them

## What drift did you notice?

- [x] CH-002 R3 incomplete: Chapter says recipe "reads current, increments, writes new" but it takes session as argument. Caller still computes increment.
