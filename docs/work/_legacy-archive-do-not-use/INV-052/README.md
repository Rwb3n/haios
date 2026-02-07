# generated: 2025-12-30
# System Auto: last updated on: 2026-01-02T21:45:32
# INV-052: HAIOS Architecture Reference

## What This Is

This investigation is the **canonical architecture documentation** for HAIOS. It's not just an audit - it's the process of refactoring HAIOS through documentation.

**The work:** Document every abstraction layer, find inconsistencies, resolve them, then spawn implementation items to make the code match the docs.

**Status:** All 6 architectural gaps DESIGNED. Ready for implementation spawning. See [GAPS.md](GAPS.md).

---

## Core Insight: Portable Plugin Architecture

HAIOS is a **portable plugin** that lives in `.claude/haios/` (or `.gemini/haios/`, etc.) and PUSHES to LLM-native formats:

```
.[claude|gemini|whatever]/haios/   ← PLUGIN SOURCE (LLM-agnostic)
├── config/                        ← Canonical manifests
│   ├── cycle-definitions.yaml
│   ├── skill-manifest.yaml
│   ├── agent-manifest.yaml
│   └── ...
        │
        │  Plugin installer generates...
        ▼
.claude/commands/, .claude/skills/, .claude/agents/   ← LLM-SPECIFIC
```

The plugin is portable. The generated output is LLM-specific.

---

## Why This Exists

Organic growth created inconsistencies:
- Hook handlers proliferated (22 handlers, no config)
- Skills added without normalization (7 cycles, 3 bridges, 5 utilities)
- State scattered across 6+ locations
- No single reference for "how does HAIOS work?"

This investigation creates that reference.

---

## Section Inventory (21 files)

### Design Sections (S148-S150, Complete)

| Section | Content |
|---------|---------|
| 1A | Hooks - Current state (22 handlers) |
| 1B | Hooks - Target architecture (19 handlers) |
| 2A | Session lifecycle (ephemeral) |
| 2B | Work item lifecycle (DAG, node_history) |
| 2C | Work item directory (self-contained universe) |
| 2D | ~~Cycle extensibility~~ (superseded by 2F) |
| 2E | Cycle skill analysis (7 cycles normalized) |
| 2F | Cycle definitions schema (YAML spec) |
| 2G | Cycle extension guide |
| 2 (diagram) | 8 ASCII lifecycle diagrams |
| 3 | State storage (WORK.md is truth) |
| 4 | Data flow (single writer principle) |

### Operational Sections (S151, Complete)

| Section | Content |
|---------|---------|
| 5 | Session number computation |
| 6 | Configuration surface (9 config files) |
| 7 | Justfile recipes (~50 recipes) |
| 8 | Memory integration (haios-memory MCP) |

### Abstraction Paradigm (S151, Complete)

| Section | Content |
|---------|---------|
| 9 | Slash commands (18 commands) |
| 10 | Skills taxonomy (7 cycles, 3 bridges, 5 utilities) |
| 11 | Subagents (7 agents) |
| 12 | Invocation paradigm (7-layer stack) |
| 13 | MCP servers (10 + 2 tools) |

### Bootstrap & Information Architecture (S152→S156, Design)

| Section | Content | Status |
|---------|---------|--------|
| 14 | Bootstrap architecture (L0-L4 Manifesto Corpus) | DESIGN |
| 15 | Information architecture (token budgets, drop order) | DESIGN |
| 16 | Scaffold templates (9 templates, L4 mapping) | DESIGN |

### Modular Architecture (S153, Design)

| Section | Content | Status |
|---------|---------|--------|
| 17 | 5-module black box architecture (ADR-040) | DESIGN |

### Gap Resolution Sections (S156, Design)

| Section | Content | Status |
|---------|---------|--------|
| 17.11 | Config file schemas (7 YAML files) | DESIGN |
| 17.12 | Implementation sequence (5 modules) | DESIGN |
| 17.13 | Migration path (4 violations) | DESIGN |
| 17.14 | Event schemas (7 events) | DESIGN |
| 17.15 | Error handling (5 modules) | DESIGN |
| 18 | Portable plugin specification | DESIGN |

---

## The 7-Layer Stack

```
LAYER 4: CYCLES        - Phase-based workflows (7)
LAYER 3: SKILLS        - Prompt orchestration (15)
LAYER 2: SUBAGENTS     - Isolated execution (7)
LAYER 1: COMMANDS      - Human entry points (18)
LAYER 0: RECIPES       - Shell execution (~50)
LAYER -1: HOOKS        - Automatic governance (22→19)
LAYER -2: MCP          - External tools (12)
```

---

## Key Design Decisions

| Decision | Choice |
|----------|--------|
| State ownership | WORK.md, not session events |
| Single writer | PostToolUse → node_history |
| Cycle normalization | YAML schema + thin executor + SKILL.md |
| Gate defense | objective_complete = deliverables + remaining_work + anti-pattern |
| Config path | `.claude/haios/config/` (future) |

---

## Verified Design Gaps (S153 → S156)

All 6 architectural gaps have been DESIGNED. See [GAPS.md](GAPS.md) for full details.

| Gap | Description | Status | Section |
|-----|-------------|--------|---------|
| G1 | Implementation Sequence | **DESIGNED** | S17.12 |
| G2 | Event Schema | **DESIGNED** | S17.14 |
| G3 | Error Handling | **DESIGNED** | S17.15 |
| G4 | Migration Path | **DESIGNED** | S17.13 |
| G5 | Config Files | **DESIGNED** | S17.11 |
| G6 | Portable Plugin Structure | **DESIGNED** | S18 |

### Per-Section Gaps

Each section 5-16 includes a "Gaps Identified" table with target fixes. These are implementation details; the 6 gaps above were architectural blockers (now resolved).

---

## Remaining Work

1. ~~Populate operational sections (S1-13)~~ - Complete (S151)
2. ~~Gap analysis per section~~ - Complete (S152)
3. ~~Full read-through and verification~~ - Complete (S153)
4. ~~Resolve 6 architectural gaps~~ - Complete (S156)
5. ~~Populate sections 14-16~~ - Complete (S156, aligned with Manifesto Corpus)
6. **Spawn implementation items** - Ready to spawn

---

## How to Continue

1. ~~Populate S14-16~~ - Complete (aligned with Manifesto Corpus L0-L4)
2. **Spawn implementation items** - Create E2-* work items from the specifications:
   - E2-240: Implement GovernanceLayer module
   - E2-241: Implement MemoryBridge module
   - E2-242: Implement WorkEngine module
   - E2-243: Implement ContextLoader module
   - E2-244: Implement CycleRunner module
   - E2-245: Implement Event Bus infrastructure
3. **Close INV-052** - After implementation items spawned
4. **The docs ARE the optimization** - Implementation just makes code match

---

## Session History

| Session | Focus | Outcome |
|---------|-------|---------|
| S148-150 | Initial audit, lifecycle design | Sections 1-4, lifecycle diagram |
| S151 | Operational sections | Sections 5-13 complete |
| S152 | Gap analysis, bootstrap sections | Sections 14-16 scaffolded, per-section gaps identified |
| S153 | Full read-through | 6 architectural gaps verified, GAPS.md created |
| S154-155 | Manifesto Corpus | L0-L4 created, integrated into coldstart |
| S156 | Gap resolution | All 6 gaps DESIGNED (S17.11-17.15, S18) |

---

*Last updated: Session 156*
