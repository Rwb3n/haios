# generated: 2025-12-29
# System Auto: last updated on: 2025-12-30T21:25:04
# Section 4: Data Flow - Redesign

Generated: 2025-12-29 (Session 149)
Purpose: Simplify data flow around work-centric model

---

## Review Process (Same as Sections 1-3)

1. Read current diagram
2. Verify against implementation
3. Identify gaps
4. Apply lens (nouns, verbs, track, gaps)
5. Propose normalized architecture
6. Identify algorithm opportunities

---

## Current Diagram Summary

The diagram shows:
- User Input → UserPromptSubmit → status.py → slim.json
- Claude Response → Edit/Write/Bash/MCP → PostToolUse → scattered writes
- Timestamp injection, cycle logging, error capture, status refresh

**Problem:** Data flows to many destinations. No single path for work item state.

---

## Proposed Data Flow (Work-Centric)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SIMPLIFIED DATA FLOW                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  USER INPUT                                                              │
│      │                                                                   │
│      ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ UserPromptSubmit                                                 │    │
│  │   • Read WORK.md (active work item)                             │    │
│  │   • Read haios-status-slim.json (cache)                         │    │
│  │   • Inject: work context + vitals + thresholds                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│      │                                                                   │
│      ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ PreToolUse                                                       │    │
│  │   • Read WORK.md (current node, gate state)                     │    │
│  │   • Validate: is this edit allowed for current node?            │    │
│  │   • Gate check: can agent transition nodes?                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│      │                                                                   │
│      ▼                                                                   │
│  TOOL EXECUTION (Edit/Write/Bash/MCP)                                   │
│      │                                                                   │
│      ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ PostToolUse                                                      │    │
│  │   • Write WORK.md (node_history, memory_refs) ◄── SINGLE WRITER │    │
│  │   • Write file timestamps (unchanged)                            │    │
│  │   • Trigger scaffold suggestions (unchanged)                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│      │                                                                   │
│      ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Stop                                                             │    │
│  │   • Write WORK.md (mark exited: null if crash)                  │    │
│  │   • Extract learnings → memory + WORK.md memory_refs            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

STATE FLOW:

  WORK.md ◄───────────────── PRIMARY STATE ──────────────────────────────
     │
     ├── Read by: UserPromptSubmit, PreToolUse, coldstart
     │
     └── Written by: PostToolUse (single writer)

  haios-status-slim.json ◄── COMPUTED CACHE ─────────────────────────────
     │
     ├── Read by: UserPromptSubmit (vitals)
     │
     └── Written by: status.py (on refresh)

  haios-events.jsonl ◄────── AUDIT LOG ──────────────────────────────────
     │
     ├── Read by: coldstart (orphan detection)
     │
     └── Written by: session-start/end only
```

---

## Key Simplifications

| Before | After |
|--------|-------|
| PostToolUse writes to 4 places | PostToolUse writes to WORK.md (single writer) |
| cycle_transition → haios-events.jsonl | cycle_transition → WORK.md node_history |
| gate_results → governance-events.jsonl | gate_results → WORK.md node_history |
| Memory unlinked | Memory linked via WORK.md memory_refs |
| status.py scans everything | status.py reads WORK.md files (simpler) |

---

## Read/Write Matrix

| Component | Reads | Writes |
|-----------|-------|--------|
| UserPromptSubmit | WORK.md, slim.json | (none) |
| PreToolUse | WORK.md | (none, or DENY) |
| PostToolUse | WORK.md | WORK.md (node_history, memory_refs) |
| Stop | WORK.md | WORK.md (incomplete mark) |
| status.py | WORK.md files, checkpoints | slim.json, status.json |
| coldstart | WORK.md, slim.json, events.jsonl | (none) |

**Single Writer Principle:** Only PostToolUse writes to WORK.md node_history.

**Note on Orchestrator:** The cycle orchestrator (Section 2E) coordinates phase transitions
but triggers PostToolUse to perform the actual write. The orchestrator is the decision-maker;
PostToolUse is the writer. This maintains single-writer semantics while enabling orchestration.

---

## Connection to Sections 1-3

- **Section 1:** Handlers simplified from 22 to 19
- **Section 2:** Session ephemeral, WORK.md durable (confirmed by data flow)
- **Section 3:** State consolidated into WORK.md (data flow shows single writer)

---

## Open Questions (from simulation)

Carried forward from Sections 2-3:
1. node_history size limits
2. Atomic YAML updates
3. Migration from events.jsonl
4. Query patterns across WORK.md files
5. Cache invalidation for status.json
6. Orphan session handling
7. Partial edit recovery
8. Multiple incomplete items

---

*Context at 87%. Recommend checkpoint after this section.*
