---
allowed-tools: Read, Glob, Bash, mcp__haios-memory__memory_search_with_experience,
  mcp__haios-memory__db_query
description: Initialize session by loading essential context files
generated: '2025-12-25'
last_updated: '2026-02-21T00:40:00'
---

# Cold Start Initialization

**MUST** run at the start of every session.

---

## Step 1: Load Context via Orchestrator (WORK-011, WORK-180)

Run the unified coldstart orchestrator:

```
mcp__haios-operations__coldstart_orchestrator()
```

**Tier selection (ADR-047):** The orchestrator auto-detects the appropriate tier, or you can specify one explicitly:

```
mcp__haios-operations__coldstart_orchestrator(tier="full")    # New epoch/arc work, first session after transition
mcp__haios-operations__coldstart_orchestrator(tier="light")   # Continuation of prior session work
mcp__haios-operations__coldstart_orchestrator(tier="minimal") # Housekeeping (doc fixes, drift correction)
```

| Tier | When | Phases |
|------|------|--------|
| **Full** (default) | New work, stale checkpoint (>24h), no checkpoint | Identity + Session + Work + Epoch + Operations + Validation |
| **Light** | Fresh checkpoint with pending work | Session + Work |
| **Minimal** | Housekeeping tasks | Session only |

The orchestrator runs loaders in sequence with `[BREATHE]` markers:
1. **[PHASE: IDENTITY]** - Mission, principles, constraints from manifesto
2. **[PHASE: SESSION]** - Prior session, memory refs, drift warnings, pending
3. **[PHASE: WORK]** - Queue items, epoch alignment warnings
4. **[PHASE: EPOCH]** - Epoch status, arc chapters, exit criteria
5. **[PHASE: OPERATIONS]** - Tier model, recipe catalogue, agent table, common patterns
6. **[PHASE: VALIDATION]** - Epoch drift warnings (full tier only)

**All context is injected by the orchestrator** — no manual Read calls needed for epoch, arc, or operational context.

The output includes:
- `=== IDENTITY ===` block with extracted manifesto essence (~50 lines)
- `=== SESSION CONTEXT ===` with drift warnings PROMINENT
- `=== WORK OPTIONS ===` with queue and pending items
- `=== EPOCH CONTEXT ===` with arc/chapter status and exit criteria
- `=== OPERATIONS ===` with tier model, recipes, agents, governance triggers
- `[READY FOR SELECTION]` marker when complete

---

## Step 2: Query Memory Refs

If the SESSION CONTEXT output shows "Memory IDs to query: [...]":

Query those IDs via db_query or let the orchestrator handle it.

**Note:** SessionLoader extracts memory_refs from checkpoint but doesn't query them automatically. Manual query may still be needed.

---

## Step 3: Session Start

```
mcp__haios-operations__session_start(session_number=N)
```

Where N = current session + 1 from `.claude/session` (read last line as integer, increment by 1).

---

## Step 4: Summary Output

Provide brief summary:
- **Context loaded:** Via orchestrator (which tier, which phases)
- **Epoch context:** From orchestrator [PHASE: EPOCH] output
- **Memory loaded:** From orchestrator output
- **Drift warnings:** Any from session context or validation output

---

## Step 5: Invoke Survey Cycle

**MUST** chain to survey-cycle for work selection:

```
Skill(skill="survey-cycle")
```

Survey-cycle owns routing:
- Checks checkpoint `pending` for prior work
- Presents options from `mcp__haios-operations__queue_ready()`
- Routes to correct cycle based on work type

---

## Escape Hatch

If an agent in Light or Minimal tier discovers it needs more context mid-session:

```
mcp__haios-operations__coldstart_orchestrator(tier="full")
```

**Note:** `--extend` was a Tier 3 flag (deferred to WORK-181, not yet implemented). Use the MCP tool with `tier="full"` as the workaround.

---

## Key Principle

**Ground yourself first. Orchestrator -> Memory Refs -> Session Start -> Survey.**

Coldstart loads context. Survey-cycle selects work. Agent doesn't skip the chain.
