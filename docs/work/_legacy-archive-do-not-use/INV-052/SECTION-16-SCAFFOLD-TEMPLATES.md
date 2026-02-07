# generated: 2025-12-30
# System Auto: last updated on: 2026-01-02T21:44:59
# Section 16: Scaffold Templates

Generated: 2025-12-30 (Session 152)
Updated: 2026-01-02 (Session 156) - Aligned with L0-L4 hierarchy
Purpose: Document template system and how it enforces information architecture
Status: DESIGN

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Templates not in portable plugin** | .claude/templates/ is Claude-specific | Move to .claude/haios/templates/ |
| **No template → context level mapping** | Templates exist but not tied to L0-L3 | Add level field to templates |
| **Validation is post-hoc** | validate.py checks after creation | Add pre-scaffold validation |

---

## Target Architecture: Template Hierarchy

```
.claude/haios/templates/           <- HAIOS CORE (LLM-agnostic)
├── checkpoint.md                  <- L3 (session context)
├── work_item.md                   <- L3 (work context)
├── implementation_plan.md         <- L3 (work context)
├── investigation.md               <- L3 (work context)
├── observations.md                <- L3 (work context)
├── architecture_decision_record.md <- L1/L2 (durable decisions)
├── report.md                      <- L2 (operational)
├── handoff_investigation.md       <- L3 (session context)
│
└── bootstrap/                     <- Special: generate agent bootstrap
    └── agent-bootstrap.md.j2      <- Generates CLAUDE.md, GEMINI.md, etc.
```

---

## Template → Context Level Mapping (L0-L4 Hierarchy)

| Template | Output Path | Level | Purpose |
|----------|-------------|-------|---------|
| checkpoint.md | docs/checkpoints/ | L4 | Session capture |
| work_item.md | docs/work/active/{id}/ | L4 | Work tracking |
| implementation_plan.md | docs/work/active/{id}/plans/ | L4 | Implementation spec |
| investigation.md | docs/investigations/ | L4 | Research tracking |
| observations.md | docs/work/active/{id}/ | L4 | Session observations |
| architecture_decision_record.md | docs/ADR/ | L3→L4 | Durable decisions (may affect L3 requirements) |
| report.md | docs/reports/ | L4 | Analysis output |

**Note:** All templates produce L4 (implementation) documents. ADRs are special - they may formalize patterns that get promoted to L3 requirements.

---

## Template Anatomy

```yaml
---
# Template frontmatter (parsed by scaffold.py)
template: checkpoint
version: "1.3"
level: L3                          # <- Context level
required_fields:
  - session
  - date
  - title
  - backlog_ids
optional_fields:
  - memory_refs
  - prior_session
validation:
  - rule: session_is_number
  - rule: date_is_iso
  - rule: backlog_ids_exist
---

# Session {{session}} Checkpoint: {{title}}

> **Date:** {{date}}
> **Focus:** {{title}}

## Session Summary
[To be filled]

## Completed Work
- [ ] [To be filled]

...
```

---

## Scaffold → Validate → Populate Flow

```
/new-checkpoint 152 "S152 Analysis"
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│  1. SCAFFOLD (scaffold.py)                                      │
│  ──────────────────────────────────────────────────────────────│
│  • Load template: .claude/haios/templates/checkpoint.md         │
│  • Parse frontmatter: required_fields, validation rules         │
│  • Generate filename: 2025-12-30-03-SESSION-152-s152-analysis.md│
│  • Populate frontmatter: session=152, date=2025-12-30           │
│  • Write to docs/checkpoints/                                   │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│  2. VALIDATE (PostToolUse hook → validate.py)                   │
│  ──────────────────────────────────────────────────────────────│
│  • Detect file written to governed path                         │
│  • Load template for that path                                  │
│  • Check required_fields present                                │
│  • Run validation rules                                         │
│  • Log to validation.jsonl                                      │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────────────┐
│  3. POPULATE (checkpoint-cycle skill)                           │
│  ──────────────────────────────────────────────────────────────│
│  • FILL phase: Agent populates sections                         │
│  • VERIFY phase: anti-pattern-checker validates claims          │
│  • CAPTURE phase: ingester_ingest stores learnings              │
└────────────────────────────────────────────────────────────────┘
```

---

## Template Governance Rules

| Rule | Check | Enforcement |
|------|-------|-------------|
| **Path governance** | File path matches template output path | PreToolUse blocks Write to wrong path |
| **Required fields** | Frontmatter has all required fields | PostToolUse validation |
| **Field types** | session is number, date is ISO | PostToolUse validation |
| **Placeholder detection** | "[To be filled]" still present | DoD validation gate |
| **Template version** | Document version matches template | PostToolUse warning |

---

## Template Registry (Target)

```yaml
# .claude/haios/config/template-registry.yaml
templates:
  checkpoint:
    path: templates/checkpoint.md
    output_pattern: "docs/checkpoints/{{date}}-{{seq}}-SESSION-{{session}}-{{slug}}.md"
    level: L3
    governed: true
    validation:
      required: [session, date, title, backlog_ids]
      rules: [session_is_number, date_is_iso, backlog_ids_exist]

  work_item:
    path: templates/work_item.md
    output_pattern: "docs/work/active/{{id}}/WORK.md"
    level: L3
    governed: true
    validation:
      required: [backlog_id, title, status, current_node]
      rules: [backlog_id_format, status_enum, node_enum]

  architecture_decision_record:
    path: templates/architecture_decision_record.md
    output_pattern: "docs/ADR/ADR-{{number}}-{{slug}}.md"
    level: L1  # ADRs are durable - affect invariants
    governed: true
    validation:
      required: [number, title, status, date]
```

---

## Template → Information Architecture Link (L0-L4)

```
Template creates document at L4 (implementation)
        │
        ▼
Document may formalize pattern worth promoting
        │
        ▼
ADR captures decision, potentially affects L3 requirements
        │
        ▼
coldstart loads L0-L3 manifesto + L4 context
        │
        ▼
Agent has appropriate grounding for work

Example:
- ADR created (L4 document)
- ADR formalizes pattern (e.g., "Certainty Ratchet")
- Pattern promoted to L3-requirements.md (immutable)
- Next coldstart: Pattern is foundational context

This is the GOVERNANCE FLYWHEEL:
L4 Templates → L4 Documents → Promote to L3 → Context → Behavior → Feedback
```

---

## Current Templates (9)

| Template | Status | Notes |
|----------|--------|-------|
| checkpoint.md | Active | L3, well-used |
| work_item.md | Active | L3, directory structure |
| implementation_plan.md | Active | L3, Ground Truth section |
| investigation.md | Active | L3, spawns work |
| observations.md | Active | L3, gate in close-work |
| architecture_decision_record.md | Active | L1/L2, durable |
| report.md | Active | L2, analysis |
| handoff_investigation.md | Active | L3, session handoff |
| ~~handoff.md~~ | Deprecated | Merged into handoff_investigation |

---

## Related

- **SECTION-14:** Bootstrap Architecture (templates for bootstrap files)
- **SECTION-15:** Information Architecture (L0-L3 that templates populate)
- **scaffold.py:** Implementation of template scaffolding
- **validate.py:** Implementation of template validation

---

*Scaffolded Session 152, Updated Session 156*
