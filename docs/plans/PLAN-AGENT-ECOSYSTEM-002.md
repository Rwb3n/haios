---
template: implementation_plan
status: draft
date: 2025-11-30
title: "Agent Ecosystem MVP Hardening"
author: Hephaestus
session: 17
backlog_id: PLAN-AGENT-ECOSYSTEM-002
generated: 2025-11-30
last_updated: 2025-11-30T23:54:59
---
# PLAN: Agent Ecosystem MVP Hardening (Session 17)

> **Context:** [Session 17 Checkpoint](../checkpoints/2025-11-30-SESSION-17-agent-ecosystem-vision.md) -> [PLAN-001](PLAN-AGENT-ECOSYSTEM-001.md) -> [Walkthrough](../walkthroughs/2025-11-30-WALKTHROUGH-agent-ecosystem-mvp.md) -> **Hardening Plan (YOU ARE HERE)**

## References

- @docs/checkpoints/2025-11-30-SESSION-17-agent-ecosystem-vision.md - Session 17 checkpoint
- @docs/walkthroughs/2025-11-30-WALKTHROUGH-agent-ecosystem-mvp.md - MVP walkthrough
- @docs/plans/PLAN-AGENT-ECOSYSTEM-001.md - Original ecosystem plan

---

## 1. Goal Description

Address gaps identified in the Agent Ecosystem MVP evaluation:
- Add missing tests (test-first methodology compliance)
- Implement missing MCP tools referenced by agents
- Update bidirectional references for document integrity

---

## 2. Gap Summary (From Evaluation)

| Gap | Severity | Status |
|-----|----------|--------|
| No tests for registry methods | MEDIUM | TO DO |
| No tests for marketplace MCP tools | MEDIUM | TO DO |
| `memory_store` tool missing | HIGH | TO DO |
| `extract_content` tool missing | HIGH | TO DO |
| Bidirectional references incomplete | LOW | TO DO |

---

## 3. Implementation Phases

### Phase 1: Test Coverage (MEDIUM priority)

**Objective:** Bring registry functionality under test coverage.

#### 1.1 Database Registry Tests (`tests/test_database.py`)

Add tests for:
```python
def test_register_agent(db_manager):
    """Verify agent registration."""
    # Insert agent card
    # Verify retrieval
    # Verify idempotent update

def test_get_agent(db_manager):
    """Verify agent retrieval by ID."""
    # Register agent
    # Get by ID
    # Verify all fields

def test_list_agents(db_manager):
    """Verify agent listing with capability filter."""
    # Register multiple agents with different capabilities
    # List all
    # List with filter
    # Verify correct filtering
```

#### 1.2 MCP Marketplace Tests (`tests/test_mcp.py` - NEW)

Add tests for:
```python
def test_marketplace_list_agents():
    """Verify marketplace_list_agents tool."""
    # Call tool
    # Verify markdown output format
    # Verify capability filtering

def test_marketplace_get_agent():
    """Verify marketplace_get_agent tool."""
    # Call with valid ID
    # Verify JSON output
    # Call with invalid ID
    # Verify error handling
```

**Deliverables:**
- [ ] 3 tests in `test_database.py`
- [ ] 2 tests in `test_mcp.py` (new file)
- [ ] All tests passing

---

### Phase 2: Missing Tool Implementation (HIGH priority)

**Objective:** Implement MCP tools referenced by Ingester agent.

#### 2.1 `memory_store` Tool

**Purpose:** Store processed content into memory database.

**Signature:**
```python
def memory_store(
    content: str,
    content_type: str,  # "episteme", "techne", "doxa"
    source_path: str,
    metadata: str = None  # JSON string
) -> str:
    """Store content in memory with classification."""
```

**Implementation Notes:**
- Wraps `database.py` insert methods
- Applies Greek Triad classification
- Returns confirmation with stored IDs

#### 2.2 `extract_content` Tool

**Question for Operator:** Should this be:
- A) A new MCP tool wrapping `extraction.py`?
- B) Reuse of existing `extraction.py` via direct import?
- C) A Claude Code skill instead of MCP tool?

**Proposed Signature (Option A):**
```python
def extract_content(
    file_path: str,
    extraction_mode: str = "full"  # "full", "entities_only", "concepts_only"
) -> str:
    """Extract entities and concepts from a file."""
```

**Deliverables:**
- [ ] `memory_store` tool in `mcp_server.py`
- [ ] `extract_content` tool (pending decision)
- [ ] Tests for new tools

---

### Phase 3: Documentation Integrity (LOW priority)

**Objective:** Complete bidirectional references.

#### 3.1 Update Session 17 Checkpoint

Add link to walkthrough:
```markdown
## References
- [Walkthrough](../walkthroughs/2025-11-30-WALKTHROUGH-agent-ecosystem-mvp.md)
```

#### 3.2 Update Epistemic State

Add Session 17 implementation status.

**Deliverables:**
- [ ] Checkpoint updated with walkthrough link
- [ ] Epistemic state updated

---

## 4. Implementation Order

```
Phase 1.1 (Database Tests)
    │
    ▼
Phase 1.2 (MCP Tests)
    │
    ▼
Phase 2.1 (memory_store tool) ← Requires operator decision on scope
    │
    ▼
Phase 2.2 (extract_content tool) ← Requires operator decision (A/B/C)
    │
    ▼
Phase 3 (Documentation)
```

**Rationale:** Tests first ensures we don't break existing functionality while adding new tools.

---

## 5. Questions Requiring Operator Decision

### Q1: `extract_content` Implementation
> Should `extract_content` be:
> - **A)** New MCP tool wrapping `extraction.py`
> - **B)** Direct import (no MCP wrapper needed)
> - **C)** Claude Code skill instead

### Q2: Test File Organization
> Should MCP tests go in:
> - **A)** New file `test_mcp.py`
> - **B)** Existing `test_integration.py`

### Q3: Phase Priority
> Which phase should be executed first:
> - **A)** Phase 1 (Tests) - Methodology compliance
> - **B)** Phase 2 (Tools) - Functional completeness

---

## 6. Success Criteria

| Criterion | Metric |
|-----------|--------|
| Test coverage for registry | 3 passing tests |
| Test coverage for marketplace | 2 passing tests |
| `memory_store` operational | Tool callable via MCP |
| `extract_content` operational | Tool callable (per decision) |
| Documentation complete | All bidirectional refs present |

---

## 7. Verification Plan

### Automated
```bash
pytest tests/test_database.py -k "registry or agent" -v
pytest tests/test_mcp.py -v  # If new file created
```

### Manual
1. Call `memory_store` via MCP client
2. Call `extract_content` via MCP client (if applicable)
3. Verify walkthrough link works from checkpoint

---

**Status:** COMPLETE
**Date:** 2025-11-30
**Predecessor:** PLAN-AGENT-ECOSYSTEM-001
**Session:** 17
