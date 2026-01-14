# 01 SUBSTRATE

The filesystem is the conversation medium between agents across time.

---

## Files as Memory

- No agent holds state
- All state lives in files
- Files are the only source of truth

---

## Directories as Scope

```
/instance/
├── config          # Immutable parameters
├── state/          # Current truth
├── inbox/          # Pending inputs
├── outbox/         # Outputs awaiting collection
├── history/        # Append-only, immutable
└── sub_agents/     # Scoped children
```

- Agent's read scope: its directory and below
- Agent's write scope: its outbox only
- No agent reaches up. No agent reaches sideways.

---

## Inbox/Outbox Protocol

```
WRITER promises:
  - File is self-contained
  - Sufficient context for reader to act
  - Explicitly states expected action

READER promises:
  - Assumes no context beyond file contents
  - Modifies only own outbox
  - Records reasoning for decisions made
```

---

## File Lifecycle

```
CREATED → PENDING → PROCESSED → ARCHIVED

inbox/*     # PENDING
outbox/*    # PROCESSED
history/*   # ARCHIVED
```

---

## File Properties

Every file has:

1. **Identity** — What is this, who wrote it, when
2. **Context** — What situation produced this
3. **Content** — The payload
4. **Reasoning** — Why this content
5. **Handoff** — What should reader do next

[TODO: Define which properties are mandatory vs optional per file type]
