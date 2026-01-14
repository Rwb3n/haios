# 07 ERRORS

Failures are first-class outputs.

---

## Principle

When something fails, the agent:

1. Writes what happened to outbox
2. Includes enough context to diagnose
3. Lets parent decide what to do

Errors propagate up through files, same as success.

---

## Error File Format

```
IDENTITY:       [agent, timestamp]
STATUS:         ERROR
ERROR_TYPE:     [category]
CONTEXT:        [what was being attempted]
DETAIL:         [what went wrong]
ATTEMPTED:      [recovery attempts made]
RECOMMENDATION: [suggested next action]
```

Still a high-quality prompt component.

---

## Error Types

```
INPUT_INVALID       → inbox malformed or missing required fields
LLM_FAILURE         → timeout, rate limit, invalid response
UTILITY_FAILURE     → external interface unavailable or errored
CONSTRAINT_VIOLATION→ output violates rules (e.g. risk limits)
INTERNAL_ERROR      → unexpected failure in harness/agent logic
```

[TODO: Define handling policy per error type]

---

## Propagation

```
Child errors   → written to child outbox
Parent reads   → decides: retry, skip, escalate, halt
Escalation     → parent writes error to own outbox
```

Errors bubble up until handled or reach operator.

---

## Recovery

[TODO: Define retry policies]

[TODO: Define circuit breaker patterns]

---

## Logging

All errors append to history regardless of handling.

Errors are never silent.
