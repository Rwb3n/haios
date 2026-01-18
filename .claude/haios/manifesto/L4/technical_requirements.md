# generated: 2026-01-18
# System Auto: last updated on: 2026-01-18T20:10:18
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
| Hooks | Built | Governance gates |
| Work items | Built (needs universal update) | Track progress |
| Project Foreman | **Not built** | Decompose requirements |
| Validator Agent | **Not built** | Check against requirements |
| Role-based loading | **Not built** | Separation of concerns |
| Atomic observations | **Not built** | Capture learnings |

## File Structure (Target)

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
│       └── technical_requirements.md
├── epochs/
│   └── E2_3/
│       ├── EPOCH.md
│       ├── architecture/
│       ├── arcs/
│       ├── observations/
│       │   ├── obs-206-001.md
│       │   └── obs-206-002.md
│       └── work/
│           ├── WORK-001/
│           │   └── WORK.md
│           └── WORK-002/
│               └── WORK.md
└── config/
```

**Key decisions:**
- Work items in epochs, not `docs/work/` (obs-206-008)
- No active/archive split - status is metadata (ADR-041)
- Observations are atomic files, not monolith (obs-206-006)
- Project's `docs/` stays clean - plugin is portable

## References

- @agent_user_requirements.md (source)
- @.claude/haios/epochs/E2_3/architecture/S26-pipeline-architecture.md
