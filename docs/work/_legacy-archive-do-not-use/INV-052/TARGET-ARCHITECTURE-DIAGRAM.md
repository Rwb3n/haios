# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:47:09
# HAIOS Target Architecture - Revised Diagram

Generated: 2025-12-30 (Session 152)
Purpose: Synthesized target state from all 21 section files
Status: DESIGN COMPLETE

---

## Table of Contents

| # | Section | Description |
|---|---------|-------------|
| 1 | [Portable Plugin Architecture](#1-portable-plugin-architecture) | LLM-agnostic core |
| 2 | [7-Layer Invocation Stack](#2-7-layer-invocation-stack) | Abstraction layers |
| 3 | [Plugin Manifest Structure](#3-plugin-manifest-structure) | Config file hierarchy |
| 4 | [Work Item Lifecycle](#4-work-item-lifecycle) | DAG with node_history |
| 5 | [Session Lifecycle](#5-session-lifecycle) | Bidirectional binding |
| 6 | [Data Flow](#6-data-flow) | Single writer principle |
| 7 | [Hook Architecture](#7-hook-architecture) | 19 handlers (target) |
| 8 | [Cycle Execution](#8-cycle-execution) | YAML-driven thin executor |
| 9 | [Memory Integration](#9-memory-integration) | Auto-linked concepts |
| 10 | [Gap Resolution Map](#10-gap-resolution-map) | S152 findings |

---

## 1. PORTABLE PLUGIN ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         HAIOS: PORTABLE PLUGIN ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    PLUGIN SOURCE (LLM-Agnostic)                              │   │
│  │                    .[claude|gemini|whatever]/haios/                          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌───────────────────────────────┐    ┌───────────────────────────────┐           │
│  │  config/                       │    │  state/                        │           │
│  │  ─────────────────────────────│    │  ─────────────────────────────│           │
│  │  cycle-definitions.yaml       │    │  session-registry.yaml         │           │
│  │  skill-manifest.yaml          │    │  work-index.yaml               │           │
│  │  agent-manifest.yaml          │    │  (derived, regenerable)        │           │
│  │  command-manifest.yaml        │    └───────────────────────────────┘           │
│  │  recipe-chains.yaml           │                                                 │
│  │  hook-handlers.yaml           │    ┌───────────────────────────────┐           │
│  │  mcp-registry.yaml            │    │  manifest.yaml                 │           │
│  │  gates.yaml                   │    │  ─────────────────────────────│           │
│  │  node-bindings.yaml           │    │  name: haios                   │           │
│  │  thresholds.yaml              │    │  version: 2.0.0                │           │
│  │  (canonical source of truth)  │    │  target_llm: [claude, gemini]  │           │
│  └───────────────────────────────┘    └───────────────────────────────┘           │
│                                                                                     │
│                              │                                                      │
│                              │  Plugin Installer                                    │
│                              │  (generates LLM-specific format)                     │
│                              ▼                                                      │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    LLM-SPECIFIC (Generated)                                  │   │
│  │                    .claude/ (Claude CLI native format)                       │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ commands/    │  │ skills/      │  │ agents/      │  │ settings.    │           │
│  │ *.md         │  │ */SKILL.md   │  │ *.md         │  │ local.json   │           │
│  │ (18 files)   │  │ (15 dirs)    │  │ (7 files)    │  │ (hooks,perms)│           │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                                     │
│  ════════════════════════════════════════════════════════════════════════════════  │
│                                                                                     │
│  PRINCIPLE: The plugin is the SOURCE OF TRUTH.                                     │
│             LLM-specific format is GENERATED, not hand-maintained.                  │
│             Switch LLMs by regenerating to new target format.                       │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 7-LAYER INVOCATION STACK

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              7-LAYER INVOCATION STACK                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 4: CYCLES (7)                                                         │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  Phase-based workflows with gates                                            │   │
│  │  Source: cycle-definitions.yaml                                              │   │
│  │                                                                              │   │
│  │  implementation   investigation   close-work   work-creation                 │   │
│  │  checkpoint       observation-triage   plan-authoring                        │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  LAYER 3: SKILLS (15 = 7 cycles + 3 bridges + 1 router + 4 utilities)        │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  Prompt orchestration with context injection                                 │   │
│  │  Source: skill-manifest.yaml                                                 │   │
│  │                                                                              │   │
│  │  Bridges: plan-validation, design-review-validation, dod-validation          │   │
│  │  Router: routing-gate (continuation selector - chooses next prompt)          │   │
│  │  Utilities: memory-agent, audit, schema-ref, extract-content                 │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  LAYER 2: SUBAGENTS (7)                                                      │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  Isolated execution with restricted tools                                    │   │
│  │  Source: agent-manifest.yaml                                                 │   │
│  │                                                                              │   │
│  │  REQUIRED: preflight-checker, schema-verifier                                │   │
│  │  OPTIONAL: validation-agent, investigation-agent, test-runner,               │   │
│  │            why-capturer, anti-pattern-checker                                │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  LAYER 1: COMMANDS (18)                                                      │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  Human entry points (user types /name)                                       │   │
│  │  Source: command-manifest.yaml                                               │   │
│  │                                                                              │   │
│  │  /coldstart, /new-work, /new-plan, /new-investigation, /close, etc.          │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  LAYER 0: RECIPES (~50)                                                      │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  Shell execution (just <recipe>)                                             │   │
│  │  Source: recipe-chains.yaml (for composite chains)                           │   │
│  │                                                                              │   │
│  │  Atomic + Composite chains with rollback semantics                           │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  LAYER -1: HOOKS (22 current → 19 target)                                    │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  Automatic governance (no manual invocation)                                 │   │
│  │  Source: hook-handlers.yaml                                                  │   │
│  │                                                                              │   │
│  │  PreToolUse (5), PostToolUse (7), UserPromptSubmit (4), Stop (3)             │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  LAYER -2: MCP (10 HAIOS tools)                                              │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  External tools via JSON-RPC                                                 │   │
│  │  Source: mcp-registry.yaml                                                   │   │
│  │                                                                              │   │
│  │  haios-memory: 10 tools (memory, schema, ingest, marketplace, interpreter)   │   │
│  │  External: context7 (2 tools) - NOT part of HAIOS, available infrastructure  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  INVOCATION RULES:                                                                  │
│  • Higher layers invoke lower layers (normal)                                       │
│  • Lower cannot invoke higher (boundary)                                            │
│  • Cycles can chain to cycles (via CHAIN phase)                                     │
│  • Subagents CANNOT invoke other subagents (isolation)                              │
│                                                                                     │
│  ════════════════════════════════════════════════════════════════════════════════   │
│                                                                                     │
│  THE EMERGENCE: AUTONOMOUS WORK LOOPS VIA PROMPT CHAINING                           │
│                                                                                     │
│  The 7-layer stack isn't just abstraction hierarchy - it's a PROMPT INJECTION       │
│  CASCADE:                                                                           │
│                                                                                     │
│  • Commands inject prompts that invoke Skills                                       │
│  • Skills inject prompts that invoke other Skills (CHAIN phase)                     │
│  • routing-gate is the SELECTOR that chooses WHICH prompt gets injected next        │
│  • The LLM's completion IS the execution                                            │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  CHAIN phase ──► routing-gate ──► "invoke implementation-cycle"              │   │
│  │                                           │                                  │   │
│  │                                           ▼                                  │   │
│  │                                    That string IS the next prompt            │   │
│  │                                           │                                  │   │
│  │                                           ▼                                  │   │
│  │                                    LLM processes it                          │   │
│  │                                           │                                  │   │
│  │                                           ▼                                  │   │
│  │                                    implementation-cycle SKILL.md loads       │   │
│  │                                           │                                  │   │
│  │                                           ▼                                  │   │
│  │                                    New context, new completion               │   │
│  │                                           │                                  │   │
│  │                                           ▼                                  │   │
│  │                                    ... CHAIN ... routing-gate ... loop       │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  routing-gate is the CONTINUATION TRIGGER - the decision point where autonomous    │
│  work either chains forward or yields to operator.                                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. PLUGIN MANIFEST STRUCTURE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           PLUGIN CONFIG FILE HIERARCHY                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  .claude/haios/                                                                     │
│  │                                                                                  │
│  ├── manifest.yaml                    ← Plugin metadata                             │
│  │   name: haios                                                                    │
│  │   version: 2.0.0                                                                 │
│  │   description: Trust Engine for AI Agents                                        │
│  │   target_llms: [claude, gemini, openai]                                          │
│  │                                                                                  │
│  ├── config/                                                                        │
│  │   │                                                                              │
│  │   ├── cycle-definitions.yaml       ← Layer 4 structure                           │
│  │   │   cycles:                                                                    │
│  │   │     implementation-cycle:                                                    │
│  │   │       phases: [PLAN, DO, CHECK, DONE, CHAIN]                                 │
│  │   │       node_binding: implement                                                │
│  │   │       gates:                                                                 │
│  │   │         PLAN: [plan-validation-cycle, preflight-checker]                     │
│  │   │         CHECK: [dod-validation-cycle]                                        │
│  │   │                                                                              │
│  │   ├── skill-manifest.yaml          ← Layer 3 registry                            │
│  │   │   skills:                                                                    │
│  │   │     routing-gate:                                                            │
│  │   │       category: bridge                                                       │
│  │   │       invoked_by: [5 cycles]                                                 │
│  │   │       standalone: false                                                      │
│  │   │                                                                              │
│  │   ├── agent-manifest.yaml          ← Layer 2 registry                            │
│  │   │   agents:                                                                    │
│  │   │     preflight-checker:                                                       │
│  │   │       required: true                                                         │
│  │   │       tools: [Read, Glob]                                                    │
│  │   │       enforcement: hard                                                      │
│  │   │                                                                              │
│  │   ├── command-manifest.yaml        ← Layer 1 registry                            │
│  │   │   commands:                                                                  │
│  │   │     new-work:                                                                │
│  │   │       arguments: [{name: backlog_id, pattern: "^(E2|INV)-\\d+$"}]            │
│  │   │       chains_to: work-creation-cycle                                         │
│  │   │                                                                              │
│  │   ├── recipe-chains.yaml           ← Layer 0 chains                              │
│  │   │   chains:                                                                    │
│  │   │     close-work:                                                              │
│  │   │       steps: [update-status, move-archive, cascade]                          │
│  │   │       on_failure: rollback_all                                               │
│  │   │                                                                              │
│  │   ├── hook-handlers.yaml           ← Layer -1 config                             │
│  │   │   handlers:                                                                  │
│  │   │     PreToolUse: [sql_block, powershell_block, path_governance, ...]          │
│  │   │     PostToolUse: [timestamp_inject, node_history_update, ...]                │
│  │   │                                                                              │
│  │   ├── mcp-registry.yaml            ← Layer -2 tools                              │
│  │   │   servers:                                                                   │
│  │   │     haios-memory:                                                            │
│  │   │       tools: [memory_search_with_experience, ingester_ingest, ...]           │
│  │   │                                                                              │
│  │   ├── gates.yaml                   ← Gate check definitions                      │
│  │   │   gates:                                                                     │
│  │   │     objective_complete:                                                      │
│  │   │       checks: [deliverables_done, remaining_work_empty, anti_pattern_clear]  │
│  │   │                                                                              │
│  │   ├── node-bindings.yaml           ← DAG node → cycle mapping                    │
│  │   │   nodes:                                                                     │
│  │   │     backlog: {cycle: null}                                                   │
│  │   │     discovery: {cycle: investigation-cycle}                                  │
│  │   │     plan: {cycle: plan-authoring-cycle}        # FIXED from plan-cycle       │
│  │   │     implement: {cycle: implementation-cycle}                                 │
│  │   │     close: {cycle: close-work-cycle}           # FIXED from closure-cycle    │
│  │   │                                                                              │
│  │   └── thresholds.yaml              ← Health thresholds                           │
│  │       thresholds:                                                                │
│  │         observation_pending: {max_count: 10, divert_to: triage-cycle}            │
│  │                                                                                  │
│  └── state/                           ← Derived state (regenerable)                 │
│      ├── session-registry.yaml        ← Session ↔ work item links                   │
│      └── work-index.yaml              ← Work item quick lookup                      │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. WORK ITEM LIFECYCLE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           WORK ITEM LIFECYCLE (DAG)                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         5-NODE DAG (from SECTION-2B)                         │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│       ┌─────────┐      ┌───────────┐      ┌──────────┐      ┌───────────┐         │
│       │ BACKLOG │─────►│ DISCOVERY │─────►│   PLAN   │─────►│ IMPLEMENT │         │
│       │         │      │           │      │          │      │           │         │
│       │ (entry) │      │ INV-*     │      │ E2-*     │      │ E2-*      │         │
│       └─────────┘      └───────────┘      └──────────┘      └─────┬─────┘         │
│            │                │                   │                  │               │
│            │                │                   │                  ▼               │
│            │                │                   │           ┌───────────┐          │
│            │                └───────────────────┴──────────►│   CLOSE   │          │
│            │                                                │           │          │
│            └───────────────────────────────────────────────►│ (archive) │          │
│                                                             └───────────┘          │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    NODE → CYCLE BINDING (from node-bindings.yaml)            │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  │ Node      │ Cycle                  │ Scaffold on Entry        │ Exit Gate     │ │
│  │───────────│────────────────────────│──────────────────────────│───────────────│ │
│  │ backlog   │ null                   │ /new-work                │ null          │ │
│  │ discovery │ investigation-cycle    │ /new-investigation       │ inv_complete  │ │
│  │ plan      │ plan-authoring-cycle   │ /new-plan                │ plan_approved │ │
│  │ implement │ implementation-cycle   │ (none)                   │ dod_validated │ │
│  │ close     │ close-work-cycle       │ (none)                   │ archived      │ │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    WORK.md node_history (TARGET)                             │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ```yaml                                                                            │
│  # docs/work/active/E2-150/WORK.md                                                  │
│  current_node: implement                                                            │
│  node_history:                                                                      │
│    - node: backlog                                                                  │
│      entered: 2025-12-28T10:00:00                                                   │
│      exited: 2025-12-28T10:30:00                                                    │
│      session: 148                    # ← BIDIRECTIONAL LINK TO SESSION              │
│    - node: plan                                                                     │
│      entered: 2025-12-28T10:30:00                                                   │
│      exited: 2025-12-29T14:00:00                                                    │
│      session: 149                                                                   │
│    - node: implement                                                                │
│      entered: 2025-12-29T14:00:00                                                   │
│      exited: null                    # ← Current node (not exited)                  │
│      session: 150                                                                   │
│  memory_refs: [80123, 80124]         # ← Auto-populated by PostToolUse              │
│  ```                                                                                │
│                                                                                     │
│  SINGLE WRITER PRINCIPLE:                                                           │
│  • PostToolUse hook is the ONLY writer to node_history                              │
│  • Detects node transitions, appends entry, logs to governance-events.jsonl         │
│  • Memory refs auto-populated when ingester_ingest called with work item path       │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. SESSION LIFECYCLE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SESSION LIFECYCLE (TARGET)                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  SESSION SOURCE OF TRUTH: Checkpoint filenames                               │   │
│  │  docs/checkpoints/YYYY-MM-DD-NN-SESSION-{N}-{title}.md                       │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  BIDIRECTIONAL BINDING (TARGET):                                                    │
│                                                                                     │
│  ┌──────────────────────────────┐         ┌──────────────────────────────┐         │
│  │  Checkpoint (SESSION-151)    │         │  WORK.md (E2-150)            │         │
│  │  ────────────────────────────│         │  ────────────────────────────│         │
│  │  backlog_ids:                │◄───────►│  node_history:               │         │
│  │    - E2-150                  │         │    - node: implement         │         │
│  │    - INV-052                 │         │      session: 151  ◄─────────│         │
│  │  memory_refs: [80343]        │         │  memory_refs: [80343]        │         │
│  └──────────────────────────────┘         └──────────────────────────────┘         │
│            │                                          │                             │
│            │                                          │                             │
│            └──────────────────┬───────────────────────┘                             │
│                               │                                                     │
│                               ▼                                                     │
│                    ┌──────────────────────────────┐                                 │
│                    │  haios_memory.db (concepts)  │                                 │
│                    │  ────────────────────────────│                                 │
│                    │  id: 80343                   │                                 │
│                    │  source_path: contains E2-150│                                 │
│                    └──────────────────────────────┘                                 │
│                                                                                     │
│  SESSION FLOW:                                                                      │
│                                                                                     │
│  /coldstart                                                                         │
│       │                                                                             │
│       ├──► Read checkpoint → derive session N+1                                     │
│       ├──► Auto: just session-start N+1                    # TARGET: auto          │
│       ├──► memory_search_with_experience(mode=session_recovery)                     │
│       ├──► Route to work via just ready                                             │
│       │                                                                             │
│       ▼                                                                             │
│  SESSION WORK                                                                       │
│       │                                                                             │
│       ├──► UserPromptSubmit: inject vitals, refresh slim status                     │
│       ├──► PostToolUse: update node_history.session, timestamps                     │
│       ├──► ingester_ingest: auto-link memory_refs                                   │
│       │                                                                             │
│       ▼                                                                             │
│  /new-checkpoint                                                                    │
│       │                                                                             │
│       ├──► checkpoint-cycle: SCAFFOLD → FILL → VERIFY → CAPTURE → COMMIT            │
│       ├──► just session-end N+1                                                     │
│       └──► Git commit                                                               │
│                                                                                     │
│  CRASH RECOVERY (TARGET):                                                           │
│  • coldstart detects orphan sessions (start without end)                            │
│  • Creates synthetic recovery checkpoint                                            │
│  • Logs synthetic session-end                                                       │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. DATA FLOW

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW (SINGLE WRITER PRINCIPLE)                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      AUTHORITATIVE STATE (Source of Truth)                   │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌────────────────────────┐          ┌────────────────────────┐                    │
│  │  WORK.md               │          │  haios_memory.db       │                    │
│  │  ─────────────────────│          │  ─────────────────────│                    │
│  │  current_node          │          │  concepts              │                    │
│  │  node_history          │◄────────►│  entities              │                    │
│  │  memory_refs           │  auto-   │  reasoning_traces      │                    │
│  │                        │  link    │                        │                    │
│  │  SINGLE WRITER:        │          │  SINGLE WRITER:        │                    │
│  │  PostToolUse hook      │          │  MCP tools only        │                    │
│  └────────────────────────┘          └────────────────────────┘                    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      COMPUTED STATE (Cache - Regenerable)                    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌────────────────────────┐          ┌────────────────────────┐                    │
│  │  haios-status-slim.json│          │  haios-status.json     │                    │
│  │  ─────────────────────│          │  ─────────────────────│                    │
│  │  session_delta         │          │  Full workspace scan   │                    │
│  │  milestone             │          │                        │                    │
│  │  counts                │          │  WRITER:               │                    │
│  │                        │          │  just update-status    │                    │
│  │  WRITER:               │          └────────────────────────┘                    │
│  │  UserPromptSubmit hook │                                                        │
│  └────────────────────────┘                                                        │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      AUDIT LOGS (Append-Only)                                │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌────────────────────────┐          ┌────────────────────────┐                    │
│  │  haios-events.jsonl    │          │  governance-events.jsonl│                   │
│  │  ─────────────────────│          │  ─────────────────────│                    │
│  │  session start/end     │          │  CyclePhaseEntered     │                    │
│  │  cycle_transition      │          │  ValidationOutcome     │                    │
│  │  heartbeat             │          │                        │                    │
│  │                        │          │  WRITER:               │                    │
│  │  WRITERS:              │          │  governance_events.py  │                    │
│  │  just session-*, hooks │          └────────────────────────┘                    │
│  └────────────────────────┘                                                        │
│                                                                                     │
│  AUTO-LINKING FLOW (TARGET):                                                        │
│                                                                                     │
│  ingester_ingest(content, source_path="docs/work/active/E2-150/...")                │
│       │                                                                             │
│       ▼                                                                             │
│  Store concept → get concept_id                                                     │
│       │                                                                             │
│       ▼                                                                             │
│  PostToolUse detects MCP ingest result                                              │
│       │                                                                             │
│       ▼                                                                             │
│  Extract work_id from source_path (E2-150)                                          │
│       │                                                                             │
│       ▼                                                                             │
│  Update WORK.md: memory_refs: [..., concept_id]                                     │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. HOOK ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           HOOK ARCHITECTURE (19 TARGET HANDLERS)                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  hook_dispatcher.py → Routes all events to handler functions                 │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌────────────────────────────┐      ┌────────────────────────────┐               │
│  │  PreToolUse (5 handlers)   │      │  PostToolUse (7 handlers)  │               │
│  │  ────────────────────────  │      │  ────────────────────────  │               │
│  │  ☐ sql_blocking            │      │  ☐ timestamp_injection     │               │
│  │  ☐ powershell_blocking     │      │  ☐ node_history_update     │               │
│  │  ☐ path_governance         │      │  ☐ error_capture           │               │
│  │  ☐ exit_gate_check         │      │  ☐ template_validation     │               │
│  │  ☐ backlog_id_unique       │      │  ☐ artifact_refresh        │               │
│  │                            │      │  ☐ cascade_trigger         │               │
│  │  Config: governance-       │      │  ☐ memory_refs_auto_link   │ ← NEW         │
│  │          toggles.yaml      │      │                            │               │
│  └────────────────────────────┘      │  Config: hook-handlers.yaml│               │
│                                      └────────────────────────────┘               │
│                                                                                     │
│  ┌────────────────────────────┐      ┌────────────────────────────┐               │
│  │  UserPromptSubmit (4)      │      │  Stop (3 handlers)         │               │
│  │  ────────────────────────  │      │  ────────────────────────  │               │
│  │  ☐ date_time_inject        │      │  ☐ reasoning_bank_extract  │               │
│  │  ☐ context_percentage      │      │  ☐ session_summary         │               │
│  │  ☐ slim_status_refresh     │      │  ☐ checkpoint_reminder     │               │
│  │  ☐ vitals_inject           │      │                            │               │
│  │                            │      │  Config: hook-handlers.yaml│               │
│  │  Config: hook-handlers.yaml│      └────────────────────────────┘               │
│  └────────────────────────────┘                                                    │
│                                                                                     │
│  HANDLER LIFECYCLE:                                                                 │
│                                                                                     │
│  1. Event fires → hook_dispatcher.py receives                                       │
│  2. Dispatcher reads hook-handlers.yaml for enabled handlers                        │
│  3. For each enabled handler: import + execute                                      │
│  4. Handlers can ALLOW, DENY (PreToolUse), or modify output                         │
│                                                                                     │
│  TARGET vs CURRENT:                                                                 │
│  • Current: 22 handlers, scattered logic                                            │
│  • Target: 19 handlers, config-driven, clear single responsibility                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. CYCLE EXECUTION

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           CYCLE EXECUTION (YAML-DRIVEN)                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  cycle-definitions.yaml → Thin Executor → SKILL.md prompts                   │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ```yaml                                                                            │
│  # .claude/haios/config/cycle-definitions.yaml                                      │
│  cycles:                                                                            │
│    implementation-cycle:                                                            │
│      phases:                                                                        │
│        - name: PLAN                                                                 │
│          entry_criteria: [work_file_exists, current_node_is_implement]              │
│          gates: [plan-validation-cycle, preflight-checker]                          │
│          exit_criteria: [plan_complete, preflight_passed]                           │
│        - name: DO                                                                   │
│          gates: [design-review-validation]                                          │
│          exit_criteria: [implementation_complete]                                   │
│        - name: CHECK                                                                │
│          gates: [dod-validation-cycle]                                              │
│          exit_criteria: [tests_pass, why_captured]                                  │
│        - name: DONE                                                                 │
│          exit_criteria: [docs_updated]                                              │
│        - name: CHAIN                                                                │
│          routing: routing_gate                                                      │
│      node_binding: implement                                                        │
│      memory:                                                                        │
│        query_at: [DO]                                                               │
│        store_at: [DONE]                                                             │
│  ```                                                                                │
│                                                                                     │
│  EXECUTION FLOW:                                                                    │
│                                                                                     │
│  Skill(skill="implementation-cycle")                                                │
│       │                                                                             │
│       ▼                                                                             │
│  ┌────────────────────────────────────────────────────────────────┐                │
│  │  Thin Executor (cycle_executor.py)                              │                │
│  │  ──────────────────────────────────────────────────────────────│                │
│  │  1. Load cycle definition from cycle-definitions.yaml           │                │
│  │  2. Determine current phase from context                        │                │
│  │  3. Check entry_criteria                                        │                │
│  │  4. Invoke phase-specific gates (bridges/agents)                │                │
│  │  5. Load SKILL.md for phase prompt                              │                │
│  │  6. Execute phase actions                                       │                │
│  │  7. Verify exit_criteria                                        │                │
│  │  8. Transition to next phase or CHAIN                           │                │
│  └────────────────────────────────────────────────────────────────┘                │
│       │                                                                             │
│       ▼                                                                             │
│  ┌────────────────────────────────────────────────────────────────┐                │
│  │  SKILL.md (Human-readable prompts)                              │                │
│  │  ──────────────────────────────────────────────────────────────│                │
│  │  ### 2. DO Phase                                                │                │
│  │  **Goal:** Execute implementation according to plan.            │                │
│  │  **Actions:** ...                                               │                │
│  │  **Exit Criteria:**                                             │                │
│  │  - [ ] Code written                                             │                │
│  │  - [ ] Tests written                                            │                │
│  └────────────────────────────────────────────────────────────────┘                │
│                                                                                     │
│  PATTERN: YAML defines structure, SKILL.md provides human-readable prompts          │
│           Executor is thin - just orchestrates flow                                 │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. MEMORY INTEGRATION

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           MEMORY INTEGRATION (AUTO-LINKED)                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  haios-memory MCP Server (10 tools)                                          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  TOOLS:                                                                             │
│  │ Tool                        │ Purpose                    │ Category    │        │
│  │─────────────────────────────│────────────────────────────│─────────────│        │
│  │ memory_search_with_experience│ Query + strategy injection │ Retrieval   │        │
│  │ memory_stats                │ Database counts            │ Retrieval   │        │
│  │ ingester_ingest             │ Auto-classify + store      │ Storage     │        │
│  │ extract_content             │ Entity/concept extraction  │ Storage     │        │
│  │ schema_info                 │ Table/column info          │ Schema      │        │
│  │ db_query                    │ Read-only SQL              │ Schema      │        │
│  │ marketplace_list_agents     │ List agents                │ Marketplace │        │
│  │ marketplace_get_agent       │ Get agent details          │ Marketplace │        │
│  │ interpreter_translate       │ Intent → directive         │ Interpreter │        │
│  │ memory_store                │ (DEPRECATED)               │ Storage     │        │
│                                                                                     │
│  AUTO-LINKING (TARGET):                                                             │
│                                                                                     │
│  ```yaml                                                                            │
│  # .claude/haios/config/memory-integration.yaml                                     │
│  memory:                                                                            │
│    auto_link:                                                                       │
│      enabled: true                                                                  │
│      extract_work_id_from_path: true    # Parse E2-xxx from source_path             │
│      update_work_file: true             # Auto-append to memory_refs                │
│    strategy_injection:                                                              │
│      enabled: true                                                                  │
│      table: reasoning_traces                                                        │
│    toon_encoding:                                                                   │
│      enabled: true                                                                  │
│      token_reduction: 57%                                                           │
│  ```                                                                                │
│                                                                                     │
│  FLOW WITH AUTO-LINKING:                                                            │
│                                                                                     │
│  Agent: ingester_ingest(content="WHY: ...", source_path="docs/work/.../E2-150/...")  │
│       │                                                                             │
│       ▼                                                                             │
│  MCP Server: Store concept → concept_id = 80345                                     │
│       │                                                                             │
│       ▼                                                                             │
│  PostToolUse Hook: Detect MCP result with concept_id                                │
│       │                                                                             │
│       ▼                                                                             │
│  Extract work_id from source_path: E2-150                                           │
│       │                                                                             │
│       ▼                                                                             │
│  Edit docs/work/active/E2-150/WORK.md:                                              │
│       memory_refs: [80123, 80124, 80345]  ← Auto-appended                           │
│                                                                                     │
│  RETRIEVAL WITH STRATEGY INJECTION:                                                 │
│                                                                                     │
│  Agent: memory_search_with_experience(query="how to implement X", mode="semantic")   │
│       │                                                                             │
│       ▼                                                                             │
│  MCP Server: Query concepts + reasoning_traces                                      │
│       │                                                                             │
│       ▼                                                                             │
│  Return: concepts + reasoning_trace (strategies from similar past work)             │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. GAP RESOLUTION MAP

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           GAP RESOLUTION MAP (S152)                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  HIGH PRIORITY:                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  Gap                          │ Section │ Target Fix                         │   │
│  │───────────────────────────────│─────────│─────────────────────────────────── │   │
│  │  Wrong cycle names in         │ S6      │ plan-cycle → plan-authoring-cycle  │   │
│  │  node-cycle-bindings.yaml     │         │ closure-cycle → close-work-cycle   │   │
│  │──────────────────────────────────────────────────────────────────────────────│   │
│  │  No work item auto-linking    │ S8      │ PostToolUse: detect ingest result, │   │
│  │                               │         │ extract work_id, update memory_refs│   │
│  │──────────────────────────────────────────────────────────────────────────────│   │
│  │  context7 listed as HAIOS     │ S13     │ Clarified: external utility,       │   │
│  │  config                       │         │ not part of HAIOS plugin           │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  MEDIUM PRIORITY:                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  Gap                          │ Section │ Target Fix                         │   │
│  │───────────────────────────────│─────────│─────────────────────────────────── │   │
│  │  Legacy paths in              │ S5      │ Check docs/work/archive/ not       │   │
│  │  _find_completed_items        │         │ docs/plans/ or docs/pm/            │   │
│  │──────────────────────────────────────────────────────────────────────────────│   │
│  │  No session binding in        │ S5      │ Add session field to node_history  │   │
│  │  WORK.md                      │         │ entries                            │   │
│  │──────────────────────────────────────────────────────────────────────────────│   │
│  │  Composite recipe chains      │ S7      │ Define recipe-chains.yaml with     │   │
│  │  implicit                     │         │ rollback semantics                 │   │
│  │──────────────────────────────────────────────────────────────────────────────│   │
│  │  Argument handling            │ S9      │ Standardize in command-manifest    │   │
│  │  inconsistent                 │         │ with pattern validation            │   │
│  │──────────────────────────────────────────────────────────────────────────────│   │
│  │  Category is documentation    │ S10     │ Add category to SKILL.md frontmatter│  │
│  │  only (7+3+5 split)           │         │ or skill-manifest.yaml             │   │
│  │──────────────────────────────────────────────────────────────────────────────│   │
│  │  Tool access not enforced     │ S11     │ Task dispatcher reads agent-       │   │
│  │  for subagents                │         │ manifest, restricts tools          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  LOW PRIORITY / FUTURE:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  Gap                          │ Section │ Target Fix                         │   │
│  │───────────────────────────────│─────────│─────────────────────────────────── │   │
│  │  No cross-config validation   │ S6      │ Add just validate-config recipe    │   │
│  │  No transaction semantics     │ S7      │ Recipe chain rollback mechanism    │   │
│  │  Layer definitions are        │ S12     │ Add layer metadata to all manifests│   │
│  │  documentation only           │         │                                    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  IMPLEMENTATION ITEMS TO SPAWN:                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  ID      │ Title                                   │ Priority              │   │
│  │──────────│─────────────────────────────────────────│───────────────────────│   │
│  │  E2-241  │ Fix node-cycle-bindings.yaml cycle names│ High                  │   │
│  │  E2-242  │ Implement memory_refs auto-linking      │ High                  │   │
│  │  E2-243  │ Create skill-manifest.yaml              │ Medium                │   │
│  │  E2-244  │ Create agent-manifest.yaml              │ Medium                │   │
│  │  E2-245  │ Create command-manifest.yaml            │ Medium                │   │
│  │  E2-246  │ Create recipe-chains.yaml               │ Medium                │   │
│  │  E2-247  │ Add session to node_history             │ Medium                │   │
│  │  E2-248  │ Create cycle-definitions.yaml + executor│ Medium                │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

*This diagram synthesizes the target architecture from all 21 INV-052 section files.*
*Source: SECTION-1A through SECTION-13, analyzed in Session 152.*
*Status: Design complete. Ready for implementation item spawning.*
