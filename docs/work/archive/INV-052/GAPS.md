# generated: 2026-01-01
# System Auto: last updated on: 2026-01-02T20:16:06
# INV-052: Verified Design Gaps

Generated: 2026-01-01 (Session 153)
Purpose: Track gaps that must be resolved before spawning implementation work

---

## Overview

After full read-through of all 17 sections, these gaps were verified as blocking implementation readiness. Each gap must be addressed before INV-052 can close and spawn E2-* implementation items.

---

## Gap Tracker

| # | Gap | Status | Section Impact | Priority |
|---|-----|--------|----------------|----------|
| G1 | Implementation Sequence | **DESIGNED** | S17.12 | HIGH |
| G2 | Event Schema | **DESIGNED** | S17.14 | HIGH |
| G3 | Error Handling | **DESIGNED** | S17.15 | MEDIUM |
| G4 | Migration Path | **DESIGNED** | S17.13 | HIGH |
| G5 | Config Files | **DESIGNED** | S17.11 | HIGH |
| G6 | Portable Plugin Structure | **DESIGNED** | S18 | MEDIUM |

---

## G1: Implementation Sequence

**Status:** DESIGNED (Session 156)

**Problem:** No defined build order for the 5 modules. Which module do we implement first? What are the dependencies between modules?

**Evidence:**
- Section 17.2 maps sections to modules but doesn't specify build order
- Module dependencies (17.3-17.7) show inter-module calls but no sequencing

**Resolution:**
- [x] Module dependency graph created
- [x] Build order defined: GovernanceLayer → MemoryBridge → WorkEngine → ContextLoader → CycleRunner
- [x] Circular dependency (MemoryBridge ↔ WorkEngine) resolved via late binding
- [x] Validation checkpoints defined for each phase

**Reference:** SECTION-17.12-IMPLEMENTATION-SEQUENCE.md

---

## G2: Event Schema

**Status:** DESIGNED (Session 156)

**Problem:** Section 17.9 lists 7 inter-module events but no JSON schema for payloads.

**Evidence:**
```
| Event | Producer | Consumers | Payload |
|-------|----------|-----------|---------|
| SessionStarted | ContextLoader | GovernanceLayer | `{session, prior}` |
```
Payload `{session, prior}` is a sketch, not a schema.

**Resolution:**
- [x] JSON Schema draft-07 for all 7 events
- [x] Common envelope structure (type, version, timestamp, session, payload)
- [x] Required vs optional fields specified
- [x] Type constraints with enums and patterns
- [x] Event versioning strategy (1.x backward-compatible, 2.x breaking)
- [x] events.yaml config file schema

**Reference:** SECTION-17.14-EVENT-SCHEMAS.md

---

## G3: Error Handling

**Status:** DESIGNED (Session 156)

**Problem:** No specification for what happens when modules fail.

**Evidence:**
- Section 17.3 (ContextLoader): What if north-star.md is missing?
- Section 17.4 (WorkEngine): What if invalid node transition requested?
- Section 17.5 (CycleRunner): What if gate fails unexpectedly?
- Section 17.6 (MemoryBridge): What if MCP server times out?

**Resolution:**
- [x] Error types taxonomy with module-prefixed codes (CL, WE, CR, MB, GL)
- [x] Four error categories: critical, blocking, degraded, warning
- [x] Per-module error handling with propagation strategies
- [x] Recovery mechanisms: retry, fallback, escalation
- [x] ErrorOccurred event schema
- [x] Cycle phase error behavior defined

**Reference:** SECTION-17.15-ERROR-HANDLING.md

---

## G4: Migration Path

**Status:** DESIGNED (Session 156)

**Problem:** Section 17.10 identifies 4 boundary violations in current code but no migration strategy.

**Evidence:**
```
| Violation | Current | Module A | Module B | Fix |
|-----------|---------|----------|----------|-----|
| Hook reads WORK.md | post_tool_use.py edits node_history | GovernanceLayer | WorkEngine | ? |
```
The "Fix" column has descriptions but no migration steps.

**Resolution:**
- [x] All 4 violations analyzed with current code locations
- [x] Target architecture specified for each
- [x] Migration steps defined with phases (M1a/M1b/M1c, etc.)
- [x] Backward compatibility concerns addressed
- [x] Migration order: V3 → V2 → V1 (V4 marked acceptable)
- [x] Event bus prerequisite identified

**Reference:** SECTION-17.13-MIGRATION-PATH.md

---

## G5: Config Files

**Status:** DESIGNED (Session 156)

**Problem:** Multiple sections reference YAML config files that don't exist.

**Evidence:**
- Section 2F: `.claude/haios/config/cycle-definitions.yaml` - referenced but not created
- Section 17: `.claude/haios/config/gates.yaml` - referenced but not created
- Section 10: `.claude/haios/config/skill-manifest.yaml` - referenced but not created
- Section 11: `.claude/haios/config/agent-manifest.yaml` - referenced but not created

**Resolution:**
- [x] Consolidated all config file schemas in Section 17.11
- [x] cycle-definitions.yaml - Schema defined
- [x] gates.yaml - Schema defined
- [x] skill-manifest.yaml - Schema defined
- [x] agent-manifest.yaml - Schema defined
- [x] hook-handlers.yaml - Schema defined
- [x] node-bindings.yaml - Schema defined
- [x] thresholds.yaml - Schema defined

**Reference:** SECTION-17.11-CONFIG-FILE-SCHEMAS.md

**Note:** manifest.yaml deferred to G6 (Portable Plugin Structure)

---

## G6: Portable Plugin Structure

**Status:** DESIGNED (Session 156)

**Problem:** Multiple sections mention `.claude/haios/` as portable plugin root but no manifest or installation mechanism defined.

**Evidence:**
- Section 6: Shows target structure but no manifest.yaml spec
- Section 12: Mentions "plugin installer PUSHES to LLM-native format" but no mechanism
- Section 14: References `.claude/haios/bootstrap/` but doesn't exist

**Resolution:**
- [x] manifest.yaml schema with components, targets, dependencies
- [x] Directory structure for LLM-agnostic source
- [x] Installation mechanism with pre/post hooks
- [x] LLM target transformation rules (Claude CLI)
- [x] Versioning strategy (semver + migrations)
- [x] LLM-agnostic design principles defined

**Reference:** SECTION-18-PORTABLE-PLUGIN-SPEC.md

---

## Resolution Order (Proposed)

Based on dependencies:

1. **G5: Config Files** - Creates the foundation files other gaps reference
2. **G1: Implementation Sequence** - Needed to understand build order
3. **G4: Migration Path** - Depends on knowing sequence
4. **G2: Event Schema** - Can be done in parallel with G4
5. **G3: Error Handling** - Depends on understanding normal flow first
6. **G6: Portable Plugin** - Can be done last (optimization)

---

## Progress Log

| Date | Session | Gap | Action | Status |
|------|---------|-----|--------|--------|
| 2026-01-01 | S153 | All | Identified and documented 6 gaps | OPEN |
| 2026-01-02 | S156 | G5 | Created SECTION-17.11 with all config schemas | DESIGNED |
| 2026-01-02 | S156 | G1 | Created SECTION-17.12 with build order and dependency graph | DESIGNED |
| 2026-01-02 | S156 | G4 | Created SECTION-17.13 with migration steps for 4 violations | DESIGNED |
| 2026-01-02 | S156 | G2 | Created SECTION-17.14 with JSON schemas for 7 events | DESIGNED |
| 2026-01-02 | S156 | G3 | Created SECTION-17.15 with error handling per module | DESIGNED |
| 2026-01-02 | S156 | G6 | Created SECTION-18 with portable plugin specification | DESIGNED |

---

*This file tracks design gaps. When all gaps are CLOSED, INV-052 can proceed to CONCLUDE phase.*
