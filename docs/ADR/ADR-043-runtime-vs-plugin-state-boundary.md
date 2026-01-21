---
template: architecture_decision_record
status: accepted
date: 2026-01-21
adr_id: ADR-043
title: Runtime vs Plugin State Boundary
author: Hephaestus
session: 216
lifecycle_phase: decide
decision: accepted
spawned_by: CH-002
memory_refs: []
version: '1.0'
generated: 2026-01-21
last_updated: '2026-01-21T11:05:48'
---
# ADR-043: Runtime vs Plugin State Boundary

> **Status:** Accepted
> **Date:** 2026-01-21
> **Decision:** Approved (Session 216)

---

## Context

During triage of CH-002 (Session Simplify), a design question arose: should `.claude/session` live within `.claude/haios/` or at the `.claude/` level?

This surfaced a broader architectural question: **what is the boundary between the HAIOS plugin and its runtime outputs?**

---

## Decision Drivers

- **Portability principle:** `.claude/haios/` should be self-contained and copyable to another project
- **Clarity:** Developers should know what travels with the plugin vs what is project-specific
- **Existing precedent:** `haios-status.json`, `haios-events.jsonl` already live at `.claude/` level

---

## Considered Options

### Option A: All State in `.claude/haios/state/`

**Description:** Create a `state/` subdirectory within the plugin for runtime outputs.

```
.claude/haios/
├── config/
├── manifesto/
├── modules/
└── state/           # Runtime outputs
    ├── session
    ├── status.json
    └── events.jsonl
```

**Pros:**
- Everything in one place
- Plugin is fully self-contained
- Cleaner `.claude/` directory

**Cons:**
- Breaks existing paths (haios-status.json, events.jsonl)
- State travels with plugin on copy (may not be desired)
- Migration effort

### Option B: Runtime State at `.claude/` Level

**Description:** Keep runtime outputs at `.claude/` level, plugin code in `.claude/haios/`.

```
.claude/
├── haios/           # Plugin (portable)
│   ├── config/
│   ├── manifesto/
│   └── modules/
├── session          # Runtime state
├── haios-status.json
└── haios-events.jsonl
```

**Pros:**
- Matches existing precedent
- Clear separation: plugin vs project state
- No migration needed for existing files
- Plugin copy doesn't include project-specific state

**Cons:**
- State files scattered at `.claude/` level
- Less obvious what belongs to HAIOS

---

## Decision

**Adopt Option B: Runtime state at `.claude/` level**

The boundary is:

| Location | Contains | Characteristic |
|----------|----------|----------------|
| `.claude/haios/` | Plugin definition | Portable, copyable |
| `.claude/*.json`, `.claude/session` | Runtime state | Project-specific, generated |

**Rationale:**
1. Matches existing precedent (`haios-status.json`, `haios-events.jsonl`)
2. When copying plugin to new project, you want fresh state, not old session numbers
3. Clear mental model: "haios/ is the code, .claude/ files are the outputs"

---

## Consequences

**Positive:**
- Clear boundary definition
- Existing files don't need migration
- Plugin portability improved (copy haios/, leave state behind)

**Negative:**
- Runtime files at `.claude/` level aren't obviously "HAIOS files"
- Need to document which `.claude/` files are HAIOS-generated

**Neutral:**
- No code changes needed (just documentation)

---

## Implementation

- [x] Document boundary in this ADR
- [ ] Add comment header to runtime files identifying them as HAIOS-generated
- [ ] Update `.claude/haios/README.md` to reference this boundary
- [ ] CH-002 implementation uses `.claude/session` (not `.claude/haios/session`)

---

## References

- CH-002: Session Simplify (surfaced this question)
- Session 216: Triage discussion with operator
