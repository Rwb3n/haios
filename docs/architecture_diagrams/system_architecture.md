# HAIOS System Architecture Diagram

This document contains an ASCII representation of the current state of the HAIOS (Hybrid AI Operating System) architecture as of Epoch 2.8.

## The Big Picture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           INTERFACES & TOUCHPOINTS                      │
│                                                                         │
│  ┌───────────────────────────┐         ┌─────────────────────────────┐  │
│  │   Claude Code Plugin      │         │         MCP Server          │  │
│  │ (/coldstart, /haios,      │         │ (Claude Desktop Integration)│  │
│  │  skills, commands)        │         │                             │  │
│  └─────────────┬─────────────┘         └──────────────┬──────────────┘  │
│                │                                      │                 │
├────────────────┼──────────────────────────────────────┼─────────────────┤
│                │                                      │                 │
│                v                                      v                 │
│  ┌───────────────────────────┐         ┌─────────────────────────────┐  │
│  │    Governance Hooks       │         │      Agent Ecosystem        │  │
│  │ (Pre/PostToolUse, Stop,   │ ◄─────► │ Main, Builder (Hephaestus), │  │
│  │  UserPromptSubmit)        │         │ Utility (Critique, verifiers│  │
│  └─────────────┬─────────────┘         └─────────────────────────────┘  │
│                │                                      │                 │
│                v                                      v                 │
│  ┌───────────────────────────┐         ┌─────────────────────────────┐  │
│  │  Independent Lifecycles   │         │       Work Management       │  │
│  │ (Investigation, Design,   │ ◄─────► │  docs/work/active/WORK-XXX  │  │
│  │  Implementation, Validate)│         │   Ceremonies & Approvals    │  │
│  └─────────────┬─────────────┘         └─────────────────────────────┘  │
│                |                                                        │
├────────────────┼────────────────────────────────────────────────────────┤
│                │                                                        │
│                v                                                        │
│                      COGNITIVE MEMORY ENGINE                            │
│                                                                         │
│  ┌───────────────────────────┐         ┌─────────────────────────────┐  │
│  │       LangExtract         │         │        ReasoningBank        │  │
│  │ (Structured Extraction    │         │ (Experience/Strategy        │  │
│  │  from Unstructured Data)  │         │  Extraction)                │  │
│  └─────────────┬─────────────┘         └──────────────┬──────────────┘  │
│                │                                      │                 │
│                v                                      v                 │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                haios_memory.db (SQLite + Vectors)                 │  │
│  │  [81k+ Concepts, 9k+ Entities, Episteme/Techne/Doxa Taxonomy]     │  │
│  └─────────────────────────────────┬─────────────────────────────────┘  │
│                                    ^                                    │
│                                    │                                    │
│                      ┌─────────────┴─────────────┐                      │
│                      │      Memory Synthesis     │                      │
│                      │ (Clustering, Pollination) │                      │
│                      └───────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Subsystems & Principles

1. **Interfaces**: How users interact with the system (Plugin for CLI, MCP for Desktop).
2. **Governance (L0-L4)**: Enforces rule boundaries, lifecycles (Explore, Design, Plan, Do, Check, Done), and work item progression (`WORK-XXX` format routing).
3. **Agent Ecosystem**: Role-specific agents dynamically load context based on `haios.yaml` to execute portions of workflows without overwhelming their context window.
4. **Cognitive Memory Engine**: 
   - *LangExtract* turns text into structured data (Concepts, Entities) heavily grounded in source material.
   - *ReasoningBank* answers "what worked/failed" based on outcomes, returning actionable experience blocks.
   - *Memory Synthesis* keeps the persistent SQLite repository pruned and clustered.
