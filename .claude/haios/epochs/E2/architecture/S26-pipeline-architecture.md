# generated: 2026-01-18
# System Auto: last updated on: 2026-01-18T16:17:28
# Section 26: Doc-to-Product Pipeline Architecture

Generated: 2026-01-18 (Session 206)
Source: Strategic Review with Operator
Status: FOUNDATIONAL

---

## The Mission

HAIOS is a **multi-agent operational framework** that transforms documentation into working products.

```
INPUT:  Corpus of documents (specs, requirements, designs)
PROCESS: Multi-agent pipeline
OUTPUT: Functional product (aligned to source specs)
```

**The portability test:**
> Can you drop `.claude/haios/` into a fresh workspace with a corpus of docs and have it produce a working product?

This is the success criterion. Everything else is implementation detail.

---

## Pipeline Stages

```
CORPUS → INGEST → PLAN → BUILD → VALIDATE → PRODUCT
```

### Stage 1: INGEST

**Purpose:** Transform raw documents into structured requirements.

**Input:** Arbitrary corpus (markdown, code, specs, designs)
**Output:** Requirement set (structured, actionable items)

**Components:**
| Component | Responsibility |
|-----------|----------------|
| Corpus Loader | Discover and read documents from arbitrary paths |
| Requirement Extractor | Parse docs → extract what needs to be built |

**Interface:**
```
ingest(corpus_path: Path) → RequirementSet
```

**RequirementSet structure:**
```yaml
requirements:
  - id: REQ-001
    source: specs/auth.md:15-42
    type: feature|constraint|interface
    description: "User authentication via OAuth2"
    acceptance_criteria:
      - "OAuth2 flow completes"
      - "Tokens stored securely"
    dependencies: []
```

---

### Stage 2: PLAN

**Purpose:** Decompose requirements into ordered work items.

**Input:** RequirementSet
**Output:** Work items with dependencies and ordering

**Components:**
| Component | Responsibility |
|-----------|----------------|
| Planner Agent | Analyze requirements, identify dependencies, sequence work |

**Interface:**
```
plan(requirements: RequirementSet) → WorkPlan
```

**WorkPlan structure:**
```yaml
work_items:
  - id: WORK-001
    requirement_refs: [REQ-001, REQ-003]
    title: "Implement OAuth2 authentication"
    blocked_by: [WORK-000]  # dependency
    estimated_complexity: medium

execution_order: [WORK-000, WORK-001, WORK-002, ...]
```

---

### Stage 3: BUILD

**Purpose:** Execute work items to produce artifacts.

**Input:** Single work item from WorkPlan
**Output:** Code, tests, documentation artifacts

**Components:**
| Component | Responsibility |
|-----------|----------------|
| Builder Agent | Execute work item: write code, tests, docs |
| Memory | Store learnings, retrieve prior patterns |

**Interface:**
```
build(work_item: WorkItem, context: BuildContext) → Artifacts
```

**Artifacts structure:**
```yaml
artifacts:
  - path: src/auth/oauth.py
    type: code
  - path: tests/test_oauth.py
    type: test
changes:
  - file: src/auth/oauth.py
    action: created
```

**Loop:** Orchestrator calls `build()` for each work item in execution_order.

---

### Stage 4: VALIDATE

**Purpose:** Verify output matches source requirements.

**Input:** Artifacts + original RequirementSet
**Output:** Validation report (pass/fail per requirement)

**Components:**
| Component | Responsibility |
|-----------|----------------|
| Validator Agent | Check artifacts against acceptance criteria |
| Test Runner | Execute tests, report results |

**Interface:**
```
validate(artifacts: Artifacts, requirements: RequirementSet) → ValidationReport
```

**ValidationReport structure:**
```yaml
results:
  - requirement_id: REQ-001
    status: pass|fail|partial
    evidence:
      - "OAuth2 flow test passes"
      - "Token storage test passes"
    gaps: []

overall: pass|fail
coverage: 95%  # requirements with evidence
```

---

## Orchestrator

**Purpose:** Drive the pipeline, manage state, route between stages.

**Responsibilities:**
1. Initialize pipeline with corpus path
2. Call stages in sequence
3. Handle failures (retry, skip, escalate)
4. Track progress persistently
5. Report to operator on completion or block

**State machine:**
```
IDLE → INGESTING → PLANNING → BUILDING → VALIDATING → COMPLETE
                                  ↑           │
                                  └───────────┘
                                  (loop per work item)
```

**Escalation triggers:**
- Ambiguous requirement (needs operator clarification)
- Build failure after retry
- Validation failure (requirement not met)

---

## What Exists vs What's Needed

| Component | Current State | Gap |
|-----------|---------------|-----|
| **Corpus Loader** | ContextLoader (HAIOS-specific) | Generalize to arbitrary paths |
| **Requirement Extractor** | None | Build from scratch |
| **Planner Agent** | Operator writes plans | Automate decomposition |
| **Builder Agent** | CycleRunner + skills | Works, needs interface cleanup |
| **Validator Agent** | None | Build from scratch |
| **Orchestrator** | Partial (survey-cycle routes) | Needs pipeline state machine |
| **Memory** | Works | Reusable as-is |
| **Work Items** | WORK.md structure | Reusable, add requirement_refs |

---

## Reusable Infrastructure

These components transfer directly:

| Component | Location | Reuse Strategy |
|-----------|----------|----------------|
| Memory system | haios-memory MCP | As-is |
| Work item structure | WorkEngine | Add requirement_refs field |
| Hooks | PreToolUse, PostToolUse | As-is for governance |
| Session state | haios-status.json | As-is |
| Test runner | test-runner agent | As-is |

---

## HAIOS-Specific (Not Portable)

These are for HAIOS development, not the framework:

| Component | Purpose | Disposition |
|-----------|---------|-------------|
| L0-L4 manifesto | HAIOS philosophy | Example corpus, not framework |
| Epochs/Arcs/Chapters | HAIOS PM hierarchy | Remove from portable plugin |
| `/coldstart`, `/implement` | HAIOS workflows | Replace with pipeline commands |
| 70+ recipes | Mixed | Audit: keep generic, remove HAIOS-specific |

---

## Implementation Path

### Phase 1: Generalize Corpus Loader
- Remove hardcoded HAIOS paths from ContextLoader
- Accept `corpus_path` parameter
- Discover docs recursively

### Phase 2: Build Requirement Extractor
- LLM-based extraction from arbitrary docs
- Output structured RequirementSet
- Link back to source (file:line)

### Phase 3: Build Planner Agent
- Input: RequirementSet
- Output: WorkPlan with dependencies
- Algorithm: topological sort on dependencies

### Phase 4: Clean Builder Interface
- Wrap existing CycleRunner
- Standardize input/output
- Add requirement_refs to work items

### Phase 5: Build Validator Agent
- Input: Artifacts + Requirements
- Run tests, check acceptance criteria
- Output: ValidationReport

### Phase 6: Build Orchestrator
- Pipeline state machine
- Call stages in sequence
- Handle escalation

### Phase 7: Integration Test
- Test corpus: HAIOS specs themselves
- Run full pipeline
- Validate output matches specs

---

## Success Criteria

The pipeline is complete when:

1. **Portability test passes:** Drop plugin into fresh workspace, point at corpus, get product
2. **No operator steering:** Pipeline runs without human routing decisions
3. **Traceability:** Every artifact links to source requirement
4. **Validation:** Output demonstrably matches input specs

---

## References

- L4: Implementation (Session 206 strategic insight)
- S14: Bootstrap Architecture (context loading patterns)
- S17: Modular Architecture (module boundaries)
- S20: Pressure Dynamics (stage rhythm: ingest[volumous] → plan[tight] → build[mixed] → validate[tight])

---

*This document defines what HAIOS is. Implementation details live in TRD-PIPELINE.md (to be created).*
