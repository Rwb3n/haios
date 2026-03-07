# Subsystem: Governance Layer

```text
┌──────────────────────────────────────────────────────────────────┐
│                        GOVERNANCE LAYER                          │
│                                                                  │
│  ┌──────────────────────┐          ┌──────────────────────────┐  │
│  │   Governance Hooks   │          │  L4: Tech Requirements   │  │
│  ├──────────────────────┤          ├──────────────────────────┤  │
│  │ • PreToolUse         │ ───────► │ Rules & Constants        │  │
│  │ • PostToolUse        │          │ (e.g. haios.yaml)        │  │
│  │ • UserPromptSubmit   │          └────────────┬─────────────┘  │
│  │ • Stop               │                       │                │
│  └──────────┬───────────┘                       │                │
│             │                                   v                │
│             │                      ┌──────────────────────────┐  │
│             v                      │ Independent Lifecycles   │  │
│  ┌──────────────────────┐          ├──────────────────────────┤  │
│  │   Ceremony Engine    │ ───────► │ • Investigation          │  │
│  ├──────────────────────┤          │ • Design                 │  │
│  │ Boundary enforcement │          │ • Implementation         │  │
│  │ for state transitions│          │ • Validation             │  │
│  │ and memory commits.  │          │                          │  │
│  └──────────┬───────────┘          └────────────┬─────────────┘  │
│             │                                   │                │
│             v                                   v                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                       Work Items                           │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │ Format: WORK-XXX (docs/work/active/WORK-XXX/)              │  │
│  │ Status dictates current Lifecycle stage (e.g., PLAN, DO)  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Description
The **Governance Layer** implements the operational rules (L0-L4) of HAIOS:
- **Hooks**: Intercept Claude Code operations (e.g., preventing unauthorized SQL queries or tracking session vitals).
- **Independent Lifecycles**: Strict phases for discrete work types (Investigation, Design, Implementation).
- **Work Items**: The realization of governed tasks tracking progress via status fields.
