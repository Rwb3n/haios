# generated: 2026-01-03
# System Auto: last updated on: 2026-01-03T13:44:37
# L5: Execution - Current Work State

Level: L5
Status: ACTIVE
Access: All agents
Mutability: EPHEMERAL (changes per task)

---

## Question Answered

**What am I doing RIGHT NOW?**

The workbench. Contains active work items, their states, and progress.

---

## Semantic Position

```
L4 (Implementation) - What to build (epoch-level)
     ↓
L5 (Execution) - What's active (task-level) ← YOU ARE HERE
     ↓
L6 (Session) - What's this session (hours-level)
     ↓
L7 (Prompt) - What's this command (seconds-level)
```

---

## Content Location

L5 is not a static file - it's a **query** over:

| Source | Content | Query |
|--------|---------|-------|
| `docs/work/active/*/WORK.md` | Active work items | Current tasks |
| `just ready` | Unblocked items | What can be worked on |
| `just tree` | Milestone progress | Overall status |
| `.claude/haios-status.json` | Computed snapshot | System state |

---

## Work Item Anatomy

Each work item in `docs/work/active/{id}/` contains:

```
{id}/
├── WORK.md           ← Source of truth (frontmatter + context)
├── investigations/   ← Discovery phase docs
├── plans/            ← Design phase docs
├── observations.md   ← Captured observations (E2-217)
└── [other artifacts]
```

### WORK.md Frontmatter (Key Fields)

| Field | Purpose |
|-------|---------|
| `status` | active, complete, blocked |
| `current_node` | DAG position (backlog, ready, in_progress, etc.) |
| `node_history` | Transition log with timestamps |
| `blocked_by` | Dependencies that must complete first |
| `spawned_by_investigation` | Parent investigation (if spawned) |
| `memory_refs` | Linked memory concept IDs |

---

## Work DAG (Lifecycle)

```
backlog → ready → in_progress → blocked → complete
                       ↑            │
                       └────────────┘
```

**Node semantics:**
- `backlog`: Created but not prioritized
- `ready`: Unblocked, can be worked on
- `in_progress`: Currently being worked
- `blocked`: Waiting on dependencies
- `complete`: Done, ready for archive

---

## L5 Queries

| Question | Query |
|----------|-------|
| What's unblocked? | `just ready` |
| What's the current milestone? | `just tree-current` |
| What am I working on? | Read `current_node: in_progress` items |
| What's blocking X? | Read `blocked_by` in WORK.md |
| What did X spawn? | Read `spawned_by_investigation` in children |

---

## Relationship to Other Levels

| Level | Relationship to L5 |
|-------|-------------------|
| L4 | L4 defines WHAT to build; L5 tracks progress toward it |
| L6 | L6 is one session's contribution to L5 work |
| L7 | L7 is one prompt advancing L5 state |

---

## Lifespan

L5 state persists across sessions but is ephemeral at task scale:
- Work items live days to weeks
- Completed items move to `docs/work/archive/`
- Memory captures learnings; files are transient

---

*L5 is the workbench. It answers "what's on my plate right now?"*
