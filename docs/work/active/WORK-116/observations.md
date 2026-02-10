---
template: observations
work_id: 'WORK-116'
captured_session: '338'
generated: '2026-02-10'
last_updated: '2026-02-10T21:44:12'
---
# Observations: WORK-116

## What surprised you?

The test isolation bug was caused by Python module identity divergence, not ContextVar logic. Multiple test files using `_load_module("governance_layer", ...)` at module scope each create a new module instance with a new ContextVar. Pytest collects all test files (importing them) before running any tests, so the collection ORDER determines which module instance ends up in `sys.modules`. The last file collected wins, but earlier files retain stale local references. The `ceremony_context` function and `check_ceremony_required` function ended up reading/writing different ContextVars despite appearing to share the same module. This was non-obvious — the symptom ("test passes alone, fails in suite") pointed toward fixture cleanup issues, but the root cause was module-level state duplication from repeated `_load_module` calls. Debugging required tracing function `__globals__` dict identity and ContextVar object identity across module boundaries.

## What's missing?

A consistent test module loading pattern across the test suite. `test_work_engine.py`, `test_queue_ceremonies.py`, and `test_ceremony_context.py` each have their own module loading approach (`_load_module` vs `_ensure_module` vs `from X import`). This inconsistency is the root cause of the ContextVar divergence. A shared `conftest.py` fixture or helper that loads `governance_layer` once and provides it to all test files would prevent this class of bug entirely. This is not in scope for WORK-116 but should be a future work item.

## What should we remember?

- **Pattern: `_get_gov_mod()` for runtime module resolution** — When test files share modules that contain `ContextVar`, `threading.local`, or other module-level state, resolve the module reference at test runtime via `sys.modules[name]`, not at collection time. This prevents stale references from pytest's multi-file collection. Applied in `test_ceremony_context.py:288-298`.
- **Pattern: Rebind cross-module function references** — When module A imports a function from module B at load time, and tests may reload module B, use `monkeypatch.setattr(mod_A, "func", mod_B_current.func)` to rebind. Applied in `w116_patch_events` fixture for `work_engine_mod.check_ceremony_required`.
- **Anti-pattern: `_load_module` for shared modules** — Never use unconditional `_load_module` for modules that contain ContextVars or are imported by other test-loaded modules. Use `_ensure_module` (check `sys.modules` first) instead.

## What drift did you notice?

The `_load_module` pattern in `test_work_engine.py` and `test_queue_ceremonies.py` was always silently creating duplicate module instances. It only became visible when WORK-116 introduced ContextVar-dependent cross-module behavior (`ceremony_context` + `check_ceremony_required`). The test suite has a latent fragility — any future feature using module-level state (ContextVars, singletons, module globals) across `governance_layer` and `work_engine` will hit the same issue unless a shared conftest pattern is adopted.
