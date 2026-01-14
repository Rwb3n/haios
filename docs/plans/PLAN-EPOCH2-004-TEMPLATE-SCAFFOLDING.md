---
template: implementation_plan
status: approved
date: 2025-12-06
backlog_id: E2-004
title: "PLAN-EPOCH2-004: Template Scaffolding Commands"
author: Hephaestus
project_phase: Phase 8 Complete
version: "1.0"
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-08 22:53:12
# Implementation Plan: Template Scaffolding Commands

@docs/README.md
@.claude/COMMANDS-REF.md

> **ID:** PLAN-EPOCH2-004-TEMPLATE-SCAFFOLDING
> **Status:** Draft
> **Author:** Hephaestus (Builder)
> **Context:** Epoch 2 Enablement - Reduce Validation Friction

---

## 1. Goal

Create slash commands that scaffold new files from validated templates, eliminating YAML validation errors and enforcing consistent document structure.

## 2. Problem Statement

Every new document (plan, checkpoint, handoff, report) requires:
- Manually adding YAML frontmatter with correct fields
- Remembering to add 2+ @ references
- Knowing the correct template type for the file location

**Result:** Validation errors accumulate, create noise, and slow down work.

**Evidence:** The three PLAN-EPOCH2-00X files all have validation errors because they were created without proper templates.

## 3. Proposed Commands

### 3.1. `/new-plan <name>`

Creates: `docs/plans/PLAN-<NAME>.md`

**Template:**
```markdown
---
template: plan
status: draft
date: <TODAY>
title: "PLAN-<NAME>"
author: <CURRENT_AGENT>
project_phase: Phase 8 Complete
version: "1.0"
---
# generated: <TODAY>
# Implementation Plan: <NAME>

@docs/README.md
@docs/specs/TRD-ETL-v2.md

> **ID:** PLAN-<NAME>
> **Status:** Draft
> **Author:** <CURRENT_AGENT>
> **Context:** <USER_PROVIDED or TBD>

---

## 1. Goal

<Describe the goal>

## 2. Problem Statement

<Describe the problem>

## 3. Proposed Changes

### 3.1. <Change 1>

<Details>

## 4. Verification Plan

### 4.1. <Test 1>

<Steps and expectations>

## 5. Risks

- <Risk 1>
```

### 3.2. `/new-report <name>`

Creates: `docs/reports/<DATE>-REPORT-<name>.md`

**Template:**
```markdown
---
template: report
status: final
date: <TODAY>
title: "Report: <NAME>"
author: <CURRENT_AGENT>
project_phase: Phase 8 Complete
version: "1.0"
---
# generated: <TODAY>
# <NAME> Report

@docs/README.md
@docs/plans/README.md

> **Date:** <TODAY>
> **Status:** Final
> **Author:** <CURRENT_AGENT>

## Executive Summary

<Summary>

## 1. <Section>

<Content>

## Recommendations

1. <Recommendation>
```

---

## 4. Implementation

### 4.1. File Structure

```
.claude/commands/
  new-plan.md
  new-report.md
```

### 4.2. Command Logic

Each command file will:
1. Parse arguments (name, type, etc.)
2. Generate filename with date prefix
3. Substitute template variables (<TODAY>, <NAME>, etc.)
4. Write file using Write tool
5. Report success with file path

### 4.3. Template Variables

| Variable | Source |
|----------|--------|
| `<TODAY>` | Current date (YYYY-MM-DD) |
| `<NAME>` | User-provided argument |
| `<CURRENT_AGENT>` | From output-style or default "Hephaestus" |
| `<NUM>` | Session number (for checkpoints) |
| `<TYPE>` | Handoff type argument |

---

## 5. Verification Plan

### 5.1. Test `/new-plan`

1. Run `/new-plan TEST-EXAMPLE`
2. Verify file created at `docs/plans/PLAN-TEST-EXAMPLE.md`
3. Verify no validation errors on next prompt



---

## 6. Risks

- **Argument parsing:** Slash commands have limited argument parsing; may need simple patterns
- **Date formatting:** Ensure consistent YYYY-MM-DD format across platforms
- **Template drift:** Templates must be updated when validation rules change

---

## 7. Priority

**HIGH** - This is a force multiplier. Every future document benefits from this.

---

**Requested:** 2025-12-06
**Status:** DRAFT - Ready for implementation


<!-- VALIDATION ERRORS (2025-12-06 15:01:39):
  - ERROR: Unknown template type 'plan'. Valid types: architecture_decision_record, backlog_item, checkpoint, directive, guide, implementation_plan, implementation_report, meta_template, readme, verification
-->
