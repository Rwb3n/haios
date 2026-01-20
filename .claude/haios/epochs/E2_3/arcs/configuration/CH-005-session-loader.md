# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:06:18
# Chapter: Session Loader

## Definition

**Chapter ID:** CH-005
**Arc:** configuration
**Status:** Planned
**Depends:** CH-002 (Session Simplify), CH-003 (Loader Base)

---

## Problem

Agent manually reads checkpoint, parses frontmatter, queries memory IDs individually.

Current state:
```
1. Find latest checkpoint (ls + sort)
2. Read checkpoint file
3. Parse frontmatter for load_memory_refs
4. For each ID, query memory
5. Parse frontmatter for drift_observed
6. Parse frontmatter for pending
```

6 steps, multiple tools, fragile.

---

## Agent Need

> "What happened last session? What should I know? What's drifting?"

---

## Requirements

### R1: Session Extraction Config

```yaml
# config/loaders/session.yaml
sources:
  session_number:
    file: "{discovery.session}"
    type: integer

  checkpoint:
    method: latest
    directory: docs/checkpoints/
    extract:
      prior_session: frontmatter.session
      pending: frontmatter.pending
      drift: frontmatter.drift_observed
      memory_refs: frontmatter.load_memory_refs
      completed: frontmatter.completed
      discoveries: frontmatter.key_discoveries

  memory:
    method: query_ids
    ids: "{checkpoint.memory_refs}"
    fields: [id, type, content]
```

### R2: Memory Integration

Loader queries memory refs and formats inline:

```yaml
output:
  template: |
    === SESSION {session_number} ===
    Prior: {checkpoint.prior_session}

    Completed last session:
    {checkpoint.completed}

    Key discoveries:
    {checkpoint.discoveries}

    Memory context:
    {memory}

    Drift warnings:
    {checkpoint.drift}

    Pending:
    {checkpoint.pending}
```

### R3: Drift Prominence

Drift warnings appear clearly. Agent cannot miss them.

### R4: Single Invocation

```bash
just session-context
# Outputs everything agent needs about session state
```

---

## Interface

```bash
just session-context
# Outputs formatted session context
```

---

## Success Criteria

- [ ] Session context loaded via one command
- [ ] Memory refs queried and included
- [ ] Drift warnings prominent
- [ ] Coldstart Phase 2 uses this loader

---

## Non-Goals

- Session history beyond last checkpoint
- Memory search (just ID lookup)
- Work item details (that's work loader)
