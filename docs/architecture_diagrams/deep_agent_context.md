# Deep Detail: Agent Context & Prompt Injection

```text
┌─────────────────────────────────────────────────────────────┐
│                 haios.yaml Configuration                    │
│                                                             │
│  Defines Role -> File Mappings                              │
│  e.g., "builder" -> [L4 constraints, active work items]     │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                  AGENT SYSTEM PROMPTS                       │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                 STATIC IDENTITY                     │   │
│   │  (Who the agent is, base constraints & purpose)     │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │                 DYNAMIC CONTEXT                     │   │
│   │  (Loaded via .claude/haios/config paths)            │   │
│   │  • L0-L3 Manifesto (Main Agent)                     │   │
│   │  • L4 Requirements (Builder Agent)                  │   │
│   │  • Preflight Context (Validation Gate)              │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │                 REASONING INJECTION                 │   │
│   │  (From ReasoningBank Retrieval)                     │   │
│   │  • "Strategy: Avoid raw string formatting in SQL"   │   │
│   │  • "Strategy: Ensure PreToolUse blocks SQLite"      │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                      EXECUTION PHASE                        │
│   Agent uses injected context + rules to call MCP tools     │
└─────────────────────────────────────────────────────────────┘
```

## Description
The **Agent Ecosystem** delegates capabilities primarily by *what knowledge an agent is allowed to possess at startup*, controlled by `haios.yaml`.
- **Static Identity**: The base `.claude/agents/*.md` definition.
- **Dynamic Context**: Files from `manifesto/` bound to particular roles (ensuring the Context Window isn't blown out by unneeded L0 philosophy for a simple validation task).
- **Reasoning Injection**: The realization of the `ReasoningBank` paper. Past experiential strategies (from `reasoning_traces`) are injected directly into the system prompt window before execution to proactively avoid known failure patterns.
