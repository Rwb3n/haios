# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:14:44
# Section 6: Configuration Surface

Generated: 2025-12-30 (Session 151)
Purpose: Document all YAML/JSON config files and their purposes
Status: COMPLETE

---

## Overview

HAIOS configuration is spread across multiple files by concern. This section documents the complete configuration surface.

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Wrong cycle names in node-cycle-bindings.yaml** | `plan-cycle` should be `plan-authoring-cycle`, `closure-cycle` should be `close-work-cycle` | Update bindings file |
| **No cross-config validation** | Config files reference skills/cycles that may not exist | Add `just validate-config` recipe |
| **SQL blocking not in toggles** | `block_sql` is hardcoded in pre_tool_use.py, not configurable | Migrate to governance-toggles.yaml |

---

## Target Architecture: Portable Plugin

```
.[claude|gemini|whatever]/haios/   ← PLUGIN SOURCE (LLM-agnostic, portable)
├── config/                        ← Canonical config (source of truth)
│   ├── cycle-definitions.yaml
│   ├── gates.yaml
│   ├── hook-handlers.yaml
│   ├── node-bindings.yaml
│   └── thresholds.yaml
├── state/                         ← Derived state (can be regenerated)
│   ├── session-registry.yaml
│   └── work-index.yaml
└── manifest.yaml                  ← Plugin metadata, version
        │
        │  Plugin installer PUSHES to LLM-native format
        ▼
.claude/                           ← LLM-SPECIFIC (Claude CLI native)
├── settings.local.json            ← Generated: hooks, permissions
├── commands/                      ← Generated: slash commands
├── skills/                        ← Generated: skill definitions
└── agents/                        ← Generated: subagent definitions
```

**Principle:** `.claude/haios/` is the SOURCE OF TRUTH. It pushes/generates to Claude CLI native format. For Gemini, it would push to Gemini's structure. The plugin is portable; the target is LLM-specific.

---

## Configuration Files

### `.claude/settings.local.json`

**Purpose:** Hook configuration, permissions, output style
**Updated by:** Manual or Claude Code CLI
**Size:** ~200 lines

```json
{
  "hooks": {
    "PreToolUse": [{ "matcher": "...", "hooks": [...] }],
    "PostToolUse": [...],
    "UserPromptSubmit": [...],
    "Stop": [...]
  },
  "permissions": {
    "allow": ["Bash(...)", "Skill(...)", "mcp__haios-memory__*"]
  },
  "outputStyle": "hephaestus"
}
```

| Section | Purpose |
|---------|---------|
| hooks | Event → handler mappings (all route to hook_dispatcher.py) |
| permissions | Pre-approved tool patterns (84 rules) |
| outputStyle | Agent persona (hephaestus = Builder) |

---

### `.claude/config/governance-toggles.yaml`

**Purpose:** Feature flags for PreToolUse governance checks
**Updated by:** Manual (operator control)

```yaml
# Current toggles (Session 133+)
block_powershell: true  # Blocks powershell.exe through Bash

# Future toggles (not yet implemented)
# block_sql: true  # Currently hardcoded in pre_tool_use.py
```

| Toggle | Effect | Reason |
|--------|--------|--------|
| `block_powershell: true` | DENY powershell, pwsh in Bash | `$_` and `$variable` get mangled |
| `block_sql` | (Hardcoded) | Must use schema-verifier subagent |

---

### `.claude/config/routing-thresholds.yaml`

**Purpose:** System health thresholds for routing-gate diversions
**Updated by:** Manual
**Schema:** INV-048

```yaml
thresholds:
  observation_pending:
    enabled: true
    max_count: 10                    # Trigger if > 10 pending
    divert_to: observation-triage-cycle
    escape_priorities: [critical]    # Skip for critical work
```

| Threshold | Trigger | Diversion |
|-----------|---------|-----------|
| `observation_pending` | >10 pending observations | observation-triage-cycle |
| `memory_stale` | (Future) >7 days | memory-refresh-cycle |
| `plan_incomplete` | (Future) >5 incomplete | plan-audit-cycle |

---

### `.claude/config/node-cycle-bindings.yaml`

**Purpose:** Maps DAG nodes to cycle skills, scaffolding, exit criteria
**Updated by:** Manual
**Source:** INV-022, E2-154, E2-155

```yaml
nodes:
  backlog:
    cycle: null
    scaffold: []
    exit_criteria: []

  discovery:
    cycle: investigation-cycle
    scaffold:
      - type: investigation
        command: '/new-investigation {id} "{title}"'
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"
    exit_criteria:
      - type: file_status
        field: status
        value: complete

  plan:
    cycle: plan-cycle
    scaffold:
      - type: plan
        command: '/new-plan {id} "{title}"'
    exit_criteria:
      - type: file_status
        field: status
        value: approved

  implement:
    cycle: implementation-cycle
    scaffold: []
    exit_criteria: []

  close:
    cycle: closure-cycle
    scaffold: []
    exit_criteria: []
```

| Node | Cycle | Scaffold On Entry |
|------|-------|-------------------|
| backlog | (none) | (none) |
| discovery | investigation-cycle | /new-investigation |
| plan | plan-cycle | /new-plan |
| implement | implementation-cycle | (none - plan exists) |
| close | closure-cycle | (none) |

---

### `.claude/config/north-star.md`

**Purpose:** L0 context - mission, purpose, non-negotiable principles
**Updated by:** Rarely (evergreen)

Contains:
- Mission: "Make the OPERATOR successful"
- Purpose: Trust Engine for AI agents
- 6 Non-Negotiable Principles (Operator Success, Evidence-Based Trust, etc.)

---

### `.claude/config/invariants.md`

**Purpose:** L1 context - patterns, anti-patterns, operational rules
**Updated by:** Rarely (evergreen)

Contains:
- Certainty Ratchet, Three Pillars, Governance Flywheel
- 6 LLM Anti-Patterns (Assume over verify, Generate over retrieve, etc.)
- Definition of Done (ADR-033)
- Context level definitions (L0-L3)

---

### `.claude/config/roadmap.md`

**Purpose:** Strategic direction, epoch definitions, milestone goals
**Updated by:** Per-epoch

Contains:
- Current position (Epoch 2, active milestones)
- Epoch definitions (E1: Foundation, E2: Governance, E3: FORESIGHT)
- Milestone definitions (M7a-M8, future M9-M12)

---

## State Files (Not Config, but Related)

| File | Purpose | Updated By |
|------|---------|------------|
| `.claude/haios-status.json` | Full workspace status (~500 lines) | `just update-status` |
| `.claude/haios-status-slim.json` | Compact status (~85 lines) | UserPromptSubmit hook |
| `.claude/haios-events.jsonl` | Event log (session, cycle, heartbeat) | Various hooks/recipes |
| `.claude/governance-events.jsonl` | Cycle phase events (E2-108) | governance_events.py |
| `.claude/pending-alerts.json` | Queued validation failures | PostToolUse hook |
| `.claude/validation.jsonl` | Template validation history | validate.py |

---

## Target Architecture (from SECTION-1B)

Future config files in `.claude/haios/config/`:

| File | Purpose |
|------|---------|
| `cycle-definitions.yaml` | All 7 cycles with phases and gates |
| `gates.yaml` | Gate check definitions |
| `hook-handlers.yaml` | Handler registry + config |

---

## Configuration Hierarchy

```
.claude/
├── settings.local.json      ← Claude Code CLI config
├── config/
│   ├── governance-toggles.yaml  ← Feature flags
│   ├── routing-thresholds.yaml  ← Health thresholds
│   ├── node-cycle-bindings.yaml ← DAG→cycle mapping
│   ├── north-star.md            ← L0 (mission)
│   ├── invariants.md            ← L1 (patterns)
│   └── roadmap.md               ← Strategic direction
└── haios/config/            ← (FUTURE) Plugin-specific config
    ├── cycle-definitions.yaml
    ├── gates.yaml
    └── hook-handlers.yaml
```

---

*Populated Session 151*
