# generated: 2026-01-30
# System Auto: last updated on: 2026-01-30T19:06:36
---
id: OBS-262-001
session: 262
dimension: tooling
triage_status: pending
potential_action: skill-update
priority: low
---
# Observation: No /new-chapter Command

## What Was Observed

When creating CH-004-builder-interface.md, discovered there is no `/new-chapter` command for scaffolding chapter files.

## Context

- Chapters are part of the Arc > Chapter > Work hierarchy (ADR-042)
- We have governed creation paths for:
  - `/new-work` - work items
  - `/new-plan` - implementation plans
  - `/new-investigation` - investigations
  - `/new-adr` - architecture decision records
  - `/new-checkpoint` - session checkpoints
- But no `/new-chapter` for chapter specification files

## Impact

Had to manually create the chapter file, which:
- Bypasses any template consistency
- No frontmatter validation
- No automatic linking to Arc

## Potential Actions

1. **skill-update**: Add `/new-chapter` command that scaffolds chapter files with proper frontmatter and links to parent Arc
2. **defer**: Chapters are created infrequently, manual creation is acceptable
3. **investigate**: Determine if chapter scaffolding would provide enough value vs complexity

## Related

- ADR-042: Arc > Chapter > Work hierarchy
- CH-004: The chapter that triggered this observation
