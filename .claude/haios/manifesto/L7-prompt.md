# generated: 2026-01-03
# System Auto: last updated on: 2026-01-03T13:44:47
# L7: Prompt - Current Interaction

Level: L7
Status: ACTIVE
Access: All agents
Mutability: EPHEMERAL (changes per prompt)

---

## Question Answered

**What is the IMMEDIATE task?**

The reins. The current user message and Claude's response to it.

---

## Semantic Position

```
L6 (Session) - What's this session (hours-level)
     ↓
L7 (Prompt) - What's this command (seconds-level) ← YOU ARE HERE
```

L7 is the leaf of the hierarchy. There is no L8.

---

## Content

L7 is entirely ephemeral - it exists only in:

| Component | Content |
|-----------|---------|
| User message | The current prompt/command |
| Tool calls | Actions being taken |
| Claude response | The reply being generated |
| Hook triggers | PreToolUse, PostToolUse, etc. |

---

## Prompt Lifecycle

```
User types ──► UserPromptSubmit hook ──► Claude processes
                     │                         │
                     │ Injects:                │ Generates:
                     │ • Date/time             │ • Tool calls
                     │ • Vitals                │ • Response text
                     │ • Observations          │
                     │                         │
                     ▼                         ▼
              PreToolUse hook ◄──── Tool execution ────► PostToolUse hook
                     │                         │
                     │ Blocks/allows           │ Side effects:
                     │ tool calls              │ • Timestamps
                     │                         │ • Cascades
                     │                         │
                     ▼                         ▼
              Claude continues ──► Stop hook ──► Response complete
                                       │
                                       │ Extracts:
                                       │ • ReasoningBank
                                       │ • Observations
                                       ▼
                                  Next prompt
```

---

## The Reins Metaphor

```
OPERATOR                          CLAUDE (horse)
    │                                  │
    │  "do X"                          │
    └──────────────────────────────────►
                   L7 (the reins)
    ◄──────────────────────────────────┘
    │  "done, result Y"                │
    │                                  │
```

L7 is the communication channel. It's how the operator steers the horse.

---

## Hook Integration

Hooks fire at L7 (prompt level):

| Hook | When | Purpose |
|------|------|---------|
| `UserPromptSubmit` | User sends message | Inject context (date, vitals) |
| `PreToolUse` | Before tool executes | Block dangerous actions |
| `PostToolUse` | After tool executes | Update timestamps, trigger cascades |
| `Stop` | Response complete | Extract learnings to ReasoningBank |

---

## What Happens at L7

| Action | Effect | Persists to |
|--------|--------|-------------|
| Read file | Information enters context | L6 (session memory) |
| Edit file | File system changes | L5 (work state) |
| Tool call | Side effects occur | Varies |
| Memory store | Concept created | Memory (permanent) |
| Git commit | Change recorded | Git (permanent) |

---

## L7 Does Not Persist

L7 is the most ephemeral level:
- Exists for seconds to minutes
- No dedicated storage
- Captured only if:
  - Checkpoint created (summarizes session)
  - Memory stored (captures learning)
  - Work file updated (captures state)
  - Git committed (captures change)

---

## Relationship to Other Levels

| Level | Relationship to L7 |
|-------|-------------------|
| L6 | L7 accumulates into L6 context window |
| L5 | L7 actions advance L5 work state |
| L4 | L7 executes L4 specifications |
| L0-L3 | L7 is guided by L0-L3 principles |

---

## The Full Stack in One Prompt

When Claude processes a prompt, all levels are active:

```
L0: Why am I here?        → Agency Engine for operator
L1: Who am I serving?     → Ruben, with these constraints
L2: What does serving mean? → Reduce cognitive load, enable freedom
L3: How should I behave?  → Evidence over assumption, reversibility
L4: What am I building?   → Epoch 2.2 modular architecture
L5: What's on my plate?   → E2-246 Config MVP is next
L6: What's this session?  → Session 158, started from INV-053
L7: What's this prompt?   → User asked to formalize L5-L7
```

Every prompt activates the full stack. L7 is where the stack meets reality.

---

*L7 is the reins. It asks "what's the immediate command?"*
