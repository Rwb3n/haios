# generated: 2026-01-11
# System Auto: last updated on: 2026-01-12T00:00:30
# S25: SDK Path to Autonomy

**Status:** Vision (Epoch 4 prerequisite)
**Source:** Session 188 discovery, INV-062 findings
**Memory Refs:** 81309-81324

---

## Context

### The Enforcement Problem (INV-062)

Epoch 2.2 operates within Claude Code constraints. Investigation INV-062 found:

| Gap | Description |
|-----|-------------|
| Skill() unhookable | Claude reads markdown - no interception point |
| Stateless hooks | Fire per-tool-call, can't track session state |
| CycleRunner stateless | L4 invariant: "MUST NOT own persistent state" |
| Soft enforcement only | Warnings possible, hard blocks not possible |

**Conclusion:** Within Claude Code, hard enforcement of cycles is architecturally impossible.

---

## The Solution: Claude Agent SDK

The Claude Agent SDK (formerly Claude Code SDK) provides harness-level control that solves INV-062 gaps.

### SDK Architecture

```
┌─────────────────────────────────────────┐
│           Your Application              │
│  ┌─────────────────────────────────┐   │
│  │      Claude Agent SDK           │   │
│  │  ┌──────────┐  ┌─────────────┐  │   │
│  │  │ Hooks    │  │Custom Tools │  │   │
│  │  │(PreTool) │  │(In-Process) │  │   │
│  │  └────┬─────┘  └──────┬──────┘  │   │
│  │       │               │         │   │
│  │  ┌────▼───────────────▼─────┐   │   │
│  │  │      Harness Loop        │   │
│  │  │  READ → LLM → WRITE      │   │
│  │  └──────────────────────────┘   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Gap Resolution

| INV-062 Gap | SDK Solution |
|-------------|--------------|
| Skill() unhookable | Custom tools run in-process - fully hookable |
| Stateless hooks | Hooks access full application context |
| CycleRunner stateless | Harness owns execution loop and state |
| Soft enforcement only | PreToolUse can `deny` any action |

---

## SDK Capabilities

### 1. PreToolUse Hooks (Hard Enforcement)

```python
async def enforce_cycle(input_data, tool_use_id, context):
    """Block actions outside active cycle."""
    if session_state["active_cycle"] is None:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "No active cycle. Invoke skill first."
            }
        }
    return {}
```

### 2. Custom Tools (In-Process Execution)

```python
@tool("execute_cycle", "Execute a HAIOS cycle", {"cycle_name": str, "work_id": str})
async def execute_cycle(args):
    """Cycle execution controlled by harness, not Claude."""
    cycle_name = args["cycle_name"]
    work_id = args["work_id"]

    # Harness controls state
    session_state["active_cycle"] = cycle_name
    session_state["work_id"] = work_id

    # Execute cycle phases with gates
    result = await harness.run_cycle(cycle_name, work_id)

    # Clear state on completion
    session_state["active_cycle"] = None
    return {"content": [{"type": "text", "text": result}]}
```

### 3. Session State Tracking

```python
# Application-level state (not in Claude, not in files)
session_state = {
    "active_cycle": None,
    "current_phase": None,
    "work_id": None,
    "entered_at": None
}

# Hooks can read and enforce
async def check_cycle_state(input_data, tool_use_id, context):
    if session_state["active_cycle"] != expected_cycle:
        return deny("Wrong cycle active")
```

---

## Alignment with Epoch 4 Vision

### epoch4_vision/ Corpus Principles

| Principle | SDK Implementation |
|-----------|-------------------|
| Agents are stateless | Claude is stateless; harness owns state |
| Files are the only memory | SDK works with filesystem |
| Every file written for LLM | Custom tools can enforce file format |
| Agents write to own outbox | Harness controls write permissions |
| Parents invoke via inbox | Custom tools implement inbox/outbox |

### The Harness Pattern

```
epoch4_vision pattern:
  READ inbox → ASSEMBLE prompt → CALL LLM → PARSE → WRITE outbox

SDK implementation:
  Custom tool reads inbox → SDK calls Claude → Hook validates → Tool writes outbox
```

---

## Migration Path

### Phase 1: Epoch 2.2 (Current)
- Soft enforcement via warnings
- State in haios-status-slim.json
- Skills are markdown instructions

### Phase 2: Epoch 3 (FORESIGHT)
- Memory enhancement
- Prediction capabilities
- SDK exploration begins

### Phase 3: Epoch 4 (AUTONOMY)
- SDK-based harness runtime
- Hard enforcement via hooks
- Multi-agent orchestration
- inbox/outbox protocol

### What Carries Forward

| Epoch 2 Asset | Epoch 4 Role |
|---------------|--------------|
| Chariot modules | Harness components |
| Cycle definitions | SDK tool implementations |
| Work file schema | inbox/outbox format |
| Memory integration | Cross-agent knowledge |
| Portal system | Inter-agent references |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| SDK as bridge | Use Claude Agent SDK | Provides harness control without building from scratch |
| State ownership | Harness, not files | SDK enables application-level state |
| Enforcement level | Hard (deny) | SDK hooks can block, not just warn |
| LLM swappability | Via SDK backends | SDK supports claude-api, gpt-api, local |

---

## References

- **INV-062:** Session State Tracking investigation (gaps identified)
- **L4-implementation.md:** Epoch 4 AUTONOMY section (vision)
- **epoch4_vision/:** Architecture corpus (detailed design)
- **Memory 81309-81324:** epoch4_vision synthesis
- **Claude Agent SDK:** [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)

---

*S25 documents the technical path from Epoch 2 constraints to Epoch 4 autonomy via the Claude Agent SDK.*
