# 08 OPERATOR

Human is just another agent. Same protocol.

---

## Principle

No special interface for humans.

- Read: `cat` any file
- Write: edit any inbox
- Intervene: write to inbox, agent reads it

---

## Operator Capabilities

```
OBSERVE     → read any file in system
AUDIT       → trace any decision through history
INTERVENE   → write to any inbox
PAUSE       → change instance state
CONFIGURE   → edit config files
OVERRIDE    → write directly to state (escape hatch)
```

---

## Intervention Points

Where operators typically act:

```
Before cycle    → modify inbox before agent reads
After decision  → approve/reject before execution
On error        → decide recovery action
On threshold    → respond to alerts
```

---

## Alerts

System notifies operator when:

```
ERROR_RATE      → above threshold
ANOMALY         → unexpected pattern detected
THRESHOLD       → metric crosses boundary
HEALTH          → agent/utility unavailable
```

[TODO: Define alert mechanism]

---

## Audit Trail

Operator actions are logged same as agent actions.

No invisible changes.

---

## Escape Hatches

Sometimes you need to break the rules:

- Direct state edit (bypass inbox/outbox)
- Force state transition
- Kill and restart

These are logged with OPERATOR_OVERRIDE flag.

Use sparingly.
