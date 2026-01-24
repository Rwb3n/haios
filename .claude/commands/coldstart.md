---
allowed-tools: Read, Glob, Bash, mcp__haios-memory__memory_search_with_experience,
  mcp__haios-memory__db_query
description: Initialize session by loading essential context files
generated: '2025-12-25'
last_updated: '2026-01-24T18:42:52'
---

# Cold Start Initialization

**MUST** run at the start of every session.

---

## Step 1: Load Config

Read `.claude/haios/config/haios.yaml` first - this drives everything else.

Extract:
- `epoch.epoch_file` - path to current epoch
- `epoch.active_arcs` - list of active arcs (ADR-042: arcs > chapters)
- `epoch.arcs_dir` - path to arcs directory

---

## Step 2: Identity Context (Injected - WORK-009)

The identity context is loaded by `just coldstart` and injected into context.

**No Read calls needed** - identity content appears in the `=== IDENTITY ===` block above.

Extract from the injected content:
- **Mission:** The Prime Directive (from L0-telos)
- **Companion Relationship:** Trust principles (from L0-telos)
- **Constraints:** Known operator constraints (from L1-principal)
- **Principles:** Core behavioral principles (from L3-requirements)
- **L4 Context Loading:** Technical patterns (from L4-implementation)

This replaces manual reads of L0-L4 manifesto files with extracted essence (~50 lines vs 1137 lines).

---

## Step 3: Load Epoch Context (MUST)

**MUST** read from paths in haios.yaml:

1. Read `epoch.epoch_file` - current epoch definition
2. For each arc in `epoch.active_arcs`:
   - Read `{epoch.arcs_dir}/{arc}/ARC.md`

---

## Step 4: Load Session Context (CH-005)

Session context is loaded by `just session-context` and provides:
- Prior session number and completed work
- Memory refs from checkpoint (queried automatically)
- Drift warnings (PROMINENT - cannot be missed)
- Pending items for work selection

```bash
just session-context
```

**No manual checkpoint/memory queries needed** - SessionLoader extracts and formats everything.

The output includes a `=== DRIFT WARNINGS ===` section. If non-empty, note these before proceeding.

---

## Step 5: Load Principles (from manifest)

For each file in checkpoint's `load_principles`:
- Read the file
- Note key principles that govern this session's work

**Note:** Memory refs are already loaded by Step 4. Only `load_principles` requires manual reads.

---

## Step 6: Load Agent Instructions

Read `CLAUDE.md` - agent bootstrap and quick reference.

---

## Step 7: Session Start

```bash
just session-start {N}
```

Where N = current session + 1 from `.claude/session` (read last line as integer, increment by 1).

**Note (CH-002):** Session number now lives in `.claude/session` for simplicity. Use `tail -1 .claude/session` to read current value.

---

## Step 8: Summary Output

Provide brief summary:
- **Manifesto loaded:** L0-L4 (confirm read)
- **Epoch context:** Which epoch + which arcs loaded
- **Principles loaded:** Which files from `load_principles`
- **Memory loaded:** From `just session-context` output
- **Drift warnings:** Any from session context output

---

## Step 9: Invoke Survey Cycle

**MUST** chain to survey-cycle for work selection:

```
Skill(skill="survey-cycle")
```

Survey-cycle owns routing:
- Checks checkpoint `pending` for prior work
- Presents options from `just ready`
- Routes to correct cycle based on work type

---

## Key Principle

**Ground yourself first. Config → Manifesto → Epoch → Checkpoint → Survey.**

Coldstart loads context. Survey-cycle selects work. Agent doesn't skip the chain.
