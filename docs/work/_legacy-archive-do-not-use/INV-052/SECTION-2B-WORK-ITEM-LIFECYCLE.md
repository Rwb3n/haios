# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T23:26:11
# Section 2B: Work Item Lifecycle

Generated: 2025-12-29 (Session 149)
Purpose: The gated DAG, node_history, idempotency

---

## The Gated DAG

```
┌────────┐    ┌───────────┐    ┌──────┐    ┌───────────┐    ┌───────┐
│backlog │───►│ discovery │───►│ plan │───►│ implement │───►│ close │
└────────┘    └───────────┘    └──────┘    └───────────┘    └───────┘
                   │                             │
                   │ EXIT GATE                   │ EXIT GATE
                   │ - investigation exists      │ - tests pass
                   │ - conclusion reached        │ - WHY captured
                   ▼                             ▼
              GATE CHECK                    GATE CHECK
```

---

## node_history Schema

```yaml
node_history:
  - node: implement
    session: 149
    entered: 2025-12-29T21:50:00
    exited: null                      # null = in progress or crashed
    outcome: null                     # completed | promoted | blocked | session_crashed
    gate_results:
      tests_pass: true
      why_captured: false
    recovery_from: null               # set when recovering from crashed session
```

---

## Idempotency Principle

**Same file + same state = same gate decision**

Gates are idempotent checks:
- Any agent can run them
- Results don't depend on who runs them
- Safe to re-run after crash

---

## Crash Recovery

```
Session 149 crashes
    │
    ▼
Session 150 coldstart
    │
    ├── Detect: E2-150 has exited: null in node_history
    │
    ├── Report: "E2-150 was in implement node, incomplete from S149"
    │
    └── Agent resumes with new node_history entry:
        - recovery_from: 149
```

---

## Key Properties

1. **Work item knows its position** - current_node in WORK.md
2. **Work item knows its history** - node_history array
3. **Gates are idempotent** - same check, same result
4. **Any agent can pick up** - read WORK.md, continue
