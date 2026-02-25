---
template: investigation
status: active
date: 2026-02-25
backlog_id: WORK-218
title: "MCP Operations Server Investigation"
author: Hephaestus
session: 449
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 86035
- 85949
- 85956
- 86012
- 85948
- 85950
- 85958
- 85951
version: "2.0"
generated: 2026-02-25
last_updated: 2026-02-25T09:55:00
---
# Investigation: MCP Operations Server

---

## Context

**Trigger:** CH-066 (MCPOperationsServer) is the largest remaining E2.8 Arc 1 (call) chapter. All dependency chapters complete. Operator directed investigation-first to discover unknowns and innovation opportunities.

**Problem Statement:** What is the right design for an MCP operations server that replaces `just` recipes as the agent-native Tier 2 interface, and what unknown challenges and innovation opportunities exist beyond recipe parity?

**Prior Observations:**
- Full ceremony chain = ~104% of 200k context budget (mem:85390) — architectural impossibility
- Agents invoke `just X` via Bash tool: shell overhead, untyped I/O, no discoverability (violates REQ-DISCOVER-002)
- S419 design note: tool naming is first-class UX concern
- MCP tools auto-discovered in system prompt (mem:85949) — agents call tools naturally like `mcp__haios-memory__*`
- Operator vision (mem:85951): recipes grouped into skillsets, MCP server IS the ADR-045 Tier 2 implementation

---

## Prior Work Query

**Memory Query:** `memory_search_with_experience` with query: "MCP operations server haios-operations"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 86035 | MCP operations server — agent-native interface replacing just recipes | Direct target |
| 85949 | MCP tools auto-discovered in system prompt | Architecture pattern |
| 85956 | Hook blockers unnecessary when MCP is the only path | Governance simplification |
| 86012 | Directive: replace just recipes with MCP tools | Operator intent |
| 85948 | haios-operations MCP server with grouped tool namespaces | Naming approach |
| 85950 | Tier 1/2/3 refined: MCP tools = Tier 2 | Tier model |
| 85951 | Recipes grouped into skillsets; MCP server IS Tier 2 | Vision |
| 85958 | MCP tools as exclusive agent interface = mature architecture | Target state |

**Prior Investigations:** No prior INV-* or WORK investigation on MCP operations server design.

---

## Objective

What is the right architecture for a `haios-operations` MCP server: tool taxonomy, scope boundary, technical feasibility, governance integration, and innovation opportunities beyond just-recipe parity?

---

## Scope

### In Scope
- Tool naming convention and taxonomy (all operation groups)
- Scope boundary: which operations move to MCP vs stay in `just`
- Technical feasibility: import paths, state management, error handling
- Governance integration: how MCP tools interact with PreToolUse hooks and activity matrix
- Innovation: MCP resources, typed returns, atomic composition, progress notifications
- Packaging: single vs multi-server, transport, registration

### Out of Scope
- Actual implementation (this spawns implementation work items)
- MCP prompts for ceremony templates (lower value, future consideration)
- Cross-server composition between haios-memory and haios-operations (agent orchestrates)
- Retirement of just recipes (separate work item — gradual migration)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files examined | ~15 | justfile, mcp_server.py, cli.py, work_engine.py, hooks, etc. |
| Hypotheses to test | 5 | Listed below |
| Evidence sources | 3 | Codebase, Memory, External (steipete/claude-code-mcp) |
| Estimated complexity | High | Architectural scope, multiple unknowns |

---

## Hypotheses

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | A single `haios-operations` FastMCP server can wrap all operational Python modules with the existing dual-path import pattern | Med | Verify import chain from hypothetical server location; identify collisions | 1st |
| **H2** | 4-5 justfile recipes with inline JSON state writes need new lib/ abstractions before MCP wrapping is possible | High | Enumerate all inline writers in justfile; check for lib/ equivalents | 2nd |
| **H3** | PreToolUse hooks do NOT fire for MCP tool calls, creating a governance gap that must be addressed in-server | High | Check hook matcher patterns in settings.local.json; verify MCP tool coverage | 3rd |
| **H4** | MCP resources (typed URIs) for work items and queue state are a high-value innovation beyond recipe parity | Med | Verify FastMCP resource support; assess value of `work://WORK-218` pattern | 4th |
| **H5** | Atomic multi-step operations (close = close + cascade + status update in one call) provide genuine improvement over shell chaining | High | Compare justfile close-work recipe (3 subprocesses) vs single Python call | 5th |

---

## Evidence Collection

### Codebase Evidence

| Finding | Source | Supports | Notes |
|---------|--------|----------|-------|
| FastMCP("haios-memory") produces tools prefixed `mcp__haios-memory__` | `haios_etl/mcp_server.py:40` | H1 | Naming convention confirmed |
| cli.py bootstraps both sys.paths (modules + lib) | `.claude/haios/modules/cli.py:19-26` | H1 | Pattern to replicate |
| work_engine.py uses try/except ImportError for dual-mode imports | `.claude/haios/modules/work_engine.py:51-62` | H1 | Robust pattern |
| `modules/cli.py` and `lib/cli.py` name collision | Both exist | H1 | Risk: `import cli` resolves to wrong module |
| `set-cycle` writes inline JSON to haios-status-slim.json | `justfile:310` | H2 | No lib/ function wraps this |
| `clear-cycle` writes inline JSON reset | `justfile:321` | H2 | No lib/ function |
| `set-queue` writes inline JSON mutation | `justfile:326` | H2 | No lib/ function |
| `session-start` compound write (session file + JSON) | `justfile:300` | H2 | No unified lib/ function |
| PreToolUse matcher: `Write\|Edit\|MultiEdit\|Bash\|EnterPlanMode\|ExitPlanMode` | `settings.local.json:140-149` | H3 | No MCP tools in matcher |
| PostToolUse has one MCP tool: `mcp__haios-memory__ingester_ingest` | `settings.local.json:152-159` | H3 | Shows MCP tools CAN be added |
| `governance_layer.map_tool_to_primitive()` has hardcoded `mcp__haios-memory__*` branch | `governance_layer.py:432-440` | H3 | New server needs parallel branch |
| Unrecognized tools fall through to `"unknown"` → default-allow | `governance_layer.py` | H3 | Silent governance bypass |
| FastMCP Context has `report_progress(progress, total)` | Installed package introspection | H4/H5 | Progress notifications available |
| `close-work` recipe chains 3 separate python invocations | `justfile` | H5 | 3 process startups |
| `execute_queue_transition` returns `{success, error, work_id}` dict | `queue_ceremonies.py` | H5 | Already typed internally |
| WorkState dataclass has 14+ typed fields | `work_engine.py` | H4 | Ready for structured MCP return |

### Memory Evidence

| Concept ID | Content | Supports | Notes |
|------------|---------|----------|-------|
| 85949 | MCP tools auto-discovered in system prompt | H1 | No manual registration needed |
| 85956 | Hook blockers unnecessary when MCP is the only path | H3 | Governance moves into server |
| 85950 | Tier model: MCP = Tier 2, just = Tier 3 | H1 | Architectural target |
| 85951 | Recipes grouped into skillsets; MCP server IS Tier 2 | H1, H4 | Operator vision |

### External Evidence

| Source | Finding | Supports | Reference |
|--------|---------|----------|-----------|
| steipete/claude-code-mcp | Single-tool wrapping CLI — opposite of our fine-grained approach | H1 (contrast) | github.com/steipete/claude-code-mcp |
| steipete/claude-code-mcp | Validates MCP as viable agent tooling pattern | H1 | Same |
| FastMCP docs | Resources are typed, cacheable, URI-addressable data endpoints | H4 | MCP protocol spec |
| FastMCP docs | `ctx.report_progress()` emits notifications over stdio | H5 | MCP protocol spec |

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1: Single server can wrap all modules | **Confirmed** | cli.py dual-path bootstrap pattern is replicable; work_engine try/except handles both modes. cli.py name collision is manageable with importlib. | High |
| H2: 4-5 recipes need new lib/ abstractions | **Confirmed** | `set-cycle`, `clear-cycle`, `set-queue`, `session-start` all write inline JSON with no lib/ wrapper. Need `cycle_state.set_cycle_state()`, `cycle_state.clear_cycle_state()`, `cycle_state.set_active_queue()`, `session_mgmt.start_session()`. | High |
| H3: Hooks don't fire for MCP tools — governance gap | **Confirmed** | PreToolUse matcher excludes all MCP tools. `map_tool_to_primitive` returns "unknown" for unrecognized tools → silent allow. MCP tools MUST implement governance internally OR be added to hook matchers. | High |
| H4: MCP resources are high-value innovation | **Confirmed** | `@mcp.resource("work://{work_id}")` gives URI-addressable typed data. WorkState has 14+ fields ready for structured return. Queue state as resource eliminates prose-to-struct extraction. No subscription support in current version (polling only). | Med-High |
| H5: Atomic multi-step operations improve over shell chaining | **Confirmed** | `close-work` spawns 3 separate Python processes. Single MCP tool call executes all in one process with shared state, typed return, and proper error propagation. | High |

### Detailed Findings

#### F1: Import Path Architecture is Solvable

**Evidence:** `cli.py:19-26` shows the canonical bootstrap: insert `modules/` then `lib/` onto sys.path relative to the server file. `work_engine.py:51-62` demonstrates the try/except ImportError pattern for dual-mode (package vs standalone).

**Analysis:** A new MCP server at any location can replicate this pattern. The anchor is relative path from server file to `.claude/haios/modules/` and `.claude/haios/lib/`. The `cli.py` name collision is real but solvable — the MCP server should never `import cli` directly; it uses `WorkEngine`, `GovernanceLayer`, `queue_ceremonies`, etc.

**Implication:** Server can live at project root (e.g., `haios_ops/mcp_server.py`) or inside `.claude/haios/` (e.g., `.claude/haios/mcp_ops.py`). Project root is cleaner for `.mcp.json` registration.

#### F2: State Management Gap Requires New Abstractions

**Evidence:** Four justfile recipes write to `haios-status-slim.json` with inline Python, bypassing any lib/ function:
- `set-cycle` (line 310): writes full `session_state` dict + calls `sync_work_md_phase` + `log_phase_transition`
- `clear-cycle` (line 321): resets `session_state` to null/empty
- `set-queue` (line 326): mutates `session_state.active_queue`
- `session-start` (line 300): writes `session_delta` to `haios-status.json` + truncates `.claude/session`

**Analysis:** These are compound operations (JSON mutation + side effects). Before wrapping as MCP tools, each needs a lib/ function that encapsulates the full operation. `cycle_state.py` already has `advance_cycle_phase()` and `sync_work_md_phase()` — extend it with `set_cycle_state()`, `clear_cycle_state()`, `set_active_queue()`. Create `session_mgmt.py` for `start_session()`.

**Implication:** Phase 1 of implementation should extract these abstractions. Phase 2 wraps them as MCP tools. This is prerequisite work.

#### F3: Governance Must Move Into the Server

**Evidence:** PreToolUse matcher (`settings.local.json:140-149`) only fires for `Write|Edit|MultiEdit|Bash|EnterPlanMode|ExitPlanMode`. MCP tools are invisible to hooks unless explicitly added. `map_tool_to_primitive()` returns `"unknown"` for unrecognized tool names → fail-permissive (default-allow).

**Analysis:** Two approaches:
1. **Add each MCP tool to hook matchers** — requires settings.local.json updates per tool, hooks fire per call (external process overhead)
2. **Implement governance inline in MCP server** — GovernanceLayer already importable, call `check_activity()` directly in tool handler

Option 2 is superior: zero hook overhead, governance runs in-process, and the MCP server becomes a self-governing boundary. The existing haios-memory server is already self-governing (db_query blocks non-SELECT internally, not via hooks).

**Implication:** The MCP server imports `GovernanceLayer` and calls `check_activity(state, primitive)` before executing operations. This is the L3.21 (Computable Means Mechanical) pattern — enforcement in Python, not in agent-read markdown.

#### F4: MCP Resources Enable Structured Agent Reasoning

**Evidence:** FastMCP supports `@mcp.resource("work://{work_id}")` with typed returns. WorkState dataclass has 14+ fields. Current `just ready` returns prose like `"  WORK-212: Title"` — agent must parse text to extract ID and title.

**Analysis:** Resources differ from tools: they are addressable URIs for data, not imperative actions. An agent reading `work://WORK-218` gets a JSON document it can branch on field-by-field. Queue state as `haios://queue/ready` returns `List[WorkState]` — sortable, filterable. No subscription support in installed FastMCP (content changes still require polling).

**Implication:** Expose key state as resources (work items, queue, status, session state). Tools are for mutations. Resources are for reads. This separation aligns with CQRS and makes agent reasoning cleaner.

#### F5: Tool Naming Convention

**Evidence:** S419 design note: "just work < good name". Memory 85948: "grouped tool namespaces". Existing pattern: `mcp__haios-memory__memory_search_with_experience`.

**Analysis:** The server name becomes the namespace prefix automatically (`mcp__haios-operations__`). Function names become tool suffixes. Convention: `{domain}_{verb}` — e.g., `work_get`, `work_close`, `queue_ready`, `session_start`, `scaffold_work`. Keep names short and intuitive.

**Proposed taxonomy:**

| Group | Tools | Backing |
|-------|-------|---------|
| **work** | `work_get`, `work_create`, `work_close`, `work_transition` | WorkEngine |
| **queue** | `queue_ready`, `queue_list`, `queue_next`, `queue_prioritize`, `queue_commit`, `queue_park`, `queue_unpark` | WorkEngine + queue_ceremonies |
| **session** | `session_start`, `session_end`, `cycle_set`, `cycle_get`, `cycle_clear` | governance_events + new session_mgmt |
| **scaffold** | `scaffold_work`, `scaffold_plan`, `scaffold_investigation` | GovernanceLayer.scaffold_template |
| **status** | `status_update`, `status_get` | status.py |
| **hierarchy** | `hierarchy_arcs`, `hierarchy_chapters`, `hierarchy_work` | hierarchy_engine |
| **audit** | `audit_sync`, `audit_gaps`, `audit_stale` | audit.py |
| **observations** | `observations_validate`, `observations_scan` | observations.py |

Total: ~25-30 tools across 8 groups.

#### F6: Atomic Composition Reduces Latency and Improves Reliability

**Evidence:** `just close-work` spawns 3 separate Python processes: (1) close work, (2) cascade status, (3) update status JSON. Each process re-initializes the module graph.

**Analysis:** A single MCP `work_close` tool can execute all three steps in one process call. Shared state means no re-initialization. Typed return includes success/failure for each substep. If cascade fails, the tool returns partial success with error details — currently the justfile chain stops silently on failure.

**Implication:** Multi-step operations are a natural fit for MCP tools. Enumerate which just recipes chain multiple subprocess calls and collapse them.

---

## Design Outputs

### Tool Taxonomy

See F5 above for the complete taxonomy (8 groups, ~25-30 tools).

### Architecture Design

```
.mcp.json
  haios-memory: python -m haios_etl.mcp_server     (existing)
  haios-operations: python -m haios_ops.mcp_server  (new)

haios_ops/
  __init__.py
  mcp_server.py          # FastMCP("haios-operations"), @mcp.tool() + @mcp.resource()
  bootstrap.py           # sys.path setup for modules/ and lib/

Agent calls:
  mcp__haios-operations__work_get(work_id="WORK-218")
  → returns typed WorkState JSON

  Read resource: work://WORK-218
  → returns typed WorkState JSON (cacheable)
```

### Governance Integration Design

```
TRIGGER: Agent calls mcp__haios-operations__work_transition(work_id, to_node)

ACTION (inside MCP tool handler):
    1. Read current session_state from haios-status-slim.json
    2. Call GovernanceLayer.check_activity(state, "work_transition")
    3. If blocked: return {success: false, error: "Blocked by governance: {reason}"}
    4. If allowed: execute WorkEngine.transition(work_id, to_node)
    5. Log governance event via governance_events.log_*

OUTCOME: Governance enforced in-process, zero hook overhead
```

### Implementation Phasing

| Phase | Scope | Effort |
|-------|-------|--------|
| **Phase 0** | Extract lib/ abstractions for inline JSON state writes (set-cycle, clear-cycle, set-queue, session-start) | Small |
| **Phase 1** | Core MCP server: work + queue + session tools (15 tools) | Medium |
| **Phase 2** | MCP resources: work items, queue state, status | Small |
| **Phase 3** | Governance integration: in-server activity checking | Medium |
| **Phase 4** | Extended tools: scaffold, hierarchy, audit, observations | Medium |
| **Phase 5** | Migration: update skills/CLAUDE.md to reference MCP tools over just recipes | Small |

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Single server vs multi | Single `haios-operations` | One process, shared module state, simpler registration. Memory stays separate (different dependency: SQLite + embeddings). |
| Server location | `haios_ops/` at project root | Mirrors `haios_etl/` pattern. Clean `.mcp.json` registration. |
| Governance enforcement | In-server (GovernanceLayer import) | Zero hook overhead. L3.21: computable predicates enforced mechanically in Python. Self-governing boundary. |
| Tool vs Resource | Tools for mutations, Resources for reads | CQRS-aligned. Resources are cacheable, typed URIs. Tools are imperative actions. |
| Naming convention | `{domain}_{verb}` (e.g., `work_get`) | S419 design note: naming is UX. Short, intuitive, discoverable. |
| Phased rollout | 5 phases, Phase 0 prerequisite | Phase 0 extracts lib/ abstractions. Each subsequent phase is independently valuable and deployable. |

---

## Spawned Work Items

### Immediate (Can implement now)

- [ ] **WORK-219: Extract State Management Abstractions (Phase 0)**
  - Description: Create lib/ functions for set-cycle, clear-cycle, set-queue, session-start — prerequisite for MCP wrapping
  - Fixes: H2 finding — 4 recipes with inline JSON writes have no lib/ abstraction
  - Type: implementation, effort: small

- [ ] **WORK-220: MCP Operations Server Core (Phase 1)**
  - Description: Implement haios-operations FastMCP server with work + queue + session tool groups (~15 tools)
  - Fixes: H1/H5 — agent-native typed operations replacing just recipes
  - Blocked by: WORK-219
  - Type: implementation, effort: medium

### Future (Requires Phase 1 completion)

- [ ] **MCP Resources for Work Items and Queue State (Phase 2)**
  - Description: Add @mcp.resource decorators for work://{id}, haios://queue/ready, haios://status/slim
  - Blocked by: WORK-220

- [ ] **In-Server Governance Integration (Phase 3)**
  - Description: Import GovernanceLayer into MCP server, enforce activity matrix per tool call
  - Blocked by: WORK-220

---

## References

- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md
- @haios_etl/mcp_server.py (existing pattern)
- @.mcp.json (registration)
- @justfile (recipes to replace)
- @.claude/haios/modules/work_engine.py
- @.claude/haios/lib/queue_ceremonies.py
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-DISCOVER-002, REQ-CONFIG-001)
- External: github.com/steipete/claude-code-mcp (contrast pattern — single tool wrapping CLI)
- Memory: 85390, 85949, 85956, 86012, 85948, 85950, 85951, 85958
