---
id: CH-004
arc: migration
name: RecipeAudit
status: Active
created: 2026-01-27
spawned_from:
- WORK-027
generated: '2026-01-27'
last_updated: '2026-01-27T21:47:15'
---
# Chapter: Recipe Audit - Legacy Scaffolding Removal

## Purpose

Audit `just` recipes for legacy scaffolding that bypasses the module-first principle. Recipes like `just work`, `just inv`, `just scaffold` produce files with unfilled placeholders (`{{TYPE}}`, wrong session numbers) because they predate the cycle skills that properly populate work items.

## Context

Session 250: Agent called `just work INV-069 "title"` directly instead of using `/new-work` or `work-creation-cycle`. The resulting WORK.md had `type: {{TYPE}}`, wrong session number, and placeholder deliverables. This is a safety hazard - malformed artifacts can pass through governance gates because they're syntactically valid YAML.

## Traces

- Module-First Principle (Session 218): Commands/skills MUST call modules
- REQ-TRACE-005: Full traceability chain must exist
- Migration arc CH-004 definition in ARC.md: "70+ recipes: keep generic, remove HAIOS-specific"
