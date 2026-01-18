# generated: 2026-01-18
# System Auto: last updated on: 2026-01-18T19:54:30
# L4: Implementation Layer

## Structure

L4 is not a single file. It decomposes into requirement types:

```
L4/
├── README.md                    # This file
├── project_requirements.md      # What the project IS
├── agent_user_requirements.md   # What users/agents must be able to DO
└── technical_requirements.md    # HOW to enable those capabilities
```

## Derivation Chain

```
project_requirements (WHAT we're building)
         ↓
agent_user_requirements (WHAT users/agents can DO with it)
         ↓
technical_requirements (HOW to enable those capabilities)
```

## Loading Responsibility

| Layer | Loaded By |
|-------|-----------|
| L0-L3 | Main Agent (philosophical grounding) |
| L4/* | Project Foreman (operational context) |

Each agent loads what IT needs. Separation of concerns through selective context loading.

## HAIOS agent/user_requirements

> Must allow a team of agents of varying roles to:
> - Concern themselves with their own roles (separation of concerns)
> - Collaborate on developing a project to completion
> - Produce a product that supports L0-L3, presented in a box with a bow tie

## Role-Based Context Loading

| Role | Loads | Purpose |
|------|-------|---------|
| Main Agent | L0-L3 | Philosophy, principal, intent |
| Project Foreman | L4/* | Requirements, work coordination |
| Builder Agent | technical_requirements + work item | Implementation |
| Validator Agent | agent_user_requirements + artifacts | Verification |

Files ARE context windows. Each role gets composed context from files relevant to its concerns.

## References

- @L0-telos.md
- @L1-principal.md
- @L2-intent.md
- @L3-requirements.md
