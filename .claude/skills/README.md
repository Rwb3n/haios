# generated: 2025-12-25
# System Auto: last updated on: 2026-02-01T16:05:52
# Skills

Skills are prompt injection components that provide domain-specific guidance and workflows for Claude Code.

## Available Skills

| Skill | Type | Description |
|-------|------|-------------|
| `audit` | Utility | Run all HAIOS audit checks |
| `checkpoint-cycle` | Cycle | SCAFFOLD->FILL->VERIFY->CAPTURE->COMMIT workflow for session checkpoints with anti-pattern verification |
| `close-work-cycle` | Cycle | VALIDATE->ARCHIVE->MEMORY workflow for work item closure |
| `design-review-validation` | Validation | COMPARE->VERIFY->APPROVE bridge for design alignment |
| `dod-validation-cycle` | Validation | CHECK->VALIDATE->APPROVE bridge for DoD before closure |
| `extract-content` | Utility | Extract entities/concepts from documents |
| `ground-cycle` | Cycle | PROVENANCE->ARCHITECTURE->MEMORY->CONTEXT MAP for loading architectural context |
| `implementation-cycle` | Cycle | PLAN->DO->CHECK->DONE workflow for implementation |
| `investigation-cycle` | Cycle | EXPLORE->HYPOTHESIZE->VALIDATE->CONCLUDE workflow for research |
| `memory-agent` | Utility | Intelligent context retrieval and learning |
| `observation-capture-cycle` | Cycle | **DEPRECATED** - replaced by `retro-cycle` (WORK-142) |
| `retro-cycle` | Ceremony | Multi-step autonomous reflection with typed provenance (REFLECT->DERIVE->EXTRACT->COMMIT) |
| `observation-triage-cycle` | Cycle | SCAN->TRIAGE->PROMOTE workflow for processing captured observations |
| `plan-authoring-cycle` | Cycle | ANALYZE->AUTHOR->VALIDATE workflow for plan population |
| `plan-validation-cycle` | Validation | CHECK->VALIDATE->APPROVE bridge for plan readiness |
| `routing-gate` | Bridge | Work-type routing in CHAIN phase |
| `schema-ref` | Utility | Database schema reference |
| `survey-cycle` | Cycle | GATHER->ASSESS->OPTIONS->CHOOSE->ROUTE workflow for session-level work selection |
| `work-creation-cycle` | Cycle | VERIFY->POPULATE->READY workflow for work item creation |

## Skill Types (INV-033)

**Cycle Skills:** Multi-phase workflows with gate contracts (entry conditions, guardrails, exit criteria)
- `checkpoint-cycle`
- `close-work-cycle`
- `ground-cycle`
- `implementation-cycle`
- `investigation-cycle`
- `observation-capture-cycle` *(deprecated — replaced by `retro-cycle`)*
- `observation-triage-cycle`
- `retro-cycle`
- `plan-authoring-cycle`
- `survey-cycle`
- `work-creation-cycle`

**Validation Skills (Bridges):** Quality gates between workflow stages
- `design-review-validation`
- `dod-validation-cycle`
- `plan-validation-cycle`
- `routing-gate`

**Utility Skills:** Single-purpose recipe cards
- `audit`
- `extract-content`
- `memory-agent`
- `schema-ref`

## Gate Contract Pattern (INV-033)

Each phase in a Cycle Skill SHOULD define three components:

### 1. Entry Conditions
Prerequisites that must be true to enter the phase:
- File existence checks (plan/investigation file exists)
- Status checks (not draft, is active)
- Prior phase completion

### 2. Guardrails (Runtime Constraints)
Rules enforced during phase execution:
- **MUST rules:** Absolute requirements (e.g., "Write tests first")
- **SHOULD rules:** Strong recommendations (e.g., "One change at a time")

Enforcement levels:
- L3/L4: Mechanical (hooks, scripts)
- L2: Prompt-based (skill instructions)

### 3. Exit Criteria
Conditions that must be satisfied before phase transition:
- Checklist items (tests pass, docs updated)
- Memory integration (query at start, store at end)
- Command invocations (/close, /validate)

### Example: implementation-cycle DO Phase

**Entry:** PLAN phase exit criteria met

**Guardrails:**
- MUST write tests before implementation code
- SHOULD create file manifest before writing
- SHOULD pause for confirmation if >3 files

**Exit:**
- [ ] Tests written BEFORE implementation
- [ ] File manifest complete and followed
- [ ] Implementation matches Detailed Design

## Invocation

```
Skill(skill="skill-name")
```

## Directory Structure

```
.claude/skills/
├── audit/
│   └── SKILL.md
├── checkpoint-cycle/
│   ├── README.md
│   └── SKILL.md
├── close-work-cycle/
│   ├── README.md
│   └── SKILL.md
├── design-review-validation/
│   ├── README.md
│   └── SKILL.md
├── dod-validation-cycle/
│   ├── README.md
│   └── SKILL.md
├── extract-content/
│   └── SKILL.md
├── ground-cycle/
│   └── SKILL.md
├── implementation-cycle/
│   └── SKILL.md
├── investigation-cycle/
│   └── SKILL.md
├── memory-agent/
│   └── SKILL.md
├── observation-capture-cycle/
│   └── SKILL.md
├── observation-triage-cycle/
│   └── SKILL.md
├── plan-authoring-cycle/
│   ├── README.md
│   └── SKILL.md
├── plan-validation-cycle/
│   ├── README.md
│   └── SKILL.md
├── retro-cycle/
│   └── SKILL.md
├── routing-gate/
│   └── SKILL.md
├── schema-ref/
│   └── SKILL.md
├── survey-cycle/
│   └── SKILL.md
└── work-creation-cycle/
    ├── README.md
    └── SKILL.md
```

## Related

- ADR-039: Work Item as File Architecture
- INV-033: Skill as Node Entry Gate Formalization
- INV-035: Skill Architecture Refactoring
