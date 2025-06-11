# Phase-1 Titanium Roadmap

<!-- now fully aligned with ADR-OS-018 / 019 / 020 and everything built -->

| Stream                        | Outcome at GA                                             | Epic tasks (done / in-progress / new)                                                                                                                                                                               | ADR anchor            |
| ----------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| A. Core Engine                | PlanRunner + TaskExecutor run scaffolding → snapshot end-to-end. | done: Exec loop & handlers, Snapshot handler import fix                                                                                                                                                            | 006 / 013 / 016 / 017 |
| B. Safety & Integrity         | Registry never corrupts; bad writes quarantined.         | done: Registry rotation & nightly `registry-fsck` CLI, new: Quarantine temp file on schema-fail (`atomic_write`)                                                                                             | 006 / 009 / 018-S2    |
| C. Security Baseline (ADR-018)| Vault, isolation, rlimits, kill-switches live.            | done: Vault CLI + scope tags (18-S1), Snapshot redaction hook (18-S2), Isolation modes + chroot (18-S3), CPU/MEM rlimits & CostMeter tie-in (18-S4), Kill-switch flags & SIGTERM handler (18-S5), Detached signatures verify on load (18-S6), new: OPA outbound-whitelist side-car (18-S7) | 018                   |
| D. Observability & Budgets (ADR-019)| Prom + Grafana + alerts; auto soft-kill on overspend.            | done: `/metrics` endpoint + gauges (19-O1,O2), CostMeter writes exec-status blocks (19-O3), Budget caps & soft-kill (19-O4), Weekly `COST_REPORT_g###.md` plan (19-O5), Dashboards & Alertmanager yaml (19-O6), OTel traces (19-O7)                                                               | 019                   |
| E. Developer Mode (ADR-020)   | Fast local loop without losing audit trail.                      | done: Add `runtime.mode` to config loader, PlanRunner branches on STRICT vs DEV_FAST, Scaffold CLI `haios scaffold plan --template dev-fast`                                                                                                                                                                                         | 020                   |
| F. Test & CI Gate             | ≥ 85 % coverage; static-analysis, pip-audit, SBOM.               | done: Core + utils unit tests, in-progress: Concurrency stress test, new: CI job: SBOM (CycloneDX) generation & diff                                                                                                                                                                                                                                                          | 007 / 018 / 019       |
| G. Documentation & DR         | Ops run-book, threat model, DR drill artefact.                   | in-progress: README/quick-start update, new: DR exercise report (`dr_exercise_report_g###.md`)                                                                                                                                                                                                                                                                              | 014                   |

---

### Sequenced timeline (8-week titanium sprint)

| Week | Milestones                                                                                      |
| ---- | ------------------------------------------------------------------------------------------------ |
| 1    | done: ADRs approved & config schema merged → bump `haios.config.json`                             |
| 2    | done: C1: Vault CLI, C2: Snapshot redaction hook                                                      |
| 3    | done: C3, C4: Isolation & rlimits with unit tests                                                      |
| 4    | done: C5, C6: Kill-switch layer and detached signature verification                                    |
| 5    | done: D1: Metrics endpoint & gauges, D2: CostMeter exec-status                                          |
| 6    | done: D3: Budget caps & soft-kill, D4: Weekly cost report plan, D5: Dashboards and alerts                                             |
| 7    | done: D6: OTel traces, E1–E3: DEV_FAST mode implementation                                              |
| 8    | done: B1: Registry rotation/fsck, new: B2: Quarantine path, G: DR drill & docs → tag **v1.0.0-titanium**      |

---

### Remaining ADR work

* **ADR-018, -019, -020** are drafted and PROPOSED.
* They need second-maintainer signatures → status **APPROVED**, then lock their `_goal_locked` fields.
* No further ADRs required for Phase-1; tweaks (e.g. registry fsck detail) can be minor version bumps inside ADR-006/009.

---

### Definition-of-Done – Titanium

1. Engine passes **STRICT** CI with ≥ 85 % coverage and SBOM diff clean.
2. `haios run --mode dev-fast` executes demo plan in <5 s, skips snapshot, labels artefacts `*_devfast.txt`.
3. Hard-kill signal writes ABORTED exec-status and tamper-proof issue.
4. Overspend simulation triggers soft-kill + budget alert.
5. DR drill restores from object-lock backup, `registry-fsck` passes, signatures verify.

Achieve those five points and Phase 1 is “titanium-grade” under its new ADRs.
