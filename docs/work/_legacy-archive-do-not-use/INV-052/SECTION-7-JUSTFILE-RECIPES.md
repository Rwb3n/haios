# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:11:18
# Section 7: Justfile Recipes

Generated: 2025-12-30 (Session 151)
Purpose: Document execution layer - how commands actually run
Status: COMPLETE

---

## Overview

Justfile is the execution layer. **Pattern: "Slash commands are prompts, just recipes are execution."**

**Location:** `justfile` (~300 lines)
**Invocation:** `Bash("just <recipe>")`

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Deprecated haios_etl path** | `just synthesis` uses `haios_etl/cli.py` which is deprecated | Migrate to `.claude/lib/synthesis.py` |
| **Composite recipe chains implicit** | `just close-work` chains to cascade → update-status but failure breaks chain | Define explicit recipe-chains.yaml |
| **No transaction semantics** | Chain failure leaves partial state | Add rollback or checkpoint mechanism |

---

## Target Architecture: Recipe Chains

```yaml
# .claude/haios/config/recipe-chains.yaml
chains:
  close-work:
    steps:
      - recipe: update-work-status
        args: ["{{id}}", "complete"]
        rollback: update-work-status {{id}} active
      - recipe: move-to-archive
        args: ["{{id}}"]
        rollback: move-to-active {{id}}
      - recipe: cascade
        args: ["{{id}}", "complete"]
      - recipe: update-status
    on_failure: rollback_all

  session-complete:
    steps:
      - recipe: scaffold
        args: ["checkpoint", "{{session}}", "{{title}}"]
      - recipe: commit-session
        args: ["{{session}}", "{{title}}"]
      - recipe: session-end
        args: ["{{session}}"]
    on_failure: warn  # Non-critical
```

---

## Recipe Categories

### 1. Governance Recipes

| Recipe | Purpose | Implementation |
|--------|---------|----------------|
| `just validate <file>` | Validate markdown against templates | `.claude/lib/validate.py` |
| `just scaffold <type> <id> <title>` | Create document from template | `.claude/lib/scaffold.py` |
| `just plan <id> <title>` | Alias: scaffold implementation_plan | |
| `just inv <id> <title>` | Alias: scaffold investigation | |
| `just adr <id> <title>` | Alias: scaffold architecture_decision_record | |
| `just work <id> <title>` | Alias: scaffold work_item | |
| `just node <id> <node>` | Move work item to DAG node | `.claude/lib/work_item.py` |
| `just link <id> <type> <path>` | Link document to work item | `.claude/lib/work_item.py` |
| `just link-spawn <parent> <ms> <ids>` | Link spawned items to parent | `.claude/lib/work_item.py` |
| `just close-work <id>` | Atomic close + archive + cascade | `.claude/lib/work_item.py` |
| `just validate-observations <id>` | Check observation capture gate | `.claude/lib/observations.py` |
| `just scaffold-observations <id>` | Create observations.md | `.claude/lib/observations.py` |
| `just scan-observations` | Find uncaptured observations | `.claude/lib/observations.py` |
| `just triage-observations` | Scan archived for untriaged | `.claude/lib/observations.py` |
| `just governance-metrics` | Show cycle phase metrics | `.claude/lib/governance_events.py` |

### 2. Status Recipes

| Recipe | Purpose | Writes To |
|--------|---------|-----------|
| `just update-status` | Full + slim status | haios-status*.json |
| `just update-status-dry` | Preview without write | stdout |
| `just update-status-slim` | Slim only | haios-status-slim.json |
| `just cascade <id> <status>` | Propagate status change | dependent items |
| `just backfill <id>` | Backfill work item from backlog | WORK.md |
| `just backfill-all` | Backfill all work items | docs/work/active/ |

### 3. ETL Recipes

| Recipe | Purpose | Implementation |
|--------|---------|----------------|
| `just status` | Show ETL pipeline status | `haios_etl.cli status` |
| `just synthesis` | Run memory synthesis | `haios_etl.cli synthesis run` |
| `just synthesis-status` | Show synthesis stats | `haios_etl.cli synthesis stats` |
| `just synthesis-full` | Full overnight run | `--concept-sample 0 --max-bridges 500` |
| `just process` | Run full ETL | `haios_etl.cli process` |
| `just ingest <path>` | Ingest file to memory | `haios_etl.cli ingest` |
| `just ingest-r <path>` | Ingest directory recursively | `haios_etl.cli ingest -r` |
| `just embeddings-backfill` | Backfill synthesis embeddings | `scripts/backfill_synthesis_embeddings.py` |
| `just embeddings-generate` | Generate missing embeddings | `scripts/generate_embeddings.py` |

### 4. Session Recipes

| Recipe | Purpose | Writes To |
|--------|---------|-----------|
| `just session-start <N>` | Log session start | haios-events.jsonl |
| `just session-end <N>` | Log session end | haios-events.jsonl |
| `just checkpoint-latest` | Get most recent checkpoint | stdout |
| `just commit-session <N> <title>` | Git commit session | git |
| `just commit-close <id>` | Git commit closure | git |

### 5. Event Recipes

| Recipe | Purpose | Reads From |
|--------|---------|------------|
| `just events` | Show last 20 events | haios-events.jsonl |
| `just events-since <date>` | Events since date | haios-events.jsonl |
| `just events-stats` | Event counts by type | haios-events.jsonl |
| `just cycle-events` | Last 10 cycle transitions | haios-events.jsonl |
| `just events-clear` | Clear event log | haios-events.jsonl |

### 6. Plan Tree Recipes

| Recipe | Purpose |
|--------|---------|
| `just tree` | Show milestone progress |
| `just tree-current` | Show active milestone only |
| `just ready` | Show unblocked work items |
| `just spawns <id>` | Show spawn tree for ID |

### 7. Audit Recipes

| Recipe | Purpose |
|--------|---------|
| `just audit-sync` | Find sync issues (INV active, work archived) |
| `just audit-gaps` | Find gaps (plan complete, work active) |
| `just audit-stale` | Find stale investigations (>10 sessions) |

### 8. Testing Recipes

| Recipe | Purpose |
|--------|---------|
| `just test` | Run all tests |
| `just test-cov` | Tests with coverage |
| `just test-file <file>` | Run specific test file |

### 9. Utility Recipes

| Recipe | Purpose |
|--------|---------|
| `just git-status` | Show git status |
| `just git-log` | Show recent commits |
| `just health` | Tests + git status |
| `just memory-stats` | Database stats |
| `just heartbeat` | Hourly rhythm (synthesis + status) |
| `just stage-governance` | Stage all governance files |

---

## Recipe → Python Module Mapping

```
Justfile Recipe              → Python Module
──────────────────────────────────────────────
just validate               → .claude/lib/validate.py
just scaffold               → .claude/lib/scaffold.py
just update-status          → .claude/lib/status.py
just cascade                → .claude/lib/cascade.py
just close-work             → .claude/lib/work_item.py
just node/link              → .claude/lib/work_item.py
just *-observations         → .claude/lib/observations.py
just governance-metrics     → .claude/lib/governance_events.py
just backfill               → .claude/lib/backfill.py
just audit-*                → .claude/lib/audit.py
just spawns                 → .claude/lib/spawn.py
just tree/ready             → scripts/plan_tree.py
just synthesis/*            → haios_etl/cli.py (DEPRECATED path)
```

---

## Recipe Design Patterns

### Pattern 1: Inline Python
```just
validate file:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); from validate import validate_template; ..."
```

### Pattern 2: Module CLI
```just
synthesis:
    python -m haios_etl.cli synthesis run
```

### Pattern 3: Script
```just
tree:
    python scripts/plan_tree.py
```

### Pattern 4: Composite (Recipe Chain)
```just
close-work id:
    python -c "..."  # Update status + archive
    just cascade {{id}} complete
    just update-status
```

---

## Key Execution Flows

### Session Lifecycle
```
/coldstart (prompt)
    ↓
just session-start N (recipe)
    ↓
[session work]
    ↓
checkpoint-cycle (skill)
    ↓
just scaffold checkpoint N "title" (recipe)
    ↓
just commit-session N "title" (recipe)
    ↓
just session-end N (recipe)
```

### Work Item Closure
```
/close <id> (prompt)
    ↓
close-work-cycle (skill)
    ↓
just validate-observations <id> (recipe)
    ↓
just close-work <id> (recipe)
    ↓
just cascade <id> complete (recipe)
    ↓
just update-status (recipe)
```

---

*Populated Session 151*
