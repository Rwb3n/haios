# generated: 2026-01-18
# System Auto: last updated on: 2026-01-20T21:14:49
# Arc: Pipeline

## Arc Definition

**Arc ID:** Pipeline
**Epoch:** E2.3 (The Pipeline)
**Name:** Doc-to-Product Stages
**Status:** Planned
**Pressure:** [volumous] - thematic exploration

---

## Theme

Build the four stages that transform documents into products.

```
CORPUS → INGEST → PLAN → BUILD → VALIDATE → PRODUCT
```

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | CorpusLoader | Planned | Read arbitrary docs, not hardcoded paths |
| CH-002 | RequirementExtractor | Planned | Parse docs → structured requirements |
| CH-003 | PlannerAgent | Planned | Decompose requirements → work items |
| CH-004 | BuilderInterface | Planned | Clean interface for existing build capability |
| CH-005 | ValidatorAgent | Planned | Check output against source specs |
| CH-006 | Orchestrator | Planned | Pipeline state machine, routing |
| CH-007 | [ChapterTriage](CH-007-chapter-triage.md) | Planned | Design → work item decomposition |

---

## Stage Interfaces (From S26)

### INGEST
```
ingest(corpus_path: Path) → RequirementSet
```

### PLAN
```
plan(requirements: RequirementSet) → WorkPlan
```

### BUILD
```
build(work_item: WorkItem, context: BuildContext) → Artifacts
```

### VALIDATE
```
validate(artifacts: Artifacts, requirements: RequirementSet) → ValidationReport
```

---

## Exit Criteria

- [ ] At least INGEST stage functional
- [ ] Corpus loads from arbitrary path
- [ ] Requirements extracted and structured

---

## References

- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md
- @.claude/haios/epochs/E2_3/EPOCH.md
