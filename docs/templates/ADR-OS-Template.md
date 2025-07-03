# ADR-OS-XXX: [Short Decision Title]

**Status**: {Proposed | Accepted | Deprecated}  
**Date**: YYYY-MM-DD  
**Deciders**: [List of decision-makers]  
**Reviewed By**: [List of reviewers]

## Context

Describe the background and motivation for this decision. Explain what problem or requirement the architecture must address.

Include:
- The fundamental challenge being addressed
- How this decision fits into the broader system architecture
- Any critical dependencies or relationships with other components
- Why this decision is needed now

## Assumptions

List the key assumptions underlying this decision. Number each assumption for easy reference.

1. **[Assumption Category]**: [Detailed assumption statement]
2. **[Assumption Category]**: [Detailed assumption statement]
3. **[Assumption Category]**: [Detailed assumption statement]

*Example categories: Performance, Scalability, Security, User Behavior, Technical Constraints, Resource Availability*

## Models and Frameworks Applied

List all governing models, frameworks, and design/engineering heuristics that inform or constrain this decision. For each, provide specific evidence of application.

### [Model/Framework Name]
- **Application**: How this model/framework is specifically applied in this decision
- **Proof**: Concrete evidence or implementation details demonstrating compliance
- **Rationale**: Why this model/framework is relevant to this decision

*Example:*
### Evidence-Based Development
- **Application**: Every component produces verifiable artifacts with integrity checks
- **Proof**: All outputs include SHA-256 hashes and timestamp validation
- **Rationale**: Ensures tamper-proof audit trails and reproducible results

### Distributed Systems Principles
- **Application**: All operations designed for idempotency and eventual consistency
- **Proof**: Retry logic with exponential backoff, unique request IDs
- **Rationale**: Enables reliable operation in unreliable network conditions

## Decision

### Primary Decision
**[State the main architectural or design decision in one clear sentence]**

### Detailed Decisions

1. **[Decision Component 1]**
   - [Detailed description of this aspect of the decision]
   - Confidence: {Very High (0.95) | High (0.85-0.94) | Medium (0.70-0.84) | Low (<0.70)}
   - Self-critique: [What assumptions might be wrong? What could fail?]

2. **[Decision Component 2]**
   - [Detailed description of this aspect of the decision]
   - Confidence: {Very High (0.95) | High (0.85-0.94) | Medium (0.70-0.84) | Low (<0.70)}
   - Self-critique: [Potential weaknesses or limitations]

### Confidence Indicators
- Overall Architectural Confidence: **[Level] ([Numeric])**
- Technical Implementation Confidence: **[Level] ([Numeric])**
- Integration Confidence: **[Level] ([Numeric])**

## Rationale

Explain why this decision was made. Structure each rationale section with clear headers.

### Why [Specific Choice 1]
1. **[Benefit/Reason 1]**: [Detailed explanation]
2. **[Benefit/Reason 2]**: [Detailed explanation]
3. **[Benefit/Reason 3]**: [Detailed explanation]

*Self-critique: [What are the potential downsides or risks of this choice? What assumptions might prove incorrect?]*

### Why [Specific Choice 2]
1. **[Benefit/Reason 1]**: [Detailed explanation]
2. **[Benefit/Reason 2]**: [Detailed explanation]

*Self-critique: [Honest assessment of limitations or concerns]*

## Alternatives Considered

### Alternative 1: [Alternative Name]
- **Description**: [What this alternative would entail]
- **Pros**: [Key advantages]
- **Cons**: [Key disadvantages]
- **Rejection Reason**: [Why this wasn't chosen]

### Alternative 2: [Alternative Name]
- **Description**: [What this alternative would entail]
- **Pros**: [Key advantages]
- **Cons**: [Key disadvantages]
- **Rejection Reason**: [Why this wasn't chosen]

## Consequences

### Positive Consequences
1. **[Benefit Category]**: [Detailed positive outcome]
2. **[Benefit Category]**: [Detailed positive outcome]
3. **[Benefit Category]**: [Detailed positive outcome]

### Negative Consequences
1. **[Risk Category]**: [Detailed negative outcome or cost]
2. **[Risk Category]**: [Detailed negative outcome or cost]
3. **[Risk Category]**: [Detailed negative outcome or cost]

### Risk Mitigation Strategies
1. **[Risk from above]**: [Specific mitigation approach]
2. **[Risk from above]**: [Specific mitigation approach]
3. **[Risk from above]**: [Specific mitigation approach]

## Clarifying Questions

### Q1: [Question requiring future investigation]
*Context: [Why this question matters and what depends on the answer]*

### Q2: [Question requiring future investigation]
*Context: [Why this question matters and what depends on the answer]*

### Q3: [Question requiring future investigation]
*Context: [Why this question matters and what depends on the answer]*

## References

- [Related ADR]: [Brief description of relationship]
- [Related Schema]: [Path to schema file]
- [Related Implementation]: [Path to code or configuration]
- [External Documentation]: [Links to relevant external resources]

---

*This template incorporates:*
- *Structured decision components with individual confidence ratings*
- *Explicit self-critique sections throughout*
- *Risk mitigation strategies paired with negative consequences*
- *Contextual clarifying questions*
- *Numbered lists for better organization and reference*
- *Clear separation between primary and detailed decisions*
- *Comprehensive alternatives analysis*

*Template version: 2.0 (Enhanced based on ADR-OS-041 patterns)*