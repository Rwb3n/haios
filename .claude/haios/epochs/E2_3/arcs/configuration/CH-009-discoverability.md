---
id: CH-009
arc: configuration
name: DiscoverabilityArchitecture
status: Active
created: 2026-01-26
spawned_from:
- obs-222-001
- obs-214-002
generated: '2026-01-26'
last_updated: '2026-01-26T19:29:24'
---
# Chapter: Discoverability Architecture Investigation

## Purpose

Design discoverability patterns for agent capabilities (recipes, commands, skills).

## Context

obs-222-001 and obs-214-002 documented that agents can't discover available capabilities. No `just help`, no `/spellbook`, no categorized recipe listing.

## Questions to Answer

1. What discoverability patterns exist in similar systems?
2. Should discoverability be recipe-based (`just help`) or command-based (`/help`)?
3. How should capabilities be categorized?
4. Where should discoverability metadata live (haios.yaml, skill frontmatter, etc.)?

## Success Criteria

- [ ] INV document with discoverability design
- [ ] Decision on implementation approach
- [ ] Spawn work items for implementation

## References

- obs-222-001: Discoverability patterns missing
- obs-214-002: CLAUDE.md bloat and recipe discoverability
