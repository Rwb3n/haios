# Subsystem: Agent Ecosystem

```text
┌─────────────────────────────────────────────────────────────┐
│                       AGENT ECOSYSTEM                       │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                    MAIN AGENT                       │   │
│   │                                                     │   │
│   │ • Role: Philosophical grounding & user facing       │   │
│   │ • Context: [L0-L3 Manifesto files]                  │   │
│   │ • Operations: Handles general requests, delegates   │   │
│   └─────────────────────────┬───────────────────────────┘   │
│                             │                               │
│                             v                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                 BUILDER (Hephaestus)                │   │
│   │                                                     │   │
│   │ • Role: Work execution & artifact generation        │   │
│   │ • Context: [L4 Tech Reqs, Active Work Items]        │   │
│   │ • Operations: Write code, update specs, DO phase    │   │
│   └─────────────────────────┬───────────────────────────┘   │
│                             │                               │
│                             v                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              UTILITY / VERIFICATION                 │   │
│   │                                                     │   │
│   │ ┌────────────────┐ ┌────────────────┐ ┌───────────┐ │   │
│   │ │    Critique    │ │ Schema Verifier│ │ Validator │ │   │
│   │ │ (Assumption    │ │ (SQL gating)   │ │ (Checks   │ │   │
│   │ │  surfacing)    │ │                │ │  Reqs)    │ │   │
│   │ └────────────────┘ └────────────────┘ └───────────┘ │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Description
The **Agent Ecosystem** delegates work across specialized agents to keep their context windows focused and token costs constrained:
- **Main Agent**: Anchors interaction to the system's philosophical principles (L0-L3).
- **Builder Agent**: Executes the actual coding/creation for active work items (L4 contextual).
- **Utility / Gate Agents**: Lightweight agents invoked during specific lifecycle transitions or sensitive actions (e.g., `schema-verifier` for SQL).
