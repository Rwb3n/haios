# Canonical Models and Frameworks Registry

**Version:** 1.0  
**Status:** ACTIVE  
**Last Updated:** 2025-01-27  
**Compliance Reference:** ADR-OS-032

---

## Purpose

This registry defines the canonical models and frameworks that all HaiOS artifacts MUST explicitly reference and prove compliance with, as mandated by ADR-OS-032: Canonical Models and Frameworks Registry & Enforcement.

---

## Core Frameworks

### KISS (Keep It Simple, Stupid) v1.0
- **Description:** Favor simplicity over complexity in design decisions
- **Compliance Requirements:** Justify complexity; default to simpler solutions
- **Common Applications:** Architecture decisions, API design, process workflows

### DRY (Don't Repeat Yourself) v1.0  
- **Description:** Avoid duplication of information and logic
- **Compliance Requirements:** Identify and eliminate redundancy; single source of truth
- **Common Applications:** Code structure, data models, documentation

### Theory of Constraints (ToC) v1.0
- **Description:** Focus on identifying and optimizing system bottlenecks
- **Compliance Requirements:** Identify constraints; optimize constraint points
- **Common Applications:** Performance optimization, workflow design, resource allocation

### Assumption Surfacing v1.0
- **Description:** Make implicit assumptions explicit and validate them
- **Compliance Requirements:** Document assumptions with confidence levels and validation checkboxes
- **Common Applications:** All ADRs, planning documents, architectural decisions

### Explicit Diagramming v1.0
- **Description:** Use visual diagrams to clarify complex relationships and processes
- **Compliance Requirements:** Include relevant diagrams; identify when diagrams are missing
- **Common Applications:** System architecture, process flows, data relationships

---

## Distributed Systems Frameworks

### Distributed Systems Principles v1.0
- **Description:** Core principles for building robust distributed systems
- **Compliance Requirements:** Address CAP theorem, consistency, availability, partition tolerance
- **Common Applications:** Service design, data consistency, failure handling

### CAP Theorem v1.0
- **Description:** Choose between Consistency, Availability, and Partition tolerance
- **Compliance Requirements:** Explicitly state CAP choice and trade-offs
- **Common Applications:** Database design, service architecture, data synchronization

### Event Ordering v1.0
- **Description:** Ensure proper ordering of events in distributed systems
- **Compliance Requirements:** Use logical clocks, vector clocks for causality
- **Common Applications:** Event logging, state management, audit trails

### Idempotency v1.0
- **Description:** Operations can be repeated safely without side effects
- **Compliance Requirements:** Design idempotent operations; handle retries safely
- **Common Applications:** API design, failure recovery, retry mechanisms

---

## Quality & Testing Frameworks

### AAA (Arrange, Act, Assert) v1.0
- **Description:** Structure tests and processes with clear phases
- **Compliance Requirements:** Separate preparation, execution, and validation phases
- **Common Applications:** Test design, process workflows, validation procedures

### Evidence-Based Verification v1.0
- **Description:** Require verifiable proof rather than self-reporting
- **Compliance Requirements:** Provide evidence artifacts; independent verification
- **Common Applications:** Testing, quality assurance, compliance validation

### Zero Trust Security v1.0
- **Description:** Never trust, always verify security model
- **Compliance Requirements:** Verify all access; no implicit trust relationships
- **Common Applications:** Security design, access control, agent interactions

---

## Design & Architecture Frameworks

### Separation of Concerns v1.0
- **Description:** Separate different aspects of functionality into distinct components
- **Compliance Requirements:** Clear boundaries between components; minimal coupling
- **Common Applications:** System architecture, module design, responsibility allocation

### Separation of Duties v1.0
- **Description:** Different roles should handle different aspects of critical processes
- **Compliance Requirements:** No single entity controls entire critical path
- **Common Applications:** Security processes, approval workflows, validation chains

### Single Source of Truth v1.0
- **Description:** Designate one authoritative source for each piece of information
- **Compliance Requirements:** Identify canonical sources; eliminate conflicting sources
- **Common Applications:** Data management, configuration, documentation

### First-Class Citizen Principle v1.0
- **Description:** Important concepts should be treated as primary entities in the system
- **Compliance Requirements:** Dedicated representations; full lifecycle support
- **Common Applications:** Entity modeling, API design, system architecture

---

## Process & Management Frameworks

### Traceability v1.0
- **Description:** Maintain complete audit trails and relationship mapping
- **Compliance Requirements:** Link decisions to sources; maintain change history
- **Common Applications:** Requirements tracking, change management, audit compliance

### Fail-Safe Design v1.0
- **Description:** Systems should fail in a safe, predictable manner
- **Compliance Requirements:** Define failure modes; ensure safe degradation
- **Common Applications:** Error handling, system design, recovery procedures

### Human-Centered Design v1.0
- **Description:** Design systems with human users and operators in mind
- **Compliance Requirements:** Consider human factors; provide appropriate interfaces
- **Common Applications:** UI design, process design, reporting systems

---

## Implementation Guidelines

### Compliance Documentation Format

Each artifact applying these frameworks MUST include a "Frameworks/Models Applied" section with:

```markdown
## Frameworks/Models Applied

### [Framework Name] v[Version]
- **Compliance Proof:** [How this artifact complies with the framework]
- **Self-Critique:** [Honest assessment of potential non-compliance or weaknesses]
- **Mitigation:** [If non-compliant, describe mitigation strategy]
```

### Enforcement Mechanisms

1. **Code Review:** All artifacts must demonstrate framework compliance
2. **CI/CD Integration:** Automated checks for required framework references
3. **Documentation Standards:** Framework compliance sections mandatory
4. **Audit Processes:** Regular compliance reviews and updates

---

## Registry Maintenance

- **Updates:** Framework additions/changes require ADR approval
- **Versioning:** Semantic versioning for framework definitions
- **Deprecation:** Formal process for retiring outdated frameworks
- **Compliance Tracking:** Monitor and report framework adoption across artifacts

---

*This registry is maintained as part of ADR-OS-032 compliance and is subject to the same governance and change management processes as other architectural decisions.*
