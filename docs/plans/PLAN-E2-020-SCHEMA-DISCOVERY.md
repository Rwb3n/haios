---
template: implementation_plan
status: complete
date: 2025-12-09
backlog_id: E2-020
title: "Schema Discovery via Skill-Limited Subagent"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-09
# System Auto: last updated on: 2025-12-09 20:11:15
# Implementation Plan: Schema Discovery via Skill-Limited Subagent

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Prevent schema assumption errors by implementing context-efficient schema verification using the skill-limited subagent pattern. Agent must verify table/column names before executing SQL.

**Success Criteria:**
- SQL queries blocked until schema verified via subagent
- Main context receives only verified schema info (not full 500-line schema file)
- Pattern reusable for other reference lookups

---

## Problem Statement

**Proven Failure Pattern (Session 51):**
1. Query 1: `SELECT COUNT(*) FROM clusters` - Error: no such table
2. Query 2: `SELECT COUNT(*) FROM synthesis_cluster` - Error (missed 's')
3. Query 3: Listed tables, found `synthesis_clusters`

Result: 2 wasted queries before doing the right thing. This is a recurring anti-pattern.

**Root Cause:** Agent assumes schema instead of verifying. CLAUDE.md warning exists but no enforcement.

**Memory Reference:** Concepts 64679-64696 (E2-020 investigation findings)

---

## Methodology: AODEV TDD

```
OBSERVE -> ANALYZE -> DECIDE -> EXECUTE -> VERIFY
              |          |
              v          v
           (Tests)   (Implementation)
```

Each phase writes tests BEFORE implementation. Red-Green-Refactor.

**For this plan:**
- OBSERVE: Proven failure pattern documented above
- ANALYZE: Design pattern validated against reference docs
- DECIDE: DD-E2-020-01 to DD-E2-020-04 recorded
- EXECUTE: Create skill → subagent → hook → command (tests first per component)
- VERIFY: Verification criteria defined below

---

## Design: Subagent + Skill Composition Pattern

**Core Insight:** Subagent with restricted tools + auto-discovered skill provides maximum context economy:
- Subagent operates in isolated context with `tools: [Read, Bash]`
- Skill auto-discovered based on description match (NOT tool restriction)
- Skill provides PROCEDURE, subagent tools EXECUTE it
- Returns only result to parent
- Both contexts stay isolated from main conversation

**How Subagents Use Skills:**
Per Anthropic blog (Nov 2025): "Subagents can access and use Skills just like the main agent."
Skills are auto-discovered, not tool-invoked. `Skill` is NOT a valid tool name.

**Enforcement:** Subagent system prompt makes skill usage MANDATORY, not optional.
Pattern: "You MUST use the schema-ref skill. Do not proceed without it."

**Flow:**
```
Main Context -> Task(schema-verifier) -> [Skill auto-discovered] -> Read/Bash executes -> Result -> Subagent discarded
```

**Memory Reference:** Concepts 64697-64721 (corrected pattern)

---

## Proposed Changes

### 1. Create schema-ref Skill
- [ ] Create `.claude/skills/schema-ref/SKILL.md`
- [ ] Include sqlite3 PRAGMA commands for table info
- [ ] Include `.tables` listing command
- [ ] Reference `@docs/specs/memory_db_schema_v3.sql` as fallback

### 2. Create schema-verifier Subagent
- [ ] Create `.claude/agents/schema-verifier.md`
- [ ] Restrict tools to `[Read, Bash]` (skill auto-discovered, not tool-restricted)
- [ ] Instructions: MUST use schema-ref skill (enforced in system prompt)
- [ ] System prompt: "You MUST use the schema-ref skill. Do not proceed without it."

### 3. Add PreToolUse Hook (Hard Block)
- [ ] Extend `PreToolUse.ps1` to match Bash tool
- [ ] Detect SQL keywords (SELECT|INSERT|UPDATE|DELETE|FROM) in command
- [ ] Block with `permissionDecision: deny`
- [ ] Message: "SQL blocked. Use Task(schema-verifier) first."

### 4. Add /schema Command (Convenience)
- [ ] Create `.claude/commands/schema.md`
- [ ] Quick lookup: `/schema <table>` runs PRAGMA table_info
- [ ] `/schema` alone lists all tables

---

## Verification

- [ ] SQL query without verification is blocked by hook
- [ ] Task(schema-verifier, "concepts") returns column info
- [ ] Main context does NOT contain full schema file after verification
- [ ] `/schema concepts` returns column info
- [ ] Pattern documented in CLAUDE.md

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Legitimate SQL in scripts blocked | Medium | Hook checks if query matches known safe patterns |
| SQL in test assertions blocked | Medium | Hook allows if path contains `/tests/` |
| Subagent overhead for simple queries | Low | /schema command as lightweight alternative |
| False positive SQL detection | Low | Require FROM keyword + table-like word |

---

## Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-E2-020-01 | 4-layer approach (skill + subagent + hook + command) | Each layer serves different purpose |
| DD-E2-020-02 | Subagent + skill composition (not skill-restricted) | Skills auto-discovered, not tool-invoked |
| DD-E2-020-03 | Hard block (not soft warn) | Per operator: "lets hard block on sql detection" |
| DD-E2-020-04 | Subagent tools: [Read, Bash] | Minimum tools needed; `Skill` not a valid tool name |

---

## References

- Memory: Concepts 64679-64696 (investigation), 64697-64721 (corrected pattern)
- Spec: `.claude/SUBAGENTS-REF.md` (subagent tools restriction)
- Spec: `.claude/SKILLS-REF.md` (skill progressive disclosure)
- Spec: `.claude/HOOKS-REF.md` (PreToolUse blocking)
- Blog: `skills-subagents-blog-post.txt` (Anthropic Nov 2025 - subagents use skills)
- Pattern: `PreToolUse.ps1` (existing governance hook)
- Pattern: `memory-agent` skill (existing skill structure)

---


<!-- VALIDATION ERRORS (2025-12-09 20:11:07):
  - ERROR: Invalid status 'completed' for implementation_plan template. Allowed: draft, approved, rejected, complete
-->
