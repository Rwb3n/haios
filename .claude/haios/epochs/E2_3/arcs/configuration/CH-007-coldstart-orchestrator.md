# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:06:55
# Chapter: Coldstart Orchestrator

## Definition

**Chapter ID:** CH-007
**Arc:** configuration
**Status:** Planned
**Depends:** CH-004, CH-005, CH-006

---

## Problem

Coldstart is a markdown file with instructions. Agent interprets and executes.

Current state:
```
/coldstart
  → Agent reads coldstart.md
  → Agent follows 10 steps
  → Agent makes 15+ Read calls
  → Agent invokes survey-cycle
```

Procedural. Fragile. Token-heavy.

---

## Agent Need

> "Initialize me. Give me context in phases. Let me breathe between."

---

## Requirements

### R1: Coldstart Config

```yaml
# config/coldstart.yaml
phases:
  - id: identity
    loader: loaders/identity.yaml
    recipe: just identity
    breathe: true

  - id: session
    loader: loaders/session.yaml
    recipe: just session-context
    breathe: true

  - id: work
    loader: loaders/work.yaml
    recipe: just work-options
    breathe: false
    next: selection
```

### R2: Phase Execution

```bash
just coldstart
# Executes all phases in order with breathing room markers
```

Output:
```
[PHASE 1: IDENTITY]
{identity output}

[BREATHE]

[PHASE 2: SESSION]
{session output}

[BREATHE]

[PHASE 3: WORK]
{work output}

[READY FOR SELECTION]
```

### R3: Breathing Room

`[BREATHE]` marker tells agent: process before continuing.

Future: Agent self-evaluates understanding. Misalignment triggers re-init.

### R4: No Manual Reads

Agent does not invoke Read tool during coldstart. All context injected via recipe output.

---

## Interface

```bash
just coldstart
# Full coldstart with all phases
```

Or individual phases:
```bash
just identity
just session-context
just work-options
```

---

## Success Criteria

- [ ] Coldstart runs via single `just coldstart`
- [ ] No Read tools invoked by agent
- [ ] Phases clearly separated
- [ ] Breathing room marked
- [ ] Agent receives same information as current coldstart (content parity)

---

## Non-Goals

- Agent self-evaluation (future)
- Re-initialization logic (future)
- Parallel phase loading
