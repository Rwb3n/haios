---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-25
backlog_id: WORK-226
title: "MCP Operations Server Phase 4: Scaffold and Query Tools"
author: Hephaestus
lifecycle_phase: plan
session: 455
generated: 2026-02-25
last_updated: 2026-02-25T14:39:09

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-226/WORK.md"
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
# Implementation Plan: MCP Operations Server Phase 4: Scaffold and Query Tools

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Add 5 MCP tools (scaffold_checkpoint, scaffold_investigation, scaffold_adr, link_document, spawn_tree) to mcp_server.py so agents can replace all remaining `just`-recipe Bash calls with typed MCP tool invocations, completing MCP parity for CH-066.

---

## Open Decisions

<!-- No operator_decisions in WORK.md — all design choices are derivable from
     Phase 1-3 patterns and source spec interfaces. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No open decisions | — | — | All scaffold templates verified in scaffold.py TEMPLATE_CONFIG; all backends confirmed in source specs |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/haios_ops/mcp_server.py` | MODIFY | 2 |
| `tests/test_mcp_operations.py` | MODIFY | 2 |

### Consumer Files

<!-- No new modules created — all new tools are additions to existing mcp_server.py.
     No import-side updates needed; scaffold_template and _engine already imported. -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/haios_ops/mcp_server.py` | imports scaffold_template, _engine already present | 34, 52 | No change needed — backends already available |
| `.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md` | Work item table | — | UPDATE — add WORK-225 and WORK-226 rows |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_mcp_operations.py` | MODIFY | Add 10 new test functions for 5 new tools (Tests 37-46) |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files — all additions to existing mcp_server.py |
| Files to modify | 2 | mcp_server.py + test_mcp_operations.py |
| Consumer files to update | 1 | CH-066 CHAPTER.md work item table |
| Tests to write | 10 | Test Files table (2 per scaffold tool + 1 investigation error, 2 link_document, 2 spawn_tree + 1 no-children) |
| Total blast radius | 3 | mcp_server.py + test file + CHAPTER.md |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent -->

### Current State

```python
# .claude/haios/haios_ops/mcp_server.py — lines 497-563 (scaffold tools section end)
# After coldstart_orchestrator tool at line 701, before MCP Resources section

@mcp.tool()
def scaffold_plan(
    work_id: str,
    title: str,
    plan_type: str = "implementation",
) -> Dict[str, Any]:
    ...

# <--- NEW TOOLS INSERTED HERE (after scaffold_plan, before hierarchy tools) --->

# Then hierarchy tools, coldstart tool, MCP Resources
```

**Behavior:** mcp_server.py currently has scaffold_work and scaffold_plan only. Five recipe equivalents (checkpoint, investigation, adr, link, spawns) remain Bash-only.

**Problem:** Agents using checkpoint-cycle, /new-investigation, /new-adr, work-creation-cycle, and close ceremonies must fall back to Bash `just` recipes instead of using MCP tools.

### Desired State

Five new MCP tools added to `.claude/haios/haios_ops/mcp_server.py` in the Scaffold tools section after `scaffold_plan`:

```python
# .claude/haios/haios_ops/mcp_server.py — new additions after scaffold_plan()


@mcp.tool()
def scaffold_checkpoint(
    session_number: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold a checkpoint file for the current session.

    Args:
        session_number: Session number used as backlog_id (e.g., "455")
        title: Checkpoint title (e.g., "pre-compact")

    Returns:
        {"success": True, "path": "<checkpoint_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_checkpoint")
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "checkpoint",
            backlog_id=session_number,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_checkpoint failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def scaffold_investigation(
    work_id: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold an investigation document inside a work item directory.

    Args:
        work_id: Work item ID the investigation belongs to (e.g., "WORK-226")
        title: Investigation title

    Returns:
        {"success": True, "path": "<investigation_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_investigation", work_id)
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "investigation",
            backlog_id=work_id,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_investigation failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def scaffold_adr(
    adr_number: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold an Architecture Decision Record (ADR) file.

    Args:
        adr_number: ADR number used as backlog_id (e.g., "049")
        title: ADR title (e.g., "Event Sourcing for Audit Trail")

    Returns:
        {"success": True, "path": "<adr_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_adr")
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "architecture_decision_record",
            backlog_id=adr_number,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_adr failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def link_document(
    work_id: str,
    doc_type: str,
    doc_path: str,
) -> Dict[str, Any]:
    """Link a document to a work item (plan, investigation, checkpoint).

    Updates cycle_docs and documents section of WORK.md.

    Args:
        work_id: Work item ID (e.g., "WORK-226")
        doc_type: Document type: plan | investigation | checkpoint
        doc_path: Path to the document being linked

    Returns:
        {"success": True, "work_id": ..., "doc_type": ..., "doc_path": ...}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-mutate", "link_document", work_id)
    if blocked:
        return blocked
    try:
        _engine.add_document_link(work_id, doc_type, doc_path)
        return {"success": True, "work_id": work_id, "doc_type": doc_type, "doc_path": doc_path}
    except WorkNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"link_document failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def spawn_tree(
    root_id: str,
    max_depth: int = 5,
) -> Dict[str, Any]:
    """Return spawn tree for a work item as formatted ASCII art and raw dict.

    Read-only query — no mutations. Scans active and archive WORK.md files
    for spawned_by relationships.

    Args:
        root_id: Root work item ID (e.g., "WORK-220")
        max_depth: Maximum recursion depth (default: 5)

    Returns:
        {"success": True, "root_id": ..., "tree": <nested dict>, "formatted": "<ascii art>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-read", "spawn_tree", root_id)
    if blocked:
        return blocked
    try:
        tree = _engine.spawn_tree(root_id, max_depth=max_depth)
        formatted = _engine.format_tree(tree, use_ascii=True)
        return {
            "success": True,
            "root_id": root_id,
            "tree": tree,
            "formatted": formatted,
        }
    except Exception as e:
        logger.error(f"spawn_tree failed: {e}")
        return {"success": False, "error": str(e)}
```

**Behavior:** Five new `@mcp.tool()` functions available via MCP protocol. Each gates through `_check_tool_gate` and delegates to existing backends.

**Result:** Agents can replace `just checkpoint`, `just inv`, `just adr`, `just link`, `just spawns` with typed MCP tool calls.

### Tests

<!-- Write test specs BEFORE implementation code. -->

#### Test 37: scaffold_checkpoint success
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_checkpoint_returns_dict()`
- **setup:** `@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)`, `@patch("haios_ops.mcp_server.scaffold_template", return_value="/fake/docs/checkpoints/2026-02-25-01-SESSION-455-pre-compact.md")`
- **assertion:** `result == {"success": True, "path": "/fake/docs/checkpoints/2026-02-25-01-SESSION-455-pre-compact.md"}` and `mock_scaffold.assert_called_once_with("checkpoint", backlog_id="455", title="pre-compact")`

#### Test 38: scaffold_checkpoint error
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_checkpoint_error()`
- **setup:** `scaffold_template` raises `FileNotFoundError("Template not found")`
- **assertion:** `result["success"] is False` and `"Template not found" in result["error"]`

#### Test 39: scaffold_investigation success
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_investigation_returns_dict()`
- **setup:** `scaffold_template` returns `"/fake/docs/work/active/WORK-226/investigations/001-my-inv.md"`
- **assertion:** `result == {"success": True, "path": "/fake/docs/work/active/WORK-226/investigations/001-my-inv.md"}` and `mock_scaffold.assert_called_once_with("investigation", backlog_id="WORK-226", title="My Inv")`

#### Test 40: scaffold_adr success
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_adr_returns_dict()`
- **setup:** `scaffold_template` returns `"/fake/docs/ADR/ADR-049-my-adr.md"`
- **assertion:** `result == {"success": True, "path": "/fake/docs/ADR/ADR-049-my-adr.md"}` and `mock_scaffold.assert_called_once_with("architecture_decision_record", backlog_id="049", title="My ADR")`

#### Test 41: scaffold_adr error
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_adr_error()`
- **setup:** `scaffold_template` raises `ValueError("template not found")`
- **assertion:** `result["success"] is False` and `"template not found" in result["error"]`

#### Test 42: link_document success
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_link_document_returns_dict()`
- **setup:** `@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)`, `@patch("haios_ops.mcp_server._engine")` with `mock_eng.add_document_link.return_value = None`
- **assertion:** `result == {"success": True, "work_id": "WORK-226", "doc_type": "plan", "doc_path": "docs/work/active/WORK-226/plans/PLAN.md"}` and `mock_eng.add_document_link.assert_called_once_with("WORK-226", "plan", "docs/work/active/WORK-226/plans/PLAN.md")`

#### Test 43: link_document work not found
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_link_document_not_found()`
- **setup:** `mock_eng.add_document_link.side_effect = WorkNotFoundError("Work item WORK-999 not found")`
- **assertion:** `result["success"] is False` and `"WORK-999" in result["error"]`

#### Test 44: spawn_tree success
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_spawn_tree_returns_dict()`
- **setup:** `@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)`, `@patch("haios_ops.mcp_server._engine")` with `mock_eng.spawn_tree.return_value = {"WORK-220": {"WORK-221": {}, "WORK-222": {}}}` and `mock_eng.format_tree.return_value = "WORK-220\n+-- WORK-221\n+-- WORK-222"`
- **assertion:** `result["success"] is True`, `result["root_id"] == "WORK-220"`, `result["tree"] == {"WORK-220": {"WORK-221": {}, "WORK-222": {}}}`, `"WORK-221" in result["formatted"]`; `mock_eng.spawn_tree.assert_called_once_with("WORK-220", max_depth=5)`

#### Test 45: scaffold_investigation error (WORK.md missing)
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_investigation_error()`
- **setup:** `@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)`, `@patch("haios_ops.mcp_server.scaffold_template")` with `mock_scaffold.side_effect = ValueError("Work file required for template 'investigation'")`
- **assertion:** `result["success"] is False` and `"Work file required" in result["error"]`

#### Test 46: spawn_tree no children
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_spawn_tree_no_children()`
- **setup:** `@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)`, `@patch("haios_ops.mcp_server._engine")` with `mock_eng.spawn_tree.return_value = {"WORK-220": {}}` and `mock_eng.format_tree.return_value = "WORK-220 (no spawned items found)"`
- **assertion:** `result["success"] is True`, `result["tree"] == {"WORK-220": {}}`, `"no spawned items" in result["formatted"]`

### Design

#### File 1 (MODIFY): `.claude/haios/haios_ops/mcp_server.py`

**Location:** After `scaffold_plan()` function ending at approximately line 563, before the hierarchy tools comment block starting with `# ---------------------------------------------------------------------------`.

**Current Code (insertion point):**
```python
# .claude/haios/haios_ops/mcp_server.py — lines 560-570 (approximate)
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_plan failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Hierarchy tools (WORK-223)
# ---------------------------------------------------------------------------
```

**Target Code (with new tools inserted):**
```python
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_plan failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Scaffold tools (WORK-226) — Phase 4: checkpoint, investigation, adr
# ---------------------------------------------------------------------------

@mcp.tool()
def scaffold_checkpoint(
    session_number: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold a checkpoint file for the current session.

    Args:
        session_number: Session number used as backlog_id (e.g., "455")
        title: Checkpoint title (e.g., "pre-compact")

    Returns:
        {"success": True, "path": "<checkpoint_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_checkpoint")
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "checkpoint",
            backlog_id=session_number,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_checkpoint failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def scaffold_investigation(
    work_id: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold an investigation document inside a work item directory.

    Args:
        work_id: Work item ID the investigation belongs to (e.g., "WORK-226")
        title: Investigation title

    Returns:
        {"success": True, "path": "<investigation_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_investigation", work_id)
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "investigation",
            backlog_id=work_id,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_investigation failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def scaffold_adr(
    adr_number: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold an Architecture Decision Record (ADR) file.

    Args:
        adr_number: ADR number used as backlog_id (e.g., "049")
        title: ADR title (e.g., "Event Sourcing for Audit Trail")

    Returns:
        {"success": True, "path": "<adr_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_adr")
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "architecture_decision_record",
            backlog_id=adr_number,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_adr failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Document link and spawn query tools (WORK-226) — Phase 4
# ---------------------------------------------------------------------------

@mcp.tool()
def link_document(
    work_id: str,
    doc_type: str,
    doc_path: str,
) -> Dict[str, Any]:
    """Link a document to a work item (plan, investigation, checkpoint).

    Updates cycle_docs and documents section of WORK.md.

    Args:
        work_id: Work item ID (e.g., "WORK-226")
        doc_type: Document type: plan | investigation | checkpoint
        doc_path: Path to the document being linked

    Returns:
        {"success": True, "work_id": ..., "doc_type": ..., "doc_path": ...}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-mutate", "link_document", work_id)
    if blocked:
        return blocked
    try:
        _engine.add_document_link(work_id, doc_type, doc_path)
        return {"success": True, "work_id": work_id, "doc_type": doc_type, "doc_path": doc_path}
    except WorkNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"link_document failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def spawn_tree(
    root_id: str,
    max_depth: int = 5,
) -> Dict[str, Any]:
    """Return spawn tree for a work item as formatted ASCII art and raw dict.

    Read-only query — no mutations. Scans active and archive WORK.md files
    for spawned_by relationships.

    Args:
        root_id: Root work item ID (e.g., "WORK-220")
        max_depth: Maximum recursion depth (default: 5)

    Returns:
        {"success": True, "root_id": ..., "tree": <nested dict>, "formatted": "<ascii art>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-read", "spawn_tree", root_id)
    if blocked:
        return blocked
    try:
        tree = _engine.spawn_tree(root_id, max_depth=max_depth)
        formatted = _engine.format_tree(tree, use_ascii=True)
        return {
            "success": True,
            "root_id": root_id,
            "tree": tree,
            "formatted": formatted,
        }
    except Exception as e:
        logger.error(f"spawn_tree failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Hierarchy tools (WORK-223)
# ---------------------------------------------------------------------------
```

**Diff (summary):**
```diff
         return {"success": True, "path": path}
     except Exception as e:
         logger.error(f"scaffold_plan failed: {e}")
         return {"success": False, "error": str(e)}


+# ---------------------------------------------------------------------------
+# Scaffold tools (WORK-226) — Phase 4: checkpoint, investigation, adr
+# ---------------------------------------------------------------------------
+
+@mcp.tool()
+def scaffold_checkpoint(...) -> Dict[str, Any]: ...
+
+@mcp.tool()
+def scaffold_investigation(...) -> Dict[str, Any]: ...
+
+@mcp.tool()
+def scaffold_adr(...) -> Dict[str, Any]: ...
+
+# ---------------------------------------------------------------------------
+# Document link and spawn query tools (WORK-226) — Phase 4
+# ---------------------------------------------------------------------------
+
+@mcp.tool()
+def link_document(...) -> Dict[str, Any]: ...
+
+@mcp.tool()
+def spawn_tree(...) -> Dict[str, Any]: ...
+
 # ---------------------------------------------------------------------------
 # Hierarchy tools (WORK-223)
 # ---------------------------------------------------------------------------
```

#### File 2 (MODIFY): `tests/test_mcp_operations.py`

**Location:** Append new test functions after the last existing test (resource_queue_ready, ~line 606), before any file-end markers.

**Target Code (new tests block appended):**
```python
# ---------------------------------------------------------------------------
# Phase 4 tools tests (Tests 37-46) — WORK-226
# ---------------------------------------------------------------------------


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
def test_scaffold_checkpoint_returns_dict(mock_scaffold, mock_gate):
    """Test 37: scaffold_checkpoint creates checkpoint and returns typed dict."""
    from haios_ops.mcp_server import scaffold_checkpoint

    mock_scaffold.return_value = "/fake/docs/checkpoints/2026-02-25-01-SESSION-455-pre-compact.md"

    result = scaffold_checkpoint(session_number="455", title="pre-compact")

    assert result == {
        "success": True,
        "path": "/fake/docs/checkpoints/2026-02-25-01-SESSION-455-pre-compact.md",
    }
    mock_scaffold.assert_called_once_with(
        "checkpoint",
        backlog_id="455",
        title="pre-compact",
    )


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
def test_scaffold_checkpoint_error(mock_scaffold, mock_gate):
    """Test 38: scaffold_checkpoint returns error dict on exception."""
    from haios_ops.mcp_server import scaffold_checkpoint

    mock_scaffold.side_effect = FileNotFoundError("Template not found")

    result = scaffold_checkpoint(session_number="455", title="bad")

    assert result["success"] is False
    assert "Template not found" in result["error"]


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
def test_scaffold_investigation_returns_dict(mock_scaffold, mock_gate):
    """Test 39: scaffold_investigation creates investigation doc and returns typed dict."""
    from haios_ops.mcp_server import scaffold_investigation

    mock_scaffold.return_value = "/fake/docs/work/active/WORK-226/investigations/001-my-inv.md"

    result = scaffold_investigation(work_id="WORK-226", title="My Inv")

    assert result == {
        "success": True,
        "path": "/fake/docs/work/active/WORK-226/investigations/001-my-inv.md",
    }
    mock_scaffold.assert_called_once_with(
        "investigation",
        backlog_id="WORK-226",
        title="My Inv",
    )


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
def test_scaffold_adr_returns_dict(mock_scaffold, mock_gate):
    """Test 40: scaffold_adr creates ADR file and returns typed dict."""
    from haios_ops.mcp_server import scaffold_adr

    mock_scaffold.return_value = "/fake/docs/ADR/ADR-049-my-adr.md"

    result = scaffold_adr(adr_number="049", title="My ADR")

    assert result == {
        "success": True,
        "path": "/fake/docs/ADR/ADR-049-my-adr.md",
    }
    mock_scaffold.assert_called_once_with(
        "architecture_decision_record",
        backlog_id="049",
        title="My ADR",
    )


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
def test_scaffold_adr_error(mock_scaffold, mock_gate):
    """Test 41: scaffold_adr returns error dict on exception."""
    from haios_ops.mcp_server import scaffold_adr

    mock_scaffold.side_effect = ValueError("template not found")

    result = scaffold_adr(adr_number="999", title="Bad ADR")

    assert result["success"] is False
    assert "template not found" in result["error"]


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_link_document_returns_dict(mock_eng, mock_gate):
    """Test 42: link_document links doc to work item and returns typed dict."""
    from haios_ops.mcp_server import link_document

    mock_eng.add_document_link.return_value = None

    result = link_document(
        work_id="WORK-226",
        doc_type="plan",
        doc_path="docs/work/active/WORK-226/plans/PLAN.md",
    )

    assert result == {
        "success": True,
        "work_id": "WORK-226",
        "doc_type": "plan",
        "doc_path": "docs/work/active/WORK-226/plans/PLAN.md",
    }
    mock_eng.add_document_link.assert_called_once_with(
        "WORK-226", "plan", "docs/work/active/WORK-226/plans/PLAN.md"
    )


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_link_document_not_found(mock_eng, mock_gate):
    """Test 43: link_document returns error dict when work item not found."""
    from haios_ops.mcp_server import link_document
    from work_engine import WorkNotFoundError

    mock_eng.add_document_link.side_effect = WorkNotFoundError("Work item WORK-999 not found")

    result = link_document(
        work_id="WORK-999",
        doc_type="plan",
        doc_path="docs/work/active/WORK-999/plans/PLAN.md",
    )

    assert result["success"] is False
    assert "WORK-999" in result["error"]


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_spawn_tree_returns_dict(mock_eng, mock_gate):
    """Test 44: spawn_tree returns nested tree dict and formatted ASCII art."""
    from haios_ops.mcp_server import spawn_tree

    mock_eng.spawn_tree.return_value = {"WORK-220": {"WORK-221": {}, "WORK-222": {}}}
    mock_eng.format_tree.return_value = "WORK-220\n+-- WORK-221\n+-- WORK-222"

    result = spawn_tree(root_id="WORK-220")

    assert result["success"] is True
    assert result["root_id"] == "WORK-220"
    assert result["tree"] == {"WORK-220": {"WORK-221": {}, "WORK-222": {}}}
    assert "WORK-221" in result["formatted"]
    mock_eng.spawn_tree.assert_called_once_with("WORK-220", max_depth=5)
    mock_eng.format_tree.assert_called_once_with(
        {"WORK-220": {"WORK-221": {}, "WORK-222": {}}}, use_ascii=True
    )


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
def test_scaffold_investigation_error(mock_scaffold, mock_gate):
    """Test 45: scaffold_investigation returns error dict when WORK.md missing."""
    from haios_ops.mcp_server import scaffold_investigation

    mock_scaffold.side_effect = ValueError("Work file required for template 'investigation'")

    result = scaffold_investigation(work_id="WORK-999", title="Bad Inv")

    assert result["success"] is False
    assert "Work file required" in result["error"]


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_spawn_tree_no_children(mock_eng, mock_gate):
    """Test 46: spawn_tree returns tree with no children."""
    from haios_ops.mcp_server import spawn_tree

    mock_eng.spawn_tree.return_value = {"WORK-220": {}}
    mock_eng.format_tree.return_value = "WORK-220 (no spawned items found)"

    result = spawn_tree(root_id="WORK-220")

    assert result["success"] is True
    assert result["tree"] == {"WORK-220": {}}
    assert "no spawned items" in result["formatted"]
```

### Call Chain

```
MCP client call
    |
    +-> scaffold_checkpoint(session_number, title)
    |       _check_tool_gate("mcp-scaffold", ...)  -> None (allowed)
    |       scaffold_template("checkpoint", backlog_id=session_number, title=title)
    |           Returns: str path
    |
    +-> scaffold_investigation(work_id, title)
    |       _check_tool_gate("mcp-scaffold", ...)  -> None (allowed)
    |       scaffold_template("investigation", backlog_id=work_id, title=title)
    |           Routes into work dir if exists: docs/work/active/{work_id}/investigations/
    |           Returns: str path
    |
    +-> scaffold_adr(adr_number, title)
    |       _check_tool_gate("mcp-scaffold", ...)  -> None (allowed)
    |       scaffold_template("architecture_decision_record", backlog_id=adr_number, title=title)
    |           Returns: str path (docs/ADR/ADR-{adr_number}-{slug}.md)
    |
    +-> link_document(work_id, doc_type, doc_path)
    |       _check_tool_gate("mcp-mutate", ...)  -> None (allowed)
    |       _engine.add_document_link(work_id, doc_type, doc_path)
    |           Raises: WorkNotFoundError if work item not found
    |           Returns: None (side-effect only)
    |
    +-> spawn_tree(root_id, max_depth=5)
            _check_tool_gate("mcp-read", ...)  -> None (allowed)
            _engine.spawn_tree(root_id, max_depth=max_depth)
                Delegates to SpawnTree.spawn_tree()
                Returns: nested dict {root_id: {child_id: {...}}}
            _engine.format_tree(tree, use_ascii=True)
                Returns: ASCII art string
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| scaffold_checkpoint backlog_id param named `session_number` | String (not int) | scaffold_template expects str; session number IS backlog_id for checkpoint template pattern `{date}-{NN}-SESSION-{backlog_id}-{slug}.md`; matches just checkpoint recipe which passes session as positional arg |
| scaffold_adr param named `adr_number` | String (not int) | ADR uses backlog_id as number prefix in path; passing as str avoids zero-padding confusion and matches scaffold.py TEMPLATE_CONFIG pattern `{prefix}-{backlog_id}-{slug}.md` |
| link_document primitive | `mcp-mutate` | Writes to WORK.md files — mutation, not scaffold |
| spawn_tree primitive | `mcp-read` | Read-only filesystem scan, no writes — aligns with queue_ready/queue_list pattern |
| spawn_tree returns both `tree` (dict) and `formatted` (str) | Both included | Agents may need machine-parseable tree dict OR human-readable ASCII; returning both avoids a second call |
| scaffold_investigation work_file_required check | Handled by scaffold.py | `investigation` is in `WORK_FILE_REQUIRED_TEMPLATES`; scaffold_template raises ValueError if WORK.md missing; MCP tool catches and returns error dict — consistent with scaffold_plan behavior |
| No ceremony_context wrapper on scaffold_* tools | Omitted | scaffold_work and scaffold_plan in existing code have NO ceremony_context; maintaining consistency with Phase 2 pattern |
| link_document catches WorkNotFoundError separately | Yes | Explicit error type for "not found" vs generic exception — matches work_close, work_transition pattern (lines 211-215, 236-240 of mcp_server.py) |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| scaffold_checkpoint: template file missing | scaffold_template raises FileNotFoundError → caught, error dict returned | Test 38 |
| scaffold_investigation: WORK.md doesn't exist | scaffold_template raises ValueError("Work file required") → caught, error dict returned | Test 45 |
| scaffold_adr: template missing | scaffold_template raises ValueError → caught, error dict returned | Test 41 |
| link_document: work item not found | WorkNotFoundError explicitly caught → {"success": False, "error": ...} | Test 43 |
| spawn_tree: no children | SpawnTree returns `{"WORK-220": {}}` → `formatted` = `"WORK-220 (no spawned items found)"` — both returned | Test 46 |
| governance gate blocks tool | _check_tool_gate returns error dict → tool returns immediately | Gate is mocked to None in all tests; gate behavior tested in Tests 29-36 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| scaffold_investigation WORK_FILE_REQUIRED check fails silently | M | Test 39 verifies scaffold_template called with correct args; integration tests in existing test_scaffold.py cover the gate |
| spawn_tree function name collision with module-level `spawn_tree` import | H | mcp_server.py does NOT import spawn_tree directly; `_engine.spawn_tree()` delegates to SpawnTree internally — no name collision risk |
| WorkNotFoundError import path in test | M | Test 43 imports `from work_engine import WorkNotFoundError` — same pattern as top-level mcp_server.py import; must ensure conftest sys.path includes modules/ |
| scaffold_template "checkpoint" template name verification | L | TEMPLATE_CONFIG in scaffold.py line 65-69 confirms "checkpoint" key exists; verified during spec reading |
| scaffold_template "architecture_decision_record" name | L | TEMPLATE_CONFIG line 75-79 confirms key exists; verified during spec reading |
| spawn_tree `format_tree` is a `@staticmethod` on WorkEngine | M | WorkEngine.format_tree is a static method (line 1129 work_engine.py); calling `_engine.format_tree(tree, use_ascii=True)` works on instance — Python allows static method call on instance |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Append 10 new test functions (Tests 37-46) to `tests/test_mcp_operations.py` from Layer 1 Tests section. Import `WorkNotFoundError` inside test_link_document_not_found.
- **output:** 10 new test functions exist in file, all 10 fail with `ImportError` (scaffold_checkpoint etc. not yet defined)
- **verify:** `pytest tests/test_mcp_operations.py::test_scaffold_checkpoint_returns_dict tests/test_mcp_operations.py::test_scaffold_adr_returns_dict tests/test_mcp_operations.py::test_link_document_returns_dict tests/test_mcp_operations.py::test_spawn_tree_returns_dict -v 2>&1 | grep -c "FAILED\|ERROR"` equals 4

### Step 2: Add 5 New MCP Tools (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Insert 5 new `@mcp.tool()` functions into `.claude/haios/haios_ops/mcp_server.py` after `scaffold_plan()` function and before `# ---------------------------------------------------------------------------\n# Hierarchy tools (WORK-223)` comment block, exactly as specified in Layer 1 Design
- **output:** All 10 tests pass
- **verify:** `pytest tests/test_mcp_operations.py -v 2>&1 | tail -5` shows `46 passed, 0 failed` (or N passed where N >= prior count + 10)

### Step 3: Update CHAPTER.md Work Item Table
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 2 complete (all tests green)
- **action:** Add WORK-225 and WORK-226 rows to the `## Work Items` table in `.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md`
- **output:** Table has rows for WORK-225 and WORK-226
- **verify:** `grep "WORK-225\|WORK-226" .claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md` returns 2 matches

### Step 4: Full Test Suite Regression Check
- **spec_ref:** Ground Truth Verification > Tests
- **input:** Step 3 complete
- **action:** Run full pytest suite to verify no regressions introduced
- **output:** All previously passing tests still pass; 10 new tests pass
- **verify:** `pytest tests/ -v 2>&1 | tail -10` shows 0 new failures vs baseline (1571 + 10 = 1581 passed expected)

---

## Ground Truth Verification

<!-- Computable verification protocol. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_mcp_operations.py -v` | 46 passed, 0 failed (36 existing + 10 new) |
| `pytest tests/ -v 2>&1 \| tail -3` | 0 new failures vs 1571 baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| scaffold_checkpoint MCP tool added | `grep "def scaffold_checkpoint" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| scaffold_investigation MCP tool added | `grep "def scaffold_investigation" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| scaffold_adr MCP tool added | `grep "def scaffold_adr" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| link_document MCP tool added | `grep "def link_document" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| spawn_tree MCP tool added | `grep "def spawn_tree" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| All 5 tools gated with _check_tool_gate | `grep "_check_tool_gate" .claude/haios/haios_ops/mcp_server.py \| grep -c "scaffold_checkpoint\|scaffold_investigation\|scaffold_adr\|link_document\|spawn_tree"` | 5 matches |
| Tests for all 5 tools | `grep -c "def test_scaffold_checkpoint\|def test_scaffold_investigation\|def test_scaffold_adr\|def test_link_document\|def test_spawn_tree" tests/test_mcp_operations.py` | 10 matches |
| CH-066 CHAPTER.md updated | `grep "WORK-225\|WORK-226" .claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md` | 2 matches |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No stale just-recipe references in mcp_server.py | `grep "subprocess\|just checkpoint\|just inv\|just adr\|just link\|just spawns" .claude/haios/haios_ops/mcp_server.py` | 0 matches |
| scaffold_template already imported | `grep "from scaffold import scaffold_template" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| WorkNotFoundError already imported | `grep "from work_engine import.*WorkNotFoundError" .claude/haios/haios_ops/mcp_server.py` | 1 match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify — 46 passed)
- [ ] All WORK.md deliverables verified (table above — 8 deliverables)
- [ ] No stale references (Consumer Integrity table above)
- [ ] CHAPTER.md updated (Step 3 verify — 2 matches)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/haios/haios_ops/mcp_server.py` — integration target, existing tool patterns, _check_tool_gate
- `.claude/haios/lib/scaffold.py` — scaffold_template() function, TEMPLATE_CONFIG (checkpoint line 65, investigation line 52-60, architecture_decision_record line 75-79)
- `.claude/haios/modules/work_engine.py` — add_document_link() line 868, spawn_tree() line 1116, format_tree() line 1129
- `.claude/haios/modules/spawn_tree.py` — SpawnTree class, spawn_tree() returns nested dict, format_tree() returns ASCII string
- `.claude/haios/modules/cli.py` — cmd_link() line 116-125, cmd_spawn_tree() line 173-178
- `tests/test_mcp_operations.py` — existing test patterns (mock_scaffold, mock_eng, @patch decorators)
- `docs/work/active/WORK-220/WORK.md` — Phase 1 MCP server core
- `docs/work/active/WORK-223/WORK.md` — Phase 2 extended tools
- `docs/work/active/WORK-224/WORK.md` — Phase 3 governance integration

---
