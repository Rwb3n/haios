# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T23:25:53
# Section 2A: Session Lifecycle

Generated: 2025-12-29 (Session 149)
Purpose: Session as ephemeral ceremony (init, work, end)

---

## Key Insight

**Session is ephemeral. Work item is durable.**

Session lifecycle is ceremony - the real state lives in work items.

---

## The Three Phases

### Phase 1: INIT (/coldstart)

```
/coldstart
├── Read context (CLAUDE.md, L0, L1, L2)
├── Read last checkpoint
├── Read haios-status-slim.json
├── Query memory (session_recovery mode)
├── Log session-start event
└── Route to work item
```

### Phase 2: WORK (loop)

```
Every prompt:
├── UserPromptSubmit: inject context
├── PreToolUse: gate/validate
├── Tool execution
└── PostToolUse: update state
```

### Phase 3: END

```
checkpoint-cycle:
├── SCAFFOLD → FILL → VERIFY → CAPTURE → COMMIT
├── Log session-end event
└── Stop hook: extract learnings
```

---

## What Session Tracks

| State | Location | Purpose |
|-------|----------|---------|
| Session number | Derived from checkpoints | Identification |
| Session events | haios-events.jsonl | Audit trail |
| Current focus | Agent context (ephemeral) | Routing |

**Session does NOT track:**
- Work item progress (lives in WORK.md)
- Node transitions (lives in WORK.md node_history)
- Gate results (lives in WORK.md node_history)

---

## Crash Recovery

Session state is ephemeral, so crash recovery reads from durable state:

1. Detect orphaned session (session-start without session-end)
2. Scan WORK.md files for `exited: null` entries
3. Report incomplete work to agent
4. Agent resumes from WORK.md state
