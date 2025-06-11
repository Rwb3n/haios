# Phase-1 → Phase-2 Hand-off Model

Phase-1 ends with a single-node, file-driven "titanium" engine. Phase-2 will layer on multi-agent orchestration, distributed workers, and external services (LLMs, CI runners, reviewers).

The safest bridge is to treat the Phase-1 engine as a deterministic black-box executor with a stable contract:

## Contract Surface

| Contract Surface      | What Phase-1 Guarantees                                                                 | How Phase-2 Plugs In                                                                                 |
|----------------------|----------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Artefact schemas     | Immutable `exec_plan_*.txt`, `exec_status_*.txt`, `state.txt`, snapshots, registry map — all validated by JSON-schema versions pinned in ADR-006/019/020. | Phase-2 agents create or mutate only through these files; they never reach inside the engine's process. |
| CLI / daemon API     | `haios run <plan> --mode {STRICT, DEV_FAST}`<br>`haios state read`                    |                                                                                                      |
| Prometheus metrics   | `/metrics` endpoint with task, budget, kill-switch, lock-wait series (ADR-019).         | Phase-2 autoscaler / queue manager watches these metrics to decide when to spin additional workers or back-off load. |
| Kill-switch flags    | `soft_kill.flag`, `write_lockdown.flag`, `state.kill_mode`, plan-scoped `desired_state=CANCELLED`. | Phase-2 SRE bots can toggle these flags via the CLI wrapper; human overrides remain identical.         |
| Secrets vault & scopes | Vault decrypts only requested scopes (global/initiative/plan/agent) at plan start (ADR-018). | When Phase-2 spawns a remote LLM agent, it scopes a transient key just for that agent & plan; engine enforces least-privilege. |
| Cost records & budgets | Each task writes `cost_record`; budgets enforce soft-kill at 100% (STRICT) or 150% (DEV_FAST). | Phase-2 financial controller aggregates cost snapshots across many nodes, raises cross-project budget alarms. |
| Runtime modes        | Exactly two (`STRICT`, `DEV_FAST`), artefacts label dev-fast suffix.                    | Phase-2 CI pipeline runs STRICT; developer sandboxes can run DEV_FAST on the same node set without poisoning prod artefacts. |
| Detached signatures  | Every artefact carries `.sig`; loader verifies before use.                              | Phase-2 remote workers must sign artefacts with a registered key; the core engine refuses unsigned inputs. |

---

## Sequence Diagram – Adding a Phase-2 Testing Agent

```mermaid
title Phase-2 Orchestrator, Phase-1 Engine (CLI), Worker node / Agent
sequenceDiagram
    participant Orchestrator as Phase-2 Orchestrator
    participant Engine as Phase-1 Engine (CLI)
    participant Agent as Worker node / Agent

    Orchestrator->>Engine: create TEST exec_plan
    Engine->>Engine: exec_plan_00030.txt parsed, tasks queued
    Engine->>Agent: Task: RUN_TEST_SUITE (remote)
    Agent->>Agent: run tests, produce artifact test_results_g250.json
    Agent-->>Engine: signed artifact + cost_record
    Engine->>Engine: registry update, exec_status updated, snapshot created
    Engine-->>Orchestrator: Prometheus /metrics emits haios_task_total{type="RUN_TEST_SUITE",result="success"}
    Orchestrator->>Engine: polls exec_status_00030.txt, sees COMPLETED
```

All interactions use existing artefact, metric, or CLI contracts; Phase-1 code remains untouched.

---

## Do More ADRs Need to Be Written for Phase-1?

**No** — ADR-018/019/020 lock the last moving pieces (security, observability, runtime modes).
Phase-2 work (multi-node scheduling, new plan types, agent lifecycle) should live in new ADR-02x series, but they extend, not modify, Phase-1 contracts.

---

## Developer Checklist to Keep the Seam Clean

- **Never bypass CLI/artefact interface** — Phase-2 code generates plans or reacts to statuses; the engine remains sovereign over execution.
- **Sign everything** — remote agents append `.sig` files; engine will reject unsigned artefacts on load.
- **Tag mode correctly** — DEV_FAST artefacts must not feed STRICT plans; Validator already enforces this.
- **Respect budgets** — remote tasks must report cost; CostMeter totals guard the soft-kill path.
- **OPA policies first** — any new task type or outbound domain should ship with a matching Rego rule; ADR-018 makes OPA hot-patchable without engine redeploy.

Follow those rules and Phase-1 becomes a rock-solid kernel that Phase-2 can orchestrate and scale without weakening the security or audit guarantees already in place.