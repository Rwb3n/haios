# generated: 2026-01-18
# System Auto: last updated on: 2026-01-30T17:46:02
# Arc: Pipeline

## Arc Definition

**Arc ID:** Pipeline
**Epoch:** E2.3 (The Pipeline)
**Name:** Doc-to-Product Stages
**Status:** Active
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
| CH-001 | [CorpusLoader](CH-001-corpus-loader.md) | **Complete** | Read arbitrary docs, not hardcoded paths |
| CH-002 | [RequirementExtractor](CH-002-requirement-extractor.md) | **Complete** | Parse docs → structured requirements |
| CH-003 | [PlannerAgent](CH-003-planner-agent.md) | **Complete** | Decompose requirements → work items |
| CH-004 | BuilderInterface | Planned | Clean interface for existing build capability |
| CH-005 | ValidatorAgent | Planned | Check output against source specs |
| CH-006 | [Orchestrator](CH-006-orchestrator.md) | **Complete** | Pipeline state machine, routing |
| CH-007 | [ChapterTriage](CH-007-chapter-triage.md) | Planned | Design → work item decomposition |
| CH-008 | [CalibrationCycle](CH-008-calibration-cycle.md) | Planned | Post-implementation feedback loop |

---

## Design Constraints (L4 MUST - Session 218)

**Module-First:** Each stage MUST be a module in `.claude/haios/modules/`.
- CorpusLoader → `modules/corpus_loader.py`
- RequirementExtractor → `modules/requirement_extractor.py`
- PlannerAgent → `modules/planner_agent.py`
- etc.

**Content Injection:** Stage outputs MUST be injectable content, not file references.

**Design Gate:** "Which module does the work? If none, why not?"

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

- [x] At least INGEST stage functional (CorpusLoader + RequirementExtractor)
- [x] Corpus loads from arbitrary path (CorpusLoader with YAML config)
- [x] Requirements extracted and structured (RequirementSet schema)
- [x] PLAN stage functional (PlannerAgent has runtime consumer via Orchestrator)
- [x] Orchestrator wires stages together (WORK-033, `just pipeline-run`)

---

## References

- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md
- @.claude/haios/epochs/E2_3/EPOCH.md
