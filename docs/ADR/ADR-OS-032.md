# ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement
Status: Proposed
Date: 2025-06-23
Deciders: Architecture Team
Reviewed By: [TBD]

## Context
Most software projects claim to follow best practices, but drift, partial adoption, or ambiguous cultural norms lead to silent technical debt and regressions.
To achieve consistently high standards, de-risking, and legible execution, this system formalizes a Registry of Canonical Models and Frameworks. All major artifacts (ADRs, roadmaps, plans, schemas, designs, test specs, etc.) must explicitly declare which models/frameworks they apply, how compliance is demonstrated, and what critiques or exceptions exist.

### Assumptions

- [ ] Best-practice models/frameworks must be explicitly cataloged and referenced, not assumed.
- [ ] Agents and humans both need to reference and apply these models/frameworks in reasoning, review, and execution.
- [ ] Compliance with models/frameworks is provable (via logic, critique, code, diagrams, or enforcement).
- [ ] Word contracts alone are insufficient; visual, structural, and behavioral contracts (diagrams, test patterns, checklists) are also mandatory.
- [ ] The models/frameworks registry and enforcement process is robust against drift, omission, and schema evolution.
- [ ] The system can detect and recover from registry/annotation omissions or compliance failures.
- [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-021) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Decision
We create and maintain a versioned, agent-readable Registry of Canonical Models and Frameworks, including but not limited to:

- Distributed Systems Principles (e.g., The Network Is Not Reliable, CAP Theorem)
- Theory of Constraints (ToC)
- AAA Testing (Arrange-Act-Assert)
- KISS (Keep It Simple, Stupid)
- DRY (Dont Repeat Yourself)
- Assumption Surfacing / Second Order Thinking
- Jobs-To-Be-Done (JTBD)
- User Stories
- Self-Critique
- Explicit Diagramming (state, flow, data, sequence, etc.)
- [Any additional models, named and versioned]

### Registry Requirements
Each model/framework entry includes:

- **Name & Version:** E.g., KISS v1.0
- **Definition:** What is required/forbidden
- **Compliance Heuristics:** What counts as proof (diagram, code, linter, etc.)
- **Enforcement Mode:** Required, Recommended, Optional
- **Agent/Inventory Representation:** Schema for agent/toolkit use

### Artifact Compliance Rules
Every major artifact (ADR, plan, doc, schema, test, etc.):

- Lists all governing models/frameworks
- Surfaces, for each, how compliance is achieved/proven (with self-critique)
- Flags any exceptions or non-compliance with justification
- Links to registry entry (with version)
- Includes diagrams/visuals when required by the model
- CI/linter must fail merges if required frameworks are omitted, unproven, or unjustified.

## Rationale
- **No cultural slop:** Every practice is explicit, versioned, and auditable.
- **Agent/automation ready:** Agents can reference and enforce models/frameworks in code or reviews.
- **Evolvable:** Models/frameworks can be updated, deprecated, or versioned as rigor or context grows.

## Alternatives Considered
- **Team culture/docstrings only:** Led to silent drift, partial adoption, and inconsistent agent reasoning.
- **Enforcement by code only:** Misses design and non-code artifacts; does not serve human review.

## Consequences
- **Positive:**
  - Architectural, design, and execution standards become legible and enforceable for humans and agents.
  - Faster onboarding, higher rigor, and safer automation.
- **Negative:**
  - Upfront documentation cost; must maintain registry and artifact annotations.

## Clarifying Questions
- Should some models/frameworks be system mandatory (cannot be omitted)?
- Who owns and updates the registry?
- How are exceptions (temporary non-compliance) tracked and resolved?

This ADR is a system requirement: all downstream ADRs, roadmaps, plans, schemas, and designs must reference and comply with at least the applicable models/frameworks in the registry, or surface their non-compliance with critique and rationale.
