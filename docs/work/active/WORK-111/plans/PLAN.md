---
template: implementation_plan
status: complete
date: 2026-02-09
backlog_id: WORK-111
title: "Ceremony Contract Schema Design"
author: Hephaestus
lifecycle_phase: plan
session: 332
version: "1.5"
generated: 2026-02-09
last_updated: 2026-02-09T22:35:00
---
# Implementation Plan: Ceremony Contract Schema Design

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Validation tests for schema parsing (test_ceremony_contracts.py) |
| Query prior work | DONE | Memory 84249 (zero contracts), 84251 (registry need), 84262 (Release=close-work-cycle) |
| Document design decisions | MUST | See Key Design Decisions below |
| Ground truth metrics | MUST | See Scope Metrics below |

---

## Goal

Define the ceremony contract YAML schema, create a persistent ceremony registry, and produce a ceremony skill template — so that WORK-112 (retrofit) and WORK-113 (validation) have an unambiguous specification to build against.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | Design task — no existing files modified |
| New files to create | 3 | ceremony_registry.yaml, ceremony SKILL.md template, test file |
| Tests to write | 6 | Schema parsing, registry loading, contract field shape, category validation, dual-category, template validation |
| Dependencies | 0 | No code imports this yet (WORK-113 will) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Schema is standalone — consumed later by WORK-112/113 |
| Risk of regression | Low | No existing code modified |
| External dependencies | Low | Only YAML parsing (PyYAML, already in use) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Schema design | 15 min | High |
| Registry creation | 20 min | High |
| Template creation | 10 min | High |
| Tests | 15 min | High |
| **Total** | ~60 min | High |

---

## Current State vs Desired State

### Current State

```yaml
# From .claude/skills/queue-commit/SKILL.md (lines 1-8)
---
name: queue-commit
description: Move work item from ready to working queue position...
generated: 2026-02-09
last_updated: '2026-02-09'
---
```

**Behavior:** Skills have `name` and `description` in frontmatter. Contracts exist as markdown tables (## Input Contract, ## Output Contract) but are not machine-readable.

**Result:** No automated contract validation possible. No category field. No side_effects declaration.

### Desired State

```yaml
# Target ceremony skill frontmatter
---
name: queue-commit
description: Move work item from ready to working queue position...
category: queue
input_contract:
  - field: work_id
    type: string
    required: true
    description: Work item ID to commit
  - field: rationale
    type: string
    required: false
    description: Why starting now
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: Whether transition succeeded
  - field: work_id
    type: string
    guaranteed: always
    description: The work item ID
side_effects:
  - "Transitions queue_position from ready to working"
  - "Logs QueueCeremony event to governance-events.jsonl"
generated: 2026-02-09
last_updated: '2026-02-09'
---
```

**Behavior:** Every ceremony skill declares category, typed input/output contracts, and side effects in machine-readable YAML frontmatter.

**Result:** Automated validation possible. Registry can be built from scanning frontmatter. Contracts are both human-readable (markdown sections remain) and machine-readable (YAML frontmatter).

---

## Tests First (TDD)

### Test 1: Parse ceremony contract from YAML frontmatter
```python
def test_parse_ceremony_contract():
    """Verify contract schema can be parsed from YAML frontmatter."""
    sample_yaml = {
        'name': 'queue-commit',
        'category': 'queue',
        'input_contract': [
            {'field': 'work_id', 'type': 'string', 'required': True, 'description': 'Work item ID'}
        ],
        'output_contract': [
            {'field': 'success', 'type': 'boolean', 'guaranteed': 'always', 'description': 'Result'}
        ],
        'side_effects': ['Logs event']
    }
    contract = CeremonyContract.from_frontmatter(sample_yaml)
    assert contract.name == 'queue-commit'
    assert contract.category == 'queue'
    assert len(contract.input_contract) == 1
    assert contract.input_contract[0].field == 'work_id'
    assert contract.input_contract[0].required is True
```

### Test 2: Load ceremony registry
```python
def test_load_ceremony_registry():
    """Verify registry YAML loads and contains all 19 ceremonies."""
    registry = load_ceremony_registry()
    assert len(registry.ceremonies) == 19
    categories = {c.category for c in registry.ceremonies}
    assert categories == {'queue', 'session', 'closure', 'feedback', 'memory', 'spawn'}
```

### Test 3: Contract field validation shape
```python
def test_contract_field_required_attributes():
    """Each input contract field must have field, type, required, description."""
    field = ContractField(field='work_id', type='string', required=True, description='The ID')
    assert field.field == 'work_id'
    assert field.type == 'string'
    assert field.required is True
    assert field.description == 'The ID'
```

### Test 4: Category validation
```python
def test_invalid_category_rejected():
    """Category must be one of the 6 valid categories."""
    with pytest.raises(ValueError):
        CeremonyContract(name='test', category='invalid', input_contract=[], output_contract=[], side_effects=[])

def test_dual_category_accepted():
    """Dual-category (list) must be accepted for ceremonies like close-work-cycle."""
    contract = CeremonyContract(name='close-work', category=['closure', 'queue'], input_contract=[], output_contract=[], side_effects=[])
    assert contract.category == ['closure', 'queue']
```

### Test 5: Template renders valid schema
```python
def test_ceremony_template_renders_valid_yaml():
    """Ceremony skill template produces parseable YAML frontmatter."""
    # Read template, substitute sample values, parse YAML, verify schema fields present
    template_path = Path('.claude/templates/ceremony/SKILL.md')
    assert template_path.exists()
    content = template_path.read_text()
    # Template must contain contract schema placeholders
    assert 'category:' in content
    assert 'input_contract:' in content
    assert 'output_contract:' in content
    assert 'side_effects:' in content
```

---

## Detailed Design

### Schema Definition

The contract schema has 3 components added to ceremony skill frontmatter:

**1. `category` field (required)**
```yaml
category: queue|session|closure|feedback|memory|spawn
```

**2. `input_contract` list (required)**
```yaml
input_contract:
  - field: <name>           # string, required
    type: <type>            # string|boolean|list|path|integer, required
    required: <bool>        # true/false, required
    description: <text>     # string, required
    pattern: <regex>        # string, optional (e.g., "WORK-\\d{3}")
```

**3. `output_contract` list (required)**
```yaml
output_contract:
  - field: <name>           # string, required
    type: <type>            # string|boolean|list|path|integer, required
    guaranteed: <when>      # always|on_success|on_failure, required
    description: <text>     # string, required
```

**4. `side_effects` list (required)**
```yaml
side_effects:
  - "Human-readable description of state change"
```

### Registry Schema

File: `.claude/haios/config/ceremony_registry.yaml`

```yaml
# Ceremony Registry - Single source of truth for all 19 ceremonies
# Generated from L4/functional_requirements.md ceremony definitions table

version: "1.0"
ceremony_count: 19

ceremonies:
  # Queue ceremonies (4)
  - name: intake
    category: queue
    skill: queue-intake
    signature: "Idea -> BacklogItem"
    has_contract: false  # Updated by WORK-112
    has_skill: true
    notes: null

  - name: prioritize
    category: queue
    skill: queue-prioritize
    signature: "[BacklogItems] -> [ReadyItems]"
    has_contract: false
    has_skill: true
    notes: null

  # ... (all 19 entries)
```

### Ceremony Skill Template

File: `.claude/templates/ceremony/SKILL.md`

A template for creating new ceremony skills with the contract schema pre-populated.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Contract in frontmatter vs separate file | Frontmatter | Co-located with skill content. Single file to read. Matches existing `name`/`description` pattern. |
| `required` vs `RFC2119` levels | `required: true/false` | Simpler. RFC2119 (MUST/SHOULD/MAY) is overkill for machine validation. Human nuance stays in markdown section. |
| `guaranteed` field for outputs | `always/on_success/on_failure` | Outputs aren't "required" — they're conditional on outcome. `guaranteed` better captures when a field appears. |
| close-work-cycle category | `[closure, queue]` (list) | Serves dual role: Close Work (closure) + Release (queue). Per CH-008 decision, memory 84262. |
| Registry format | YAML | Machine-readable, consistent with haios.yaml ecosystem. Can be loaded by Python trivially. |
| Contract types | string, boolean, list, path, integer | Covers all current ceremony fields. Extensible later without breaking. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Dual-category ceremony (close-work-cycle) | `category` accepts string or list | Test 4 extended |
| Ceremony with no inputs (e.g., session-start) | `input_contract: []` (empty list) | Implicit in Test 1 |
| Optional `pattern` field on input | Only validated if present | Test 3 shape check |
| Feedback ceremonies (no skill yet) | Registry marks `has_skill: false` | Test 2 counts all 19 |

### Open Questions

**Q: Should `category` allow lists or just strings?**
Yes — close-work-cycle is both `closure` and `queue`. Use list format `category: [closure, queue]` when dual-role. Validation accepts both string and list.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None — all design decisions resolved above | — | — | — |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_ceremony_contracts.py` with 6 tests
- [ ] Verify all tests fail (red) — modules don't exist yet

### Step 2: Create ceremony_registry.yaml
- [ ] Create `.claude/haios/config/ceremony_registry.yaml` with all 19 ceremonies
- [ ] Populate from L4 ceremony definitions table (functional_requirements.md:326-346)
- [ ] Test 2 passes (green)

### Step 3: Create contract dataclasses
- [ ] Create `.claude/haios/lib/ceremony_contracts.py` with CeremonyContract, ContractField dataclasses
- [ ] Implement `from_frontmatter()` class method
- [ ] Implement `load_ceremony_registry()` function
- [ ] Tests 1, 3, 4 pass (green)

### Step 4: Create ceremony skill template
- [ ] Create `.claude/templates/ceremony/SKILL.md` with contract schema pre-populated
- [ ] Verify template matches schema definition

### Step 5: Integration Verification
- [ ] All 6 tests pass
- [ ] Registry loads and counts 19 ceremonies
- [ ] Template renders valid YAML frontmatter (Test 5)

### Step 6: README Sync
- [ ] Update `.claude/haios/config/` README if exists
- [ ] Update `.claude/templates/` README if exists

---

## Verification

- [ ] Tests pass (6 tests in test_ceremony_contracts.py)
- [ ] Registry loads 19 ceremonies across 6 categories
- [ ] Template produces valid frontmatter when filled in

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema too rigid for future ceremonies | Medium | Keep types extensible, allow optional fields |
| Dual-category adds parsing complexity | Low | Accept both string and list for `category` |
| Registry goes stale like EPOCH.md | Medium | WORK-113 MUST include registry-skill sync verification (auto-compare registry entries vs actual skill files). Critique A5. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 332 | 2026-02-09 | - | PLAN | Plan authored |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Contract YAML schema defined | [ ] | ceremony_contracts.py dataclasses + tests |
| Ceremony registry (YAML) listing all 19 ceremonies | [ ] | ceremony_registry.yaml loads, count == 19 |
| Schema documented in ceremony template file | [ ] | .claude/templates/ceremony/SKILL.md exists with schema |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/ceremony_registry.yaml` | 19 ceremonies, valid YAML | [ ] | |
| `.claude/haios/lib/ceremony_contracts.py` | CeremonyContract, ContractField, load functions | [ ] | |
| `.claude/templates/ceremony/SKILL.md` | Template with contract schema | [ ] | |
| `tests/test_ceremony_contracts.py` | 6 tests, all green | [ ] | |

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-002, lines 326-346)
- @.claude/skills/queue-commit/SKILL.md (reference: current frontmatter format)
- @.claude/skills/close-work-cycle/SKILL.md (reference: dual-category ceremony)
- Memory: 84249, 84251, 84262
