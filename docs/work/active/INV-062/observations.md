---
template: observations
work_id: INV-062
captured_session: '188'
generated: '2026-01-11'
last_updated: '2026-01-11T22:23:05'
---
# Observations: INV-062

## What surprised you?

Skill() invocation is fundamentally unhookable in Claude Code - Skills are just Claude reading markdown files, no tool call to intercept. Hard enforcement ("must be in cycle") is architecturally impossible without API changes.

CycleRunner has explicit L4 invariant "MUST NOT own persistent state" - design deliberately made it stateless.

## What's missing?

- Skill invocation hooks in Claude Code API
- Session-level state tracking (haios-status-slim tracks work, not cycle)
- Investigation subtype support (E2-213) for landscape→deep-dive→synthesis passes

## What should we remember?

- Soft enforcement is the viable path (warnings, not blocks)
- "Governance harness creates affordances for patience, not forcing it" (memory 81288)
- State location: haios-status-slim.json (already read by hooks)
- Spawned 4 concrete items: E2-286/287/288 (implementation), INV-063 (API research)
