---
template: implementation_plan
status: complete
date: 2026-01-22
backlog_id: WORK-008
title: ContextLoader Identity Integration
author: Hephaestus
lifecycle_phase: plan
session: 226
version: '1.5'
generated: 2026-01-22
last_updated: '2026-01-22T20:36:01'
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

Make ContextLoader config-driven per L4 principles: role-based selective loading where haios.yaml defines the role→loaders mapping, enabling extensible context composition without code changes.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `context_loader.py`, `haios.yaml` |
| Lines of code affected | ~60 | Refactor to config-driven loader dispatch |
| New files to create | 0 | Uses existing loaders infrastructure |
| Tests to write | 5 | Role-based loading, config parsing, extensibility |
| Dependencies | 2 | identity_loader.py, haios.yaml |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Config + multiple loaders + role dispatch |
| Risk of regression | Medium | Changing load_context() behavior |
| External dependencies | Low | All loaders already tested |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add role config to haios.yaml | 15 min | High |
| Refactor ContextLoader for config-driven dispatch | 30 min | Medium |
| Tests | 20 min | High |
| **Total** | ~65 min | Medium |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/context_loader.py:108-119
# HARDCODED file reads - no config, no roles, not extensible
ctx = GroundedContext(
    session_number=session,
    prior_session=prior,
    l0_telos=self._read_manifesto_file("L0-telos.md"),
    l1_principal=self._read_manifesto_file("L1-principal.md"),
    # ... hardcoded for each file
)
```

**Behavior:** Hardcoded file reads, no role awareness, not extensible

**Problem:** Violates L4 principle: "Selective loading by role | haios.yaml defines role → files mapping"

### Desired State

```python
# .claude/haios/modules/context_loader.py - config-driven per L4
def load_context(self, role: str = "main") -> GroundedContext:
    """Load context based on role from haios.yaml config."""
    loaders = self._get_loaders_for_role(role)  # from haios.yaml
    context_parts = {}
    for loader_name in loaders:
        loader = self._get_loader(loader_name)  # extensible registry
        context_parts[loader_name] = loader.load()
    return GroundedContext(
        session_number=session,
        prior_session=prior,
        loaded_context=context_parts,  # Dict of loader outputs
        # ...
    )
```

```yaml
# haios.yaml - role → loaders mapping
context:
  roles:
    main:
      loaders: [identity]
    builder:
      loaders: [identity, work_item]
    validator:
      loaders: [identity, artifacts]
```

**Behavior:** Config-driven, role-based, extensible

**Result:** Follows L4 principles, new loaders added via config not code

---

## Tests First (TDD)

### Test 1: Role Parameter Accepted
```python
def test_load_context_accepts_role():
    """load_context() accepts role parameter."""
    loader = ContextLoader()
    ctx = loader.load_context(role="main")
    assert ctx is not None
```

### Test 2: Config Defines Loaders Per Role
```python
def test_config_has_role_loader_mapping():
    """haios.yaml has context.roles section."""
    import yaml
    with open(".claude/haios/config/haios.yaml") as f:
        config = yaml.safe_load(f)
    assert "context" in config
    assert "roles" in config["context"]
    assert "main" in config["context"]["roles"]
```

### Test 3: Main Role Loads Identity
```python
def test_main_role_loads_identity():
    """Role 'main' loads identity context."""
    loader = ContextLoader()
    ctx = loader.load_context(role="main")
    assert "identity" in ctx.loaded_context
    assert "IDENTITY" in ctx.loaded_context["identity"] or "Mission" in ctx.loaded_context["identity"]
```

### Test 4: Unknown Role Raises Error
```python
def test_unknown_role_raises():
    """Unknown role raises ValueError."""
    loader = ContextLoader()
    with pytest.raises(ValueError):
        loader.load_context(role="nonexistent_role")
```

### Test 5: Extensible - New Loader in Config Works
```python
def test_loader_registry_extensible():
    """New loaders can be added to registry."""
    loader = ContextLoader()
    # Should have identity loader registered
    assert "identity" in loader._loader_registry
```

---

## Detailed Design

### Architecture Overview (Per L4 Principles)

```
haios.yaml (config)
    |
    +-> context.roles.{role}.loaders: [identity, ...]
           |
           +-> ContextLoader._get_loaders_for_role(role)
                   |
                   +-> ContextLoader._loader_registry["identity"]
                           |
                           +-> IdentityLoader().load()
```

### Change 1: Add role config to haios.yaml

**File:** `.claude/haios/config/haios.yaml`

```yaml
# Add after existing config sections
context:
  roles:
    main:
      loaders: [identity]
      description: "Main agent - philosophical grounding"
    builder:
      loaders: [identity]
      description: "Builder agent - identity + work context"
    validator:
      loaders: [identity]
      description: "Validator agent - identity + requirements"
  loader_registry:
    identity:
      module: identity_loader
      class: IdentityLoader
```

### Change 2: Refactor GroundedContext

**File:** `.claude/haios/modules/context_loader.py`

```python
@dataclass
class GroundedContext:
    """Result of context loading - role-based composition."""

    session_number: int
    prior_session: Optional[int] = None
    role: str = "main"
    loaded_context: Dict[str, str] = field(default_factory=dict)  # loader_name -> content
    checkpoint_summary: str = ""
    strategies: List[Dict[str, Any]] = field(default_factory=list)
    ready_work: List[str] = field(default_factory=list)

    # DEPRECATED - kept for backward compat, will be empty
    l0_telos: str = ""
    l1_principal: str = ""
    l2_intent: str = ""
    l3_requirements: str = ""
    l4_implementation: str = ""
```

### Change 3: Add loader registry and dispatch

```python
class ContextLoader:
    # Loader registry - extensible via config
    _loader_registry: Dict[str, type] = {}

    def __init__(self, ...):
        # ... existing init
        self._register_default_loaders()
        self._load_config()

    def _register_default_loaders(self):
        """Register built-in loaders."""
        from identity_loader import IdentityLoader
        self._loader_registry["identity"] = IdentityLoader

    def _load_config(self):
        """Load context config from haios.yaml."""
        config_path = self._project_root / ".claude/haios/config/haios.yaml"
        with open(config_path) as f:
            self._config = yaml.safe_load(f)

    def _get_loaders_for_role(self, role: str) -> List[str]:
        """Get loader names for role from config."""
        roles = self._config.get("context", {}).get("roles", {})
        if role not in roles:
            raise ValueError(f"Unknown role: {role}. Available: {list(roles.keys())}")
        return roles[role].get("loaders", [])

    def load_context(self, role: str = "main", trigger: str = "coldstart") -> GroundedContext:
        """Load context based on role from config."""
        session, prior = self.compute_session_number()

        # Load context via registered loaders per role
        loaded_context = {}
        for loader_name in self._get_loaders_for_role(role):
            loader_class = self._loader_registry.get(loader_name)
            if loader_class:
                try:
                    loaded_context[loader_name] = loader_class().load()
                except Exception as e:
                    logger.warning(f"Loader {loader_name} failed: {e}")
                    loaded_context[loader_name] = ""

        return GroundedContext(
            session_number=session,
            prior_session=prior,
            role=role,
            loaded_context=loaded_context,
            checkpoint_summary=self._get_latest_checkpoint(),
            strategies=self._get_strategies(trigger),
            ready_work=self._get_ready_work(),
        )
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Config in haios.yaml | `context.roles` section | Follows L4: "haios.yaml defines role → files mapping" |
| Loader registry | Dict[str, type] | Extensible - new loaders added via config |
| Role parameter | Default "main" | Backward compat - existing calls work |
| loaded_context as dict | loader_name → content | Flexible, extensible, introspectable |
| Keep deprecated fields | Empty strings | Backward compat for transition period |

### Input/Output Examples

**load_context(role="main"):**
```python
GroundedContext(
    session_number=226,
    role="main",
    loaded_context={
        "identity": "=== IDENTITY ===\nMission: ...\n..."  # ~54 lines
    },
    # ... other fields
)
```

**load_context(role="builder"):**
```python
GroundedContext(
    session_number=226,
    role="builder",
    loaded_context={
        "identity": "=== IDENTITY ===\n...",
        # future: "work_item": "..."
    },
)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Unknown role | ValueError with available roles | Test 4 |
| Loader not in registry | Skip with warning | Graceful degradation |
| Config missing context section | Default to identity-only | Graceful degradation |
| Loader raises exception | Log warning, return empty | Try/except in dispatch |

### Open Questions

**Q: Should config be reloaded on each call or cached?**

A: Cached at init. Hot-reload is future enhancement.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | No unresolved decisions - spawned from completed WORK-007 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [x] Create `tests/test_context_loader.py` if missing
- [x] Add 5 tests per TDD section
- [x] Verify tests fail (config section doesn't exist yet)

### Step 2: Add Context Config to haios.yaml
- [x] Add `context.roles` section with main/builder/validator
- [x] Add `context.loader_registry` section
- [x] Test 2 passes (config parsing)

### Step 3: Refactor GroundedContext
- [x] Add `role` and `loaded_context` fields
- [x] Mark L0-L4 fields as DEPRECATED
- [x] Test 1 passes (role parameter accepted)

### Step 4: Implement Loader Registry
- [x] Add `_loader_registry` class attribute
- [x] Add `_register_default_loaders()` method
- [x] Add `_load_config()` method
- [x] Test 5 passes (registry extensible)

### Step 5: Implement Role-Based Dispatch
- [x] Add `_get_loaders_for_role()` method
- [x] Refactor `load_context()` to use config dispatch
- [x] Test 3 passes (main role loads identity)
- [x] Test 4 passes (unknown role raises)

### Step 6: Update Docstrings
- [x] Update module docstring to reflect config-driven design
- [x] Update GroundedContext docstring
- [x] Update load_context() docstring with role parameter

### Step 7: Integration Verification
- [x] Run `pytest tests/test_context_loader.py -v`
- [x] Run `pytest tests/test_identity_loader.py -v` (no regression)
- [x] Verify `just identity` still works

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
| haios.yaml has context.roles config | [ ] | Config section exists |
| ContextLoader accepts role parameter | [ ] | load_context(role=...) works |
| GroundedContext has loaded_context field | [ ] | Dict with loader outputs |
| Loader registry is extensible | [ ] | _loader_registry dict exists |
| Docstrings updated | [ ] | Reflects config-driven design |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/haios.yaml` | Has context.roles section | [ ] | |
| `.claude/haios/modules/context_loader.py` | Config-driven, role parameter, loader registry | [ ] | |
| `tests/test_context_loader.py` | Has 5 config-driven tests | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_context_loader.py -v
# Expected: 5 tests pass

python -c "import sys; sys.path.insert(0, '.claude/haios/modules'); from context_loader import ContextLoader; ctx = ContextLoader().load_context(role='main'); print('identity' in ctx.loaded_context)"
# Expected: True
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
- @.claude/haios/lib/identity_loader.py (first loader to integrate)
- @.claude/haios/modules/context_loader.py (refactor target)
- @.claude/haios/manifesto/L4/technical_requirements.md (L4 principles source)
- @.claude/haios/config/haios.yaml (config target)

**L4 Principles Applied:**
- "Selective loading by role | haios.yaml defines role → files mapping"
- "Agents load only what they need | Role-specific context files"

**Memory Query Results:**
- concept 82291: "ContextLoader integration deferred to follow-on work"
- concept 80654: "Decided NOT to migrate /coldstart markdown command to use ContextLoader"

**Session 226 Alignment Review:**
- Plan revised from hardcoded wiring to config-driven per L4 principles
- identity.yaml updated to extract L4/technical_requirements.md (Step 1 complete)

---
