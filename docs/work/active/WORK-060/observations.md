---
template: observations
work_id: WORK-060
captured_session: '273'
generated: '2026-02-01'
last_updated: '2026-02-01T16:24:01'
---
# Observations: WORK-060

## What surprised you?

**Two features already active without HAIOS action.** Auto skill hot-reload (v2.1.0) and large outputs to disk (v2.1.2) are already benefiting HAIOS because of matching directory conventions. The `.claude/skills/` location happens to match Claude Code's auto-reload pattern. This is a free benefit from architectural alignment - HAIOS got value without explicitly adopting anything. Implication: When evaluating platform features, check if HAIOS already benefits passively before planning adoption work.

**Setup hook doesn't solve the problem it seems to.** Initial assumption was Setup hook could auto-initialize context on fresh clone. Reality: it only triggers on explicit `--init` flag, which is no better than manually running `/coldstart`. The feature name "Setup" is misleading for the auto-initialization use case HAIOS needs. Implication: Feature names don't always describe the triggering mechanism - must read docs carefully for trigger conditions.

## What's missing?

**Auto-trigger mechanism for session initialization.** Neither SessionStart hook nor Setup hook can auto-detect "this is a fresh clone" vs "this is a returning session." HAIOS still relies on operator to invoke `/coldstart` manually. A mechanism that detects first-run-in-project would be valuable. This might require a project-local state file that coldstart creates on first run.

**MCP capability negotiation documentation.** While list_changed exists, there's no clear pattern for "announce capabilities change when server state changes." Would be useful if memory server needed to disable tools when DB is offline. Current haios-memory MCP server (`haios_etl/mcp_server.py`) uses FastMCP with static tool definitions.

## What should we remember?

**plansDirectory breaks colocation by design.** Claude Code's plansDirectory centralizes plans to `./plans/` or `~/.claude/plans`. HAIOS's pattern keeps plans with their work items via `cycle_docs.plan` field pointing to `docs/work/active/{id}/plans/PLAN.md`. These are incompatible philosophies. Future evaluations of similar "consolidation" features should ask: "Does this break work item colocation?" If yes, the feature is likely not suitable for HAIOS.

**Feature evaluation can legitimately produce no spawned work.** This investigation found no features worth implementing. That's a valid outcome - the value is documenting WHY not to adopt, preventing future re-investigation of the same features. Not all investigations produce implementation work; some produce documented decisions.

## What drift did you notice?

**Investigation template comments reference old HYPOTHESIZE-FIRST pattern.** The monolithic investigation template (`.claude/templates/investigation.md`) still says "HYPOTHESIZE PHASE: Define BEFORE exploring" in its HTML comments, but WORK-061 (Session 272) changed the cycle to EXPLORE-FIRST. The fractured templates in `.claude/templates/investigation/EXPLORE.md` are correct, but the monolithic template hasn't been updated. This is template drift - the old template gives wrong guidance. Future work should either deprecate the monolithic template or update its comments to match EXPLORE-FIRST.
