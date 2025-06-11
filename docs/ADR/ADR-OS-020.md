# ADR-OS-020 — Runtime Modes & Developer Experience

*Status*: **PROPOSED**
*Deciders*: dx-steering-committee
*Date*: 2025-06-11

## 1  Context

Phase‑1 aims for *titanium‑grade* safety, but everyday contributors need a faster inner loop.  Today every run executes full readiness checks, writes snapshots, and enforces hard budgets—great for CI, heavy for day‑to‑day coding.  We need an **official switchboard** so devs can trade off rigour for velocity *without* bypassing audit expectations.

## 2  Decision

Introduce a **`runtime.mode`** field in `haios.config.json` (override‑able by CLI flag `--mode`).  Exactly two modes are recognised for Phase‑1:

| Mode                                                                                                  | Purpose                                                                                                  | Behaviour deltas from STRICT                                                                                                                                     | Artefact labelling                   |
| ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| `STRICT` *(default)*                                                                                  | CI, prod runs, releases                                                                                  | • Full readiness checks<br>• Snapshots required<br>• Budgets enforced at 100 %<br>• Detached signatures verified<br>• Kill‑switch escalation on first violation  | No suffix (e.g. `snapshot_g230.txt`) |
| `DEV_FAST`                                                                                            | Local dev & spike branches                                                                               | • Readiness failures → *warning* only<br>• Snapshots **skipped** unless task type explicitly `CREATE_SNAPSHOT`<br>• Budgets enforced at 150 % (soft‑kill beyond) |                                      |
| • Detached signature **validation skipped**, signing still happens<br>• Prometheus metrics still emit | Artefacts gain `devfast` suffix: `exec_status_g231_devfast.txt` & registry entry flag `"dev_mode": true` |                                                                                                                                                                  |                                      |

### Config schema changes

```jsonc
"runtime": {
  "mode": "STRICT",      // enum STRICT | DEV_FAST
  "cli_override": true     // allows --mode flag
}
```

### Execution‑time enforcement

* `engine.py` resolves mode: CLI flag > config > default.
* `PlanRunner` branches on mode for:

  * snapshot scheduling,
  * readiness severity, and
  * budget threshold multiplier.
* `atomic_io` and `CostMeter` remain unchanged—safety rails still active.

## 3  Rationale

* **Make the common case fast** – skipping snapshots & downgrading early errors makes iterative coding seconds, not minutes.
* **Still audit everything** – artefact suffix + registry flag ensure dev runs are distinguishable and ignorable during formal reviews.
* **Zero hidden branches in prod** – only two modes; dev mode must be explicitly configured or flagged.

## 4  Consequences

* CI images MUST hard‑set `runtime.mode=STRICT`; otherwise PRs fail policy check.
* Any artefact produced in DEV\_FAST is *disallowed* as a dependency for STRICT plans—Validator will raise `INPUT_NOT_STRICT` error.
* Documentation and scaffold generator must include mode flag examples.

## 5  Alternatives considered

*Full continuum of tuning knobs* — more granular but explodes test matrix.  Two modes keep reasoning tractable while solving 90 % of pain.

---

```jsonc
/* EmbeddedAnnotationBlock */
{
  "artifact_id_of_host": "adr_os_020_md_g232",
  "version_tag": "v1.0",
  "g_created": 232,
  "g_last_modified": 232,
  "authors_and_contributors": ["dx-steering-committee"],
  "external_dependencies": [],
  "internal_dependencies": [
    "core_config_loader_py_g151",
    "engine_py_g120",
    "utils_cost_meter_py_g226"
  ],
  "quality_notes": {
    "unit_tests": {"status": "N/A", "notes": "Policy document"},
    "overall_quality_assessment": "PASS"
  }
}
```
