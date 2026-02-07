---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-260
title: GovernanceLayer Toggle Access
author: Hephaestus
lifecycle_phase: plan
session: 169
version: '1.5'
generated: 2026-01-04
last_updated: '2026-01-04T20:11:50'
---
# Implementation Plan: GovernanceLayer Toggle Access

@docs/README.md
@.claude/haios/modules/governance_layer.py
@.claude/lib/config.py

---

## Goal

GovernanceLayer module will expose `get_toggle(name)` method that delegates to `.claude/lib/config.py` ConfigLoader, enabling hooks to import toggle access from modules instead of lib/.

---

## Effort Estimation (Ground Truth)

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | governance_layer.py, test_governance_layer.py |
| Lines of code affected | ~15 | New method + tests |
| Tests to write | 2 | get_toggle exists, returns correct value |

---

## Current State vs Desired State

### Current State
```python
# Hooks import directly from lib/
from config import ConfigLoader
config = ConfigLoader.get()
if config.toggles.get("block_powershell"):
    # handle
```

### Desired State
```python
# Hooks import from module
from governance_layer import GovernanceLayer
layer = GovernanceLayer()
if layer.get_toggle("block_powershell"):
    # handle
```

---

## Tests First (TDD)

### Test 1: get_toggle returns toggle value
```python
def test_get_toggle_returns_value(self):
    """get_toggle returns toggle value from config."""
    from governance_layer import GovernanceLayer
    layer = GovernanceLayer()
    # block_powershell is defined in haios.yaml
    result = layer.get_toggle("block_powershell")
    assert isinstance(result, bool)
```

### Test 2: get_toggle returns default for unknown
```python
def test_get_toggle_unknown_returns_default(self):
    """get_toggle returns default for unknown toggle."""
    from governance_layer import GovernanceLayer
    layer = GovernanceLayer()
    result = layer.get_toggle("nonexistent_toggle", default=False)
    assert result is False
```

---

## Detailed Design

**File:** `.claude/haios/modules/governance_layer.py`
**Location:** After line 280 (end of scaffold_template method)

**New Code:**
```python
def get_toggle(self, name: str, default: Any = None) -> Any:
    """
    Get governance toggle value by name.

    Delegates to lib/config.ConfigLoader.toggles.

    Args:
        name: Toggle name (e.g., "block_powershell")
        default: Default value if toggle not found

    Returns:
        Toggle value from haios.yaml toggles section, or default.
    """
    from config import ConfigLoader
    return ConfigLoader.get().toggles.get(name, default)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Delegation vs copy | Delegation | Single source of truth in ConfigLoader |
| Default parameter | Allow caller default | Flexible fallback for missing toggles |
| Import location | Inside method | Lazy import, matches existing pattern in module |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 2 tests to `tests/test_governance_layer.py`
- [ ] Verify tests fail (red)

### Step 2: Add get_toggle method
- [ ] Add method to GovernanceLayer class
- [ ] Tests pass (green)

### Step 3: Update README
- [ ] Update `.claude/haios/modules/README.md` with new method

---

## Ground Truth Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/governance_layer.py` | `get_toggle()` method exists | [ ] | |
| `tests/test_governance_layer.py` | 2 new tests for get_toggle | [ ] | |
| `.claude/haios/modules/README.md` | Documents get_toggle method | [ ] | |

---

## References

- INV-056: Hook-to-Module Migration Investigation
- Memory 80682: `config.ConfigLoader.toggles -> GovernanceLayer.get_toggle() (E2-260)`
- `.claude/lib/config.py`: Source implementation
- `.claude/haios/modules/governance_layer.py`: Target module

---
