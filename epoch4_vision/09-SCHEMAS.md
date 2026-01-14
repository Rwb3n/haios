# 09 SCHEMAS

Contracts between agents.

---

## Principle

Every file type has a schema.

Schema defines:
- Required fields
- Optional fields
- Field types
- Validation rules

---

## Base Schema

All files include:

```
_meta:
  id:         [unique identifier]
  agent:      [producing agent]
  timestamp:  [ISO 8601]
  version:    [schema version]
```

---

## Inbox Contract

```
inbox/{message-id}.yaml

_meta: [base]
intent:     [what is being requested]
context:    [relevant background]
constraints:[rules that must be followed]
deadline:   [optional, when response needed]
```

---

## Outbox Contract

```
outbox/{message-id}.yaml

_meta: [base]
status:     SUCCESS | ERROR
in_response_to: [inbox message id]
content:    [the payload]
reasoning:  [why this output]
handoff:    [what reader should do next]
```

---

## State Contract

```
state/{domain}.yaml

_meta: [base]
data:       [domain-specific state]
last_modified_by: [agent that last wrote]
```

---

## History Contract

```
history/{date}.jsonl

Each line:
{
  _meta: [base],
  event_type: [what happened],
  content: [event data],
  outcome: [result, if applicable]
}
```

Append-only. Immutable once written.

---

## Config Contract

```
config.yaml

_meta: [base]
agent_type: [skill name]
parameters: [agent-specific config]
runtime:    [LLM backend config]
```

Immutable after INITIALISED state.

---

## Domain-Specific Schemas

[TODO: Define per use case]

Trading schemas would extend base with:
- portfolio state
- order format
- market data format

---

## Validation

Harness validates files against schema before processing.

Invalid files → ERROR status, not processed.
