---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-25
backlog_id: WORK-224
title: "MCP Operations Governance Integration"
author: Hephaestus
lifecycle_phase: plan
session: 453
generated: 2026-02-25
last_updated: 2026-02-25T13:01:44

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-224/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: MCP Operations Governance Integration

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Add per-tool GovernanceLayer.check_activity() enforcement to mcp_server.py so that every MCP tool call is validated against the activity matrix before executing, with mutation tools continuing to use ceremony_context (additive, not replacing), and governance gate events logged to governance-events.jsonl.

---

## Open Decisions

<!-- No operator_decisions in WORK.md frontmatter — all design choices resolved in entry critique. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| State resolution method | get_activity_state() (shells out) vs cycle_get() (direct file read) | Direct read via _get_current_state() helper | MCP server cannot shell out to `just get-cycle`; cycle_get() already reads haios-status-slim.json directly (A2 from entry critique) |
| Fail-open default when no active cycle | Block vs allow vs EXPLORE default | Fail-open as EXPLORE | Per CH-003 fail-permissive design; EXPLORE is the broadest permission state |
| check_activity + ceremony_context relationship | Replace ceremony_context / additive | Additive — both used on mutation tools | ceremony_context = outer boundary marker; check_activity = inner activity matrix gate; orthogonal concerns (A3 from entry critique) |
| activity_matrix.yaml MCP primitives | Reuse mcp-read only / add mcp-mutate group | Add 5 new MCP primitives | matrix lacks mcp-mutate, mcp-queue, mcp-scaffold, mcp-session, mcp-cascade; tool classification requires them |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/haios_ops/mcp_server.py` | MODIFY | 1 |
| `.claude/haios/config/activity_matrix.yaml` | MODIFY | 1 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_mcp_operations.py` | imports and calls mcp_server tools | 1-579 | UPDATE — add governance gate tests |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_mcp_operations.py` | UPDATE | Add 8 new governance tests (Tests 29-36) to existing 28-test file |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files — all modifications |
| Files to modify | 2 | mcp_server.py + activity_matrix.yaml |
| Test files to update | 1 | test_mcp_operations.py |
| New tests to write | 8 | Tests 29-36 (see Layer 1 Tests) |
| Total blast radius | 3 | mcp_server.py + activity_matrix.yaml + test_mcp_operations.py |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent

     MUST INCLUDE:
     1. Actual current code that will be changed (copy from source)
     2. Exact target code (not pseudocode)
     3. Function signatures with types
     4. Input/output examples with REAL system data -->

### Current State

```python
# .claude/haios/haios_ops/mcp_server.py — lines 50-53
# Module-level engine — shared across tool calls (single process lifetime)
_governance = GovernanceLayer()
_engine = WorkEngine(governance=_governance, base_path=_PROJECT_ROOT)
```

```python
# .claude/haios/haios_ops/mcp_server.py — lines 72-85 (work_get example)
@mcp.tool()
def work_get(work_id: str) -> Dict[str, Any]:
    """Get work item state by ID."""
    work = _engine.get_work(work_id)
    if work is None:
        return {"error": "not found", "work_id": work_id}
    return _work_to_dict(work)
```

```python
# .claude/haios/haios_ops/mcp_server.py — lines 88-117 (work_create example — already uses ceremony_context)
@mcp.tool()
def work_create(work_id: str, title: str, priority: str = "medium", category: str = "implementation") -> Dict[str, Any]:
    try:
        with ceremony_context("create-work"):
            path = _engine.create_work(id=work_id, title=title, priority=priority, category=category)
        return {"success": True, "path": str(path)}
    except Exception as e:
        logger.error(f"work_create failed: {e}")
        return {"success": False, "error": str(e)}
```

**Behavior:** `_governance` exists at module level but `check_activity()` is never called per-tool. All 20+ tools execute without consulting the activity matrix.

**Problem:** Agents invoking MCP tools bypass the governance activity matrix entirely. For example, a `work_create` call during EXPLORE phase is not flagged even though creating work is a mutation that should be gated.

---

### Desired State

#### Helper: `_get_current_state()` and `_check_tool_gate()`

Add two helpers immediately after the existing `_work_to_dict` helper (after line 65):

```python
# .claude/haios/haios_ops/mcp_server.py — new helpers after line 65

def _get_current_state() -> str:
    """Get current governance state from haios-status-slim.json.

    Reads directly from haios-status-slim.json (NOT get_activity_state() which
    shells out to `just get-cycle` — unavailable inside MCP server process).
    Fail-open: returns EXPLORE when no cycle is active (per CH-003).
    """
    try:
        slim_file = _PROJECT_ROOT / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return "EXPLORE"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        session_state = data.get("session_state", {})
        phase = session_state.get("current_phase")
        return phase if phase else "EXPLORE"
    except Exception:
        return "EXPLORE"


def _check_tool_gate(
    primitive: str,
    tool_name: str,
    work_id: str = "unknown",
) -> Optional[Dict[str, Any]]:
    """Check governance gate for an MCP tool invocation.

    Returns None if allowed (caller proceeds normally).
    Returns error dict if blocked (caller returns this immediately).

    Args:
        primitive: MCP primitive type (e.g., "mcp-read", "mcp-mutate")
        tool_name: Tool function name for context/logging (e.g., "work_get")
        work_id: Work item ID if available, else "unknown"
    """
    state = _get_current_state()
    context = {"tool": tool_name, "work_id": work_id}
    result = _governance.check_activity(primitive, state, context)
    # Only log non-trivial gate decisions (blocked or warned) to avoid
    # unbounded governance-events.jsonl growth from always-allowed reads.
    if not result.allowed or result.reason != "Activity allowed":
        _log_governance_gate(tool_name, primitive, state, result.allowed, result.reason)
    if not result.allowed:
        return {"success": False, "error": f"Governance gate blocked: {result.reason}"}
    return None


def _log_governance_gate(
    tool_name: str,
    primitive: str,
    state: str,
    allowed: bool,
    reason: str,
) -> None:
    """Log MCP governance gate decision to governance-events.jsonl."""
    try:
        from governance_events import _append_event
        _append_event({
            "type": "MCPGateChecked",
            "tool": tool_name,
            "primitive": primitive,
            "state": state,
            "allowed": allowed,
            "reason": reason,
        })
    except Exception:
        pass  # Fail-permissive — gate logging must not break tool execution
```

#### Modified tool pattern — read-only (work_get example)

```python
# .claude/haios/haios_ops/mcp_server.py — work_get (lines 72-85, modified)

@mcp.tool()
def work_get(work_id: str) -> Dict[str, Any]:
    """Get work item state by ID."""
    blocked = _check_tool_gate("mcp-read", "work_get", work_id)
    if blocked:
        return blocked
    work = _engine.get_work(work_id)
    if work is None:
        return {"error": "not found", "work_id": work_id}
    return _work_to_dict(work)
```

#### Modified tool pattern — mutation (work_create example, ceremony_context kept)

```python
# .claude/haios/haios_ops/mcp_server.py — work_create (lines 88-117, modified)

@mcp.tool()
def work_create(work_id: str, title: str, priority: str = "medium", category: str = "implementation") -> Dict[str, Any]:
    """Create a new work item with directory structure."""
    blocked = _check_tool_gate("mcp-mutate", "work_create", work_id)
    if blocked:
        return blocked
    try:
        with ceremony_context("create-work"):
            path = _engine.create_work(id=work_id, title=title, priority=priority, category=category)
        return {"success": True, "path": str(path)}
    except Exception as e:
        logger.error(f"work_create failed: {e}")
        return {"success": False, "error": str(e)}
```

#### Tool primitive classification (full mapping)

| Tool | Primitive | Ceremony? |
|------|-----------|-----------|
| `work_get` | `mcp-read` | No |
| `work_create` | `mcp-mutate` | Yes — ceremony_context("create-work") |
| `work_close` | `mcp-mutate` | Yes — ceremony_context("close-work") |
| `work_transition` | `mcp-mutate` | Yes — ceremony_context("transition-work") |
| `queue_ready` | `mcp-read` | No |
| `queue_list` | `mcp-read` | No |
| `queue_next` | `mcp-read` | No |
| `queue_prioritize` | `mcp-queue` | No (execute_queue_transition handles) |
| `queue_commit` | `mcp-queue` | No (execute_queue_transition handles) |
| `queue_park` | `mcp-queue` | No (execute_queue_transition handles) |
| `queue_unpark` | `mcp-queue` | No (execute_queue_transition handles) |
| `session_start` | `mcp-session` | No |
| `session_end` | `mcp-session` | No |
| `cycle_set` | `mcp-session` | No |
| `cycle_get` | `mcp-read` | No |
| `cycle_clear` | `mcp-session` | No |
| `scaffold_work` | `mcp-scaffold` | No |
| `scaffold_plan` | `mcp-scaffold` | No |
| `hierarchy_cascade` | `mcp-cascade` | No |
| `hierarchy_update_status` | `mcp-mutate` | Yes — ceremony_context("update-status") |
| `hierarchy_close_work` | `mcp-mutate` | Yes — ceremony_context("close-work") |
| `coldstart_orchestrator` | `mcp-cascade` | No |
| `resource_work_item` | `mcp-read` | No |
| `resource_queue_ready` | `mcp-read` | No |
| `resource_queue` | `mcp-read` | No |

#### activity_matrix.yaml additions

Add to `rules:` section (after `mcp-read` at line 153):

```yaml
  # MCP Operations Server primitives (WORK-224)
  mcp-mutate:
    EXPLORE: {action: warn, message: "EXPLORE phase: mutation tools should not be needed during investigation"}
    DESIGN: {action: warn, message: "DESIGN phase: mutation tools should not be needed during design"}
    PLAN: {action: allow}
    DO: {action: allow}
    CHECK: {action: warn, message: "CHECK phase: mutations should be rare — only fixes"}
    DONE: {action: allow}

  mcp-queue:
    _all_states: {action: allow}

  mcp-scaffold:
    EXPLORE: {action: warn, message: "EXPLORE phase: scaffolding new items during investigation is unusual"}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: allow}
    CHECK: {action: allow}
    DONE: {action: allow}

  mcp-session:
    _all_states: {action: allow}

  mcp-cascade:
    _all_states: {action: allow}
```

**Behavior:** Every MCP tool invocation checks the activity matrix. Read-only tools always pass. Mutation tools warn in EXPLORE/DESIGN, allow in DO/PLAN. Blocked tools return `{"success": False, "error": "Governance gate blocked: <reason>"}`. All gate decisions are logged as `MCPGateChecked` events to governance-events.jsonl.

**Result:** Governance parity with Claude Code tool-use hooks — MCP tools are governed by the same activity matrix, satisfying CH-066 exit criterion 2 (governance parity).

---

### Tests

<!-- Write test specs BEFORE implementation code.
     Each test: name, file, setup, assertion. -->

#### Test 29: _get_current_state returns EXPLORE when no slim file
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_get_current_state_no_slim_file()`
- **setup:** `patch("haios_ops.mcp_server._PROJECT_ROOT", tmp_path)` where tmp_path has no haios-status-slim.json
- **assertion:** `_get_current_state() == "EXPLORE"`

#### Test 30: _get_current_state returns phase from slim file
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_get_current_state_from_slim_file(tmp_path)`
- **setup:** Write haios-status-slim.json with `session_state.current_phase = "DO"` to tmp_path; patch `_PROJECT_ROOT`
- **assertion:** `_get_current_state() == "DO"`

#### Test 31: _check_tool_gate allows when GateResult.allowed is True
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_check_tool_gate_allows()`
- **setup:** `@patch("haios_ops.mcp_server._governance")` returning `GateResult(allowed=True, reason="Activity allowed")`; `@patch("haios_ops.mcp_server._get_current_state", return_value="DO")`
- **assertion:** `_check_tool_gate("mcp-read", "work_get") is None`

#### Test 32: _check_tool_gate blocks when GateResult.allowed is False
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_check_tool_gate_blocks()`
- **setup:** `@patch("haios_ops.mcp_server._governance")` returning `GateResult(allowed=False, reason="BLOCKED: reason")`; `@patch("haios_ops.mcp_server._get_current_state", return_value="EXPLORE")`
- **assertion:** `_check_tool_gate("mcp-mutate", "work_create") == {"success": False, "error": "Governance gate blocked: BLOCKED: reason"}`

#### Test 33: work_get calls check_activity with correct args
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_work_get_calls_check_activity()`
- **setup:** `@patch("haios_ops.mcp_server._governance")` mock; `@patch("haios_ops.mcp_server._get_current_state", return_value="PLAN")`; `@patch("haios_ops.mcp_server._engine")` returning valid work state; governance mock returns `GateResult(allowed=True, reason="Activity allowed")`
- **assertion:** `mock_governance.check_activity.assert_called_once_with("mcp-read", "PLAN", {"tool": "work_get", "work_id": "WORK-220"})`

#### Test 34: work_create blocked by governance returns error dict without calling engine
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_work_create_blocked_by_governance()`
- **setup:** `@patch("haios_ops.mcp_server._governance")` returning `GateResult(allowed=False, reason="EXPLORE phase: mutations not allowed")`; `@patch("haios_ops.mcp_server._get_current_state", return_value="EXPLORE")`; `@patch("haios_ops.mcp_server._engine")` mock
- **assertion:** result `== {"success": False, "error": "Governance gate blocked: EXPLORE phase: mutations not allowed"}`; `mock_engine.create_work.assert_not_called()`

#### Test 35: _log_governance_gate appends MCPGateChecked event
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_log_governance_gate_appends_event()`
- **setup:** `@patch("governance_events._append_event")` mock (patch at source module, not mcp_server — _append_event is imported inside function body via `from governance_events import _append_event`)
- **assertion:** `_log_governance_gate("work_get", "mcp-read", "DO", False, "BLOCKED: reason")` calls `mock_append_event` with dict containing `{"type": "MCPGateChecked", "tool": "work_get", "primitive": "mcp-read", "state": "DO", "allowed": False}`

#### Test 36: _log_governance_gate fails silently on exception
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_log_governance_gate_fails_silently()`
- **setup:** `@patch("governance_events._append_event", side_effect=RuntimeError("disk full"))` (patch at source module)
- **assertion:** `_log_governance_gate(...)` does not raise; returns None

---

### Design

#### File 1 (MODIFY): `.claude/haios/haios_ops/mcp_server.py`

**Location:** Insert new helpers after `_work_to_dict` function (after line 65). Then modify each tool handler to prepend `_check_tool_gate(...)`.

**Current Code (helpers section — lines 57-65):**
```python
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _work_to_dict(work: WorkState) -> Dict[str, Any]:
    """Convert WorkState dataclass to JSON-serializable dict."""
    d = asdict(work)
    # Path fields need str() conversion for JSON serialization
    if d.get("path") is not None:
        d["path"] = str(d["path"])
    return d
```

**Target Code (helpers section — with new additions after _work_to_dict):**
```python
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _work_to_dict(work: WorkState) -> Dict[str, Any]:
    """Convert WorkState dataclass to JSON-serializable dict."""
    d = asdict(work)
    # Path fields need str() conversion for JSON serialization
    if d.get("path") is not None:
        d["path"] = str(d["path"])
    return d


def _get_current_state() -> str:
    """Get current governance state from haios-status-slim.json.

    Reads directly from haios-status-slim.json (NOT get_activity_state() which
    shells out to `just get-cycle` — unavailable inside MCP server process).
    Fail-open: returns EXPLORE when no cycle is active (per CH-003).
    """
    try:
        slim_file = _PROJECT_ROOT / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return "EXPLORE"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        session_state = data.get("session_state", {})
        phase = session_state.get("current_phase")
        return phase if phase else "EXPLORE"
    except Exception:
        return "EXPLORE"


def _check_tool_gate(
    primitive: str,
    tool_name: str,
    work_id: str = "unknown",
) -> Optional[Dict[str, Any]]:
    """Check governance gate for an MCP tool invocation.

    Returns None if allowed (caller proceeds normally).
    Returns error dict if blocked (caller returns this immediately).

    Args:
        primitive: MCP primitive type (e.g., "mcp-read", "mcp-mutate")
        tool_name: Tool function name for context/logging (e.g., "work_get")
        work_id: Work item ID if available, else "unknown"
    """
    state = _get_current_state()
    context = {"tool": tool_name, "work_id": work_id}
    result = _governance.check_activity(primitive, state, context)
    # Only log non-trivial gate decisions (blocked or warned) to avoid
    # unbounded governance-events.jsonl growth from always-allowed reads.
    if not result.allowed or result.reason != "Activity allowed":
        _log_governance_gate(tool_name, primitive, state, result.allowed, result.reason)
    if not result.allowed:
        return {"success": False, "error": f"Governance gate blocked: {result.reason}"}
    return None


def _log_governance_gate(
    tool_name: str,
    primitive: str,
    state: str,
    allowed: bool,
    reason: str,
) -> None:
    """Log MCP governance gate decision to governance-events.jsonl."""
    try:
        from governance_events import _append_event
        _append_event({
            "type": "MCPGateChecked",
            "tool": tool_name,
            "primitive": primitive,
            "state": state,
            "allowed": allowed,
            "reason": reason,
        })
    except Exception:
        pass  # Fail-permissive — gate logging must not break tool execution
```

**Per-tool gate additions (complete list of line insertions):**

Each tool gets one `blocked = _check_tool_gate(...); if blocked: return blocked` block as the FIRST statement inside the function body.

```python
# work_get (line 82, read-only)
def work_get(work_id: str) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-read", "work_get", work_id)
    if blocked:
        return blocked
    # ... existing body unchanged

# work_create (line 106, mutation — ceremony_context kept)
def work_create(work_id: str, title: str, priority: str = "medium", category: str = "implementation") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-mutate", "work_create", work_id)
    if blocked:
        return blocked
    try:
        with ceremony_context("create-work"):
            # ... existing body unchanged

# work_close (line 121, mutation)
def work_close(work_id: str) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-mutate", "work_close", work_id)
    if blocked:
        return blocked
    try:
        with ceremony_context("close-work"):
            # ... existing body unchanged

# work_transition (line 142, mutation)
def work_transition(work_id: str, to_node: str) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-mutate", "work_transition", work_id)
    if blocked:
        return blocked
    try:
        with ceremony_context("transition-work"):
            # ... existing body unchanged

# queue_ready (line 167, read-only)
def queue_ready() -> List[Dict[str, Any]]:
    blocked = _check_tool_gate("mcp-read", "queue_ready")
    if blocked:
        return []
    # ... existing body unchanged

# queue_list (line 178, read-only)
def queue_list(queue_name: str = "default") -> List[Dict[str, Any]]:
    blocked = _check_tool_gate("mcp-read", "queue_list")
    if blocked:
        return []
    # ... existing body unchanged

# queue_next (line 192, read-only)
def queue_next(queue_name: str = "default") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-read", "queue_next")
    if blocked:
        return {"error": "governance gate blocked", "queue": queue_name}
    # ... existing body unchanged

# queue_prioritize (line 208, queue)
def queue_prioritize(work_id: str, rationale: str = "") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-queue", "queue_prioritize", work_id)
    if blocked:
        return blocked
    # ... existing body unchanged

# queue_commit (line 227, queue)
def queue_commit(work_id: str, rationale: str = "") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-queue", "queue_commit", work_id)
    if blocked:
        return blocked
    # ... existing body unchanged

# queue_park (line 246, queue)
def queue_park(work_id: str, rationale: str = "") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-queue", "queue_park", work_id)
    if blocked:
        return blocked
    # ... existing body unchanged

# queue_unpark (line 265, queue)
def queue_unpark(work_id: str, rationale: str = "") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-queue", "queue_unpark", work_id)
    if blocked:
        return blocked
    # ... existing body unchanged

# session_start (line 288, session)
def session_start(session_number: int, agent: str = "Hephaestus") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-session", "session_start")
    if blocked:
        return blocked
    # ... existing body unchanged

# session_end (line 305, session)
def session_end(session_number: int, agent: str = "Hephaestus") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-session", "session_end")
    if blocked:
        return blocked
    # ... existing body unchanged

# cycle_set (line 325, session)
def cycle_set(cycle: str, phase: str, work_id: str) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-session", "cycle_set", work_id)
    if blocked:
        return blocked
    # ... existing body unchanged

# cycle_get (line 343, read-only)
def cycle_get(project_root: Optional[Path] = None) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-read", "cycle_get")
    if blocked:
        return {"error": "governance gate blocked"}
    # ... existing body unchanged

# cycle_clear (line 367, session)
def cycle_clear() -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-session", "cycle_clear")
    if blocked:
        return blocked
    # ... existing body unchanged

# scaffold_work (line 384, scaffold)
def scaffold_work(title: str, work_id: Optional[str] = None, work_type: str = "implementation") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_work")
    if blocked:
        return blocked
    # ... existing body unchanged

# scaffold_plan (line 415, scaffold)
def scaffold_plan(work_id: str, title: str, plan_type: str = "implementation") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_plan", work_id)
    if blocked:
        return blocked
    # ... existing body unchanged

# hierarchy_cascade (line 448, cascade)
def hierarchy_cascade(work_id: str) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-cascade", "hierarchy_cascade", work_id)
    if blocked:
        return blocked
    # ... existing body unchanged

# hierarchy_update_status (line 467, mutation — ceremony_context kept)
def hierarchy_update_status(work_id: str, status: str) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-mutate", "hierarchy_update_status", work_id)
    if blocked:
        return blocked
    try:
        with ceremony_context("update-status"):
            # ... existing body unchanged

# hierarchy_close_work (line 512, mutation — ceremony_context kept)
def hierarchy_close_work(work_id: str) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-mutate", "hierarchy_close_work", work_id)
    if blocked:
        return blocked
    try:
        with ceremony_context("close-work"):
            # ... existing body unchanged

# coldstart_orchestrator (line 547, cascade)
def coldstart_orchestrator(tier: str = "auto") -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-cascade", "coldstart_orchestrator")
    if blocked:
        return blocked
    # ... existing body unchanged

# resource_work_item (line 574, read-only)
def resource_work_item(work_id: str) -> Dict[str, Any]:
    blocked = _check_tool_gate("mcp-read", "resource_work_item", work_id)
    if blocked:
        return {"error": "governance gate blocked", "work_id": work_id}
    # ... existing body unchanged

# resource_queue_ready (line 587, read-only)
def resource_queue_ready() -> List[Dict[str, Any]]:
    blocked = _check_tool_gate("mcp-read", "resource_queue_ready")
    if blocked:
        return []
    # ... existing body unchanged

# resource_queue (line 598, read-only)
def resource_queue(queue_name: str) -> List[Dict[str, Any]]:
    blocked = _check_tool_gate("mcp-read", "resource_queue")
    if blocked:
        return []
    # ... existing body unchanged
```

**Note on list-returning tools:** When a list-returning read tool is blocked, return `[]` (empty list, not error dict) because the return type annotation is `List[Dict]`. Queue read tools follow the same pattern.

#### File 2 (MODIFY): `.claude/haios/config/activity_matrix.yaml`

**Location:** Lines 149-153 (after existing `mcp-read` entry, before `skill_restrictions`)

**Current Code (lines 149-154):**
```yaml
  mcp-read:
    _all_states: {action: allow}

# =============================================================================
# Skill Restrictions (per CH-001 "Skill Restrictions in DO")
# =============================================================================
```

**Target Code:**
```yaml
  mcp-read:
    _all_states: {action: allow}

  # MCP Operations Server primitives (WORK-224)
  mcp-mutate:
    EXPLORE: {action: warn, message: "EXPLORE phase: mutation tools should not be needed during investigation"}
    DESIGN: {action: warn, message: "DESIGN phase: mutation tools should not be needed during design"}
    PLAN: {action: allow}
    DO: {action: allow}
    CHECK: {action: warn, message: "CHECK phase: mutations should be rare — only fixes"}
    DONE: {action: allow}

  mcp-queue:
    _all_states: {action: allow}

  mcp-scaffold:
    EXPLORE: {action: warn, message: "EXPLORE phase: scaffolding new items during investigation is unusual"}
    DESIGN: {action: allow}
    PLAN: {action: allow}
    DO: {action: allow}
    CHECK: {action: allow}
    DONE: {action: allow}

  mcp-session:
    _all_states: {action: allow}

  mcp-cascade:
    _all_states: {action: allow}

# =============================================================================
# Skill Restrictions (per CH-001 "Skill Restrictions in DO")
# =============================================================================
```

---

### Call Chain

```
MCP client (agent) calls tool
    |
    +-> mcp_server.tool_fn()
    |       |
    |       +-> _check_tool_gate(primitive, tool_name, work_id)
    |       |       |
    |       |       +-> _get_current_state()            # reads haios-status-slim.json
    |       |       |       Returns: str (e.g., "DO")
    |       |       |
    |       |       +-> _governance.check_activity(primitive, state, context)
    |       |       |       Returns: GateResult(allowed=bool, reason=str)
    |       |       |
    |       |       +-> _log_governance_gate(...)        # appends MCPGateChecked event
    |       |       |
    |       |       Returns: None (allowed) or {"success": False, "error": ...} (blocked)
    |       |
    |       +-- IF blocked: return error dict immediately (engine NOT called)
    |       |
    |       +-- IF mutation tool: with ceremony_context("..."): _engine.operation(...)
    |       |
    |       +-- IF read tool: _engine.operation(...)
    |       |
    |       Returns: tool result dict
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State via direct file read, not `get_activity_state()` | `_get_current_state()` reads haios-status-slim.json directly | `get_activity_state()` shells out to `just get-cycle`; MCP server is its own process — subprocess shell exec is unavailable/unreliable (A2 from entry critique) |
| Fail-open as EXPLORE on missing state | Return "EXPLORE" when slim file missing or phase is null | EXPLORE has the broadest allow posture (all reads allowed, mutations warned). Fail-permissive per CH-003 — governance degradation must not halt operations |
| ceremony_context kept on mutation tools | check_activity added INSIDE ceremony_context block boundary | ceremony_context = outer side-effect boundary marker (who did what); check_activity = inner activity matrix policy (should this happen). Additive, not redundant (A3 from entry critique) |
| `_check_tool_gate` returns None / error dict | None = allowed, dict = blocked | Caller pattern `blocked = ...; if blocked: return blocked` is idiomatic Python and avoids exception overhead |
| List-returning tools return [] on block | `return []` not `{"success": False}` | Return type is `List[Dict]` — returning a dict would violate the type contract and confuse callers expecting lists |
| New MCPGateChecked event type | New event type, not ValidationOutcome | MCPGateChecked has tool+primitive+state fields; ValidationOutcome has gate+work_id+result. Different schemas; adding new type preserves backward compat |
| mcp-mutate warns in EXPLORE/DESIGN | warn, not block | Fail-permissive starting posture; warn surfaces misuse without breaking work; can tighten to block after observing patterns |
| activity_matrix.yaml adds 5 new primitives | mcp-mutate, mcp-queue, mcp-scaffold, mcp-session, mcp-cascade | Mirrors existing structure; check_activity returns `allowed=True` for unknown primitives (fail-open), so unclassified tools already safe; explicit entries add intentional policy |
| MCPGateChecked logged only for blocked/warned | Skip logging when `result.reason == "Activity allowed"` | Always-allowed reads (mcp-read) would generate high-volume events with no signal. governance-events.jsonl has no automatic rotation. Logging only non-trivial decisions (blocked, warned, unknown-primitive) preserves audit trail without unbounded growth (critique A8) |

---

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| haios-status-slim.json missing | _get_current_state() returns "EXPLORE" | Test 29 |
| current_phase is null/None in slim file | _get_current_state() returns "EXPLORE" | Test 30 (verify null case) |
| _governance.check_activity() raises exception | Exception propagates — not caught in _check_tool_gate (governance system should not silently fail on logic errors) | No dedicated test — let standard exception handling surface bugs |
| _log_governance_gate raises exception | Caught silently — fail-permissive, logging must not break tools | Test 36 |
| List-returning tool blocked | Returns `[]` (empty list, not error dict) | Covered implicitly by governance gate tests on queue_ready et al. |
| Ceremony context + gate block | Gate runs BEFORE ceremony_context opens — blocked tools never enter ceremony | Test 34 (verify engine not called) |
| activity_matrix.yaml lacks mcp-* primitives | check_activity returns `allowed=True` with "Unknown primitive" reason (existing fail-open default) | Existing governance_layer tests cover this path |

---

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| _get_current_state() file path wrong in tests | H | cycle_get() tests (Test 16) already use `patch("haios_ops.mcp_server._PROJECT_ROOT", tmp_path)` — same pattern works for new tests |
| All 28 existing tests break because tools now call _check_tool_gate | H | Existing tests already mock `_engine` and `ceremony_context`; must ALSO mock `_governance` (or `_check_tool_gate`) — patch `_check_tool_gate` to return None for non-governance tests |
| mcp-mutate warn in EXPLORE breaks human workflows | M | warn action = allowed=True (not blocked), just logs a message; no behavior breakage |
| ceremony_context nesting error if check_activity somehow triggers ceremony | L | check_activity is a pure read of YAML config; cannot nest ceremony |
| performance: file read on every tool call | L | haios-status-slim.json is a tiny JSON file; one read per MCP call acceptable; no caching needed at this stage |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Append Tests 29-36 to `tests/test_mcp_operations.py`. Import `_get_current_state`, `_check_tool_gate`, `_log_governance_gate` from `haios_ops.mcp_server`. Import `from governance_layer import GateResult` (governance_layer is on sys.path via bootstrap). Use `@patch("haios_ops.mcp_server._PROJECT_ROOT", tmp_path)` for state tests. Use `@patch("haios_ops.mcp_server._governance")` and `GateResult` for gate tests.
- **output:** 8 new test functions appended; all 8 fail with ImportError or AttributeError (functions not yet defined)
- **verify:** `pytest tests/test_mcp_operations.py -k "test_get_current_state or test_check_tool_gate or test_log_governance_gate or test_work_get_calls or test_work_create_blocked" -v 2>&1 | grep -c "FAILED\|ERROR"` equals 8

### Step 2: Add Helpers to mcp_server.py (GREEN for helper tests)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY) — helpers section
- **input:** Step 1 complete (tests exist and fail)
- **action:** Insert `_get_current_state()`, `_check_tool_gate()`, and `_log_governance_gate()` functions into `.claude/haios/haios_ops/mcp_server.py` immediately after the `_work_to_dict` function (after line 65). Add `from governance_events import _append_event` import inside `_log_governance_gate` (already done as local import pattern). Ensure `Optional` is in typing imports (already present on line 21).
- **output:** Tests 29-32, 35, 36 pass; Tests 33-34 still fail (tools not yet modified)
- **verify:** `pytest tests/test_mcp_operations.py -k "test_get_current_state or test_check_tool_gate or test_log_governance" -v` — 6 passed, 0 failed

### Step 3: Add gate calls to all tool handlers (GREEN for all new tests)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY) — per-tool gate additions
- **input:** Step 2 complete (helpers exist and tested)
- **action:** For each of the 24 tools in mcp_server.py (work_get through resource_queue), insert `blocked = _check_tool_gate(...); if blocked: return blocked` as the first statement inside the function body. Follow the primitive classification table in Layer 1 Design. List-returning tools return `[]` on block. **ALL 28 existing tests** (Tests 1-28) must add `@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)` decorator — not just mutation tests. Rationale: without this patch, every test calls real `_get_current_state()` which reads `haios-status-slim.json` from disk, and real `_governance.check_activity()` against the real activity matrix. While fail-open design means tests would likely pass, they become impure unit tests with real filesystem dependencies. Blanket patching keeps all tests isolated. Exception: Test 1 (`test_bootstrap_adds_both_paths`) does not call any tool — no patch needed.
- **output:** All 36 tests pass; existing 28 tests continue to pass with added _check_tool_gate patch
- **verify:** `pytest tests/test_mcp_operations.py -v` — 36 passed, 0 failed

### Step 4: Update activity_matrix.yaml with MCP primitives
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 3 complete (all tests green)
- **action:** Add the 5 new primitive entries (mcp-mutate, mcp-queue, mcp-scaffold, mcp-session, mcp-cascade) to `.claude/haios/config/activity_matrix.yaml` after the existing `mcp-read` entry at line 153. Preserve YAML formatting conventions (2-space indent, consistent with existing entries).
- **output:** activity_matrix.yaml has 6 MCP primitive entries total
- **verify:** `grep "mcp-" .claude/haios/config/activity_matrix.yaml` returns 6 matches (mcp-list, mcp-read, mcp-mutate, mcp-queue, mcp-scaffold, mcp-session, mcp-cascade — note mcp-list already exists in map_tool_to_primitive, yaml has mcp-list + mcp-read already)

### Step 5: Full test suite regression check
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Step 4 complete
- **action:** Run full test suite to verify no regressions from adding gate calls to existing tools
- **output:** All 1571+ existing tests pass plus 8 new tests
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows `N passed, 0 failed` where N >= 1579

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Producer: plan-author agent
     Consumer: CHECK agent + orchestrator -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_mcp_operations.py -v` | 36 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -3` | 0 new failures (1579+ passed, 0 failed) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| check_activity() called per-tool | `grep "_check_tool_gate" .claude/haios/haios_ops/mcp_server.py \| wc -l` | 24+ matches (one per tool) |
| Ceremony contract preserved for mutation tools | `grep -A5 "work_create\|work_close\|work_transition\|hierarchy_update_status\|hierarchy_close_work" .claude/haios/haios_ops/mcp_server.py \| grep "ceremony_context"` | 5 matches |
| Governance events logged | `grep "MCPGateChecked" .claude/haios/haios_ops/mcp_server.py` | 1+ match (in _log_governance_gate) |
| Tests verify governance enforcement | `grep "test_check_tool_gate_blocks\|test_work_create_blocked_by_governance" tests/test_mcp_operations.py` | 2 matches |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No stale references to get_activity_state in mcp_server | `grep "get_activity_state" .claude/haios/haios_ops/mcp_server.py` | 0 matches |
| activity_matrix.yaml valid YAML | `python -c "import yaml; yaml.safe_load(open('.claude/haios/config/activity_matrix.yaml'))"` | No exception |
| _governance module-level instance unchanged | `grep "_governance = GovernanceLayer()" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| Existing test count preserved | `grep "^def test_" tests/test_mcp_operations.py \| wc -l` | 36 (28 original + 8 new) |

### Completion Criteria (DoD)

- [ ] All tests pass (36 in test_mcp_operations.py, 0 regressions in full suite)
- [ ] All WORK.md deliverables verified (table above)
- [ ] _check_tool_gate called as first statement in all 24 tool handlers
- [ ] activity_matrix.yaml updated with mcp-mutate, mcp-queue, mcp-scaffold, mcp-session, mcp-cascade
- [ ] MCPGateChecked events logged to governance-events.jsonl for blocked and warned invocations (non-trivial decisions only, per Key Design Decision row 9)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/work/active/WORK-220/WORK.md` — Phase 1 (deferred governance)
- `docs/work/active/WORK-223/WORK.md` — Phase 2 (prerequisite)
- `docs/work/active/WORK-218/investigations/INVESTIGATION-WORK-218.md` — F3: governance deferred finding
- `.claude/haios/modules/governance_layer.py` — check_activity API (lines 444-493), GateResult (lines 44-56), ceremony_context (lines 601-641)
- `.claude/haios/haios_ops/mcp_server.py` — integration target (611 lines)
- `.claude/haios/lib/governance_events.py` — _append_event, log_validation_outcome patterns
- `.claude/haios/config/activity_matrix.yaml` — existing primitive rules (mcp-read already at line 152)
- `tests/test_mcp_operations.py` — 28 existing tests, @patch pattern, mock_governance fixture

---
