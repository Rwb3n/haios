---
template: investigation
status: complete
date: 2025-12-18
backlog_id: INV-012
title: "Investigation: Static Registration Anti-Pattern Mitigation"
author: Hephaestus
session: 85
lifecycle_phase: discovery
spawned_by: Session-85
related: [E2-091, ADR-038]
milestone: M3-Cycles
memory_refs: [72331-72336, 72337-72354]
version: "1.1"
---
# generated: 2025-12-18
# System Auto: last updated on: 2025-12-18 23:02:05
# Investigation: Static Registration Anti-Pattern Mitigation

@docs/README.md
@docs/epistemic_state.md

---

## Context

During Session 85, while verifying E2-091 (implementation-cycle skill), we discovered that the skill was correctly created but not appearing in vitals. Investigation revealed that `UpdateHaiosStatus.ps1` had **hardcoded static lists** for discoverable artifacts (skills, agents, commands) instead of dynamic discovery.

This is a systemic anti-pattern: when new artifacts are created, they exist on disk but aren't registered because registration is static, not dynamic.

---

## Objective

1. Document the static registration anti-pattern
2. Identify all instances in the codebase
3. Implement immediate fixes
4. Design comprehensive mitigation strategy

---

## Scope

### In Scope
- UpdateHaiosStatus.ps1 hardcodes
- Discovery mechanisms for skills, agents, commands
- Preventive measures (checklists, hooks, documentation)

### Out of Scope
- MCP tool counts (intentionally static - external dependency)
- Template type discovery (already dynamic via Get-ValidTemplates)

---

## Hypotheses

1. **H1:** Static registration exists because discovery wasn't needed initially - the system was small
2. **H2:** Other hardcodes may exist in hooks/commands that haven't been audited
3. **H3:** Adding runtime discovery verification to DoD will prevent recurrence

---

## Investigation Steps

1. [x] Identify initial instance (skills hardcode at line 60)
2. [x] Audit UpdateHaiosStatus.ps1 for all hardcoded lists
3. [x] Implement Get-Skills, Get-Agents, Get-Commands functions
4. [x] Fix slim status generation to use dynamic values
5. [x] Audit other hooks for similar patterns (no critical issues found)
6. [x] Update epistemic_state.md with anti-pattern
7. [x] Enhance implementation-cycle skill CHECK phase
8. [ ] Consider PreToolUse hook enhancement (deferred - L3 skill mitigation sufficient)

---

## Findings

### Instances Found and Fixed (Session 85)

| Location | Line | Original | Fix |
|----------|------|----------|-----|
| UpdateHaiosStatus.ps1 | 60 | `skills = @("extract-content", "memory-agent")` | `Get-Skills` function |
| UpdateHaiosStatus.ps1 | 61 | `agents = @("The-Proposer", "The-Adversary")` | `Get-Agents` function |
| UpdateHaiosStatus.ps1 | 879 | Hardcoded commands array | `$FullStatus.commands` |
| UpdateHaiosStatus.ps1 | 881 | `agents = @("schema-verifier")` | `$FullStatus.agents` |

### Root Cause

No dynamic discovery functions existed for:
- `.claude/skills/*/SKILL.md` (name from frontmatter)
- `.claude/agents/*.md` (name from frontmatter)
- `.claude/commands/*.md` (name from filename)

Templates already had dynamic discovery via `Get-ValidTemplates`.

### Verification

After fix:
```
Templates: 7 found
Agents: 1 found (was hardcoded as 2 stale agents)
Skills: 4 found (was hardcoded as 2)
Commands: 13 found (was hardcoded as 8)
```

---

## Mitigation Layers

| Layer | Mechanism | Status |
|-------|-----------|--------|
| **L1: Fix** | Dynamic discovery functions | DONE |
| **L2: Document** | Add to epistemic_state.md anti-patterns | DONE |
| **L3: Skill** | implementation-cycle CHECK phase enhancement | DONE |
| **L4: Memory** | Store pattern for future retrieval | DONE (72337-72354) |
| **L5: Audit** | Scan other hooks for similar patterns | DONE (no issues) |
| **L6: Hook** | PostToolUse auto-refresh on discoverable paths | DONE |

---

## Spawned Work Items

- [x] Skill discovery fix (Session 85 - immediate fix)
- [x] Agent discovery fix (Session 85 - immediate fix)
- [x] Command discovery fix (Session 85 - immediate fix)
- [~] E2-100: Audit all hooks for hardcoded lists - NOT NEEDED (L5 audit found no issues)

---

## Expected Deliverables

- [x] Findings report (this document)
- [x] Immediate fixes implemented
- [x] epistemic_state.md updated
- [x] implementation-cycle skill enhanced
- [x] Memory concepts stored (72337-72354)

---

## References

- `.claude/hooks/UpdateHaiosStatus.ps1` - Fixed file
- `docs/checkpoints/*SESSION-84*.md` - E2-091 skill creation
- Memory concepts 72331-72336 - Initial skill fix WHY

---
