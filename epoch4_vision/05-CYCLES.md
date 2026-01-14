# 05 CYCLES

Outward: act on world. Inward: act on self.

---

## Outward Cycle

System looking out.

```
OBSERVE     → utilities pull external state
    ↓
EVALUATE    → agents interpret, add context, reason
    ↓
DECIDE      → agents choose actions
    ↓
ACT         → utilities execute on external world
    ↓
(repeat)
```

---

## Inward Cycle

System looking in.

```
INTROSPECT      → observe system performance, health
    ↓
META-EVALUATE   → judge effectiveness, detect drift
    ↓
ADAPT           → change parameters, skills, structure
    ↓
(repeat)
```

---

## Triggers

What initiates a cycle:

```
TIME-BASED      → cron, schedule
EVENT-BASED     → file appears, external signal
MANUAL          → operator triggers
THRESHOLD-BASED → metric crosses boundary
```

[TODO: Define trigger specification format]

---

## Cycle Scope

Outward cycle: typically per-instance, high frequency.

Inward cycle: typically cross-instance, lower frequency.

---

## Cycle Output

Every cycle produces files:

- What was observed
- What was evaluated
- What was decided
- What was done
- What was the outcome

Full traceability.
