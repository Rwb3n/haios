---
template: work_item
id: INV-057
title: Commands Skills Templates Portability
status: complete
owner: Hephaestus
created: 2026-01-04
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: INV-056
blocked_by: []
blocks: []
enables: []
related:
- INV-056
- INV-052
- INV-053
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-04 19:46:59
  exited: null
cycle_docs: {}
memory_refs:
- 80746
- 80747
- 80748
- 80749
- 80750
- 80751
- 80752
- 80753
- 80754
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-04T22:31:49'
---
# WORK-INV-057: Commands Skills Templates Portability

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** INV-056 focused on hooks migrating to modules, but commands, skills, and templates are also consumers of `.claude/lib/` code. For Epoch 2.2 Chariot Architecture to be complete, the modules MUST be interface-agnostic (MUST NOT be coupled to Claude Code CLI).

**Root cause:** INV-056 scope was limited to hooks. The Chariot architecture requirement (Memory 80692-80695) states that modules MUST work with any interface (CLI, API, IDE plugin), not just Claude Code.

**Source:** INV-056 observation (Memory 80690): "hooks are one consumer, but commands/skills/templates are also consumers that need module-based implementation"

---

## Findings (Session 172)

### Investigation Objective Reframed

**Original question:** Do commands, skills, templates have lib/ imports that break portability?
**Correct question:** Can HAIOS be distributed as a portable Claude Code plugin?

The lib/ imports question is **secondary**. The primary gap is **structural**: commands/skills/templates live in Claude CLI target paths (`.claude/commands/`, `.claude/skills/`), not in the portable plugin source (`.claude/haios/`).

### Current Structure vs. Target (SECTION-18)

| Component | Target Location (SECTION-18) | Current Location | Gap |
|-----------|------------------------------|------------------|-----|
| Config | `.claude/haios/config/` | `.claude/haios/config/` | None |
| Manifesto | `.claude/haios/manifesto/` | `.claude/haios/manifesto/` | None |
| Modules | `.claude/haios/modules/` | `.claude/haios/modules/` | None |
| Commands | `.claude/haios/commands/` (source) | `.claude/commands/` (target only) | MISSING |
| Skills | `.claude/haios/skills/` (source) | `.claude/skills/` (target only) | MISSING |
| Agents | `.claude/haios/agents/` (source) | `.claude/agents/` (target only) | MISSING |
| Hooks | `.claude/haios/hooks/` | `.claude/hooks/` (target only) | MISSING |
| manifest.yaml | `.claude/haios/manifest.yaml` | N/A | MISSING |

### Code Portability Issues

#### Commands (4 issues found)
| File | Issue | Severity |
|------|-------|----------|
| `status.md` | Deprecated `haios_etl.*` imports | High |
| `validate.md` | Direct PowerShell invocation | High |
| `new-handoff.md` | PowerShell + Windows-only syntax | Critical |
| `README.md` | References .ps1 scripts | High |

#### Skills (6 issues found)
| File | Issue | Severity |
|------|-------|----------|
| `investigation-cycle`, `routing-gate`, `close-work-cycle`, `implementation-cycle` | References non-existent `routing` module | High |
| `close-work-cycle`, `observation-triage-cycle` | References non-existent `observations` module | High |
| `close-work-cycle`, `implementation-cycle` | References non-existent `governance_events` module | High |
| `extract-content` | Deprecated `haios_etl.extraction` import | Medium |
| `dod-validation-cycle` | Direct `.claude/lib/validate.py` reference | Low |

#### Templates
**CLEAN** - All 9 templates are fully portable with no code dependencies.

### Conclusion

**H1 CONFIRMED:** Commands, skills, templates have portability issues, but NOT the ones originally hypothesized.

**Root cause:** No plugin manifest or source structure exists. SECTION-18-PORTABLE-PLUGIN-SPEC.md is a DESIGN, not implementation. The "push model" installer that transforms source to target format doesn't exist.

**Immediate gaps:**
1. No `manifest.yaml` to declare plugin components
2. No source structure under `.claude/haios/` for commands/skills/agents
3. Commands still use PowerShell directly (should use `just` recipes)
4. Skills reference Python modules that don't exist (`routing`, `observations`, `governance_events`)

---

## Deliverables

- [x] Analyze `.claude/commands/*.md` for lib/ imports
- [x] Analyze `.claude/skills/*/SKILL.md` for lib/ dependencies
- [x] Analyze `.claude/templates/*.md` for any lib/ coupling
- [x] Identify portability gaps (what couples to Claude Code CLI?)
- [x] Design module-based approach → **SECTION-18 already defines this**
- [x] Spawn implementation work items (E2-269, E2-270, E2-271)

---

## Spawned Work Items

| ID | Title | Purpose |
|----|-------|---------|
| E2-269 | manifest.yaml Creation | Create plugin manifest per SECTION-18 schema |
| E2-270 | Command PowerShell Elimination | Replace remaining PowerShell calls with just recipes |
| E2-271 | Skill Module Reference Cleanup | Remove/implement non-existent module references |

---

## History

### 2026-01-04 - Created (Session 169)
- Spawned from INV-056 observation (gap noticed during investigation)
- Operator requirement: "modules MUST NOT be coupled to Claude Code CLI" (Memory 80694)

### 2026-01-04 - Investigated (Session 172)
- Read SECTION-17, SECTION-18, SECTION-9, SECTION-10 from INV-052
- Analyzed commands: 4 portability issues (PowerShell, deprecated imports)
- Analyzed skills: 6 portability issues (non-existent module references)
- Analyzed templates: CLEAN
- Identified structural gap: no manifest.yaml, no source structure
- Spawned E2-269, E2-270, E2-271

---

## References

- INV-056: Hook-to-Module Migration Investigation (parent)
- Memory 80690-80695: Portability requirement findings
- INV-052: Session-State-System-Audit (full architecture documentation)
- INV-052/SECTION-18-PORTABLE-PLUGIN-SPEC.md: Target manifest schema
- INV-053: HAIOS Modular Architecture Review (5-module design)
