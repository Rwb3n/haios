# generated: 2026-01-18
# System Auto: last updated on: 2026-01-27T23:17:07
# L4: Technical Requirements

Derived from agent_user_requirements.md

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
