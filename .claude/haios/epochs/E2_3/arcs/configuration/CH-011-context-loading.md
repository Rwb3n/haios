---
id: CH-011
arc: configuration
name: ContextLoadingArchitecture
status: Active
created: 2026-01-26
spawned_from:
- obs-208-001
- obs-208-002
generated: '2026-01-26'
last_updated: '2026-01-26T19:29:30'
---
# Chapter: Context Loading Architecture Investigation

## Purpose

Design thin bootstrap + on-demand context loading to address CLAUDE.md bloat.

## Context

obs-208-001 and obs-208-002 documented:
1. CLAUDE.md grows bloated despite previous trims
2. Post-compaction recovery pattern exists but is ad-hoc

## Questions to Answer

1. What belongs in bootstrap (CLAUDE.md) vs loaded on-demand?
2. How should post-compaction/crash recovery work?
3. Should there be a context-recovery skill/subagent?
4. What's the "spellbook" metaphor - agent capabilities as mastered spells?

## Success Criteria

- [ ] INV document with context-loading architecture
- [ ] Bootstrap vs reference separation design
- [ ] Recovery skill design (if warranted)

## References

- obs-208-001: CLAUDE.md bloat cycle
- obs-208-002: Post-compaction recovery pattern
- Operator insight: "spellbook" metaphor
