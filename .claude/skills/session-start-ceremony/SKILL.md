---
name: session-start-ceremony
type: ceremony
description: "Initialize a new session with context loading and event logging."
category: session
input_contract:
  - field: config_path
    type: path
    required: false
    description: "Path to haios.yaml config (auto-detected if not provided)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether session started successfully"
  - field: session_number
    type: integer
    guaranteed: on_success
    description: "Assigned session number"
  - field: context_loaded
    type: list
    guaranteed: on_success
    description: "List of context files loaded"
side_effects:
  - "Log event, load context"
generated: 2026-02-09
last_updated: "2026-02-11"
---
# Session Start Ceremony

Initialize a new HAIOS session by loading configuration, context files, and logging the session start event.

## When to Use

- At the beginning of every new session
- After coldstart orchestrator completes

**Invocation:** `Skill(skill="session-start-ceremony")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `config_path` | SHOULD | Path to haios.yaml config (auto-detected if not provided) |

---

## Ceremony Steps

All steps execute within a `ceremony_context("session-start")` boundary per REQ-CEREMONY-001.

### Step 1: Read Session Number

- Read `.claude/session` file
- Parse current session number (last non-comment line as integer)
- Increment by 1 for new session
- If file doesn't exist (first session), start at 1

### Step 2: Update Session File and Status

- Write new session number to `.claude/session` (preserve header comments)
- Update `.claude/haios-status.json` with `session_delta`:
  ```json
  {"current_session": N, "prior_session": N-1}
  ```

### Step 3: Log SessionStarted Event

- Execute: `just session-start {N}`
- This invokes `governance_events.log_session_start(session, "Hephaestus")`
- Event appended to `.claude/haios/governance-events.jsonl`:
  ```json
  {"type": "SessionStarted", "session": N, "agent": "Hephaestus", "timestamp": "..."}
  ```

### Step 4: Load Configuration

- Read `.claude/haios/config/haios.yaml`
- Extract: `epoch.current`, `epoch.epoch_file`, `epoch.active_arcs`, `epoch.arcs_dir`
- Extract: `paths.*` for work item resolution

### Step 5: Load Epoch Context

- Read the epoch file at `epoch.epoch_file`
- For each arc in `epoch.active_arcs`, read `{arcs_dir}/{arc}/ARC.md`
- Note arc statuses (Complete, In Progress, Deferred)

### Step 6: Query Memory Refs from Prior Checkpoint

- Find latest checkpoint: `just checkpoint-latest`
- If checkpoint has `load_memory_refs`, query those concept IDs via `db_query`
- Load concept content for session context
- If no checkpoint exists (first session), skip gracefully

### Step 7: Report Session State

Report to operator:
```
Session {N} started.
- Epoch: {epoch.current}
- Active arcs: {list of active_arcs with statuses}
- Memory loaded: {count} concepts from prior checkpoint
- Drift warnings: {any from prior checkpoint, or "none"}
- Pending: {items from prior checkpoint pending field}
```

---

## Integration with Coldstart

The `/coldstart` command orchestrates the full context loading flow via ColdstartOrchestrator.
Within coldstart, this ceremony is invoked via `just session-start N`.

```
Flow:
  /coldstart
    -> ColdstartOrchestrator.run()  (loads identity, session, work context)
    -> just session-start N          (this ceremony: state change + event log)
    -> survey-cycle                  (work selection)
```

This ceremony formalizes the session entry boundary. The coldstart skill handles
orchestration; this ceremony handles the state change (session file update + event).

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether session started successfully |
| `session_number` | On success | Assigned session number |
| `context_loaded` | On success | List of context files loaded |

---

## Side Effects

- Log SessionStarted event to governance-events.jsonl
- Load context files into agent working memory

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- coldstart command: Current session initialization mechanism
- CH-011: CeremonyContracts
