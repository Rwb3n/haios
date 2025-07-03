# Appendix H: CI/CD Policy & Pipeline Reference

<!-- EmbeddedAnnotationBlock v1.0 START -->
```json
{
  "artifact_id": "appendix_h_ci_cd_policy_pipeline_reference_g27",
  "g_created": 27,
  "version": 1,
  "source_documents": [
    "docs/appendices/Appendix_H_CI_CD_Policy_Pipeline_Reference.md"
  ],
  "frameworks_models_applied": [
    "Idempotency v1.0",
    "Zero Trust Security v1.0",
    "Traceability v1.0"
  ],
  "trace_id": "g27_h_ci_cd",
  "commit_digest": null
}
```
<!-- EmbeddedAnnotationBlock v1.0 END -->

---

## Purpose
Defines the standard CI/CD workflows, gates, and security/observability requirements that every HaiOS project must implement.

*(Content of original CI/CD setup guide truncated for brevity; see source document for full detail.)* 

## CI Pipeline Overview

1. **Test Suite** – matrix test across Python 3.9-3.12, linting, typing, coverage upload.
2. **Schema Validation & Compliance** – validates JSON schemas; fails build if ADR-023-029 fields missing.
3. **Clarification Artifact Validation** – custom linter checks that every ADR (001-032) has a corresponding clarification file under `docs/ADR/clarifications/` **and** that each clarification file contains all mandatory template sections (Assumptions & Constraints, Dependencies & Risks, Summary, Clarification Questions, Responses, Traceability, Distributed-Systems Compliance). Build fails on any mismatch or missing section.
4. **End-to-End Tests** – executes demo in dev-fast mode and archives artifacts.
5. **Security Scan** – Bandit, Safety, Trivy with SARIF upload.
6. **Build Check** – validates package build integrity.

## CD Pipeline Overview

1. **Release Creation** (idempotency key = Git tag)
2. **PyPI Publishing** (idempotency key = package version)
3. **Docker Image Build** with Trivy scan
4. **Documentation Deployment** via MkDocs

## Distributed-Systems Compliance Hooks

| Principle | Enforcement in CI/CD |
|-----------|---------------------|
| **Idempotency (ADR-023)** | Idempotency keys for release/publish jobs |
| **Consistency (ADR-024)** | Jobs annotated with `STRONG` / `EVENTUAL` |
| **Zero-Trust Security (ADR-025)** | Runs with scoped tokens; runner identity logged |
| **Traceability (ADR-029)** | Propagate `TRACE_ID` to logs and artifacts |
| **Failure & Partition Tolerance (ADR-026/028)** | Retry logic, runner health logging |

## Local Development Tools

### Makefile Commands (excerpt)

| Command | Purpose |
|---------|---------|
| `make install` | Install production dependencies |
| `make install-dev` | Install dev dependencies |
| `make dev-setup` | One-shot full dev environment setup |
| `make test` / `make test-*` | Run unit / integration / e2e tests |
| `make lint` / `make type-check` | Run linting & static typing |
| `make security-scan` | Bandit + Safety + Trivy scans |
| `make ci` / `make cd` | Simulate full CI / CD locally |

### Pre-Commit Hooks

Runs on every commit:
* Formatting – Black, isort
* Linting – flake8, bandit
* Type Checking – mypy
* File Hygiene – whitespace, line endings, YAML/JSON validation
* Security – Trivy FS scan
* Schema & Distributed-Systems Compliance linter

Install with `make setup-hooks` or `pre-commit install`.

## Environment Variables & Secrets

| Variable | Description |
|----------|-------------|
| `PYPI_API_TOKEN` | Secret for PyPI publishing |
| `GITHUB_TOKEN` | Provided by GitHub runner |
| `TRACE_ID` | Unique trace for each pipeline run |
| `IDEMPOTENCY_KEY` | Prevents duplicate deployments |
| `CONSISTENCY_MODE` | `STRONG` or `EVENTUAL` annotation for jobs |
| `AUTHORIZED_AGENT` | Identity of CI/CD actor |
| `HAIOS_MODE` | Runtime mode (`development` / `production`) |
| `HAIOS_LOG_LEVEL` | Logging verbosity |

## Quality Gates

CI will fail unless:
* All tests pass with **≥ 85 % coverage**
* No lint/type/security errors
* Schema validation & distributed-systems compliance linter pass
* Clarification artefact linter confirms 1-to-1 ADR↔clarification mapping and template completeness

## Monitoring & Observability

* Codecov for coverage trends (linked by `TRACE_ID`)
* SARIF security results surfaced in GitHub Security tab
* Enhanced logging prefix: `Build: $BUILD_ID Trace: $TRACE_ID Agent: $AUTHORIZED_AGENT`

## Troubleshooting (common)

| Issue | Quick Fix |
|-------|-----------|
| Pre-commit failures | `make format` then `pre-commit autoupdate` |
| Test failures | Run `pytest -v`, examine coverage |
| Docker build issues | `make docker-build`, check `docker logs` |
| Schema validation errors | `make validate`, ensure schema fields present |

## Best Practices & Future Enhancements

Best practices:
* Conventional commit messages
* `main`/`develop` branch strategy
* Maintain coverage & security scans

Planned enhancements:
* Performance benchmarking in CI
* Multi-platform Docker builds
* Automated dependency updates
* Load testing automation
* External monitoring integration

*End of CI/CD Policy & Pipeline Reference migration.* 