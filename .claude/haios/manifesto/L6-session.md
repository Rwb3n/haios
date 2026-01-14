# generated: 2026-01-03
# System Auto: last updated on: 2026-01-03T13:44:42
# L6: Session - Current Session Context

Level: L6
Status: ACTIVE
Access: All agents
Mutability: EPHEMERAL (changes per session)

---

## Question Answered

**What has THIS horse done?**

The session. Contains what the current Claude instance has accomplished since coldstart.

---

## Semantic Position

```
L5 (Execution) - What's active (task-level)
     ↓
L6 (Session) - What's this session (hours-level) ← YOU ARE HERE
     ↓
L7 (Prompt) - What's this command (seconds-level)
```

---

## Session Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                      SESSION LIFECYCLE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  coldstart ──► work ──► work ──► ... ──► checkpoint ──► clear
│      │                                        │              │
│      │   Context accumulates                  │              │
│      │   in Claude's window                   │              │
│      │                                        ▼              │
│      │                                  Memory persists      │
│      │                                  Checkpoint persists  │
│      │                                        │              │
│      └────────────────────────────────────────┘              │
│                    Next session coldstarts                   │
│                    from checkpoint + memory                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Content Location

L6 is not a static file - it's the **current context window** plus:

| Source | Content | Lifespan |
|--------|---------|----------|
| Context window | Current conversation | Until clear |
| `docs/checkpoints/*.md` | Session summaries | Persists |
| `.claude/haios-status.json` | `session_delta` field | Updated per session |
| `haios_memory.db` | Stored learnings | Persists |

---

## Session State

### Ephemeral (Lost on Clear)
- Conversation history
- Tool call results
- Reasoning chains
- Uncommitted changes

### Persisted (Survives Clear)
- Checkpoints (`docs/checkpoints/`)
- Work file updates (`docs/work/`)
- Memory concepts (`haios_memory.db`)
- Git commits

---

## The Horse Metaphor

```
                    ┌─────────────────────────────┐
                    │          CHARIOT            │
                    │  (L4-L5: persists)          │
                    └──────────────┬──────────────┘
                                   │
     ┌─────────────────────────────┼─────────────────────────────┐
     │                             │                             │
  Session 157                 Session 158                 Session 159
  (horse 1)                   (horse 2)                   (horse 3)
     │                             │                             │
     │ checkpoint ────────────► coldstart                        │
     │                             │                             │
     │ memory ───────────────► memory query                      │
     │                             │                             │
     └─────────────────────────────┘─────────────────────────────┘

Each horse (Claude instance) is stateless.
The chariot (files + memory) carries state between horses.
```

---

## Session Events

| Event | Trigger | Effect |
|-------|---------|--------|
| `SessionStarted` | `/coldstart` | Load L0-L4, query memory, show ready work |
| `WorkStarted` | Pick work item | Transition node to `in_progress` |
| `WorkCompleted` | `/close` | Archive work, store to memory |
| `CheckpointCreated` | `/new-checkpoint` | Snapshot session progress |
| `SessionEnded` | Clear/exit | Context lost; checkpoint persists |

---

## Session Continuity

The goal of L6 design is **seamless handoff between horses**:

1. **Before clear:** Create checkpoint with pending work
2. **On coldstart:** Load checkpoint, query memory for strategies
3. **Resume:** Pick up where last horse left off

**What persists:**
- WHAT was being done (checkpoint `backlog_ids`)
- WHY decisions were made (memory concepts)
- WHERE work stands (WORK.md `current_node`)

**What's lost:**
- HOW the last horse reasoned (context window)
- WHAT tools were called (conversation history)

---

## L6 Queries

| Question | Query |
|----------|-------|
| What session is this? | `just checkpoint-latest` → extract session number |
| What did last session do? | Read latest checkpoint |
| What strategies apply? | `memory_search_with_experience(mode='session_recovery')` |
| What's the session delta? | `.claude/haios-status-slim.json` → `session_delta` |

---

## Relationship to Other Levels

| Level | Relationship to L6 |
|-------|-------------------|
| L5 | L6 advances L5 work items; L5 survives L6 clear |
| L7 | L7 is one prompt within L6 session |
| Memory | L6 queries memory on start; stores to memory before end |

---

## Lifespan

L6 state is ephemeral at session scale:
- Context window: hours (until clear/compact)
- Session identity: one coldstart to next coldstart
- Checkpoint captures L6 for next session

---

*L6 is the horse. It asks "what has this instance accomplished?"*
