# generated: 2026-01-30
# System Auto: last updated on: 2026-02-01T16:56:34
# Chapter: ActivityMatrix

## Definition

**Chapter ID:** CH-001
**Arc:** activities
**Status:** Draft
**Depends:** None (foundational)

---

## Problem

How do we govern tool usage based on workflow state? Currently:
- PreToolUse hook checks tool + path, not tool + state
- Same tool (Read, Write) has different appropriateness per phase
- DO phase should be "black-box" but no enforcement exists

**Design Question:** What is the complete matrix of Primitive × State × Rule?

---

## Core Pattern (Decision 82707)

```
Governed Activity = Primitive × State × Governance Rules
```

The same primitive becomes a different governed activity depending on phase/state.
State determines the governance envelope around primitives.

---

## Primitive Taxonomy

### Category 1: File Operations

| Primitive | Description | Tool |
|-----------|-------------|------|
| `file-read` | Read file contents | Read |
| `file-write` | Create/overwrite file | Write |
| `file-edit` | Modify existing file | Edit |
| `file-search` | Find files by pattern | Glob |
| `content-search` | Search file contents | Grep |

### Category 2: Execution

| Primitive | Description | Tool |
|-----------|-------------|------|
| `shell-execute` | Run shell command | Bash |
| `shell-background` | Run command in background | Bash (run_in_background) |
| `notebook-edit` | Edit Jupyter cells | NotebookEdit |

### Category 3: Web/External

| Primitive | Description | Tool |
|-----------|-------------|------|
| `web-fetch` | Fetch URL content | WebFetch |
| `web-search` | Search the web | WebSearch |

### Category 4: Agent/Task

| Primitive | Description | Tool |
|-----------|-------------|------|
| `task-spawn` | Create subagent task | Task |
| `task-track` | Track sub-tasks (ephemeral) | TaskCreate, TaskUpdate, TaskGet, TaskList |
| `skill-invoke` | Invoke a skill | Skill |
| `user-query` | Ask user a question | AskUserQuestion |

### Category 5: Memory (HAIOS)

| Primitive | Description | Tool |
|-----------|-------------|------|
| `memory-search` | Query memory system | mcp__haios-memory__memory_search_with_experience |
| `memory-store` | Store to memory | mcp__haios-memory__ingester_ingest |
| `schema-query` | Query database schema | mcp__haios-memory__schema_info |
| `db-query` | Execute SQL query | mcp__haios-memory__db_query |

### Category 6: Planning/Governance

| Primitive | Description | Tool |
|-----------|-------------|------|
| `plan-exit` | Exit plan mode | ExitPlanMode |
| `plan-enter` | Enter plan mode | EnterPlanMode |
| `mcp-list` | List MCP resources | ListMcpResourcesTool |
| `mcp-read` | Read MCP resource | ReadMcpResourceTool |

---

## State Definitions

| State | Phase | Purpose | Default Posture |
|-------|-------|---------|-----------------|
| `EXPLORE` | Discovery | Gather information freely | Permissive |
| `DESIGN` | Requirements → Spec | Define what to build | Permissive |
| `PLAN` | Spec → Implementation plan | Define how to build | Permissive |
| `DO` | Plan → Artifact | Execute the plan | **Restrictive** |
| `CHECK` | Artifact → Verdict | Verify correctness | Permissive |
| `DONE` | Closure | Archive and memory | Permissive |

---

## Phase-to-State Mapping (Critique A3 - BLOCKING)

Existing cycle phases must map to ActivityMatrix states:

### implementation-cycle

| Cycle Phase | ActivityMatrix State |
|-------------|---------------------|
| PLAN | PLAN |
| DO | DO |
| CHECK | CHECK |
| DONE | DONE |

### investigation-cycle

| Cycle Phase | ActivityMatrix State |
|-------------|---------------------|
| HYPOTHESIZE | DESIGN (spec-like output) |
| EXPLORE | EXPLORE |
| CONCLUDE | DONE |

### close-work-cycle

| Cycle Phase | ActivityMatrix State |
|-------------|---------------------|
| VALIDATE | CHECK |
| OBSERVE | DONE |
| ARCHIVE | DONE |
| MEMORY | DONE |

### observation-triage-cycle

| Cycle Phase | ActivityMatrix State |
|-------------|---------------------|
| SCAN | EXPLORE |
| TRIAGE | DESIGN |
| PROMOTE | DONE |

### work-creation-cycle

| Cycle Phase | ActivityMatrix State |
|-------------|---------------------|
| VERIFY | CHECK |
| POPULATE | DESIGN |
| READY | CHECK |
| CHAIN | DONE |

### Default (No Active Cycle)

When `just get-cycle` returns empty or error: State = **EXPLORE** (permissive fallback)

---

## The Activity Matrix

### Legend

| Symbol | Meaning |
|--------|---------|
| ✓ | Allowed - no restriction |
| ⚠ | Allowed with warning |
| ✗ | Blocked - returns error |
| → | Redirected to alternative |

### Matrix: File Operations

| Primitive | EXPLORE | DESIGN | PLAN | DO | CHECK | DONE |
|-----------|---------|--------|------|-----|-------|------|
| `file-read` | ✓ | ✓ | ✓ | ✓ (spec only) | ✓ | ✓ |
| `file-write` | ⚠ notes | ✓ spec | ✓ plan | ✓ artifact | ⚠ verdict | ✓ archive |
| `file-edit` | ⚠ notes | ✓ spec | ✓ plan | ✓ artifact | ⚠ verdict | ✓ archive |
| `file-search` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `content-search` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Matrix: Execution

| Primitive | EXPLORE | DESIGN | PLAN | DO | CHECK | DONE |
|-----------|---------|--------|------|-----|-------|------|
| `shell-execute` | ⚠ read-only | ⚠ | ⚠ | ✓ build | ✓ test | ⚠ |
| `shell-background` | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| `notebook-edit` | ✗ | ⚠ | ⚠ | ✓ | ✓ | ✗ |

### Matrix: Web/External

| Primitive | EXPLORE | DESIGN | PLAN | DO | CHECK | DONE |
|-----------|---------|--------|------|-----|-------|------|
| `web-fetch` | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| `web-search` | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |

### Matrix: Agent/Task

| Primitive | EXPLORE | DESIGN | PLAN | DO | CHECK | DONE |
|-----------|---------|--------|------|-----|-------|------|
| `task-spawn` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `task-track` | ✓ | ✓ | ✓ | **✓ (RECOMMENDED)** | ✓ | ✓ |
| `skill-invoke` | ✓ | ✓ | ✓ | → (see rules) | ✓ | ✓ |
| `user-query` | ✓ | ✓ | ✓ | **✗** | ✓ | ✓ |

### Matrix: Memory

| Primitive | EXPLORE | DESIGN | PLAN | DO | CHECK | DONE |
|-----------|---------|--------|------|-----|-------|------|
| `memory-search` | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| `memory-store` | ⚠ notes | ⚠ | ⚠ | ✗ | ⚠ | ✓ |
| `schema-query` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `db-query` | → verifier | → verifier | → verifier | → verifier | → verifier | → verifier |

### Matrix: Planning/Governance

| Primitive | EXPLORE | DESIGN | PLAN | DO | CHECK | DONE |
|-----------|---------|--------|------|-----|-------|------|
| `plan-enter` | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| `plan-exit` | N/A | N/A | ✓ | N/A | N/A | N/A |
| `mcp-list` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `mcp-read` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## DO Phase Restrictions (Black-Box)

**Decision 82710:** DO phase is black-box. Discovery is over, spec is frozen.

| Blocked | Reason | Error Message |
|---------|--------|---------------|
| `user-query` (AskUserQuestion) | Spec should be complete | "BLOCKED: DO phase is black-box. Spec should be complete - no user queries." |
| `memory-search` | Discovery phase is over | "BLOCKED: DO phase is black-box. Query memory during EXPLORE/DESIGN." |
| `web-fetch` | No external exploration | "BLOCKED: DO phase is black-box. Web research belongs in EXPLORE." |
| `web-search` | No external exploration | "BLOCKED: DO phase is black-box. Web research belongs in EXPLORE." |
| `file-write` to spec paths | Design is frozen | "BLOCKED: DO phase is black-box. Spec paths are frozen." |
| `file-edit` to spec paths | Design is frozen | "BLOCKED: DO phase is black-box. Spec paths are frozen." |

**Allowed in DO:**
- `file-read` (spec, existing code)
- `file-write` (artifact paths only)
- `file-edit` (artifact paths only)
- `shell-execute` (build, test commands)
- `task-spawn` (build agents)
- `task-track` (ephemeral sub-task tracking - RECOMMENDED per WORK-059)
- `schema-query` (verify structure)

---

## Governed Activity Names

When state + primitive combine, they form a named governed activity:

| State | Primitive | Governed Activity |
|-------|-----------|-------------------|
| EXPLORE | file-read | `explore-read` |
| EXPLORE | content-search | `explore-search` |
| EXPLORE | memory-search | `explore-memory` |
| EXPLORE | file-write (notes) | `capture-notes` |
| DESIGN | file-read | `requirements-read` |
| DESIGN | file-write (spec) | `spec-write` |
| DESIGN | skill-invoke (critique) | `critique-invoke` |
| PLAN | file-read | `scope-read` |
| PLAN | file-write (plan) | `plan-write` |
| PLAN | skill-invoke (critique) | `critique-invoke` |
| DO | file-read (spec) | `spec-read` |
| DO | file-write (artifact) | `artifact-write` |
| DO | file-edit (artifact) | `artifact-edit` |
| DO | shell-execute (build) | `build-execute` |
| DO | task-track | `implementation-track` |
| CHECK | file-read | `verify-read` |
| CHECK | shell-execute (test) | `test-execute` |
| CHECK | file-write (verdict) | `verdict-write` |
| DONE | memory-store | `learning-capture` |
| DONE | file-edit (archive) | `archive-update` |

---

## Redirect Behavior (Critique A6 - BLOCKING)

For matrix cells marked with `→`, the redirect behavior is:

| Redirect | Tool Affected | Deny Message |
|----------|---------------|--------------|
| `→ verifier` | db-query | "BLOCKED: Direct SQL not allowed. Use: Task(prompt='...', subagent_type='schema-verifier')" |
| `→ (see rules)` | skill-invoke in DO | See Skill Restrictions in DO below |

### Skill Restrictions in DO

In DO state, `skill-invoke` (Skill tool) is restricted:

| Skill Pattern | Allowed | Reason |
|---------------|---------|--------|
| `/validate`, `/status` | ✓ | Verification skills |
| `/critique`, `/reason` | ✗ | Design-phase skills - spec is frozen |
| `/new-*` | ✗ | Creation skills belong in DESIGN/PLAN |
| `/implement` | ✓ | Implementation continuation |
| `/close` | ✗ | Closure belongs in DONE |

Deny message: "BLOCKED: Skill '{skill}' not allowed in DO phase. Spec is frozen."

---

## Path Classification

For `file-write` and `file-edit`, the target path determines validity:

| Path Pattern | Classification | Valid In |
|--------------|----------------|----------|
| `docs/work/*/notes/*` | notes | EXPLORE |
| `docs/specs/*`, `*.spec.md` | spec | DESIGN |
| `docs/work/*/plans/*` | plan | PLAN |
| `src/*`, `lib/*`, `*.py`, `*.ts` | artifact | DO |
| `tests/*`, `*.test.*` | artifact | DO, CHECK |
| `docs/work/*/CHECK.md` | verdict | CHECK |
| `docs/work/archive/*` | archive | DONE |
| `docs/ADR/*` | spec | DESIGN |
| `docs/checkpoints/*` | archive | DONE |
| `.claude/**` | config | DESIGN, PLAN (governed paths use /new-*) |
| `README.md`, `*.md` at root | docs | EXPLORE, DESIGN |
| `*.yaml`, `*.json` | config | DESIGN, PLAN |
| **Fallback (unclassified)** | **artifact** | **Follows DO restrictions** |

**Fallback Rule (Critique A2):** Unclassified paths default to `artifact` classification. This means:
- In DO: allowed (artifact writes expected)
- In EXPLORE/DESIGN/PLAN: warning "Path unclassified, treating as artifact"
- Rationale: Fail-restrictive in non-DO phases, permissive in DO

---

## Implementation Notes

### Module Ownership (Module-First Principle)

**Owner:** `GovernanceLayer` module (`.claude/haios/modules/governance_layer.py`)

New methods to add:
- `get_activity_state()` → Returns current ActivityMatrix state
- `check_activity(primitive, state, context)` → Returns GateResult
- `map_tool_to_primitive(tool_name, tool_input)` → Returns primitive name

The matrix itself should be stored as data, not hardcoded:
- Location: `.claude/haios/config/activity_matrix.yaml`
- Format: YAML with primitive → state → rule mapping

### PreToolUse Hook Integration

The hook needs to:
1. Call `GovernanceLayer.get_activity_state()` to determine current state
2. Call `GovernanceLayer.map_tool_to_primitive(tool_name, tool_input)` for primitive
3. Call `GovernanceLayer.check_activity(primitive, state, context)` for rule lookup
4. If blocked: return deny with error message
5. If redirected: return deny with redirect guidance
6. If warning: return allow with warning
7. If allowed: return None (allow silently)

### State Detection

State detection via `GovernanceLayer.get_activity_state()`:
1. Read session state: `just get-cycle` → returns `{cycle}/{phase}/{work_id}`
2. Map cycle phase to ActivityMatrix state (see Phase-to-State Mapping section)
3. If no cycle active or error: return `EXPLORE` (permissive fallback)
4. Cache state at phase entry to avoid race conditions (Critique A10)

### State Detection Failure Handling (Critique A1)

| Failure Mode | Behavior |
|--------------|----------|
| `just get-cycle` returns empty | State = EXPLORE |
| `just get-cycle` returns malformed | State = EXPLORE + log warning |
| Phase not in mapping table | State = EXPLORE + log warning |
| Work file missing/corrupted | State = EXPLORE + log warning |

**Rationale:** Fail-permissive on state detection errors. Blocking on unknown state would halt all work.

---

## Exit Criteria

- [x] Primitive taxonomy defined (6 categories, 17 primitives)
- [x] State definitions documented (6 states)
- [x] Full matrix enumerated (17 × 6 = 102 cells)
- [x] DO phase restrictions explicit
- [x] Governed activity names defined
- [x] Path classification for write operations (with fallback rule)
- [x] Phase-to-state mapping for existing cycles (Critique A3 - RESOLVED)
- [x] Redirect behavior defined (Critique A6 - RESOLVED)
- [x] Module ownership specified (GovernanceLayer)
- [x] State detection failure handling defined
- [x] Implementation notes for PreToolUse hook

### Critique Response (Session 266)

| Blocking Assumption | Resolution |
|---------------------|------------|
| A3: Phase-to-state mapping | Added Phase-to-State Mapping section with 5 cycle mappings |
| A6: Redirect behavior | Added Redirect Behavior section with deny messages and skill restrictions |

| Non-Blocking Addressed | Resolution |
|------------------------|------------|
| A1: State detection reliability | Added failure handling table |
| A2: Path classification completeness | Added fallback rule + additional patterns |
| Module-First gap | Specified GovernanceLayer as owner |

---

## Memory Refs

Session 265 governed activities decision: 82706-82710
Session 266 design: 82745-82751 (matrix enumeration, critique response)
Session 274 task-track primitive: 82904-82914 (WORK-059 CC Task vs WorkEngine investigation)

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md
- @.claude/haios/epochs/E2_4/EPOCH.md (Decision 82706-82710)
- @.claude/hooks/hooks/pre_tool_use.py (current implementation)
- @docs/work/active/WORK-039/WORK.md (this work item)
