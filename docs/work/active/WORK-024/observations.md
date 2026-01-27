---
template: observations
work_id: WORK-024
captured_session: '249'
generated: '2026-01-27'
last_updated: '2026-01-27T00:08:50'
---
# Observations: WORK-024

## What surprised you?

**The compatibility shim architecture doesn't work for the actual usage pattern.** I expected `.claude/lib/__init__.py` to handle the transition gracefully since it re-exports from `.claude/haios/lib/`. But the shim only works when code does `import lib` or `from lib import X`. The actual pattern used by justfile (13 recipes) and tests (20+ files) is `sys.path.insert(0, '.claude/lib'); from X import Y` which completely bypasses `__init__.py`. Python finds `.claude/lib/X.py` directly on the path, never touching the shim. This means the "gradual migration" strategy from WORK-006/Session 221 was never actually working - consumers were still hitting stale files.

**The stale files have silently diverged.** I assumed the two locations had identical content. In fact, `.claude/haios/lib/governance_events.py` has 4 functions (log_session_start, log_session_end, detect_orphan_session, scan_incomplete_work) that don't exist in the stale `.claude/lib/governance_events.py`. These E2-236 functions were added to the canonical location but the deprecated copy was never updated. This explains why session logging works via `session-start` recipe (uses new path) but would fail if called via old path.

## What's missing?

**No automated test for shim effectiveness.** WORK-006 created the shim but there's no test verifying that imports via deprecated path actually work. A test like `sys.path.insert('.claude/lib'); from governance_events import log_session_start` would have caught this issue immediately. The shim looked correct in code review but didn't work for the actual usage pattern.

**No path constant consolidation.** Both library directories, justfile recipes, test files, and hooks all hardcode path strings like `.claude/lib/` and `.claude/haios/lib/`. There's no single source of truth for these paths. INV-041 (in backlog) addresses this but it's been deprioritized. This investigation shows the cost of that delay - 13 justfile recipes and 20+ tests all need individual updates.

## What should we remember?

**Pattern: `sys.path.insert` bypasses `__init__.py` shims.** When you add a directory to sys.path and then `from X import Y`, Python searches for `X.py` directly in that directory. It does NOT import the directory's `__init__.py` first. This means compatibility shims that rely on `__init__.py` re-exports only work for `import package` style imports, not `sys.path.insert` style. For the latter pattern, you MUST either delete the old files or update them in place.

**Migration order matters for breaking changes.** The spawned work items have a dependency chain: WORK-025 (delete stale files) MUST complete before WORK-026 (update justfile) and WORK-027 (update tests). If we update consumers first, they'll fail because the old path still exists but has stale content. If we delete files first, consumers fail until updated. The correct sequence: (1) delete stale files, (2) run tests to find all breakages, (3) fix consumers.

## What drift did you notice?

**WORK-006 "migration complete" claim vs reality.** Session 221 marked the migration as complete when the shim was created. But "migration complete" should mean "consumers can use either path safely." The shim provided facade compatibility but not true compatibility for the sys.path.insert pattern. The claim was technically accurate (shim exists) but practically misleading (doesn't work for actual usage).

**Memory says deprecated, but deprecated isn't enforced.** Memory concepts 82459, 82246, 82481 all say `.claude/lib/` is deprecated. CLAUDE.md says use `.claude/haios/lib/`. Yet 13 justfile recipes and 20+ tests still use the old path. There's no hook or gate preventing use of deprecated paths. "Deprecated" has become a documentation label, not a runtime enforcement.
