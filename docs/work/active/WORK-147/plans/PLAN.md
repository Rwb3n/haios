---
template: implementation_plan
status: complete
date: 2026-02-14
backlog_id: WORK-147
title: "Schema Registry and ConfigLoader Extension"
author: Hephaestus
lifecycle_phase: plan
session: 369
version: "1.5"
generated: 2026-02-14
last_updated: 2026-02-14T15:06:17
spawned_by: WORK-067
---
# Implementation Plan: Schema Registry and ConfigLoader Extension

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | WORK-067 investigation is the prior work (memory: 85286, 85290) |
| Document design decisions | MUST | See Key Design Decisions table |
| Ground truth metrics | MUST | File counts from Glob/wc below |

---

## Goal

ConfigLoader gains a `schemas` property and `get_schema(domain, key)` method that loads YAML schema files from `.claude/haios/schemas/`, and `substitute_variables()` resolves `{{schema:domain.key}}` references at scaffold time — eliminating duplicated enum definitions in templates.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | config.py (ConfigLoader), scaffold.py (substitute_variables) |
| Lines of code affected | ~40 | config.py:44-49 (init), new methods; scaffold.py:282-296 |
| New files to create | 5 | 3 schema YAMLs (core/), 1 empty dir (project/), 1 test file |
| Tests to write | 10 | 5 ConfigLoader, 3 substitute_variables, 2 integration |
| Dependencies | 2 | haios.yaml (paths entry), existing test infrastructure |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | ConfigLoader is singleton, substitute_variables is pure function |
| Risk of regression | Low | Existing tests cover current behavior; new code is additive |
| External dependencies | Low | Only PyYAML (already imported) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Schema files + haios.yaml | 10 min | High |
| ConfigLoader extension | 15 min | High |
| substitute_variables extension | 10 min | High |
| Tests | 20 min | High |
| **Total** | **55 min** | |

---

## Current State vs Desired State

### Current State

```python
# config.py:44-49 — ConfigLoader loads 3 files only
def __init__(self):
    """Load all config files on init."""
    self._haios = self._load("haios.yaml")
    self._cycles = self._load("cycles.yaml")
    self._components = self._load("components.yaml")
```

```python
# scaffold.py:282-296 — substitute_variables does simple {{VAR}} replacement
def substitute_variables(content: str, variables: dict) -> str:
    result = content
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    return result
```

**Behavior:** No schema registry. Enums are hardcoded inline in templates, validate.py, work_engine.py, etc. 46 definitions scattered across 8 file categories (WORK-067 evidence).

**Result:** Drift between spec and implementation (type: 5 in TRD vs 9 in production; queue_position: 3 in TRD vs 5 in code). No single source of truth for enum values.

### Desired State

```python
# config.py — ConfigLoader gains schema loading
def __init__(self):
    """Load all config files on init."""
    self._haios = self._load("haios.yaml")
    self._cycles = self._load("cycles.yaml")
    self._components = self._load("components.yaml")
    self._schemas = self._load_schemas()  # NEW

@property
def schemas(self) -> Dict[str, Dict[str, Any]]:
    """Schema registry (core/ and project/ tiers)."""
    return self._schemas

def get_schema(self, domain: str, key: str) -> Any:
    """Get schema value by domain.key path."""
    ...
```

```python
# scaffold.py — substitute_variables resolves {{schema:domain.key}}
def substitute_variables(content: str, variables: dict) -> str:
    result = content
    # Resolve {{schema:domain.key}} references first
    result = _resolve_schema_refs(result)
    # Then do normal {{VAR}} replacement
    for key, value in variables.items():
        ...
```

**Behavior:** Schema files in `.claude/haios/schemas/core/` define authoritative enum values. Templates use `{{schema:work_item.type}}` which resolves to `feature|investigation|bug|chore|spike` at scaffold time.

**Result:** Single source of truth for all enums. Templates consume schemas by reference (REQ-REFERENCE-002).

---

## Tests First (TDD)

### Test 1: Schema directory loading
```python
def test_config_loader_schemas_property(tmp_path):
    """ConfigLoader.schemas returns loaded schema dict."""
    # Setup: create schema dir with one file
    schema_dir = tmp_path / "schemas" / "core"
    schema_dir.mkdir(parents=True)
    (schema_dir / "work_item.yaml").write_text(yaml.dump({
        "version": "2.0",
        "enums": {"status": {"values": ["active", "blocked", "complete"]}}
    }))
    # Action: load schemas
    # Assert: schemas["core/work_item"]["enums"]["status"]["values"] has 3 items
```

### Test 2: get_schema resolves domain.key
```python
def test_get_schema_resolves_domain_key(tmp_path):
    """get_schema('work_item', 'status') returns enum values."""
    # Setup: schema with status enum
    # Action: config.get_schema("work_item", "status")
    # Assert: returns {"values": ["active", "blocked", "complete"], ...}
```

### Test 3: get_schema raises on missing domain
```python
def test_get_schema_missing_domain_raises():
    """get_schema with unknown domain raises KeyError."""
    # Assert: KeyError with descriptive message
```

### Test 4: get_schema raises on missing key
```python
def test_get_schema_missing_key_raises():
    """get_schema with unknown key raises KeyError."""
    # Assert: KeyError with descriptive message
```

### Test 5: Schema loading with empty project dir
```python
def test_schemas_empty_project_dir(tmp_path):
    """Empty project/ dir doesn't cause errors."""
    # Setup: schemas/core/ with file, schemas/project/ empty
    # Assert: schemas dict only contains core entries
```

### Test 6: substitute_variables resolves schema refs
```python
def test_substitute_schema_ref():
    """{{schema:work_item.type}} resolves to pipe-delimited values."""
    content = "type: {{schema:work_item.type}}"
    # After resolution: "type: feature|investigation|bug|chore|spike"
```

### Test 7: substitute_variables ignores unknown schema refs
```python
def test_substitute_unknown_schema_ref_raises():
    """{{schema:nonexistent.key}} raises ValueError."""
    content = "type: {{schema:nonexistent.key}}"
    # Assert: ValueError with descriptive message
```

### Test 8: substitute_variables handles mixed refs
```python
def test_substitute_mixed_refs():
    """Content with both {{VAR}} and {{schema:X.Y}} resolves both."""
    content = "title: {{TITLE}}\ntype: {{schema:work_item.type}}"
    # After: "title: My Title\ntype: feature|investigation|bug|chore|spike"
```

### Test 9: Backward compatibility — no schema refs
```python
def test_substitute_no_schema_refs_unchanged():
    """Content without {{schema:}} works exactly as before."""
    content = "title: {{TITLE}}"
    result = substitute_variables(content, {"TITLE": "Test"})
    assert result == "title: Test"
```

### Test 10: Integration — schemas path in haios.yaml
```python
def test_haios_yaml_has_schemas_path():
    """haios.yaml paths section includes schemas entry."""
    from config import ConfigLoader
    ConfigLoader.reset()
    config = ConfigLoader.get()
    assert "schemas" in config.paths
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/lib/config.py`
**Location:** Lines 44-49 (`__init__`) + new methods after line 124

**Current Code:**
```python
# config.py:44-49
def __init__(self):
    """Load all config files on init."""
    self._haios = self._load("haios.yaml")
    self._cycles = self._load("cycles.yaml")
    self._components = self._load("components.yaml")
```

**Changed Code:**
```python
def __init__(self):
    """Load all config files on init."""
    self._haios = self._load("haios.yaml")
    self._cycles = self._load("cycles.yaml")
    self._components = self._load("components.yaml")
    self._schemas = self._load_schemas()

def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
    """Load all YAML schema files from schemas directory.

    Scans both core/ and project/ subdirectories.
    Schema key = "{tier}/{filename_without_ext}" (e.g., "core/work_item").

    Returns:
        Dict mapping schema keys to loaded YAML content.
    """
    schemas_path = self._haios.get("paths", {}).get("schemas")
    if not schemas_path:
        return {}

    # Resolve relative to project root (CONFIG_DIR parent is .claude/haios/)
    schemas_dir = CONFIG_DIR.parent.parent.parent / schemas_path
    if not schemas_dir.exists():
        return {}

    result = {}
    for tier_dir in schemas_dir.iterdir():
        if not tier_dir.is_dir() or tier_dir.name.startswith("."):
            continue
        for schema_file in tier_dir.glob("*.yaml"):
            key = f"{tier_dir.name}/{schema_file.stem}"
            try:
                with open(schema_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                # A4 mitigation: validate schema format
                if not isinstance(data, dict):
                    continue  # Skip non-dict files
                if "enums" not in data and "transitions" not in data:
                    continue  # Skip files without expected sections
                result[key] = data
            except Exception:
                pass  # Skip malformed files silently (graceful degradation)
    return result
```

**New property and method (after line 124):**
```python
@property
def schemas(self) -> Dict[str, Dict[str, Any]]:
    """Schema registry content (core/ and project/ tiers)."""
    return self._schemas

def get_schema(self, domain: str, key: str) -> Any:
    """Get schema enum or section by domain and key.

    Searches all tiers (core/ first, then project/) for the domain file,
    then returns the value at the key path within 'enums' section.

    Args:
        domain: Schema file name without extension (e.g., "work_item")
        key: Key within the enums section (e.g., "status", "type")

    Returns:
        Schema entry dict (typically has 'values', 'default' keys)

    Raises:
        KeyError: If domain or key not found in any tier
    """
    # Search tiers in order: core first, then project
    for tier in ("core", "project"):
        schema_key = f"{tier}/{domain}"
        if schema_key in self._schemas:
            schema = self._schemas[schema_key]
            enums = schema.get("enums", {})
            if key in enums:
                return enums[key]
            # Also check top-level keys (for transitions, etc.)
            if key in schema:
                return schema[key]

    raise KeyError(
        f"Schema '{domain}.{key}' not found. "
        f"Available domains: {[k.split('/')[1] for k in self._schemas.keys()]}"
    )
```

---

**File:** `.claude/haios/lib/scaffold.py`
**Location:** Lines 282-296 (`substitute_variables`)

**Current Code:**
```python
# scaffold.py:282-296
def substitute_variables(content: str, variables: dict) -> str:
    """Replace {{VAR}} placeholders with variable values."""
    result = content
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    return result
```

**Changed Code:**
```python
def substitute_variables(content: str, variables: dict) -> str:
    """Replace {{VAR}} and {{schema:domain.key}} placeholders.

    Schema references are resolved first via ConfigLoader, then
    normal variable substitution occurs.

    Args:
        content: Template content with placeholders
        variables: Dict of variable names to values

    Returns:
        Content with all placeholders replaced.

    Raises:
        ValueError: If a {{schema:X.Y}} reference cannot be resolved.
    """
    result = content

    # Phase 1: Resolve {{schema:domain.key}} references
    schema_pattern = re.compile(r"\{\{schema:([a-zA-Z_]+)\.([a-zA-Z_]+)\}\}")
    def _resolve_schema_match(match):
        domain = match.group(1)
        key = match.group(2)
        try:
            from config import ConfigLoader
            config = ConfigLoader.get()
            schema_entry = config.get_schema(domain, key)
            # For enum entries with 'values' list, return pipe-delimited
            if isinstance(schema_entry, dict) and "values" in schema_entry:
                return "|".join(str(v) for v in schema_entry["values"])
            # For other types, return string representation
            return str(schema_entry)
        except KeyError as e:
            raise ValueError(f"Schema reference resolution failed: {e}")

    result = schema_pattern.sub(_resolve_schema_match, result)

    # Phase 2: Normal {{VAR}} replacement
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    return result
```

### Call Chain Context

```
scaffold_template()
    |
    +-> load_template()          # Gets template content
    +-> substitute_variables()   # <-- MODIFIED: now resolves {{schema:X.Y}}
    |       |
    |       +-> ConfigLoader.get()
    |       +-> ConfigLoader.get_schema(domain, key)
    |       |       |
    |       |       +-> _load_schemas()  # <-- NEW: loads from .claude/haios/schemas/
    |       |
    |       +-> normal {{VAR}} replacement (unchanged)
    |
    +-> write output file
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Schema file format | YAML with `enums:` section | WORK-067 H4: all config is YAML, 38/46 enums are simple lists, JSON Schema adds dependency with no benefit |
| Schema key format | `{tier}/{filename}` (e.g., `core/work_item`) | Mirrors filesystem structure, avoids collision between core and project schemas |
| Tier search order | core first, then project | Core is authoritative; project can override or extend |
| Schema ref syntax | `{{schema:domain.key}}` | Consistent with existing `{{VAR}}` pattern; `schema:` prefix prevents collision; dot notation for hierarchy |
| Pipe-delimited output | `value1\|value2\|value3` | Natural for YAML enum values in frontmatter context |
| Error on missing schema ref | ValueError | Fail-fast prevents silent template corruption; matches get_path's behavior for unresolved placeholders |
| Schema loading in __init__ | Eager load alongside other configs | Consistent with existing pattern (haios, cycles, components all loaded in __init__) |
| ConfigLoader import in scaffold.py | Lazy import inside function | Avoids circular import; scaffold.py doesn't currently import config.py |

### Input/Output Examples

**Schema file (`.claude/haios/schemas/core/work_item.yaml`):**
```yaml
version: "2.0"
source: TRD-WORK-ITEM-UNIVERSAL

enums:
  status:
    values: [active, blocked, complete, archived]
    default: active
  type:
    values: [feature, investigation, bug, chore, spike]
    default: feature
  priority:
    values: [critical, high, medium, low]
    default: medium
  effort:
    values: [small, medium, large, unknown]
    default: medium
```

**Template content before resolution:**
```
type: {{schema:work_item.type}}
```

**After substitute_variables():**
```
type: feature|investigation|bug|chore|spike
```

**get_schema() call:**
```python
config.get_schema("work_item", "status")
# Returns: {"values": ["active", "blocked", "complete", "archived"], "default": "active"}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No schemas path in haios.yaml | _load_schemas returns {} | Test 5 (graceful) |
| Empty project/ directory | Skipped, no error | Test 5 |
| Schema file with parse error | Returns {} for that file, others load fine | Follows existing _load() pattern |
| `{{schema:}}` with no domain.key | Not matched by regex (requires word chars + dot + word chars) | Regex enforces format |
| Content with no schema refs | Passes through unchanged to normal substitution | Test 9 |
| Missing schema domain | ValueError raised | Test 7 |

### Open Questions

**Q: Should schema values list format in templates be configurable (pipe vs comma vs newline)?**

Pipe-delimited is chosen as the default since it's the standard format for YAML enum documentation. If future needs require different formats, get_schema() returns the raw dict so callers can format as needed. TBD for E2.7 if needed.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Schema values for work_item.type | A) TRD values (feature, investigation, bug, chore, spike) B) Production values (+ implementation, design, bugfix, task, cleanup) | A: TRD values | WORK-067 identified drift but this work creates the *registry* — fixing drift is a separate follow-up. Start with spec-defined values. |
| Schema values for queue_position | A) TRD (backlog, in_progress, done) B) Implementation (parked, backlog, ready, working, done) | B: Implementation | The TRD is wrong here (memory 85298). Implementation values are authoritative and proven in production. |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_schema_registry.py` with all 10 tests
- [ ] Verify all tests fail (red)

### Step 2: Create Schema Directory and Files
- [ ] Create `.claude/haios/schemas/core/` directory
- [ ] Create `.claude/haios/schemas/project/` directory (empty)
- [ ] Create `core/work_item.yaml` with status, type, priority, effort enums
- [ ] Create `core/queue.yaml` with queue_position, queue_types enums
- [ ] Create `core/lifecycle.yaml` with cycle_phase, lifecycles enums
- [ ] Add `schemas: ".claude/haios/schemas"` to haios.yaml paths section
- [ ] Tests 5, 10 pass (green)

### Step 3: Extend ConfigLoader
- [ ] Add `_load_schemas()` method
- [ ] Add `schemas` property
- [ ] Add `get_schema(domain, key)` method
- [ ] Modify `__init__` to call `_load_schemas()`
- [ ] Tests 1, 2, 3, 4, 5 pass (green)

### Step 4: Extend substitute_variables
- [ ] Add schema ref regex and resolution logic
- [ ] Lazy import ConfigLoader inside resolution function
- [ ] Tests 6, 7, 8, 9 pass (green)

### Step 5: Integration Verification
- [ ] All 10 new tests pass
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)

### Step 6: Consumer Verification
- [ ] Grep for hardcoded enum values in templates that could use `{{schema:}}`
- [ ] Document migration candidates (but don't migrate — that's follow-up work)

### Step 7: README Sync (A7 mitigation)
- [ ] Create README in `.claude/haios/schemas/` with:
  - Registry purpose and two-tier structure explanation
  - Schema file format convention (version, source, enums section)
  - Template syntax reference with 5+ examples (correct and incorrect)
  - Common mistakes (missing dot, wrong domain name, typos)
  - How to add new schemas

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Circular import (scaffold -> config -> scaffold) | Medium | Lazy import in substitute_variables; config.py doesn't import scaffold.py |
| Schema load failure breaks ConfigLoader init | High | _load_schemas follows _load pattern: returns {} on failure |
| Existing tests break due to __init__ change | Medium | _load_schemas returns {} if schemas path missing from haios.yaml — graceful degradation |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 369 | 2026-02-14 | - | Plan authored | - |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-147/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Schema registry directory with core/ and project/ | [ ] | `ls .claude/haios/schemas/` |
| ConfigLoader gains schemas property and get_schema() | [ ] | Read config.py, verify methods |
| At least one core schema file (work_item.yaml) populated | [ ] | Read schemas/core/work_item.yaml |
| substitute_variables() resolves {{schema:domain.key}} | [ ] | Test 6 output |
| haios.yaml paths includes schemas entry | [ ] | Read haios.yaml paths section |
| Existing tests pass (no regressions) | [ ] | `pytest tests/ -v` output |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/schemas/core/work_item.yaml` | Has status, type, priority, effort enums | [ ] | |
| `.claude/haios/schemas/core/queue.yaml` | Has queue_position enum | [ ] | |
| `.claude/haios/schemas/core/lifecycle.yaml` | Has cycle_phase, lifecycles enums | [ ] | |
| `.claude/haios/schemas/project/` | Directory exists (empty) | [ ] | |
| `.claude/haios/lib/config.py` | Has schemas property and get_schema method | [ ] | |
| `.claude/haios/lib/scaffold.py` | substitute_variables resolves {{schema:}} | [ ] | |
| `.claude/haios/config/haios.yaml` | paths.schemas = ".claude/haios/schemas" | [ ] | |
| `tests/test_schema_registry.py` | 10 tests, all passing | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (substitute_variables is called by scaffold_template)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in schemas directory
- [ ] **MUST:** Consumer verification complete (document migration candidates)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-067/WORK.md (investigation findings — schema architecture)
- @docs/work/active/WORK-147/WORK.md (work item)
- @.claude/haios/lib/config.py (ConfigLoader — extension target)
- @.claude/haios/lib/scaffold.py (substitute_variables — extension target)
- @.claude/haios/manifesto/L4/functional_requirements.md:642-648 (REQ-REFERENCE-002)
- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (current work item schema)

---
