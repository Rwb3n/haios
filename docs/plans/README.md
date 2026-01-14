---
template: readme
status: active
date: 2025-11-30
title: "Plans Directory Index"
component: documentation
---
# generated: 2025-11-30
# System Auto: last updated on: 2025-12-06 16:09:57
# Plans Directory

> **Progressive Disclosure:** [Quick Reference](../README.md) -> [Strategic Overview](../epistemic_state.md) -> **Plans (YOU ARE HERE)**
>
> **Navigation:** [Specs](../specs/) | [Checkpoints](../checkpoints/) | [Handoffs](../handoff/)

## References

- @docs/epistemic_state.md - Strategic state
- @docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md - System vision
- @docs/specs/memory_db_schema_v3.sql - Authoritative schema

## Structure

Plans are organized by date and sequence: `YY-MM-DD-NN-plan-name/`

## Active Plans

| Plan | Status | Description |
|------|--------|-------------|
| *None* | - | All current plans completed |

## Epoch 2 Plans (Session 35-36)

| Plan | Status | Description |
|------|--------|-------------|
| [PLAN-EPOCH2-001](PLAN-EPOCH2-001-HOOKS-WIRING.md) | COMPLETE | Debug Hooks Python Scripts |
| [PLAN-EPOCH2-002](PLAN-EPOCH2-002-COMMAND-VALIDATE.md) | COMPLETE | Implement /validate Command |
| [PLAN-EPOCH2-003](PLAN-EPOCH2-003-MEMORY-INTEGRATION.md) | COMPLETE | Memory Integration & Audit |
| [PLAN-EPOCH2-004](PLAN-EPOCH2-004-TEMPLATE-SCAFFOLDING.md) | COMPLETE | Template Scaffolding Commands |
| [PLAN-EPOCH2-005](PLAN-EPOCH2-005-UTILITY-COMMANDS.md) | COMPLETE | Utility Commands (/status, /coldstart) |
| [PLAN-EPOCH2-006](PLAN-EPOCH2-006-SYSTEM-AWARENESS.md) | COMPLETE | HAIOS System Awareness |
| [PLAN-EPOCH2-007](PLAN-EPOCH2-007-VERIFICATION.md) | COMPLETE | Verification & Investigation |

## Completed Plans (Recent First)

| Plan | Session | Status | Description |
|------|---------|--------|-------------|
| [PLAN-AGENT-ECOSYSTEM-002](PLAN-AGENT-ECOSYSTEM-002.md) | 17 | DRAFT | Agent Ecosystem MVP Hardening |
| [PLAN-AGENT-ECOSYSTEM-001](PLAN-AGENT-ECOSYSTEM-001.md) | 17 | COMPLETE | Agent Ecosystem Architecture (Interpreter, Ingester) |
| [PLAN-FIX-001](PLAN-FIX-001-schema-source-of-truth.md) | 16 | COMPLETE | Schema source-of-truth restoration |
| [PLAN-INVESTIGATION-001](PLAN-INVESTIGATION-001-synthesis-schema-bug.md) | 16 | COMPLETE | Schema drift investigation |
| [PLAN-SYNTHESIS-001](PLAN-SYNTHESIS-001-memory-consolidation.md) | 15c | COMPLETE | Memory Synthesis Pipeline |
| [TRD-SYNTHESIS-EXPLORATION](../specs/TRD-SYNTHESIS-EXPLORATION.md) | 15b | COMPLETE | Memory Synthesis exploration |
| [PLAN-REASONINGBANK-001](PLAN-REASONINGBANK-001-strategy-extraction.md) | 15 | COMPLETE | ReasoningBank strategy extraction |
| [25-11-27-01-phase-integration](25-11-27-01-phase-integration/) | 14 | COMPLETE | Phase 4/8 integration analysis |
| [25-11-26-01-refinement-layer](25-11-26-01-refinement-layer/) | 13b | COMPLETE | Knowledge Refinement Layer |

## Naming Convention

```
YY-MM-DD-NN-plan-name/
   |  |  |  |  |
   |  |  |  |  +-- Descriptive name (kebab-case)
   |  |  |  +-- Sequence number (01, 02, ...)
   |  |  +-- Day
   |  +-- Month
   +-- Year (2-digit)
```

## Plan Lifecycle

1. **DRAFT** - Initial creation, investigation phase
2. **ACTIVE** - Under development, stages in progress
3. **COMPLETE** - All stages done, ready for implementation or implemented
4. **SUPERSEDED** - Replaced by newer plan

---

## Bi-directional References

### This Document Links To:
- [epistemic_state.md](../epistemic_state.md) - Strategic overview
- [specs/](../specs/) - Technical specifications
- All plan files listed above

### Documents That Link Here:
- [README.md](../README.md) - Quick reference
- [epistemic_state.md](../epistemic_state.md) - Strategic overview

---
**Last Updated:** 2025-12-06
