# generated: 2026-01-02
# System Auto: last updated on: 2026-01-02T20:04:02
# Section 17.11: Config File Schemas

Generated: 2026-01-02 (Session 156)
Purpose: Consolidated specification for all `.claude/haios/config/` files
Status: DESIGN
Resolves: G5 (Config Files)

---

## Overview

This section consolidates all config file schemas into a single reference. These files define the canonical configuration for HAIOS as a portable plugin.

**Location:** `.claude/haios/config/`
**Portability:** LLM-agnostic; installer generates LLM-specific output

---

## Directory Structure

```
.claude/haios/
├── manifest.yaml              ← Plugin metadata (G6)
├── config/
│   ├── cycle-definitions.yaml ← Cycle phases, gates, memory
│   ├── gates.yaml             ← Gate check definitions
│   ├── skill-manifest.yaml    ← Skill metadata and categories
│   ├── agent-manifest.yaml    ← Agent metadata and tool restrictions
│   ├── hook-handlers.yaml     ← Handler registry + toggles
│   ├── node-bindings.yaml     ← DAG → cycle mappings
│   └── thresholds.yaml        ← Routing diversions
├── state/
│   ├── session-registry.yaml  ← Session history (derived)
│   └── work-index.yaml        ← Work item index (derived)
└── manifesto/                 ← L0-L4 immutable context
    ├── L0-telos.md
    ├── L1-principal.md
    ├── L2-intent.md
    └── L3-requirements.md
```

---

## 17.11.1 cycle-definitions.yaml

**Purpose:** Define all cycle skills with phases, gates, memory integration, and chaining behavior.

**Source:** Section 2F

**Schema:**

```yaml
# .claude/haios/config/cycle-definitions.yaml
version: "1.0"

cycles:
  <cycle-id>:
    description: string          # Human-readable purpose
    node: string | null          # DAG node binding (backlog|discovery|plan|implement|close)
    phases: Phase[]              # Ordered phase definitions
    chain: ChainConfig           # How cycle routes to next work

Phase:
  name: string                   # UPPERCASE (PLAN, DO, CHECK, etc.)
  description: string            # What happens in this phase
  exit_gates: ExitGate[]         # Gates that MUST pass before exit
  memory: "query" | "store" | null
  scaffold: ScaffoldConfig | null
  tools: string[]                # Preferred tools for this phase

ExitGate:
  type: "skill" | "subagent" | "gate"
  name: string                   # Skill/subagent/gate identifier
  timing: "pre" | "during" | "post"  # When to invoke (default: post)
  blocking: boolean              # If false, can continue on failure (default: true)
  condition: string | null       # Optional condition (e.g., ">3 files")

ScaffoldConfig:
  recipe: string                 # Just recipe name
  args: string[]                 # Recipe arguments
  when: "phase_start" | "phase_end"

ChainConfig:
  terminal: boolean              # If true, cycle ends (no routing)
  routing_strategy: "routing_gate" | "confidence_based" | "none"
  targets: string[]              # Valid target cycles
  fallback: string               # What to do if no target matches
```

**Cycle Inventory:**

| Cycle ID | Phases | Node | Terminal |
|----------|--------|------|----------|
| implementation-cycle | PLAN→DO→CHECK→DONE→CHAIN | implement | No |
| investigation-cycle | HYPOTHESIZE→EXPLORE→CONCLUDE→CHAIN | discovery | No |
| close-work-cycle | VALIDATE→OBSERVE→ARCHIVE→MEMORY→CHAIN | close | No |
| work-creation-cycle | VERIFY→POPULATE→READY→CHAIN | backlog | No |
| checkpoint-cycle | SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT | null | Yes |
| observation-triage-cycle | SCAN→TRIAGE→PROMOTE | null | Yes |
| plan-authoring-cycle | ANALYZE→AUTHOR→VALIDATE→CHAIN | plan | No |

---

## 17.11.2 gates.yaml

**Purpose:** Define gate check logic for phase transitions.

**Source:** Section 2F

**Schema:**

```yaml
# .claude/haios/config/gates.yaml
version: "1.0"

gates:
  <gate-id>:
    description: string          # Human-readable purpose
    check: string                # Expression or function call
    composite: boolean           # If true, combines multiple checks (default: false)
    checks: Check[]              # Sub-checks if composite

Check:
  name: string
  description: string
  check: string                  # Expression
  type: "expression" | "subagent"  # Default: expression
  subagent: string               # If type == subagent
  timing: "pre" | "post"         # Default: post
  blocking: boolean              # Default: true
```

**Gate Inventory:**

| Gate ID | Description | Composite |
|---------|-------------|-----------|
| work_file_exists | WORK.md exists in work directory | No |
| no_placeholders | Context/Deliverables have no `[placeholder]` text | No |
| tests_pass | pytest returns exit code 0 | No |
| why_captured | memory_refs populated in WORK.md | No |
| plan_file_exists | Plan file exists for work item | No |
| objective_complete | Full DoD check (defense in depth) | Yes |

**objective_complete Sub-checks:**

1. `deliverables_checked` - All `[ ]` are `[x]` in Deliverables
2. `no_remaining_work` - No "Remaining Work" sections with content
3. `anti_pattern_check` - Subagent validates completion claims

---

## 17.11.3 skill-manifest.yaml

**Purpose:** Skill metadata, categories, and composition rules.

**Source:** Section 10

**Schema:**

```yaml
# .claude/haios/config/skill-manifest.yaml
version: "1.0"

skill_categories:
  - cycle          # Multi-phase workflows with gates
  - bridge         # Blocking validators invoked by cycles
  - router         # Continuation selectors
  - utility        # One-shot stateless capabilities

skills:
  <skill-id>:
    category: string             # cycle | bridge | router | utility
    description: string          # Human-readable purpose
    phases: string[]             # Phase names (cycles only)
    node_binding: string | null  # DAG node (cycles only)
    invoked_by: string[]         # Parent skills (bridges/routers)
    standalone: boolean          # Can be invoked directly
    memory:
      query_at: string[]         # Phases where memory is queried
      store_at: string[]         # Phases where memory is stored
    gates:                       # Phase → gates mapping
      <phase>: string[]          # Gate/skill/subagent names
    chain:                       # Chaining behavior (cycles only)
      terminal: boolean
      routing: string            # routing_gate | confidence_based | none
```

**Skill Inventory:**

| Category | Count | Skills |
|----------|-------|--------|
| cycle | 7 | implementation, investigation, close-work, work-creation, checkpoint, observation-triage, plan-authoring |
| bridge | 3 | plan-validation, design-review-validation, dod-validation |
| router | 1 | routing-gate |
| utility | 4 | memory-agent, audit, schema-ref, extract-content |

---

## 17.11.4 agent-manifest.yaml

**Purpose:** Subagent metadata, tool restrictions, and invocation patterns.

**Source:** Section 11

**Schema:**

```yaml
# .claude/haios/config/agent-manifest.yaml
version: "1.0"

agents:
  <agent-id>:
    description: string          # Human-readable purpose
    required: boolean            # Governance-enforced invocation
    invoked_at: string           # When/where invoked (e.g., "implementation-cycle PLAN→DO")
    trigger: string | null       # Auto-trigger condition (e.g., "PreToolUse detects SQL")
    tools: string[]              # Allowed tools (MUST enforce)
    enforcement: "hard" | "soft" # hard = Task tool MUST restrict
    checks_against: string | null  # Reference doc for validation
    output_schema:               # Expected return structure
      <field>: string            # field: type
```

**Agent Inventory:**

| Agent | Required | Tools | Enforcement |
|-------|----------|-------|-------------|
| preflight-checker | Yes | Read, Glob | hard |
| schema-verifier | Yes | Read, schema_info, db_query | hard |
| validation-agent | No | Bash, Read, Glob | soft |
| investigation-agent | No | Read, Grep, Glob, WebSearch, WebFetch, memory_search | soft |
| test-runner | No | Bash, Read | soft |
| why-capturer | No | Read, ingester_ingest | soft |
| anti-pattern-checker | No | Read, Grep, Glob | soft |

---

## 17.11.5 hook-handlers.yaml

**Purpose:** Map hook events to handlers with configuration.

**Source:** Section 1B

**Schema:**

```yaml
# .claude/haios/config/hook-handlers.yaml
version: "1.0"

handlers:
  <handler-id>:
    description: string
    event: string                # PreToolUse | PostToolUse | UserPromptSubmit | Stop
    tool_filter: string | null   # Glob pattern for tool matching
    enabled: boolean
    config:                      # Handler-specific config
      <key>: <value>

# Example handlers registry
handlers:
  sql_blocking:
    description: "Block direct SQL, require schema-verifier subagent"
    event: PreToolUse
    tool_filter: "Bash*"
    enabled: true
    config:
      patterns: ["SELECT ", "INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER "]
      subagent: schema-verifier

  powershell_blocking:
    description: "Block PowerShell, require Python scripts"
    event: PreToolUse
    tool_filter: "Bash*"
    enabled: true  # Matches governance-toggles.yaml
    config:
      patterns: ["powershell", "pwsh"]

  timestamp_injection:
    description: "Update last_updated in YAML frontmatter"
    event: PostToolUse
    tool_filter: "Edit*"
    enabled: true
    config:
      field: "last_updated"
      format: "ISO8601"

  node_history_update:
    description: "Track node transitions in WORK.md"
    event: PostToolUse
    tool_filter: "Edit*"
    enabled: true
    config:
      target_file_pattern: "docs/work/active/*/WORK.md"
```

**Handler Inventory (Target: 19):**

| Event | Handler Count | Handlers |
|-------|---------------|----------|
| PreToolUse | 5 | sql_blocking, powershell_blocking, path_governance, exit_gate_check, backlog_id_unique |
| PostToolUse | 7 | timestamp_injection, node_history_update, error_capture, template_validation, artifact_refresh, cascade_trigger, memory_refs_auto_link |
| UserPromptSubmit | 4 | date_time_inject, context_percentage, slim_status_refresh, vitals_inject |
| Stop | 3 | reasoning_bank_extract, session_summary, checkpoint_reminder |

---

## 17.11.6 node-bindings.yaml

**Purpose:** Map DAG nodes to cycles, scaffolding, and exit criteria.

**Source:** Section 6

**Schema:**

```yaml
# .claude/haios/config/node-bindings.yaml
version: "1.0"

nodes:
  <node-id>:
    cycle: string | null         # Bound cycle skill
    scaffold: ScaffoldSpec[]     # Documents to create on entry
    exit_criteria: ExitCriterion[]

ScaffoldSpec:
  type: string                   # Document type (investigation, plan, etc.)
  command: string                # Slash command to invoke
  pattern: string                # File pattern created

ExitCriterion:
  type: "file_status" | "gate"
  field: string                  # For file_status: frontmatter field
  value: string                  # Expected value
  gate: string                   # For gate type: gate ID
```

**Node Inventory:**

| Node | Cycle | Scaffold | Exit |
|------|-------|----------|------|
| backlog | null | null | null |
| discovery | investigation-cycle | /new-investigation | status: complete |
| plan | plan-authoring-cycle | /new-plan | status: approved |
| implement | implementation-cycle | null | objective_complete gate |
| close | close-work-cycle | null | null |

---

## 17.11.7 thresholds.yaml

**Purpose:** System health thresholds for routing diversions.

**Source:** Section 6, INV-048

**Schema:**

```yaml
# .claude/haios/config/thresholds.yaml
version: "1.0"

thresholds:
  <threshold-id>:
    description: string
    enabled: boolean
    metric: string               # What to measure
    max_count: integer           # Trigger threshold
    divert_to: string            # Cycle to invoke if triggered
    escape_priorities: string[]  # Priorities that skip this threshold
```

**Threshold Inventory:**

| Threshold | Metric | Max | Diversion |
|-----------|--------|-----|-----------|
| observation_pending | pending observations | 10 | observation-triage-cycle |
| memory_stale | days since last synthesis | 7 | (future) memory-refresh-cycle |
| plan_incomplete | incomplete plans | 5 | (future) plan-audit-cycle |

---

## Validation Requirements

Before implementation, these config files MUST be:

1. **Schema-validated** - JSON Schema for each YAML file
2. **Cross-referenced** - Skills/agents/gates must exist
3. **Cycle-complete** - All cycles have all referenced phases
4. **Handler-mapped** - All handlers have implementations

---

## Gap Resolution

**G5 Status:** DESIGNED

All config files now have formal schemas:
- [x] cycle-definitions.yaml (Section 2F + this section)
- [x] gates.yaml (Section 2F + this section)
- [x] skill-manifest.yaml (Section 10 + this section)
- [x] agent-manifest.yaml (Section 11 + this section)
- [x] hook-handlers.yaml (Section 1B + this section)
- [x] node-bindings.yaml (Section 6 + this section)
- [x] thresholds.yaml (Section 6 + this section)

**manifest.yaml** deferred to G6 (Portable Plugin Structure).

---

*Created Session 156*
