# Subsystem: Interfaces & Touchpoints

```text
┌─────────────────────────────────────────────────────────────┐
│                       USER WORKSPACE                        │
│                                                             │
│   ┌──────────────────┐               ┌──────────────────┐   │
│   │   Claude Code    │               │  Claude Desktop  │   │
│   │  (CLI sessions)  │               │   (GUI client)   │   │
│   └────────┬─────────┘               └─────────┬────────┘   │
│            │                                   │            │
└────────────┼───────────────────────────────────┼────────────┘
             │                                   │
┌────────────▼───────────────────────────────────▼────────────┐
│                    HAIOS ENTRY POINTS                       │
│                                                             │
│   ┌──────────────────┐               ┌──────────────────┐   │
│   │      Plugin      │               │    MCP Server    │   │
│   │  (.claude dir)   │               │ (haios_etl.mcp)  │   │
│   └────────┬─────────┘               └─────────┬────────┘   │
│            │  • /coldstart                     │            │
│            │  • /haios dashboard               │ • Tools    │
│            │  • /status                        │ • Prompts  │
│            │  • /new-work                      │ • Resources│
│            │                                   │            │
│   ┌────────▼─────────┐                         │            │
│   │     Commands     │                         │            │
│   │     & Skills     │                         │            │
│   └────────┬─────────┘                         │            │
│            │                                   │            │
└────────────┼───────────────────────────────────┼────────────┘
             │                                   │
             v                                   v
    (To Governance Hooks)              (To Memory / Agents)
```

## Description
The **Interfaces** subsystem defines how a user or agent interacts with HAIOS. 
- **Claude Code Plugin**: The primary CLI entry point. It uses slash commands (`/coldstart`, `/new-work`) and custom skills to trigger internal HAIOS workflows.
- **MCP Server**: The Model Context Protocol server exposing HAIOS memory and agents to graphical clients (like Claude Desktop) or other MCP-compatible clients.
