# ADR-OS-031: Pre-Initiative Source Artifact Standards
Status: Proposed
Date: 2025-06-23
Deciders: Architecture Team
Reviewed By: [TBD]

## Context
Project failures and execution drift are often caused not by poor implementation, but by missing, ambiguous, or inconsistent source artifacts before execution even begins.
To ensure robust, agent- and human-driven execution, we mandate a high standard for all upstream source documents (the pre-initiative phase) which define, constrain, and derisk every downstream plan.

### Assumptions

- [ ] Execution plans and initiative docs require clearly defined, agent-parsable, and fully explicit upstream artifacts.
- [ ] Oral or ad hoc documentation is forbidden as a basis for initiative planning.
- [ ] Explicit assumption surfacing, confidence/self-critique, and diagramming are as mandatory as text sections.
- [ ] Framework/model compliance must be stated and justified in every artifact.
- [ ] The pre-initiative artifact standard is robust against missing, ambiguous, or inconsistent documentation.
- [ ] The system can detect and recover from artifact/section omissions or schema drift.
- [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-021, ADR-OS-032) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Decision
We mandate that every pre-initiative effort must include, at minimum, the following structured source artifacts, each agent- and human-consumable:

1. **Vision/North Star**
   - Brief statement of why, success criteria, and primary stakeholders.

2. **PRD (Product Requirements Doc) / MRD (Market Requirements Doc)**
   - User, business, and stakeholder requirements (JTBD, user stories, constraints, personas).
   - Explicit non-negotiables and legal/compliance constraints.

3. **TRD (Technical Requirements Doc) / Architecture Overview**
   - Context/system diagrams.
   - Stack choices, tradeoff rationale, integration/interface points.
   - DS constraints (consistency, partition tolerance, etc.).
   - Security and threat models.

4. **Design System & Pattern Registry (if applicable)**
   - Design principles (KISS, DRY, a11y, etc.).
   - Pattern/component catalog (with references to diagrams, visual assets).

5. **Assumption & Constraint Register**
   - List of all explicit assumptions, each with confidence, self-critique, and mitigation.

6. **Execution/Delivery Planning Outline**
   - Major milestones, dependencies, responsible archetypes/roles, timeline (skeleton OK pre-approval).

7. **Diagram & Protocol Pack**
   - State diagrams, sequence diagrams, flow/data models.
   - All must be referenced by section in other artifacts.

### Minimum agent-compliance rules:

- All artifacts are stored as agent-readable Markdown (or convertible schema), never locked PDF/image.
- Each artifact includes a Frameworks/Models Applied section, listing all governing patterns (e.g., KISS, ToC, JTBD, etc.), and proof-of-compliance.
- Each artifact must surface clarifying questions and open issues at submission.
- CI/lint must fail merges if required artifacts, sections, or compliance fields are missing.

## Rationale
- **No artifact, no execution:** Initiatives must not begin until upstream context is fully explicit, de-risked, and agent-parsable.
- **All context is agent-loadable:** Eliminates unexplained implicits and guarantees continuity for both human and automated agents.
- **Derisking is enforced:** Early surfacing of assumptions, constraints, and diagrams removes the most common causes of failure and scope drift.

## Alternatives Considered
- **Lean/just-in-time docs:** Led to chronic drift, poor agent onboarding, and inconsistent human handoff.
- **PDF/slide decks:** Unparsable by agents; caused missed context and downstream translation errors.

## Consequences
- **Positive:** Maximal clarity, minimal unexplained implicit context, easier review/onboarding, less rework.
- **Negative:** Slight upfront authoring friction, but offset by sharply reduced project risk and scope drift.

## Clarifying Questions
- Should CI require diagram/visual compliance as strictly as text sections?
- Is there a minimal, fast-path artifact set for ultra-small/trivial initiatives?
- How often must source artifacts be reviewed/updated during long initiatives?

This ADR is foundational: downstream plans, PRs, and initiative launches will be rejected if they do not link to a complete, agent- and human-compliant pre-initiative artifact set as defined here.
