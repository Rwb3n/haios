# ADR‑OS‑018 — Security Baseline & Kill‑Switch Controls

*Status*: **PROPOSED**
*Deciders*: platform‑security‑wg
*Date*: 2025‑06‑11

## 1  Context

Phase‑1 delivers a runnable engine that executes execution‑plans on a single node.  We now need a **titanium‑grade security baseline** that lets us:

* protect credentials and signing keys,
* contain the blast‑radius of mis‑behaving agents or code,
* stop execution instantly (or gracefully) without corrupting the audit trail, and
* guarantee artefact integrity end‑to‑end.

Existing ADRs cover I/O atomicity (ADR‑006), error escalation (ADR‑011) and constraint locking (ADR‑010) but do **not** define mandatory runtime hardening controls.

## 2  Decision

We introduce the following **mandatory controls**.  Any Phase‑1 engine claiming compliance **MUST** implement them exactly as specified.

| ID        | Control                        | Mandatory artefacts / flags                                                      | Enforcement path                                                                       |                                 |                                                                |                                                                                         |
| --------- | ------------------------------ | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **18‑S1** | *Secrets vault*                | `vault/secrets.json.gpg` (age‑encrypted).  Secrets carry `scope` = \`global      | initiative                                                                             | plan                            | agent\`.                                                       | PlanRunner decrypts at start‑up and surfaces **only** required scopes to task‑handlers. |
| **18‑S2** | *Snapshot redaction*           | `snapshot_utils` filters strings matching `vault.redact_regexes` before writing. | Failing to redact triggers snapshot write abort + `EMERGENCY_STOP`.                    |                                 |                                                                |                                                                                         |
| **18‑S3** | *Process isolation*            | \`haios.config.json.execution.isolation = "none                                  | namespaces                                                                             | strict"\` (default **strict**). | TaskExecutor enters chroot + drops to UID `haios` when strict. |                                                                                         |
| **18‑S4** | *Resource limits*              | `budgets.max_cpu_seconds`, `max_mem_bytes` in config.                            | CostMeter enforces; violation → soft‑kill + `BUDGET_EXCEEDED`.                         |                                 |                                                                |                                                                                         |
| **18‑S5** | *Kill‑switches*                | Flag files:<br>• `control/soft_kill.flag`<br>• `control/write_lockdown.flag`     | PlanRunner checks each task loop; atomic\_io blocks writes when lockdown flag present. |                                 |                                                                |                                                                                         |
| **18‑S6** | *Detached artefact signatures* | `<artifact>.sig` (Ed25519).                                                      | Signature verified on load; mismatch → `TAMPER_DETECTED` Issue + hard abort.           |                                 |                                                                |                                                                                         |
| **18‑S7** | *Outbound network policy*      | `guidelines/outbound_whitelist.rego` locked.                                     | OPA side‑car denies socket connect not matching allowlist.                             |                                 |                                                                |                                                                                         |

## 3  Rationale

* **Layered defence** — Even if one guard falls (e.g. chroot escape) others (write‑lockdown, rlimits) contain damage.
* **Human‑inspectable kill paths** — Flag files & state fields leave a durable trace; auditors can prove **who** pulled which switch.
* **Future multi‑agent safe** — Scoping secrets and outbound policies per plan/agent lets us on‑board un‑trusted LLM agents without full credential exposure.

## 4  Consequences

* Adds a small run‑time overhead (OPA eval, signature checks) — acceptable for safety.
* Developers must initialise the vault and whitelist before first plan run.
* CI images need `age`, `ed25519` libs, and OPA binary (\~15 MB).
* Existing ADRs **unchanged**; this ADR plugs the security gap and references them.

## 5  Alternatives considered

*Use kernel LSMs (AppArmor/SELinux) instead of chroot* — too OS‑specific for Phase‑1 scope.

---

```jsonc
/* EmbeddedAnnotationBlock */
{
  "artifact_id_of_host": "adr_os_018_md_g230",
  "version_tag": "v1.0",
  "g_created": 230,
  "g_last_modified": 230,
  "authors_and_contributors": ["cody_architect_v1"],
  "external_dependencies": [
    {"name": "opa", "version_constraint": ">=0.59,<1.0"},
    {"name": "age", "version_constraint": ">=1.1,<2.0"},
    {"name": "pynacl", "version_constraint": ">=1.5,<2.0"}
  ],
  "internal_dependencies": [
    "core_atomic_io_py_g222",
    "core_config_py_g150",
    "utils_snapshot_utils_py_g225"
  ],
  "quality_notes": {
    "unit_tests": {"status": "N/A", "notes": "Policy document"},
    "overall_quality_assessment": "PASS"
  }
}
```
