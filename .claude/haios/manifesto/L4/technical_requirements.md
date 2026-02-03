# generated: 2026-01-18
# System Auto: last updated on: 2026-02-02T23:14:41
# L4: Technical Requirements

Derived from agent_user_requirements.md

---

## Five-Layer Hierarchy (E2.4 - Session 265)

HAIOS operates through five layers:

```
PRINCIPLES       (WHY)   - L0-L3 manifesto, S20 pressure dynamics
WAYS OF WORKING  (HOW)   - Functions/transformations (cycles, flows)
CEREMONIES       (WHEN)  - Side-effect boundaries (memory commits, checkpoints)
ACTIVITIES       (WHAT)  - Governed primitives per state
ASSETS           (OUTPUT)- Immutable artifacts
```

**Functional design lens:**
- Ways of Working are pure functions: `Input → Output`
- Ceremonies are side-effect boundaries
- Assets are immutable once produced

---

## Governed Activities (E2.4 - Session 265)

**Core pattern:**
```
Governed Activity = Primitive × State × Governance Rules
```

The same primitive (Read, Write, etc.) has different governance per state.

| State | Blocked | Allowed |
|-------|---------|---------|
| EXPLORE | (none) | explore-read, explore-search, capture-notes |
| DESIGN | (none) | requirements-read, spec-write, critique-invoke |
| PLAN | (none) | scope-read, plan-write, critique-invoke |
| DO | AskUser, explore-*, spec-write | spec-read, artifact-write, build-execute |
| CHECK | (none) | verify-read, test-execute, verdict-write |
| DONE | (none) | synthesis-read, knowledge-commit, work-close |

**DO phase black-box:**
- NO AskUser - spec should be complete
- NO explore-* activities - discovery is over
- NO spec-write - design is frozen
- ONLY artifact-* activities

---

## Independent Lifecycles (E2.5 - Session 294)

*Replaces "Universal Flow" - lifecycles are independent, not chained.*

**Lifecycles as Pure Functions:**

| Lifecycle | Signature | Phases | Output |
|-----------|-----------|--------|--------|
| Investigation | `Question → Findings` | EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE | Findings document |
| Design | `Requirements → Specification` | EXPLORE → SPECIFY → CRITIQUE → COMPLETE | Specification document |
| Implementation | `Specification → Artifact` | PLAN → DO → CHECK → DONE | Working artifact |
| Validation | `Artifact × Spec → Verdict` | VERIFY → JUDGE → REPORT | Pass/fail verdict |

**S27 Breath Model (Session 292):**

```
[inhale: gather]  →  [exhale: produce]  →  [pause: safe stop]
```

Each lifecycle follows this rhythm. Pause points are valid completion states.

**Chaining is Caller Choice:**
- Investigation MAY spawn Design (or close)
- Design MAY spawn Implementation (or close - batch design period)
- Implementation MAY spawn Validation (or close)
- No implicit side-effects forcing progression

**Critique within Design lifecycle:**
- SPECIFY → CRITIQUE: Hard gate
- Revise until PROCEED verdict
- Critique is internal to Design lifecycle, not cross-lifecycle gate

---

## Context Loading (enables: separation of concerns)

| Requirement | Implementation |
|-------------|----------------|
| Agents load only what they need | Role-specific context files |
| Files are context windows | Markdown with frontmatter |
| Selective loading by role | haios.yaml defines role → files mapping |

## Agent Roles (enables: role-based collaboration)

| Role | Context | Current State |
|------|---------|---------------|
| Main Agent | L0-L3 | Exists (coldstart loads manifesto) |
| Project Foreman | L4/* | Not built |
| Builder Agent | technical_requirements + work | Exists (Hephaestus) |
| Validator Agent | agent_user_requirements + artifacts | Not built |

## Work Structure (enables: track progress)

| Requirement | Implementation |
|-------------|----------------|
| Work items | WORK.md with lifecycle |
| Observations | obs-{session}-{seq}.md (atomic) |
| Artifacts | Listed in work item, produced by builder |

## Memory (enables: store/retrieve learnings)

| Requirement | Implementation |
|-------------|----------------|
| Store concepts | haios-memory MCP |
| Provenance | concept → artifact → file:line |
| Retrieval | semantic search, memory_refs |

## Governance (enables: quality gates)

| Requirement | Implementation |
|-------------|----------------|
| Hooks | PreToolUse, PostToolUse |
| Validation | Check against requirements |
| Escalation | Signal to higher role |

## What's Built vs Needed

| Component | Status | Enables |
|-----------|--------|---------|
| Memory system | Built | Store/retrieve learnings |
| Builder workflows | Built | Produce artifacts |
| Hooks | Built (E2-305: scaffold guard added) | Governance gates |
| Work items | Built (TRD approved Session 218, WORK-XXX format) | Track progress |
| Atomic observations | Built (observation-capture-cycle, scaffold-observations) | Capture learnings |
| Role-based loading | Partial (haios.yaml roles section, ContextLoader exists) | Separation of concerns |
| Validator Agent | Partial (validation-agent subagent exists, TD-002 queued) | Check against requirements |
| Project Foreman | **Not built** | Decompose requirements |

## File Structure (Actual)

```
.claude/haios/
├── manifesto/
│   ├── L0-telos.md
│   ├── L1-principal.md
│   ├── L2-intent.md
│   ├── L3-requirements.md
│   └── L4/
│       ├── project_requirements.md
│       ├── agent_user_requirements.md
│       ├── technical_requirements.md
│       └── functional_requirements.md
├── epochs/
│   └── E2_3/
│       ├── EPOCH.md
│       ├── architecture/
│       ├── arcs/
│       └── observations/
├── modules/         # 11 modules (Module-First Principle)
├── lib/             # Shared libraries
├── config/
│   └── haios.yaml
└── hooks/           # PreToolUse, PostToolUse, etc.

docs/work/
├── active/          # Work items (status field = lifecycle state)
│   ├── E2-305/
│   │   ├── WORK.md
│   │   ├── plans/PLAN.md
│   │   └── observations.md
│   └── WORK-001/
│       └── WORK.md
└── (archive at epoch boundary per ADR-041)
```

**Key decisions:**
- Work items in `docs/work/active/` (ADR-041: status over location)
- No active/archive directory move on close — `status: complete` is authoritative
- Observations captured per-work-item via observation-capture-cycle
- Plugin portable via `.claude/haios/`

## References

- @agent_user_requirements.md (source)
- @.claude/haios/epochs/E2_3/architecture/S26-pipeline-architecture.md
