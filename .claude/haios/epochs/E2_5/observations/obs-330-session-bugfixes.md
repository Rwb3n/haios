---
template: observations
work_id: S330-bugfixes
captured_session: 330
generated: 2026-02-09
last_updated: 2026-02-09T21:06:00
---
# Observations: Session 330 Bug Fixes

## What surprised you?

- The `prior_session` off-by-one bug (Bug 3) had a subtler root cause than expected. Initial assumption: `get_session_delta()` in status.py was miscalculating from checkpoint files. Actual cause: `session-start` in justfile reads `session_delta.current_session` from haios-status.json to set `prior_session`, but this is non-idempotent — calling `session-start 330` twice makes `prior_session == current_session == 330`. The fix was to use deterministic `s-1` instead of stale state lookup. This pattern (reading mutable state to derive a value that should be computed) is a class of bug worth watching for.

- The `{{TYPE}}` bug (Bug 2) was a simple omission — `scaffold_template()` populates 7 default variables (DATE, TIMESTAMP, PREV_SESSION, BACKLOG_ID, TITLE, SESSION, SPAWNED_BY) but TYPE was never added despite the work_item template using it. This went undetected because work items were historically created with manual frontmatter editing, not pure scaffold.

## What's missing?

- **Template lint/validation**: No automated check exists for unsubstituted `{{VAR}}` patterns in scaffolded output. A test that scaffolds each template type and asserts no `{{` remains would have caught Bug 2 immediately. This is a gap in the test infrastructure.

- **Comprehensive git add pattern**: `commit-session` and `stage-governance` recipes maintain explicit directory lists. When new directories are added (like `.claude/skills/` in WORK-110), the recipes go stale. A `just commit-all` recipe or a config-driven list would be more maintainable.

- **`stage-governance` recipe (justfile:394)** has the same gap as `commit-session` had — missing `.claude/skills/`, `.claude/commands/`, `.claude/agents/`, `.claude/hooks/`. Not fixed this session (out of scope for the specific bug), but should be addressed.

## What should we remember?

- **Bug fix sessions are high-ROI**: Four bugs fixed in ~15 minutes of focused work. The checkpoint `pending` field made this possible — bugs were precisely described with memory refs. This pattern (structured bug capture → batch fix session) is worth repeating.

- **Investigate narrowly for known bugs**: Over-investigation costs time. Bug 1 grep across all of `.claude/` returned 50+ irrelevant E2.3 hits. Should have targeted `.claude/templates/` directly. For bugs with known symptoms, go straight to the source file.

- **Non-idempotent state updates are a bug class**: The `session-start` recipe assumed it would only be called once per session. Any state update that reads-then-writes mutable state should be designed for re-entrancy.

## What drift did you notice?

- **Fractured templates have hardcoded timestamps**: All 24 fractured phase templates (investigation/, design/, implementation/, validation/, triage/) have hardcoded `last_updated` values from when they were created (2026-02-04/05). These aren't scaffolded via `scaffold_template()` currently, so it's not a runtime bug, but it's technical debt that could become a bug if the template loading path changes.

- **`stage-governance` recipe still stale**: justfile:394 has the same directory omission that was fixed in `commit-session`. This is drift between two recipes that should have the same staging scope.
