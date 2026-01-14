# generated: 2026-01-06
# System Auto: last updated on: 2026-01-06T22:03:15
# Section 12: Invocation Paradigm

Generated: 2025-12-30 (Session 151, INV-052)
Migrated: 2026-01-06 (Session 179)
Purpose: Document the 7-layer stack and when to use which layer
Status: ACTIVE

---

## The Layer Stack

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: CYCLES                                            │
│  Phase-based workflows with gates                           │
│  Invoke: Skill(skill="implementation-cycle")                │
│  Pressure: Mixed [MAY]→[MUST] pattern                       │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: SKILLS                                            │
│  Prompts with context injection (all types)                 │
│  Invoke: Skill(skill="memory-agent")                        │
│  Pressure: Varies by category                               │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: SUBAGENTS                                         │
│  Isolated execution contexts with limited tools             │
│  Invoke: Task(subagent_type="preflight-checker")            │
│  Pressure: [MUST] - binary validation                       │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: SLASH COMMANDS                                    │
│  User-invocable entry points                                │
│  Invoke: User types "/coldstart"                            │
│  Pressure: Entry point (triggers cycle)                     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 0: JUST RECIPES                                      │
│  Shell execution (Python, git, file ops)                    │
│  Invoke: Bash("just ready")                                 │
│  Pressure: [MUST] - mechanical execution                    │
├─────────────────────────────────────────────────────────────┤
│  LAYER -1: HOOKS                                            │
│  Automatic triggers (no manual invocation)                  │
│  Invoke: Automatic on tool use / prompt / stop              │
│  Pressure: [MUST] - governance enforcement                  │
├─────────────────────────────────────────────────────────────┤
│  LAYER -2: MCP SERVERS                                      │
│  External tool providers via JSON-RPC                       │
│  Invoke: mcp__<server>__<tool>                              │
│  Pressure: Varies (query=[MAY], store=[MUST])               │
└─────────────────────────────────────────────────────────────┘
```

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

## When to Use Which Layer

| Scenario | Use Layer | Pressure |
|----------|-----------|----------|
| Human wants to start work | 1 (Command) | Entry |
| Agent needs orchestration | 4 (Cycle) | Mixed |
| Agent needs isolated validation | 2 (Subagent) | [MUST] |
| Agent needs shell execution | 0 (Recipe) | [MUST] |
| System needs governance | -1 (Hook) | [MUST] |
| Agent needs external data | -2 (MCP) | Varies |

---

## Pattern: "Slash commands are prompts, just recipes are execution"

| Type | Purpose | Pressure |
|------|---------|----------|
| Slash Command | Inject context, guide agent | [MAY] - opens space |
| Just Recipe | Execute Python/shell code | [MUST] - mechanical |

Commands load prompts and may call recipes. Recipes do the actual work.

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

## Connection to Modules (S17)

The 5 Chariot modules map to layers:

| Module | Primary Layer | Function |
|--------|---------------|----------|
| ContextLoader | -1, 1 | Coldstart loads context |
| MemoryBridge | -2 | MCP wrapper |
| CycleRunner | 3, 4 | Execute cycles/skills |
| GovernanceLayer | -1, 2 | Hooks + subagent validation |
| WorkEngine | 0 | State persistence via recipes |

---

## Connection to Pressure Dynamics (S20)

Each layer has characteristic pressure:

| Layer | Typical Pressure | Why |
|-------|------------------|-----|
| Cycles | Mixed | Breath rhythm |
| Skills | Varies | Category-dependent |
| Subagents | [MUST] | Validation is binary |
| Commands | Entry | Opens space |
| Recipes | [MUST] | Mechanical |
| Hooks | [MUST] | Governance |
| MCP | Query=[MAY], Store=[MUST] | Action-dependent |

---

## Related

- S10: Skills Taxonomy (layer 3-4 detail)
- S17: Modular Architecture (module ↔ layer mapping)
- S20: Pressure Dynamics (pressure per layer)
- INV-052/SECTION-12: Original source

---

*Migrated from INV-052, enhanced with pressure annotations (Session 179)*
