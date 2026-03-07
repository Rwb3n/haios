---
id: templates
name: Fractured Phase Templates
epoch: E2.4 (The Activity Layer)
status: Planned
chapters:
- id: CH-001
  title: InvestigationFracture
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
- id: CH-002
  title: ImplementationFracture
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
- id: CH-003
  title: ContractValidation
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
- id: CH-004
  title: TemplateRouter
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
exit_criteria:
- text: Investigation template fractured (4 files)
  checked: false
- text: Implementation template fractured (6 files)
  checked: false
- text: Contract validation implemented
  checked: false
- text: Skills route to phase templates
  checked: false
---
# generated: 2026-01-30
# System Auto: last updated on: 2026-01-30T21:28:21
# Arc: Templates

## Arc Definition

**Arc ID:** templates
**Epoch:** E2.4 (The Activity Layer)
**Name:** Fractured Phase Templates
**Status:** Planned
**Pressure:** [volumous] - thematic exploration

---

## Theme

Fracture monolithic templates into phase-specific templates with contracts.

**From:**
```
investigation.md (372 lines, 25 MUST gates, 27 checkboxes)
```

**To:**
```
investigation/
├── EXPLORE.md        (~40 lines)
├── HYPOTHESIZE.md    (~40 lines)
├── VALIDATE.md       (~40 lines)
└── CONCLUDE.md       (~40 lines)
```

---

## Contract Pattern

Each phase template contains:

```markdown
# {PHASE} Phase

## Input Contract
- [ ] {What must exist before this phase}

## Governed Activities
- {activity-1}, {activity-2}

## Output Contract
- [ ] {What must exist after this phase}

## Template
{Minimal structure for outputs}
```

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | InvestigationFracture | Planned | Split investigation.md into 4 phase templates |
| CH-002 | ImplementationFracture | Planned | Split/create implementation phase templates |
| CH-003 | ContractValidation | Planned | Tooling to validate input/output contracts |
| CH-004 | TemplateRouter | Planned | Skill to route to correct phase template |

---

## Exit Criteria

- [ ] Investigation template fractured (4 files)
- [ ] Implementation template fractured (6 files)
- [ ] Contract validation implemented
- [ ] Skills route to phase templates

---

## Memory Refs

Session 265 fractured templates decision: 82724-82728

---

## References

- @.claude/haios/epochs/E2_4/EPOCH.md
- @.claude/templates/investigation.md (current monolithic)
- @docs/work/active/WORK-036/ (Template Tax findings)
