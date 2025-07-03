# Appendix F: Testing Guidelines

<!-- EmbeddedAnnotationBlock v1.0 START -->
```json
{
  "artifact_id": "appendix_f_testing_guidelines_g27",
  "g_created": 27,
  "version": 1,
  "source_documents": [
    "docs/appendices/Appendix_F_Testing_Guidelines.md"
  ],
  "frameworks_models_applied": [
    "AAA v1.0",
    "Evidence-Based Verification v1.0",
    "Traceability v1.0"
  ],
  "trace_id": "g27_f_testing",
  "commit_digest": null
}
```
<!-- EmbeddedAnnotationBlock v1.0 END -->

---

## Purpose
Consolidated reference for system-wide testing philosophy, patterns, required coverage levels, and quality gates.

> The full content of the original Testing Guidelines document follows. Future edits should occur here first.

<!-- Begin migrated content snippet -->
## 1. Core Philosophy: Evidence over Declaration

The overarching principle is **verifiability through evidence**. All testing must emit durable, machine-parsable `Test Results Artifacts`; human or agent claims alone are insufficient.

## 2. The AAA Pattern (Arrange ‑ Act ‑ Assert)

All unit tests **MUST** follow the AAA structure:
1. **Arrange:** Set up System Under Test (SUT), data, and doubles.
2. **Act:** Trigger exactly one behavior.
3. **Assert:** Verify outcomes and interactions.

## 3. Bias-Prevention Checklist

Validation and critique agents must apply this checklist:
- [ ] Clarity of intent in test names
- [ ] Isolation and cleanup
- [ ] Determinism (control time, randomness, network)
- [ ] Meaningful assertions, not trivial passes

## 4. Distributed-Systems Compliance (ADR-023 – ADR-029)

Testing artifacts must include `idempotency_key`, `trace_id`, and, where applicable, vector clocks. Test runners log agent identity; partitioned/async results are flagged.

*Refer to the full Testing Guideline for glossary, detailed patterns, and performance considerations.*

<!-- End migrated content snippet -->