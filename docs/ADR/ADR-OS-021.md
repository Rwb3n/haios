# ADR-OS-021: Explicit Assumption Surfacing

* **Status**: Proposed
* **Date**: 2025-06-23
* **Deciders**: Architecture Team
* **Reviewed By**: \[TBD]

---

## Context

As the Hybrid AI Orchestration System grows in complexity, architectural decisions increasingly rely on implicit assumptions—about payloads, network behavior, agent capabilities, external dependencies, and more. When assumptions are not documented and validated, they lead to context drift, silent failures, redundant work, and costly troubleshooting.

To enforce transparency, surface hidden risks, and support reliable agent orchestration, we require a system-wide pattern for capturing, surfacing, and validating assumptions across all ADRs, workflow definitions, and agent schemas.

## Assumptions

* [ ] Every new ADR, workflow definition, and connector must declare its key assumptions in a dedicated section, at both the plan and task level where relevant.
* [ ] Each assumption must be annotated with a confidence level (High / Medium / Low).
* [ ] Each major decision or rationale must include a self-critique and confidence annotation.
* [ ] Every artifact must end with a "Clarifying Questions" block identifying unresolved issues or risks.
* [ ] Inventory/Buffering patterns (see ADR-022) require explicit inventory assumptions for plan/task artifacts.
* [ ] All new ADRs MUST explicitly state their assumptions regarding the core distributed systems policies: Idempotency (023), Asynchronicity (024), Security (025), Topology (026), Event Ordering (027), Partition Tolerance (028), and Observability (029). If a policy is not relevant, it must be noted as such.
* [ ] The assumption surfacing process is robust against author oversight and template drift.
* [ ] The CI/linter enforcement logic is versioned and auditable for changes.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Standardization v1.0
- **Compliance Proof:** Unified ADR template ensures consistent structure and content across all architectural decisions.
- **Self-Critique:** Rigid template might not accommodate unique decision contexts; could stifle creative documentation approaches.

### DRY (Don't Repeat Yourself) v1.0
- **Compliance Proof:** Single template definition eliminates duplication of ADR structure and formatting decisions.
- **Self-Critique:** Template changes require updating all existing ADRs; potential for inconsistency during transition periods.

### Assumption Surfacing v1.0
- **Compliance Proof:** Template mandates explicit assumption sections with confidence indicators and self-critique methodology.
- **Self-Critique:** Template itself has assumptions about decision-making processes that might not apply to all contexts.

### Self-Critique Methodology v1.0
- **Compliance Proof:** Template requires self-critique sections for all major decisions and rationale points.
- **Self-Critique:** Self-critique quality depends on author's objectivity and experience; might become perfunctory over time.

### Traceability v1.0
- **Compliance Proof:** Standardized structure enables systematic tracking of decision evolution and relationships.
- **Self-Critique:** Template focus on structure might not capture all relevant decision context and nuances.

### Quality Assurance v1.0
- **Compliance Proof:** Template includes review requirements and quality checkpoints for decision documentation.
- **Self-Critique:** Template compliance doesn't guarantee decision quality; process quality depends on reviewer expertise.

## Decision

We adopt an "Assumption Surfacing" pattern, formalized as follows:

1. **Assumptions** section appears immediately after Context in every ADR, workflow definition, and connector schema. Every assumption must be explicit, not implicit.
2. **Confidence** indicators accompany each assumption and major rationale (e.g., "Confidence: Medium").
3. **Self-Critique** notes are required for every major rationale (e.g., "Self-critique: Could this design cause drift under agent restart?").
4. **Clarifying Questions** must close every artifact, capturing any uncertainties, edge cases, or open decisions.
5. **CI lint rules and PR checklists** enforce presence and completeness of these sections—empty or token placeholders fail the build.
6. **Evolution**: This ADR is to be re-audited at every major system version bump and at least once every 12 months.

## Rationale

* **Reduces Hidden Risks**: Surfacing assumptions at design time forces explicit identification of failure points before deployment.
* **Consistency Across Artifacts**: Uniform templates at plan and task level ensure all teams and agents follow the same discipline.
* **Feedback Loop for Growth**: Required self-critiques and clarifying questions drive iterative improvement and faster onboarding.
* **Links to Inventory/Buffering**: Ensures mechanical buffers (see ADR-022) have their own surfaced assumptions, closing the loop between design and runtime context safety.

## Example Usage

```markdown
## Assumptions
- [ ] Service X will respond within 200 ms. (Confidence: Medium)
- [ ] Agent state files are atomic. (Confidence: High)
- [ ] Inventory buffer contains at least one valid credential. (Confidence: Low)

## Decision
The engine will retry failed calls to Service X three times before escalating.
**Confidence:** Medium

## Rationale
1. **Retries reduce transient error impact.**  
   - Self-critique: May mask deeper bugs; needs real monitoring.  
   - Confidence: Medium

## Alternatives Considered
- Circuit breaker pattern (Confidence: Low): Too complex for first phase.
- Synchronous blocking (Confidence: High): Too brittle under real network conditions.

## Consequences
- **Positive**: Fewer task failures due to brief outages.
- **Negative**: Slightly increased latency per error.

## Clarifying Questions
- What metric threshold should escalate a retry to manual review?
- How will the system recover inventory assumptions after a catastrophic agent crash?
```

## Alternatives Considered

1. **Code Comments and Reviews**: Inconsistent, easily outdated, often skipped under deadline.
2. **Automated Runtime Checks Only**: Catches errors late; fails to surface mental models and design-time tradeoffs.
3. **Optional Assumption Sections**: Reliant on author discipline; usually skipped or left empty.

## Consequences

* **Positive**: Early risk detection, improved documentation quality, reliable onboarding, clearer PR reviews, reduced context drift.
* **Negative**: Slight increase in authoring overhead for ADRs and workflow specs; minor initial friction during culture shift.

## Clarifying Questions

* Should assumption/confidence annotations be standardized (e.g., dropdown in templates) or freeform, and how will this impact author compliance and review quality?
* What CI/linter rules will be considered a pass vs. fail, and how will these rules evolve as the system and templates change?
* How should we treat legacy artifacts that lack assumption surfacing—require migration, flag as technical debt, or allow exceptions?
* Is per-assumption confidence sufficient, or should we require confidence at plan, task, and artifact level for full traceability?
* What mechanisms are in place to audit, validate, and continuously improve the assumption surfacing process across all artifacts and system versions?

---

*See ADR-OS-022 for details on inventory/buffer assumptions. This pattern is now required for all major system artifacts and decision records.*
