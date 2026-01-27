---
template: checkpoint
session: 249
prior_session: 248
date: 2026-01-27
load_principles:
- .claude/haios/epochs/E2_3/arcs/migration/ARC.md
load_memory_refs:
- 82513
- 82514
- 82515
- 82516
- 82517
- 82518
pending:
- WORK-025
drift_observed:
- WORK-006 migration marked 'complete' but shim didn't work for actual usage pattern
- '''Deprecated'' is documentation label, not runtime enforcement - 13 recipes still
  use old path'
completed:
- WORK-024
generated: '2026-01-27'
last_updated: '2026-01-27T00:10:53'
---

## Summary

Investigated `.claude/lib/` vs `.claude/haios/lib/` path confusion. Discovered critical bug: the compatibility shim in `.claude/lib/__init__.py` only works for `import lib` pattern, NOT for `sys.path.insert(0, '.claude/lib'); from X import Y` pattern used by 13 justfile recipes and 20+ tests.

**Root Cause:** Stale `.py` files in `.claude/lib/` are found directly on sys.path, bypassing `__init__.py` re-exports.

**Spawned Work Items:**
- WORK-025: Delete stale files (blocks others)
- WORK-026: Update justfile recipes (blocked by WORK-025)
- WORK-027: Update test imports (blocked by WORK-025)

## Key Learning

Pattern: `sys.path.insert` bypasses `__init__.py` shims. When a directory is added to sys.path, Python searches for module files directly, never importing `__init__.py`. Compatibility shims only work for package-style imports.

## Next Session

Start with WORK-025 (delete stale files). This unblocks WORK-026 and WORK-027.
