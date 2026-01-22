---
template: implementation_plan
status: approved
date: 2026-01-22
backlog_id: WORK-008
title: ContextLoader Identity Integration
author: Hephaestus
lifecycle_phase: plan
session: 226
version: '1.5'
generated: 2026-01-22
last_updated: '2026-01-22T19:58:38'
---
# Implementation Plan: ContextLoader Identity Integration

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4) -->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Queried memory - found 82291, 80654, 82206 (coldstart integration context) |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Wire IdentityLoader into ContextLoader so that `load_context()` returns extracted identity essence (~35 lines) instead of full manifesto files (1137 lines), completing the first runtime consumer integration for the loader infrastructure.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/haios/modules/context_loader.py` |
| Lines of code affected | ~30 | Add import, new field, replace 5 file reads with 1 loader call |
| New files to create | 0 | All infrastructure exists |
| Tests to write | 3 | Integration tests for identity loading |
| Dependencies | 1 | identity_loader.py (WORK-007 complete) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single module, clear interface |
| Risk of regression | Low | GroundedContext fields additive, existing fields unchanged |
| External dependencies | Low | identity_loader.py already tested |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add import + field | 10 min | High |
| Modify load_context() | 15 min | High |
| Tests | 15 min | High |
| **Total** | ~40 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/context_loader.py:108-119
ctx = GroundedContext(
    session_number=session,
    prior_session=prior,
    l0_telos=self._read_manifesto_file("L0-telos.md"),       # 101 lines
    l1_principal=self._read_manifesto_file("L1-principal.md"),   # 147 lines
    l2_intent=self._read_manifesto_file("L2-intent.md"),         # 114 lines
    l3_requirements=self._read_manifesto_file("L3-requirements.md"),  # 192 lines
    l4_implementation=self._read_manifesto_file("L4-implementation.md"),  # 583 lines
    checkpoint_summary=self._get_latest_checkpoint(),
    strategies=self._get_strategies(trigger),
    ready_work=self._get_ready_work(),
)
```

**Behavior:** Reads ALL content from 5 manifesto files (1137 lines total)

**Result:** Agent context bloated with full file contents when only ~35 lines of identity essence needed

### Desired State

```python
# .claude/haios/modules/context_loader.py - after integration
ctx = GroundedContext(
    session_number=session,
    prior_session=prior,
    identity_context=self._load_identity(),  # ~35 lines via IdentityLoader
    l0_telos="",  # DEPRECATED: now in identity_context
    l1_principal="",  # DEPRECATED: now in identity_context
    l2_intent=self._read_manifesto_file("L2-intent.md"),  # Keep: meta-level intent
    l3_requirements="",  # DEPRECATED: now in identity_context
    l4_implementation=self._read_manifesto_file("L4-implementation.md"),  # Keep: technical specs
    checkpoint_summary=self._get_latest_checkpoint(),
    strategies=self._get_strategies(trigger),
    ready_work=self._get_ready_work(),
)
```

**Behavior:** Uses IdentityLoader to extract only essential content via extraction DSL

**Result:** ~35 lines of focused identity context available via `identity_context` field

---

## Tests First (TDD)

### Test 1: Identity Context Field Exists
```python
def test_grounded_context_has_identity_field():
    """GroundedContext has identity_context field."""
    ctx = GroundedContext(session_number=1)
    assert hasattr(ctx, 'identity_context')
```

### Test 2: Load Context Returns Identity
```python
def test_load_context_includes_identity():
    """load_context() populates identity_context."""
    loader = ContextLoader()
    ctx = loader.load_context()
    assert ctx.identity_context is not None
    assert len(ctx.identity_context) > 0
    assert "Mission" in ctx.identity_context or "IDENTITY" in ctx.identity_context
```

### Test 3: Identity Content Is Compact
```python
def test_identity_context_is_compact():
    """identity_context < 100 lines (vs 1137 raw)."""
    loader = ContextLoader()
    ctx = loader.load_context()
    line_count = len(ctx.identity_context.strip().split('\n'))
    assert line_count < 100, f"identity_context too long: {line_count} lines"
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/modules/context_loader.py`

**Change 1: Add import (after line 19)**

```python
# Add after existing imports
import sys

# Import IdentityLoader from sibling lib/ directory
_lib_path = str(Path(__file__).parent.parent / "lib")
if _lib_path not in sys.path:
    sys.path.insert(0, _lib_path)

from identity_loader import IdentityLoader
```

**Change 2: Add field to GroundedContext (line 25)**

```python
@dataclass
class GroundedContext:
    """Result of context loading - L0-L4 grounding."""

    session_number: int
    prior_session: Optional[int] = None
    identity_context: str = ""   # EXTRACTED: Mission, principles, constraints (~35 lines)
    l0_telos: str = ""           # WHY - DEPRECATED: use identity_context
    l1_principal: str = ""       # WHO - DEPRECATED: use identity_context
    l2_intent: str = ""          # WHAT - Goals, trade-offs
    l3_requirements: str = ""    # HOW - DEPRECATED: use identity_context
    l4_implementation: str = ""  # WHAT to build - Architecture
    checkpoint_summary: str = ""
    strategies: List[Dict[str, Any]] = field(default_factory=list)
    ready_work: List[str] = field(default_factory=list)
```

**Change 3: Add helper method (after _read_manifesto_file)**

```python
def _load_identity(self) -> str:
    """Load identity context via IdentityLoader."""
    try:
        loader = IdentityLoader()
        return loader.load()
    except Exception as e:
        logger.warning(f"Identity loading failed, falling back to empty: {e}")
        return ""
```

**Change 4: Modify load_context() (line 108)**

```python
ctx = GroundedContext(
    session_number=session,
    prior_session=prior,
    identity_context=self._load_identity(),  # NEW: Extracted essence (~35 lines)
    l0_telos="",  # DEPRECATED: now in identity_context
    l1_principal="",  # DEPRECATED: now in identity_context
    l2_intent=self._read_manifesto_file("L2-intent.md"),  # Keep: meta-level intent
    l3_requirements="",  # DEPRECATED: now in identity_context
    l4_implementation=self._read_manifesto_file("L4-implementation.md"),  # Keep: specs
    checkpoint_summary=self._get_latest_checkpoint(),
    strategies=self._get_strategies(trigger),
    ready_work=self._get_ready_work(),
)
```

### Call Chain Context

```
Programmatic consumer (just recipe, module)
    |
    +-> ContextLoader.load_context()
    |       |
    |       +-> self._load_identity()     # NEW
    |       |       |
    |       |       +-> IdentityLoader().load()
    |       |               Returns: ~35 lines identity string
    |       |
    |       +-> Returns: GroundedContext with identity_context
    |
    +-> Consumer receives context
```

### Function/Component Signatures

```python
def _load_identity(self) -> str:
    """
    Load identity context via IdentityLoader.

    Returns:
        Formatted string ~35 lines with mission, principles, constraints, epoch.
        Empty string on error (graceful degradation).
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Add field vs replace | Add `identity_context`, deprecate L0/L1/L3 | Backward compat - existing consumers won't break |
| Keep L2/L4 | L2-intent and L4-implementation still loaded | L2 is meta (serving), L4 is technical specs - both needed |
| Empty string on error | Graceful degradation | Matches existing `_read_manifesto_file` pattern |
| sys.path manipulation | Use pattern from context_loader.py:185-188 | Matches existing pattern in same file |
| Deprecate not remove | Mark fields as DEPRECATED | Memory 80654, 82206 - coldstart.md may use L0-L4 |

### Input/Output Examples

**Before (ContextLoader.load_context()):**
```
identity_context: ""
l0_telos: <101 lines>
l1_principal: <147 lines>
l3_requirements: <192 lines>
Total: ~440 lines identity content
```

**After (ContextLoader.load_context()):**
```
identity_context: <35 lines via IdentityLoader>
l0_telos: ""
l1_principal: ""
l3_requirements: ""
Total: ~35 lines (92% reduction)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| IdentityLoader not found | log warning, return "" | Implicit via try/except |
| identity.yaml missing | IdentityLoader raises → caught → return "" | Existing WORK-007 tests |
| Manifesto files missing | IdentityLoader returns partial | Covered by WORK-007 |

### Open Questions

**Q: Should L2-intent also be extracted via identity loader?**

A: No. L2-intent is meta-level ("what serving means") and short (114 lines). Keep separate. Identity is core grounding. L2 could become session_loader territory later.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | No unresolved decisions - spawned from completed WORK-007 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add tests to `tests/test_context_loader.py` (create if missing)
- [ ] Verify test for `identity_context` field fails (field doesn't exist yet)

### Step 2: Add IdentityLoader Import
- [ ] Add sys.path manipulation for lib/ import
- [ ] Add `from identity_loader import IdentityLoader`
- [ ] Verify import works (no ImportError)

### Step 3: Add identity_context Field
- [ ] Add field to GroundedContext dataclass
- [ ] Mark L0/L1/L3 fields as DEPRECATED in comments
- [ ] Test 1 passes

### Step 4: Implement _load_identity()
- [ ] Add helper method with try/except
- [ ] Modify load_context() to call _load_identity()
- [ ] Set deprecated fields to empty string
- [ ] Tests 2, 3 pass

### Step 5: Update Docstring
- [ ] Update module docstring to mention identity integration
- [ ] Update GroundedContext docstring

### Step 6: Integration Verification
- [ ] Run `pytest tests/test_context_loader.py -v`
- [ ] Run `pytest tests/test_identity_loader.py -v` (no regression)
- [ ] Verify `just identity` still works

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** Docstring updated to reflect identity integration
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import path issues | Medium | Use same pattern as existing status import in same file |
| Existing consumers expect L0/L1/L3 content | Low | Fields still exist (empty), marked DEPRECATED |
| IdentityLoader raises unexpected error | Low | Wrapped in try/except with graceful fallback |
| Test file doesn't exist | Low | Create minimal test file if needed |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 226 | 2026-01-22 | - | Plan authored | Ready for validation |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-008/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| context_loader.py imports IdentityLoader | [ ] | Import statement exists |
| load_context() calls IdentityLoader().load() | [ ] | _load_identity() called |
| GroundedContext has identity_context field | [ ] | Field exists in dataclass |
| just coldstart receives identity context | [ ] | Integration test passes |
| Docstring updated | [ ] | Module docstring reflects identity |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/context_loader.py` | Has IdentityLoader import, _load_identity(), identity_context field | [ ] | |
| `tests/test_context_loader.py` | Has 3 identity tests | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_context_loader.py -v
# Expected: identity tests pass

python -c "import sys; sys.path.insert(0, '.claude/haios/modules'); from context_loader import ContextLoader; ctx = ContextLoader().load_context(); print(len(ctx.identity_context.split('\\n')), 'lines')"
# Expected: ~35 lines
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** (ContextLoader calls IdentityLoader)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** Docstring updated
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-007/WORK.md (parent work - completed)
- @docs/work/active/WORK-007/plans/PLAN.md (Phase C deferred here)
- @.claude/haios/lib/identity_loader.py (to be integrated)
- @.claude/haios/modules/context_loader.py (modification target)
- @.claude/haios/epochs/E2_3/arcs/configuration/CH-004-identity-loader.md (chapter spec)

**Memory Query Results:**
- concept 82291: "ContextLoader integration deferred to follow-on work"
- concept 80654: "Decided NOT to migrate /coldstart markdown command to use ContextLoader"
- concept 82206: "We built ContextLoader to programmatically load L0-L4 context"

---
