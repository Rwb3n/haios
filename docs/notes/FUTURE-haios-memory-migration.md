# generated: 2026-01-28
# System Auto: last updated on: 2026-01-28T22:27:25
# Future: haios-memory Full Migration

**Created:** 2026-01-28 (Session 254)
**Target:** Epoch 3+
**Spawned by:** WORK-028 (MCP connection failure investigation)

## Context

The `haios_etl/` package provides the memory system (database, extraction, retrieval, MCP server). For HAIOS plugin portability, ideally everything would be in `.claude/haios/`.

## Current State

- **Working:** `haios_etl/` at project root
- **Broken:** `.claude/haios/lib/` has partial copies with broken imports
- **Config:** `.mcp.json` points to `python -m haios_etl.mcp_server`

## Why Migration Is Non-Trivial

1. **Internal dependencies** - `mcp_server.py` → `extraction.py` → `preprocessors/` → etc.
2. **Relative imports** - Package expects to run as `haios_etl.*`
3. **Size** - ~20 files, database schema, migrations
4. **Callers** - justfile recipes, hooks, modules, CLI all reference `haios_etl`

## Migration Strategy (When Ready)

1. Move `haios_etl/` to `.claude/haios/memory/` (or similar)
2. Update all imports to new package path
3. Update `.mcp.json`, justfile, all callers
4. Update `PYTHONPATH` references
5. Full test pass
6. Delete old `haios_etl/` directory

## Effort Estimate

Medium-High. Not urgent - current setup works. Consider when:
- Plugin needs to be truly portable (no project-root dependencies)
- Major refactoring already happening
- Epoch boundary with cleanup time

## References

- WORK-028: Investigation that discovered the issue
- `.mcp.json`: MCP server configuration
- `haios_etl/DEPRECATED.md`: Existing deprecation notes
