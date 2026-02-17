---
template: implementation_plan
subtype: design
status: draft
date: {{DATE}}
backlog_id: {{BACKLOG_ID}}
title: "{{TITLE}}"
author: Hephaestus
lifecycle_phase: plan
session: {{SESSION}}
version: "1.5"
generated: {{DATE}}
last_updated: {{TIMESTAMP}}
---
# Design Plan: {{TITLE}}

---

<!-- TEMPLATE GOVERNANCE (v1.4)
     Design plan template — optimized for ADRs, specs, and documentation work.
     No code-specific sections (TDD, code diffs, function signatures).
     WORK-152: Fractured from monolithic implementation_plan template.

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query prior work | SHOULD | Search memory for similar designs before authoring |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

[One sentence: What design artifact will exist after this plan is complete?]

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | [N] | `Glob pattern` or explicit list |
| New files to create | [N] | List them |
| Dependencies | [N] | Documents that reference changed artifacts |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| [Phase 1] | [X min/hr] | [High/Med/Low] |
| **Total** | [X min/hr] | |

---

## Current State vs Desired State

### Current State

**What exists now:** [Describe current state — prose, not code]

**Problem:** [Why the current state is insufficient]

### Desired State

**What should exist:** [Describe target state — prose, not code]

**Outcome:** [What this enables]

---

## Detailed Design

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Decision point] | [What was chosen] | [WHY this choice - this is the most important part] |

### Design Content

<!-- Document the design artifact content here.
     For ADRs: Context, Decision, Consequences.
     For specs: Requirements, Interface, Constraints.
     For documentation: Structure, Content, Audience. -->

[Design content appropriate to the artifact type]

### Open Questions

<!-- Surface any uncertainties discovered during design -->

**Q: [Question about design]**

[Answer based on analysis, or mark as "TBD - verify during authoring"]

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| [From work item operator_decisions] | [A, B] | [BLOCKED] | [Why this choice - filled when resolved] |

---

## Implementation Steps

<!-- Each step describes authoring work, not code changes -->

### Step 1: Author Design Artifact
- [ ] [Specific authoring task]

### Step 2: Review and Validate
- [ ] [Validation criteria]

### Step 3: Update References
- [ ] **MUST:** Update CLAUDE.md if behavior documented
- [ ] **MUST:** Update READMEs in affected directories

---

## Verification

- [ ] Design artifact exists and is complete
- [ ] **MUST:** All READMEs current
- [ ] Review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | [High/Medium/Low] | [Mitigation strategy] |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/{{BACKLOG_ID}}/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| [Copy each deliverable from WORK.md] | [ ] | [How you verified it] |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `[path/to/artifact]` | [Artifact exists, content correct] | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Design artifact complete
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] Ground Truth Verification completed above

---

## References

- [Related ADR or spec]
- [Related work items]

---
