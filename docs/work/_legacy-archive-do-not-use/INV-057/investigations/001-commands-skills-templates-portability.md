---
template: investigation
status: active
date: 2026-01-04
backlog_id: INV-057
title: Commands Skills Templates Portability
author: Hephaestus
session: 171
lifecycle_phase: hypothesize
spawned_by: null
related:
- docs/work/active/INV-052/
- docs/work/archive/INV-053/
memory_refs: []
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-04T22:17:27'
---
# Investigation: Commands Skills Templates Portability (REVISED)

@docs/README.md
@docs/epistemic_state.md
@docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md
@docs/work/archive/INV-053/investigations/001-haios-modular-architecture-review.md

---

## Context

**Trigger:** INV-053 designed the Chariot architecture (`.claude/haios/` with config/ + modules/). E2-264 migrated hooks to modules. But commands, skills, templates are OUTSIDE the Chariot - they live in `.claude/commands/`, `.claude/skills/`, `.claude/templates/`.

**Problem Statement:** If HAIOS is a portable Claude Code plugin, the entire Chariot must be self-contained and installable in any project. Currently commands/skills/templates are scattered outside `.claude/haios/`, breaking portability.

**Prior Observations:**
- Memory 76938: "HAIOS must be restructured as a portable Claude Code plugin"
- Memory 80363: "Portable plugin structure (.claude/haios/) has no manifest.yaml spec"
- INV-053 Chariot diagram shows `.claude/haios/` as the portable unit

---

## Objective

**What changes are needed to make HAIOS a fully portable Claude Code plugin where commands, skills, and templates are bundled within or referenced by the Chariot?**

---

## Scope

### In Scope
- Current location of commands, skills, templates vs Chariot location
- Plugin manifest requirements (plugin.json per Claude Code spec)
- Path references that would break if `.claude/haios/` is copied to another project
- Design for portable structure

### Out of Scope
- Module implementation (already done)
- Hook migration (E2-264 complete)
- haios_etl migration

---

## Hypotheses

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Commands/skills/templates need to move INTO `.claude/haios/` for true portability | High | Check if they reference paths outside haios/ | 1st |
| **H2** | A plugin.json manifest is needed to declare all components | High | Check Claude Code plugin spec | 2nd |
| **H3** | Current justfile recipes are NOT portable (project-specific) | High | Check justfile for absolute/relative paths | 3rd |

---

## Exploration Plan

### Phase 1: Evidence Gathering
1. [ ] List current locations: commands/, skills/, templates/ vs haios/
2. [ ] Check Claude Code plugin.json spec requirements
3. [ ] Check justfile for portability issues

### Phase 2: Hypothesis Testing
4. [ ] Test H1: Would copying haios/ alone break commands/skills?
5. [ ] Test H2: What does plugin.json need to declare?
6. [ ] Test H3: What justfile recipes reference project-specific paths?

### Phase 3: Design
7. [ ] Design target directory structure for portable Chariot
8. [ ] Design plugin.json manifest
9. [ ] Spawn implementation work items

---

## Findings

### Current Structure (Problem)

Per INV-052 Section 17, the Chariot is `.claude/haios/` containing:
- `config/` - 3 config files
- `modules/` - 5 black box modules

But commands/skills/templates are OUTSIDE:
- `.claude/commands/*.md` - 19 command files
- `.claude/skills/*/SKILL.md` - 15 skill files
- `.claude/templates/*.md` - 9 template files

**If you copy `.claude/haios/` to another project, you get modules but NO commands/skills/templates.**

### Hypothesis Verdicts

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| H1 | **CONFIRMED** | Commands/skills reference justfile which references `.claude/haios/modules/cli.py`. Copying haios/ alone breaks the chain. |
| H2 | **CONFIRMED** | No plugin.json exists. Claude Code plugins need manifest to declare components. |
| H3 | **CONFIRMED** | Justfile has hardcoded paths like `python .claude/haios/modules/cli.py` - not portable. |

### Target Structure (Design)

```
.claude/haios/                    # THE PORTABLE CHARIOT
├── plugin.json                   # Claude Code plugin manifest
├── config/
│   ├── haios.yaml
│   ├── cycles.yaml
│   └── components.yaml
├── modules/                      # 5 black box modules
│   ├── context_loader.py
│   ├── governance_layer.py
│   ├── memory_bridge.py
│   ├── work_engine.py
│   └── cycle_runner.py
├── commands/                     # MOVED from .claude/commands/
│   └── *.md
├── skills/                       # MOVED from .claude/skills/
│   └── */SKILL.md
├── templates/                    # MOVED from .claude/templates/
│   └── *.md
├── hooks/                        # MOVED from .claude/hooks/
│   └── hooks/*.py
└── lib/                          # MOVED from .claude/lib/
    └── *.py
```

### Key Design Decision

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bundle everything in haios/ | Yes | Single portable directory = single install |
| Use plugin.json | Yes | Claude Code standard for plugin discovery |
| Keep justfile in project root | Yes | Project-specific execution, not plugin concern |

---

## Spawned Work Items

### Immediate

- [ ] **E2-267: Plugin Structure Migration**
  - Move commands/, skills/, templates/, hooks/, lib/ INTO `.claude/haios/`
  - Create plugin.json manifest
  - Update all path references
  - Spawned via: `/new-work E2-267 "Plugin Structure Migration"`

- [ ] **E2-268: Plugin.json Manifest**
  - Define Claude Code plugin manifest schema
  - Declare all components (commands, skills, templates, hooks, agents)
  - Spawned via: `/new-work E2-268 "Plugin.json Manifest"`

---

## References

- **docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md** - Defines the 5-module Chariot architecture
- **docs/work/archive/INV-053/investigations/001-haios-modular-architecture-review.md** - Chariot diagram (lines 306-344)
- Memory 76938: "HAIOS must be restructured as a portable Claude Code plugin"
- Memory 80363: "Portable plugin structure (.claude/haios/) has no manifest.yaml spec"
