# 06 LIFECYCLE

How agents come to be, live, and end.

---

## Instance States

```
CREATED → INITIALISED → ACTIVE → PAUSED → RETIRED
              │            │         │
              │            │         └── can resume to ACTIVE
              │            │
              │            └── error can move to PAUSED
              │
              └── validation can fail, stuck here
```

---

## State Definitions

**CREATED**
- Directory exists
- Config file present
- No state, no history

**INITIALISED**
- Config validated
- Initial state files written
- Ready to run

**ACTIVE**
- Participating in cycles
- Reading inbox, writing outbox
- Accumulating history

**PAUSED**
- Not participating in cycles
- State preserved
- Can resume

**RETIRED**
- No longer active
- History preserved
- Cannot resume

---

## Transitions

[TODO: Define what triggers each transition]

[TODO: Define what files must exist at each state]

---

## Initialisation

```
1. Create directory structure
2. Write config
3. Validate config
4. Write initial state
5. Mark as INITIALISED
```

---

## Termination

```
1. Complete current cycle (if any)
2. Flush all outbox to history
3. Mark as RETIRED
4. Preserve history (read-only)
```

---

## Versioning

Agents change over time.

- Skill version tracked in config
- History records which version produced which output

[TODO: Define version format and tracking]
