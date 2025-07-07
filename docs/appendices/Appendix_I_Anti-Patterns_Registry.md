# Appendix I: Anti-Patterns Registry

<!-- EmbeddedAnnotationBlock -->
{
  "artifact_id": "appendix_i_anti_patterns_registry_g(current)",
  ...
}
<!-- END -->

## Purpose
This document serves as the canonical, version-controlled registry of known architectural and procedural anti-patterns. The HAiOS Plan Validation Gateway lints all proposed Execution Plans against this registry. Proposals that exhibit these anti-patterns will be rejected with a reference to the relevant entry.

---

## Registry of Anti-Patterns (v1.0)

| Anti-Pattern ID | Name                       | Description                                                                                                                                     | Why it is Harmful                                                                                                | Recommended Alternative                                         |
|:----------------|:---------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------|
| **AP-001**      | **Monolithic Execution Plan** | An attempt to define an entire, multi-stage initiative within a single, large Execution Plan, instead of breaking it down into smaller, sequential plans per lifecycle stage. | Violates iterative development; prevents validation at each stage; creates high-risk, "big bang" deployments; makes failure recovery complex. | Deconstruct the work into a formal `Initiative Plan` with multiple, smaller `Execution Plans`, one for each lifecycle stage. |
| **AP-002**      | **Premature Hardening**      | Implementing production-grade security, scaling, or optimization features in a v0.1 prototype before the core functionality has been proven to work. | Wastes resources on features that may be unnecessary or incorrect; adds complexity that slows down initial validation; violates the KISS principle. | Build the simplest possible "happy path" first. Harden and optimize in later, dedicated `REMEDIATION` or `REFACTORING` plans. |
| **AP-003**      | **Implicit Governance**     | Relying on descriptive text or comments to enforce a rule, instead of a machine-readable, programmatically verifiable mechanism.                    | Prone to being ignored by both humans and AI; unauditable; not enforceable by automated tooling.                 | Codify the rule in a schema, a configuration file, a dedicated governance hook, or a CI/CD linting check.        |