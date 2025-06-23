# Appendix G: Canonical Models & Frameworks Registry

<!-- EmbeddedAnnotationBlock v1.0 START -->
```json
{
  "artifact_id": "appendix_g_frameworks_registry_g27",
  "g_created": 27,
  "version": 1,
  "source_documents": [
    "docs/appendices/Appendix_G_Frameworks_Registry.md"
  ],
  "frameworks_models_applied": [
    "DRY v1.0",
    "KISS v1.0",
    "Traceability v1.0"
  ],
  "trace_id": "g27_g_frameworks",
  "commit_digest": null
}
```
<!-- EmbeddedAnnotationBlock v1.0 END -->

---

## Purpose
Authoritative catalogue of all frameworks and models that HaiOS artifacts must reference and comply with.

*(Content from the Canonical Models and Frameworks Registry follows.)*

<!-- Begin migrated content snippet: headline & Core Frameworks section only (truncated) -->
## Core Frameworks (v1.0)

| Framework | Description | Compliance Requirement |
|-----------|-------------|------------------------|
| **KISS** (Keep It Simple, Stupid) | Favour simplicity over complexity in design decisions | Justify complexity; default to simpler solutions |
| **DRY** (Don't Repeat Yourself) | Eliminate redundancy; single source of truth | Identify & remove duplication |
| **Theory of Constraints (ToC)** | Focus on identifying and optimising system bottlenecks | Surface constraints; optimise them |
| **Assumption Surfacing** | Make implicit assumptions explicit and validate them | Document assumptions with confidence levels |
| **Explicit Diagramming** | Use visual diagrams for clarity | Include relevant diagrams; identify gaps |

> For distributed-systems, quality, and design frameworks, see the full Canonical Registry document.

<!-- End migrated content snippet -->

## Distributed Systems Frameworks (v1.0)

| Framework | Description | Compliance Requirement |
|-----------|-------------|------------------------|
| **Distributed Systems Principles** | Core principles for building robust distributed systems | Address CAP, consistency, availability, partition tolerance |
| **CAP Theorem** | Trade-off between Consistency, Availability, Partition tolerance | Explicitly state CAP choice & trade-offs |
| **Event Ordering** | Maintain causal ordering via logical/vector clocks | Implement ordering mechanisms in logging & state |
| **Idempotency** | Safe repeat operations without side-effects | Design idempotent endpoints; handle retries |

## Quality & Testing Frameworks (v1.0)

| Framework | Description | Compliance Requirement |
|-----------|-------------|------------------------|
| **AAA (Arrange, Act, Assert)** | Structure tests into clear phases | Separate preparation, execution, validation |
| **Evidence-Based Verification** | Require verifiable proof over self-reporting | Provide artifacts; independent verification |
| **Zero Trust Security** | "Never trust, always verify" for security | Verify all access; no implicit trust relations |

## Design & Architecture Frameworks (v1.0)

| Framework | Description | Compliance Requirement |
|-----------|-------------|------------------------|
| **Separation of Concerns** | Separate functionality into distinct components | Clear boundaries; minimal coupling |
| **Separation of Duties** | Different roles handle different process aspects | No single entity controls full critical path |
| **Single Source of Truth** | One authoritative source per information piece | Identify canonical sources; eliminate conflicts |
| **First-Class Citizen Principle** | Important concepts treated as primary entities | Dedicated representation & lifecycle support |

## Process & Management Frameworks (v1.0)

| Framework | Description | Compliance Requirement |
|-----------|-------------|------------------------|
| **Traceability** | Maintain complete audit trails | Link decisions to sources; history preserved |
| **Fail-Safe Design** | Systems fail in safe, predictable manner | Define failure modes; ensure safe degradation |
| **Human-Centered Design** | Design with human users/operators in mind | Consider human factors; provide usable interfaces |

<!-- Pending: Implementation Guidelines & Registry Maintenance -->

## Implementation Guidelines

Every artifact applying these frameworks MUST include a dedicated **"Frameworks/Models Applied"** section with the following template:

```markdown
## Frameworks/Models Applied

### [Framework Name] v[Version]
- **Compliance Proof:** [How this artifact complies]
- **Self-Critique:** [Potential non-compliance or weaknesses]
- **Mitigation:** [If non-compliant, describe mitigation]
```

**Enforcement Mechanisms**
1. **Code Review** – Pull-requests must demonstrate framework compliance.
2. **CI/CD Integration** – Automated checks fail if required references are missing.
3. **Documentation Standards** – Compliance sections are mandatory in artifact templates.
4. **Audit Processes** – Regular reviews update compliance status across the registry.

## Registry Maintenance

| Process | Description |
|---------|-------------|
| **Updates** | Adding or changing a framework requires a new ADR approval. |
| **Versioning** | Framework entries follow semantic versioning; artifacts must declare version used. |
| **Deprecation** | Outdated frameworks are deprecated via ADR; artifacts referencing them must migrate or document exceptions. |
| **Compliance Tracking** | Automated reports monitor adoption; gaps trigger Issues for remediation. |

*End of Canonical Models & Frameworks Registry migration.*