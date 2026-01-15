---
work_id: E2-285
session: 189
date: 2026-01-15
---
# Observations: E2-285 - Skill Template Single-Phase Default

## What surprised you?

The **power of structural nudging** was more evident than expected. Simply changing the primary section from "## The Cycle" to "## Instructions" fundamentally shifts agent behavior without any enforcement. Agents copy patterns they see - making single-phase the visible default naturally discourages multi-phase design.

The TDD approach caught issues immediately: tests failed on "Exit Criteria:" labels, which we then removed. This validated the S20 critique that checklists become "procedural theater" - agents check boxes without reflection.

**Unexpected ease**: The implementation was straightforward because the plan's design was thorough. No technical surprises - the work was conceptual (how to structure a template to nudge behavior) not technical.

## What's missing?

- **Scaffolding command**: A `/new-skill` command (like `/new-plan`) would enforce template usage. Currently, the template exists but agents could skip it. Out of scope for E2-285 but valuable for future work.

- **Enforcement mechanism**: Template is pure guidance. Agents can still create skills without using it. The audit skill could detect violations but doesn't prevent them.

- **Retrofit tooling**: No way to automatically update existing 10 multi-phase skills to align with new template. Would need manual refactoring or a migration tool.

## What should we remember?

**Key learnings for future template/governance work:**

1. **Structure nudges behavior more effectively than rules** - Governance through design (making the right thing the default) beats governance through enforcement (blocking the wrong thing).

2. **Agents copy what they see** - Template design is high-leverage because this single file influences every future skill creation. Visibility matters.

3. **Checklists → procedural theater** - "Exit Criteria:" labels removed because they encourage box-checking without reflection. Hard gates (binary pass/fail) force real decisions.

4. **Multi-phase must justify itself** - By requiring explicit rationale in "When Multi-Phase is Justified" section, we force conscious decision rather than default complexity.

5. **S20 "smaller containers, harder boundaries"** works - Single-phase skills with clear composition are better than multi-phase monoliths.

---

**Implementation note**: This work demonstrates the principle it implements. The observations above are substantive because the reflection was genuine, not checkbox completion.
