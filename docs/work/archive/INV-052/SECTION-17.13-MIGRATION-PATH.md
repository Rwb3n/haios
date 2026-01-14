# generated: 2026-01-02
# System Auto: last updated on: 2026-01-02T20:09:12
# Section 17.13: Migration Path

Generated: 2026-01-02 (Session 156)
Purpose: Define migration steps for each boundary violation
Status: DESIGN
Resolves: G4 (Migration Path)

---

## Overview

This section defines the migration path for resolving the 4 boundary violations identified in Section 17.10. Each violation is analyzed with:
- Current code location
- Target module boundary
- Migration steps (what changes, what order)
- Backward compatibility concerns

---

## Violation 1: Hook Reads WORK.md

### Current State

**Location:** `.claude/hooks/hooks/post_tool_use.py`

**Behavior:**
1. `_scaffold_on_node_entry()` (line 715+) reads WORK.md content
2. Extracts `current_node` field from YAML frontmatter
3. Compares with edit to detect node transitions
4. Returns scaffold suggestion message

**Code Pattern:**
```python
content = path.read_text(encoding="utf-8")
node_match = re.search(r'^current_node:\s*(\w+)', content, re.MULTILINE)
new_node = node_match.group(1)
```

### Target Architecture

**Module A:** GovernanceLayer (post_tool_use.py)
**Module B:** WorkEngine (owns WORK.md)

**Target Flow:**
```
post_tool_use.py
    │ (detects edit to WORK.md)
    ▼
emit NodeEditDetected event
    │
    ▼
WorkEngine.handle_node_edit()
    │ (parses YAML, detects transition)
    ▼
emit NodeTransitioned event
    │
    ▼
GovernanceLayer.on_node_transitioned()
    │ (returns scaffold suggestion)
    ▼
Message to agent
```

### Migration Steps

**Phase M1a: Add Event Infrastructure**
1. Define `NodeEditDetected` event schema in events.yaml
2. Add event emission to post_tool_use.py (emit instead of read)
3. Add stub event handler in WorkEngine (no-op initially)

**Phase M1b: Move Logic to WorkEngine**
1. Move YAML parsing logic from hook to WorkEngine
2. WorkEngine detects `current_node` changes and emits `NodeTransitioned`
3. Keep hook's scaffold logic but subscribe to `NodeTransitioned` event

**Phase M1c: Clean Up**
1. Remove direct file reading from hook
2. Hook only reacts to events, not file content
3. Test end-to-end: edit WORK.md → event → scaffold message

### Backward Compatibility

**Risk:** Low

**During Migration:**
- Old hook logic continues to work
- New event-based flow runs in parallel
- Feature flag: `use_event_based_node_detection: true/false`

**After Migration:**
- Remove feature flag
- Remove old direct-read code path

---

## Violation 2: Skill Calls MCP Directly

### Current State

**Location:** `.claude/skills/*/SKILL.md` (7 skills reference ingester_ingest)

**Affected Skills:**
- implementation-cycle (DONE phase)
- investigation-cycle (CONCLUDE phase)
- close-work-cycle (MEMORY phase)
- checkpoint-cycle (CAPTURE phase)
- observation-triage-cycle (PROMOTE phase)
- extract-content (always)
- memory-agent (always)

**Code Pattern (in SKILL.md prompt):**
```markdown
## DONE Phase
Store learning using `mcp__haios-memory__ingester_ingest`:
- content: "Learning: ..."
- source_path: current work file
```

### Target Architecture

**Module A:** CycleRunner (executes skill phases)
**Module B:** MemoryBridge (wraps MCP tools)

**Target Flow:**
```
CycleRunner.execute_phase("DONE")
    │ (phase has memory: store)
    ▼
CycleRunner.store_learning(content, work_id)
    │
    ▼
MemoryBridge.store(content, source_path, work_id)
    │
    ▼
MemoryBridge calls MCP ingester_ingest
    │
    ▼
MemoryBridge calls WorkEngine.update_memory_refs()
```

### Migration Steps

**Phase M2a: Create MemoryBridge Interface**
1. Create `.claude/lib/memory_bridge.py` with:
   - `query(query, mode)` - wraps memory_search_with_experience
   - `store(content, source_path, work_id)` - wraps ingester_ingest + auto-link
2. Add to CycleRunner as dependency injection point

**Phase M2b: Update Cycle Definitions**
1. cycle-definitions.yaml already specifies `memory: store | query`
2. CycleRunner reads this and calls MemoryBridge at appropriate phases
3. SKILL.md prompts no longer need to reference MCP tools directly

**Phase M2c: Update Skill Prompts**
1. Change SKILL.md from:
   ```markdown
   Store learning using `mcp__haios-memory__ingester_ingest`
   ```
   To:
   ```markdown
   Mark this phase for memory storage (CycleRunner handles automatically)
   ```
2. Skills describe WHAT to store, not HOW

### Backward Compatibility

**Risk:** Medium (prompt changes affect agent behavior)

**During Migration:**
- Keep MCP tool references in SKILL.md (work as fallback)
- CycleRunner also calls MemoryBridge (primary path)
- Agent may double-store briefly (idempotent, no harm)

**After Migration:**
- Remove MCP references from SKILL.md
- Only CycleRunner calls MemoryBridge

---

## Violation 3: Coldstart Reads Work Files

### Current State

**Location:** `.claude/commands/coldstart.md`

**Behavior:**
1. Coldstart runs `just ready` to get unblocked work items
2. `just ready` internally runs Python that scans `docs/work/active/`
3. Directly reads WORK.md files to check status, blocked_by

**Code Pattern (in coldstart.md):**
```markdown
7. **Work Routing:** Run `just ready` to see unblocked work items
```

### Target Architecture

**Module A:** ContextLoader (coldstart behavior)
**Module B:** WorkEngine (owns work files)

**Target Flow:**
```
ContextLoader.initialize()
    │
    ▼
WorkEngine.get_ready_items()
    │ (scans work files internally)
    ▼
Returns list[WorkItem]
    │
    ▼
ContextLoader includes in GroundedContext
```

### Migration Steps

**Phase M3a: Formalize WorkEngine Interface**
1. Create `WorkEngine.get_ready_items() -> list[WorkItem]` method
2. Method encapsulates file scanning logic
3. `just ready` calls this method

**Phase M3b: Update ContextLoader**
1. ContextLoader calls `WorkEngine.get_ready_items()`
2. No longer depends on `just ready` output parsing
3. Gets structured WorkItem objects

**Phase M3c: Update Coldstart Command**
1. coldstart.md no longer prescribes `just ready`
2. Says "ContextLoader retrieves ready work items"
3. Agent receives GroundedContext with ready_work field

### Backward Compatibility

**Risk:** Low

**During Migration:**
- Both paths work: `just ready` and WorkEngine.get_ready_items()
- Coldstart continues using `just ready` until ContextLoader is built

**After Migration:**
- `just ready` becomes a thin wrapper over WorkEngine
- Coldstart no longer needs recipe invocation

---

## Violation 4: Status.py Reads Everything

### Current State

**Location:** `.claude/lib/status.py`

**Behavior:**
1. Scans `docs/work/active/` for work items
2. Scans `docs/checkpoints/` for session history
3. Reads hook configs, skill definitions, agent definitions
4. Aggregates into `.claude/haios-status.json`

### Target Architecture

**Status:** ACCEPTABLE (no migration needed)

**Rationale:**
1. Status is a **read-only aggregator** - it doesn't modify state
2. Cross-cutting concern: must read from all modules
3. "Single writer, multiple readers" is the design principle
4. Each module owns WRITE access; status has READ access

### Migration Decision

**No Migration Required**

Status.py is explicitly designed as a cross-cutting read-only service. It:
- Never writes to files it reads
- Produces derived state (haios-status.json) that modules can ignore
- Serves as observability layer, not control flow

---

## Migration Order

Based on dependencies and risk:

| Order | Violation | Risk | Reason |
|-------|-----------|------|--------|
| 1 | V3: Coldstart reads work | Low | Foundation for ContextLoader |
| 2 | V2: Skill calls MCP | Medium | Foundation for CycleRunner |
| 3 | V1: Hook reads WORK.md | Low | Requires event system |
| 4 | V4: Status reads all | N/A | No migration needed |

**Rationale:**
- V3 must be done during ContextLoader build (Phase 4 of implementation)
- V2 must be done during CycleRunner build (Phase 5 of implementation)
- V1 requires event infrastructure from GovernanceLayer (Phase 1)

---

## Event System Prerequisite

Violations 1-3 all benefit from an event system. Section 17.13.5 defines this:

### Event Bus Design

```
┌─────────────────────────────────────────────────────────────┐
│                        EVENT BUS                            │
│                                                             │
│  emit(event_type, payload)     subscribe(event_type, fn)   │
│         │                              │                    │
│         ▼                              ▼                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               EVENT STORE (in-memory)                │   │
│  │  [SessionStarted, NodeTransitioned, WorkClosed, ...]│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Persist to: .claude/haios-events.jsonl (already exists)  │
└─────────────────────────────────────────────────────────────┘
```

**Implementation Location:** `.claude/lib/event_bus.py`

**Interface:**
```python
class EventBus:
    def emit(self, event_type: str, payload: dict) -> None
    def subscribe(self, event_type: str, handler: Callable) -> None
    def get_history(self, event_type: str = None) -> list[Event]
```

---

## Validation Checkpoints

After each migration phase:

| Phase | Validation |
|-------|------------|
| M1 complete | Edit WORK.md → event emitted → scaffold message appears |
| M2 complete | Cycle DONE phase → MemoryBridge.store() called → concept stored |
| M3 complete | ContextLoader.initialize() → ready_work populated |

---

## Gap Resolution

**G4 Status:** DESIGNED

Migration path defined:
- [x] 4 violations analyzed with current code locations
- [x] Target architecture specified for each
- [x] Migration steps with phases
- [x] Backward compatibility concerns addressed
- [x] Migration order defined (V3 → V2 → V1)
- [x] V4 marked as acceptable (no migration)

---

*Created Session 156*
