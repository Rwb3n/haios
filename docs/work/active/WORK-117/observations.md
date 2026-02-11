---
template: observations
work_id: 'WORK-117'
captured_session: '351'
generated: '2026-02-11'
last_updated: '2026-02-11T23:31:37'
---
# Observations: WORK-117

## What surprised you?

The cli.py name collision was unexpected. Both `.claude/haios/modules/cli.py` and `.claude/haios/lib/cli.py` exist, and conftest's `sys.path.insert` order (lib/ at position 0, modules/ at position 1) means `import cli` resolves to lib/cli.py instead of the intended modules/cli.py. This only affected one test (TestCmdCloseCeremonyAdoption in test_ceremony_context.py) but required an inline `importlib.util` load — the exact pattern we were trying to eliminate. The critique agent's A3 finding ("conftest module-level loading affects 14+ other files") was validated: pre-loading modules genuinely changes behavior for files not in scope, though in this case it was benign for all files except the cli collision.

## What's missing?

A naming convention or namespace strategy for modules in `modules/` vs `lib/`. Having two `cli.py` files in different directories on the same `sys.path` is a latent bug. The portability arc (deferred to E2.6, CH-028 PathConfigMigration) would address this via the seed/runtime pattern, but until then, any test needing `modules/cli.py` must use explicit path loading with a unique module name (e.g., `cli_modules`). This should be tracked as a known friction point for future test infrastructure work.

## What should we remember?

1. **conftest.py module-level code runs before test file collection** — this is the correct approach for shared module loading, NOT fixtures (which run too late for `from X import Y` at module scope). The plan initially showed both approaches; the critique agent caught the contradiction (A1) before implementation.

2. **When replacing runtime module resolution (`_get_gov_mod()`)**, test files need BOTH `import governance_layer` (module object for `monkeypatch.setattr(module, attr, ...)`) AND `from governance_layer import X` (name bindings for convenience). Missing the bare import would cause NameError. The critique agent caught this (A4).

3. **The critique-agent surfaced 3 actionable revisions** (A1 contradictory design, A4 import style, A5 rebind strategy) that prevented implementation bugs. All 3 would have caused test failures if not addressed. Critique before implementation continues to pay off (also validated in S332/S343).

## What drift did you notice?

The pre-existing test failure count documented in MEMORY.md (17 failures + 3 errors) should be updated to reflect current state: 18 failures, 4 skipped. The `test_manifest::test_component_counts_match_file_system` failure changed (33 vs 18 skills), suggesting skills were added/removed without updating the test. This is not WORK-117 drift but should be noted for maintenance.
