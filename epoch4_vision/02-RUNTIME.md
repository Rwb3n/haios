# 02 RUNTIME

The LLM is the thinking substrate. The harness is the bridge.

---

## LLM as Thinking Engine

- Agents are made of LLM calls
- LLM is the only non-file, non-agent component
- Stateless: prompt in, response out

---

## Harness

The bridge between file substrate and LLM runtime.

```
READ inbox files
    ↓
ASSEMBLE prompt (template + context)
    ↓
CALL LLM
    ↓
PARSE response
    ↓
WRITE outbox files
```

- Harness is generic
- Prompt template is the skill
- LLM is swappable

---

## Backend Swapping

Agents specify LLM preference in config:

```
runtime:
  backend: claude-api | gpt-api | local
  model: [model identifier]
  fallback: [optional fallback backend]
```

Harness routes to appropriate backend.

[TODO: Define backend interface contract]

---

## Cost Tracking

Every LLM call records:

- Tokens in
- Tokens out
- Latency
- Cost
- Backend used

[TODO: Define where cost data lives]
