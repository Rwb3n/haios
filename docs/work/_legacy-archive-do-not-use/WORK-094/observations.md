---
template: observations
work_id: WORK-094
captured_session: '298'
generated: '2026-02-03'
last_updated: '2026-02-03T20:16:01'
---
# Observations: WORK-094

## What surprised you?

**ConfigLoader exists but is underutilized.** The investigation revealed that haios.yaml already has a comprehensive `paths` section (lines 51-78) with templates, skills, agents, hooks, commands all defined. ConfigLoader.get_path() was implemented in WORK-080. Yet only 8 usages exist across 3 files, while 17 hardcoded path occurrences persist across 7 files. The infrastructure for REQ-CONFIG-001 compliance EXISTS - it's just not being used. This means the fix is adoption, not invention.

**The portability gap is architectural, not code-level** (confirmed memory 80755). The issue isn't scattered hardcoded strings - it's that essential components (templates, skills, agents, hooks, commands) live OUTSIDE the `.claude/haios/` portable core. Even fixing all 17 hardcoded paths won't make HAIOS portable because the files themselves aren't in the right location.

## What's missing?

**No init ceremony exists.** manifest.yaml declares components but provides no installation mechanism. Fresh projects have no way to bootstrap from plugin to working state. This is a fundamental gap - the plugin cannot be distributed without it.

**No seed structure exists.** The proposed Seed+Runtime pattern requires `.claude/haios/templates/`, `.claude/haios/skills/`, etc. These directories don't exist yet. The "portable core" is incomplete.

**Upgrade path undefined.** When seed templates change in a new version, how does an existing installation sync? Diff logic needed.

## What should we remember?

**Seed+Runtime is the correct pattern for portable plugins with customization.** This pattern satisfies: (1) portability (seed travels with plugin), (2) customization (runtime is project-specific), (3) upgrades (diff seed vs runtime). This should become a reference pattern for any future HAIOS plugins or similar systems.

**REQ-CONFIG-001 compliance is enforcement, not documentation.** The requirement exists, the tooling exists (ConfigLoader), but modules bypass it. Need governance (PreToolUse hook?) to catch direct path construction.

**The portability test is the success criterion.** From L4: "Can you drop `.claude/haios/` into a fresh workspace with a corpus of docs and have it produce a working product?" Any architectural decision should be validated against this test.

## What drift did you notice?

**audit_decision_coverage.py:306-307 has hardcoded E2_4 epoch path.** This is a BUG - the file references the prior epoch instead of using ConfigLoader. It will fail when E2_4 is archived.

**manifest.yaml is incomplete.** It declares components exist at paths like `commands/close/` but the actual runtime structure is `.claude/commands/close/`. The manifest paths are relative to plugin root but don't match actual deployment structure.
