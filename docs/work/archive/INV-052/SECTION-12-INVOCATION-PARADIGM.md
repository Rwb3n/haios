# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:14:29
# Section 12: Invocation Paradigm

Generated: 2025-12-30 (Session 151)
Purpose: Document how abstraction layers interact and when to use which layer
Status: COMPLETE

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Layer definitions are documentation only** | No runtime layer awareness | Add layer metadata to manifests |
| **MCP count includes external tools** | Listed 12 but HAIOS core is 10 | Clarify: HAIOS MCP = 10, external = varies |

---

## Target Architecture: Portable Plugin

The 7-layer stack is **LLM-agnostic**. HAIOS is a portable plugin that PUSHES to LLM-native formats:

```
.[claude|gemini|whatever]/haios/   ← PLUGIN SOURCE (LLM-agnostic)
├── config/
│   ├── cycle-definitions.yaml        ← Layer 4 structure
│   ├── skill-manifest.yaml           ← Layer 3 registry
│   ├── agent-manifest.yaml           ← Layer 2 registry
│   ├── command-manifest.yaml         ← Layer 1 registry
│   ├── recipe-chains.yaml            ← Layer 0 chains
│   ├── hook-handlers.yaml            ← Layer -1 config
│   └── mcp-registry.yaml             ← Layer -2 tools
├── state/
│   └── work-index.yaml               ← Derived state
└── manifest.yaml                     ← Plugin metadata
        │
        │  Plugin installer PUSHES to LLM-native format
        ▼
.claude/                           ← LLM-SPECIFIC (Claude CLI native)
├── commands/*.md                  ← Generated from command-manifest
├── skills/*/SKILL.md              ← Generated from skill-manifest + cycle-definitions
├── agents/*.md                    ← Generated from agent-manifest
├── settings.local.json            ← Hooks, permissions from hook-handlers
└── mcp.json                       ← Generated from mcp-registry
```

**Principle:** The plugin is the SOURCE OF TRUTH. It generates/pushes to `.claude/commands/`, `.claude/skills/`, etc. For Gemini, it would push to Gemini's equivalent structure. The plugin is portable; the target format is LLM-specific.

---

## Overview

HAIOS has multiple abstraction layers for executing work. Understanding when to use which layer is critical for correct system behavior.

---

## The Layer Stack

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: CYCLES                                            │
│  ────────────────────────────────────────────────────────── │
│  Phase-based workflows with gates                           │
│  Invoke: Skill(skill="implementation-cycle")                │
│  Examples: implementation-cycle, investigation-cycle        │
│  Count: 7 cycles                                            │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: SKILLS                                            │
│  ────────────────────────────────────────────────────────── │
│  Prompts with context injection (all types)                 │
│  Invoke: Skill(skill="memory-agent")                        │
│  Examples: memory-agent, audit, routing-gate, bridges       │
│  Count: 15 skills (7 cycles + 3 bridges + 5 utilities)      │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: SUBAGENTS                                         │
│  ────────────────────────────────────────────────────────── │
│  Isolated execution contexts with limited tools             │
│  Invoke: Task(subagent_type="preflight-checker")            │
│  Examples: preflight-checker, validation-agent              │
│  Count: 7 agents                                            │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: SLASH COMMANDS                                    │
│  ────────────────────────────────────────────────────────── │
│  User-invocable entry points                                │
│  Invoke: User types "/coldstart"                            │
│  Examples: /coldstart, /new-work, /close                    │
│  Count: 18 commands                                         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 0: JUST RECIPES                                      │
│  ────────────────────────────────────────────────────────── │
│  Shell execution (Python, git, file ops)                    │
│  Invoke: Bash("just ready")                                 │
│  Examples: just session-start, just update-status           │
│  Count: ~50 recipes                                         │
├─────────────────────────────────────────────────────────────┤
│  LAYER -1: HOOKS                                            │
│  ────────────────────────────────────────────────────────── │
│  Automatic triggers (no manual invocation)                  │
│  Invoke: Automatic on tool use / prompt / stop              │
│  Examples: PreToolUse, PostToolUse, UserPromptSubmit        │
│  Count: 4 hook types, 22 handlers (current) → 19 (target)   │
├─────────────────────────────────────────────────────────────┤
│  LAYER -2: MCP SERVERS                                      │
│  ────────────────────────────────────────────────────────── │
│  External tool providers via JSON-RPC                       │
│  Invoke: mcp__<server>__<tool>                              │
│  Examples: haios-memory (10 tools), context7 (2 tools)      │
│  Count: 2 servers, 12 tools                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow Examples

### Example 1: Human Initiates Work

```
Human: /new-plan E2-123 "Add feature X"
    │
    ▼
LAYER 1: /new-plan command loads
    │
    ├──► LAYER 0: just scaffold plan E2-123 "Add feature X"
    │
    ▼
LAYER 3: plan-authoring-cycle skill
    │
    ├──► LAYER 3: plan-validation-cycle (bridge)
    │
    ▼
LAYER 4: implementation-cycle
    │
    ├──► LAYER 2: preflight-checker (subagent)
    ├──► LAYER 0: just test (recipe)
    ├──► LAYER -2: memory_search_with_experience (MCP)
    │
    ▼
LAYER 4: CHAIN → routing-gate → next cycle
```

### Example 2: Agent Validates Work

```
implementation-cycle CHECK phase
    │
    ▼
LAYER 2: Task(subagent_type="validation-agent")
    │
    ├──► LAYER 0: Bash("pytest")
    │
    ▼
Result returned to main agent
    │
    ▼
LAYER 4: Continue to DONE phase (if passed)
```

### Example 3: Automatic Governance

```
Agent calls Edit tool
    │
    ▼
LAYER -1: PreToolUse hook fires
    │
    ├──► Check: SQL blocking?
    ├──► Check: Path governance?
    ├──► Check: Exit gates?
    │
    ▼
Allow or Deny
    │
    ▼
LAYER -1: PostToolUse hook fires (if allowed)
    │
    ├──► Update timestamps
    ├──► Trigger cascades
```

### Example 4: Memory Query

```
memory-agent skill
    │
    ▼
LAYER -2: mcp__haios-memory__memory_search_with_experience
    │
    ├──► Database query
    ├──► Strategy injection
    │
    ▼
Return to skill
```

---

## When to Use Which Layer

| Scenario | Use Layer | Reason |
|----------|-----------|--------|
| Human wants to start work | 1 (Command) | User-friendly entry point |
| Agent needs orchestration | 3/4 (Skill/Cycle) | Phase management |
| Agent needs isolated validation | 2 (Subagent) | Unbiased, limited context |
| Agent needs shell execution | 0 (Recipe) | File ops, git, tests |
| System needs governance | -1 (Hook) | Automatic enforcement |
| Agent needs external data | -2 (MCP) | Database, web, docs |

---

## Layer Interaction Rules

### Downward Invocation (Normal)
Higher layers can invoke lower layers:
```
Cycles (4) ──► Skills (3) ──► Subagents (2) ──► Commands (1) ──► Recipes (0)
                                                                      │
                                                         All ──► MCP (-2)
```

### Upward Invocation (Limited)
Lower layers generally cannot invoke higher layers:
- Hooks cannot invoke Skills (can only output guidance)
- Recipes cannot invoke Skills (shell boundary)
- Subagents cannot invoke Skills (isolation boundary)
- MCP tools cannot invoke anything (pure data)

### Lateral Invocation
Same-layer invocation:
- **Cycles** can chain to other Cycles (via CHAIN phase)
- **Skills** can invoke other Skills
- **Subagents** CANNOT invoke other Subagents

---

## Anti-Patterns (Wrong Layer)

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Human invokes Skill directly | Skips command preprocessing | Use slash command |
| Agent uses Bash for validation | No isolation | Use subagent |
| Skill invokes raw Bash for scaffold | Skips recipe benefits | Use `just scaffold` |
| Hook tries to invoke skill | Not supported | Hook outputs guidance only |
| Agent queries DB directly | Blocked by governance | Use schema-verifier subagent |
| Subagent tries to Edit files | Tool not granted | Return findings, let main agent edit |

---

## Decision Tree

```
START: What do I need to do?
    │
    ├─► Need user input?
    │       └─► LAYER 1: Slash Command
    │
    ├─► Need multi-phase workflow?
    │       └─► LAYER 4: Cycle
    │
    ├─► Need validation/isolation?
    │       └─► LAYER 2: Subagent
    │
    ├─► Need shell execution?
    │       └─► LAYER 0: Just Recipe
    │
    ├─► Need external data?
    │       └─► LAYER -2: MCP Tool
    │
    └─► Need one-shot capability?
            └─► LAYER 3: Utility Skill
```

---

## Pattern: "Slash commands are prompts, just recipes are execution"

| Type | Purpose | Example |
|------|---------|---------|
| Slash Command | Inject context, guide agent | `/new-plan E2-123 "Feature"` |
| Just Recipe | Execute Python/shell code | `just scaffold plan E2-123 "Feature"` |

Commands load prompts and may call recipes. Recipes do the actual work.

---

## Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| Cycles | Orchestrate work through phases |
| Skills | Provide capabilities and bridges |
| Subagents | Isolated validation and queries |
| Commands | Human entry points |
| Recipes | Execution layer |
| Hooks | Automatic governance |
| MCP | External data access |

---

*Populated Session 151*
