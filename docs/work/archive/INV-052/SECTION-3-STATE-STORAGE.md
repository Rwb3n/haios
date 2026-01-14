# generated: 2025-12-29
# System Auto: last updated on: 2025-12-30T21:24:50
# Section 3: State Storage - Redesign

Generated: 2025-12-29 (Session 149)
Purpose: Map state storage as it actually exists, consolidate around work-centric model

---

## Review Process (Same as Sections 1-2)

1. **Read current diagram** - What does it claim?
2. **Verify against implementation** - What actually exists?
3. **Identify gaps** - What's missing or outdated?
4. **Apply lens:**
   - What state does this manage? (nouns)
   - What transitions does this enable? (verbs)
   - How does this connect to work item lifecycle? (track)
   - What's missing for predictive scaffolding? (gaps)
5. **Propose normalized architecture** - How should it work?
6. **Identify algorithm advancement opportunities** - What patterns emerge?

---

## Step 1: Current Diagram Claims

From SESSION-STATE-DIAGRAM.md Section 3:

**Primary State Files:**
- `haios-status-slim.json` (~85 lines) - session tracking, milestone, infrastructure
- `haios-status.json` (~500+ lines) - workspace tracking, governance

**Event Logs:**
- `haios-events.jsonl` - session, cycle_transition, heartbeat
- `governance-events.jsonl` - CyclePhaseEntered, ValidationOutcome

**Other State Files:**
- `pending-alerts.json` - queued validation failures
- `validation.jsonl` - template validation history
- `.mcp.json` - MCP server config

**Checkpoints:**
- `docs/checkpoints/*.md` - session docs with frontmatter

---

## Step 2: Verify Against Implementation

| Storage | Diagram Says | Actually Exists | Accurate? |
|---------|--------------|-----------------|-----------|
| haios-status-slim.json | ~85 lines | 86 lines | Yes |
| haios-status.json | ~500+ lines | Yes | Yes |
| haios-events.jsonl | 3 event types | Yes | Yes |
| governance-events.jsonl | 2 event types | Yes | Yes |
| pending-alerts.json | Queued failures | Yes | Yes |
| validation.jsonl | Validation history | Yes | Yes |
| .mcp.json | MCP config | Yes | Yes |
| Checkpoints | Session docs | Yes | Yes |

---

## Step 3: Identify Gaps

### Missing from Diagram

1. **WORK.md files** - 43 active work items, each with:
   - current_node
   - lifecycle_phase
   - node_history
   - blocked_by
   - spawned_by

2. **Work item subdirectories** - Per work item:
   - investigations/
   - plans/
   - observations/

3. **settings.json / settings.local.json** - Hook config, permissions, tool allowlists

4. **Memory database** (haios_memory.db) - 80,136 concepts, 8,761 entities

5. **Config files** - governance-toggles.yaml, routing-thresholds.yaml, node-cycle-bindings.yaml

### Fragmentation Problem

State for a single work item is scattered:

```
Work item E2-150 state lives in:
├── docs/work/active/E2-150/WORK.md       ← node, phase
├── .claude/haios-events.jsonl            ← cycle_transition events
├── .claude/governance-events.jsonl       ← validation events
├── .claude/haios-status.json             ← computed status
├── haios_memory.db                       ← learnings (unlinked)
├── docs/checkpoints/*.md                 ← backlog_ids (manual)
└── docs/work/active/E2-150/plans/*.md    ← plan phases (separate)
```

**No single place to see E2-150's complete journey.**

---

## Step 4: Apply the Lens

### 4a. What state does this manage? (Nouns)

| State Category | Current Location | Source of Truth? | Problem |
|----------------|------------------|------------------|---------|
| Session state | Derived from checkpoints + events | No single source | Computed, can be stale |
| Work item position | WORK.md (current_node) | Yes | But history in events.jsonl |
| Work item journey | haios-events.jsonl | No | Disconnected from WORK.md |
| Milestone progress | haios-status*.json | Computed | Scan-derived, not authoritative |
| Memory/learnings | haios_memory.db | Yes | Not linked to work items |
| Infrastructure | haios-status-slim.json | Computed | Static, rarely changes |
| Governance events | governance-events.jsonl | Yes | Disconnected from work items |
| Validation history | validation.jsonl | Yes | Grows unbounded |

### 4b. What transitions does this enable? (Verbs)

| Transition | Mechanism | Where Recorded | Gap |
|------------|-----------|----------------|-----|
| Session start | `just session-start N` | haios-events.jsonl | Manual, forgettable |
| Session end | `just session-end N` | haios-events.jsonl | Manual, forgettable |
| Work item node change | Edit WORK.md | WORK.md + haios-events.jsonl | Two places |
| Cycle phase change | Edit plan/investigation | governance-events.jsonl | Separate file |
| Gate validation | PreToolUse hook | governance-events.jsonl | Not in WORK.md |
| Memory capture | ingester_ingest | haios_memory.db | No work item link |
| Status refresh | UserPromptSubmit | haios-status-slim.json | Computed on every prompt |

### 4c. How does this connect to work item lifecycle? (Track)

**Current Connection: FRAGMENTED**

To understand E2-150's journey, you must:
1. Read WORK.md (current position)
2. Grep haios-events.jsonl for E2-150 (transitions)
3. Grep governance-events.jsonl for E2-150 (validations)
4. Search checkpoints for backlog_ids containing E2-150 (sessions)
5. Query memory for E2-150 mentions (learnings)

**No unified view exists.**

### 4d. What's missing for predictive scaffolding? (Gaps)

| Gap | Impact |
|-----|--------|
| Journey not in WORK.md | Can't see history by reading one file |
| Memory not linked | Can't auto-fetch relevant strategies |
| Gate results scattered | Can't see what's been validated |
| Multiple event logs | No unified timeline per work item |
| Computed status | Expensive to generate, can drift |

---

## Step 5: Proposed Normalized Architecture

### Principle: Work Item is the Single Source of Truth

All state related to a work item lives in its directory:

```
docs/work/active/E2-150/
│
├── WORK.md                        # STATE MACHINE (authoritative)
│   ---
│   id: E2-150
│   title: "Implement memory retrieval"
│   current_node: implement        # DAG node (backlog/discovery/plan/implement/close)
│   current_phase: DO              # Cycle phase (PLAN/DO/CHECK/DONE for implementation)
│   blocked_by: []
│   spawned_by: INV-045
│
│   node_history:                  # JOURNEY (was in events.jsonl)
│     - node: backlog
│       session: 145
│       entered: 2025-12-20T10:00:00
│       exited: 2025-12-20T10:05:00
│       outcome: promoted
│     - node: discovery
│       session: 146
│       entered: 2025-12-21T14:00:00
│       exited: 2025-12-21T16:30:00
│       outcome: investigation_complete
│       gate_results:
│         investigation_exists: true
│         conclusion_reached: true
│     - node: plan
│       session: 147
│       entered: 2025-12-22T09:00:00
│       exited: 2025-12-22T11:00:00
│       outcome: plan_approved
│     - node: implement
│       session: 149
│       entered: 2025-12-29T21:50:00
│       exited: null               # IN PROGRESS
│       outcome: null
│
│   memory_refs: [78234, 79012]    # LINKED CONCEPTS
│   ---
│
├── investigations/
│   └── INV-001-initial.md
│
├── plans/
│   ├── PLAN-v1.md
│   └── PLAN-v2.md
│
├── observations/
│   └── observations.md
│
├── references/
│   ├── REFS.md                    # PORTALS to other work items
│   └── memory-refs.md             # PORTALS to memory concepts
│
└── artifacts/
    └── test-results/
```

### What Moves Where

| Current Location | Proposed Location | Rationale |
|------------------|-------------------|-----------|
| haios-events.jsonl (cycle_transition) | WORK.md node_history | Journey belongs with work item |
| governance-events.jsonl (ValidationOutcome) | WORK.md node_history.gate_results | Gate results belong with transition |
| Memory concept IDs | WORK.md memory_refs + references/memory-refs.md | Link learnings to work |
| Checkpoint backlog_ids | Auto-derived from work items touched | Computed, not manual |

### What Stays

| Storage | Keeps | Rationale |
|---------|-------|-----------|
| haios-events.jsonl | Session start/end, heartbeat | Session-level, not work-item-level |
| governance-events.jsonl | Keep as audit log | Secondary, for debugging |
| haios-status*.json | Keep as computed cache | Performance optimization |
| validation.jsonl | Keep as audit log | Secondary, for debugging |
| haios_memory.db | Keep as memory store | Concepts are shared across work items |

### New State Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STATE ARCHITECTURE (Work-Centric)            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  AUTHORITATIVE STATE (Source of Truth)                          │
│  ─────────────────────────────────────                          │
│  docs/work/active/{id}/WORK.md                                  │
│    • current_node, current_phase                                │
│    • node_history (journey with gate results)                   │
│    • memory_refs (linked concepts)                              │
│    • blocked_by, spawned_by (portals)                          │
│                                                                  │
│  docs/work/active/{id}/references/REFS.md                       │
│    • Portals to related work, ADRs, external                   │
│                                                                  │
│  haios_memory.db                                                │
│    • Concepts, entities (shared knowledge)                      │
│    • Linked FROM work items via memory_refs                     │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  COMPUTED STATE (Cache, can be regenerated)                     │
│  ──────────────────────────────────────────                     │
│  .claude/haios-status-slim.json                                 │
│    • Milestone progress (computed from work items)              │
│    • Session delta (computed from checkpoints)                  │
│    • Infrastructure list (computed from discovery)              │
│                                                                  │
│  .claude/haios-status.json                                      │
│    • Full workspace view (computed from work items)             │
│    • Stale detection (computed from timestamps)                 │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  AUDIT LOGS (Secondary, for debugging/history)                  │
│  ─────────────────────────────────────────────                  │
│  .claude/haios-events.jsonl                                     │
│    • Session start/end events                                   │
│    • Heartbeat events                                           │
│    • (cycle_transition MOVES to WORK.md)                        │
│                                                                  │
│  .claude/governance-events.jsonl                                │
│    • Audit trail of validations                                 │
│    • (primary record now in WORK.md gate_results)               │
│                                                                  │
│  .claude/validation.jsonl                                       │
│    • Template validation history                                │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  CONFIG (Rarely changes)                                        │
│  ──────────────────────                                         │
│  .claude/haios/config/                                          │
│    • hook-handlers.yaml (handler registry)                      │
│    • node-bindings.yaml (DAG definition)                        │
│    • governance-toggles.yaml                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 6: Algorithm Advancement Opportunities

### Pattern: Derived vs Authoritative State

Current system has too much derived state being treated as authoritative:
- haios-status.json is computed but read as if authoritative
- Session number is derived from checkpoint filenames
- Milestone progress is computed from work item counts

**Opportunity: Single Writer Principle**

Each piece of state has exactly one writer:
- WORK.md → written by agent via Edit (gated by hooks)
- node_history → written by PostToolUse on node transitions
- memory_refs → written by PostToolUse on memory capture
- haios-status*.json → computed by status.py (read-only cache)

### Pattern: Event Sourcing Light

The node_history in WORK.md is essentially event sourcing:
- Each entry is an immutable event
- Current state is derived from latest entry
- Full history is preserved

**Opportunity: Replay and Recovery**

If node_history is authoritative:
- Can replay to understand journey
- Can detect incomplete entries (no exited timestamp)
- Can recover from crashes by examining last entry

### Pattern: Lazy Computation

Current: status.py runs on every prompt (expensive)
Proposed: Compute only when needed, cache aggressively

**Opportunity: Incremental Updates**

Instead of full workspace scan:
- Watch for WORK.md changes
- Update only affected work items in status
- Invalidate cache on relevant changes

---

## Implications for Sections 1 and 2

### Section 1 (Hooks) Impact

| Handler | Change |
|---------|--------|
| work_item_history_update | Writes to WORK.md node_history (not events.jsonl) |
| work_item_gate | Reads WORK.md node_history for gate validation |
| slim_status_refresh | Becomes lighter (cache, not authoritative) |

### Section 2 (Session Lifecycle) Impact

| Concept | Change |
|---------|--------|
| Session-work binding | Session focus tracked, but journey in WORK.md |
| Crash recovery | Read WORK.md for incomplete entries, not events.jsonl |
| Multi-agent | Each agent can read WORK.md independently |

---

## Simulation Validation

The crash recovery simulation (see Section 2) validated this architecture:

### What Works

1. **Dual signal crash detection:**
   - haios-events.jsonl: orphaned session-start (no matching end)
   - WORK.md: `exited: null` in node_history
   - Either signal alone is sufficient; both together is definitive

2. **State preserved in WORK.md:**
   - Node, phase, when entered, partial memory_refs all survive
   - Recovery agent knows exactly where crashed session left off

3. **Idempotent recovery:**
   - Gate checks can run again safely (same criteria, same result)
   - New node_history entry preserves audit trail
   - `recovery_from` field links to crashed session for forensics

4. **Clean separation:**
   - Authoritative state (WORK.md) - always correct
   - Computed state (status.json) - can be regenerated
   - Audit logs (events.jsonl) - secondary, for debugging

### node_history Schema (Confirmed)

```yaml
node_history:
  - node: implement
    session: 149
    entered: 2025-12-29T21:50:00
    exited: null                      # null = in progress or crashed
    outcome: null                     # completed | promoted | blocked | session_crashed
    gate_results:                     # populated when gate checked
      tests_pass: true
      why_captured: false
    recovery_from: null               # set when recovering from crashed session
```

---

## Open Questions

1. **node_history size** - Could grow large. Truncate old entries? Archive to separate file?

2. **Atomic updates** - YAML frontmatter in WORK.md. Risk of corruption on concurrent edits?

3. **Migration path** - How to migrate existing haios-events.jsonl entries to WORK.md node_history?

4. **Query patterns** - How to query "all work items in implement node"? (Currently: scan all WORK.md files)

5. **Cache invalidation** - When does haios-status*.json become stale? Timestamp-based? Content-hash?

6. **Orphan session closure** - Should crashed entries get `outcome: session_crashed` or stay `null`?

7. **Partial file edits** - What if agent was mid-Edit when crash happened? Validation on coldstart?

8. **Multiple incomplete items** - If session touched multiple work items, report all? Prioritize how?

---

## Connection to Sections 1 and 2

**Section 1 (Hooks):**
- PostToolUse writes to WORK.md node_history instead of haios-events.jsonl
- PreToolUse reads WORK.md for gate validation
- Status refresh becomes cache update, not authoritative state

**Section 2 (Session Lifecycle):**
- WORK.md is the durable state (survives crashes)
- Session is ephemeral focus tracking
- node_history enables crash recovery without session state

**Section 3 (this section):**
- Consolidates state into work item directories
- Separates authoritative (WORK.md) from computed (status.json)
- Positions event logs as audit trail, not primary state

---

*This document will be updated as we review remaining sections.*
