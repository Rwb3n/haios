---
allowed-tools: Read, Glob, Bash, mcp__haios-memory__memory_search_with_experience,
  mcp__haios-memory__db_query
description: Initialize session by loading essential context files
generated: '2025-12-25'
last_updated: '2026-01-24T20:49:21'
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

## Step 2: Load Context via Orchestrator (WORK-011)

Run the unified coldstart orchestrator:

```bash
just coldstart-orchestrator
```

This invokes ColdstartOrchestrator which runs all three loaders in sequence:
1. **[PHASE: IDENTITY]** - Mission, principles, constraints from manifesto
2. **[BREATHE]** - Process before continuing
3. **[PHASE: SESSION]** - Prior session, memory refs, drift warnings, pending
4. **[BREATHE]** - Process before continuing
5. **[PHASE: WORK]** - Queue items, epoch alignment warnings

**No manual Read calls needed** - all context is injected by the orchestrator.

The output includes:
- `=== IDENTITY ===` block with extracted manifesto essence (~50 lines)
- `=== SESSION CONTEXT ===` with drift warnings PROMINENT
- `=== WORK OPTIONS ===` with queue and pending items
- `[READY FOR SELECTION]` marker when complete

---

## Step 3: Load Epoch Context (MUST)

**MUST** read from paths in haios.yaml:

1. Read `epoch.epoch_file` - current epoch definition
2. For each arc in `epoch.active_arcs`:
   - Read `{epoch.arcs_dir}/{arc}/ARC.md`

---

## Step 4: Query Memory Refs

If the SESSION CONTEXT output shows "Memory IDs to query: [...]":

Query those IDs via db_query or let the orchestrator handle it.

**Note:** SessionLoader extracts memory_refs from checkpoint but doesn't query them automatically. Manual query may still be needed.

---

## Step 5: Load Agent Instructions

Read `CLAUDE.md` - agent bootstrap and quick reference.

---

## Step 6: Session Start

```bash
just session-start {N}
```

Where N = current session + 1 from `.claude/session` (read last line as integer, increment by 1).

---

## Step 7: Summary Output

Provide brief summary:
- **Context loaded:** Via orchestrator (identity, session, work phases)
- **Epoch context:** Which epoch + which arcs loaded
- **Memory loaded:** From orchestrator output
- **Drift warnings:** Any from session context output

---

## Step 8: Invoke Survey Cycle

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

**Ground yourself first. Config -> Orchestrator -> Epoch -> Survey.**

Coldstart loads context. Survey-cycle selects work. Agent doesn't skip the chain.
