# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:13:52
# Critique Report: Assets Arc (CH-023 through CH-027)

## Executive Summary

The Assets Arc chapters define a coherent system for typed, versioned, pipeable assets with schema validation and provenance tracking. However, a critical structural conflict between CH-023 and CH-027 must be resolved before implementation.

**Overall Verdict: REVISE**

---

## Assumptions Registry

| ID | Chapter | Statement | Confidence | Risk if Wrong |
|----|---------|-----------|------------|---------------|
| A1 | CH-023 | CycleRunner is single entry point for lifecycles | medium | Asset creation bypasses typing |
| A2 | CH-023 | Asset base class fields sufficient for downstream | medium | CH-027 needs more fields |
| A3 | CH-023 | Dependent types (Finding, Decision, etc.) exist | low | Asset classes can't compile |
| A4 | CH-023 | Markdown and dict serialization sufficient | high | Extend later if needed |
| A5 | CH-024 | Symlinks work on Windows | low | Fails without admin |
| A6 | CH-024 | Version numbers sequential integers | high | Acceptable |
| A7 | CH-024 | AssetStore is singleton or consistent | medium | Inconsistent versioning |
| A8 | CH-024 | Storage path structure is fixed | medium | Multiple same-type assets conflict |
| A9 | CH-025 | VALID_PIPES map is complete | medium | Missing transitions block workflows |
| A10 | CH-025 | Asset.pipe() has access to cycle_runner | low | Circular dependency |
| A11 | CH-025 | Piped asset inherits source_work | medium | Multi-work pipeline traceability lost |
| A12 | CH-025 | Findings→Implementation invalid is intentional | high | Design decision |
| A13 | CH-026 | Schema validation only at store time | medium | Invalid assets can be piped |
| A14 | CH-026 | YAML schemas sufficient for type checking | medium | Complex types need runtime checking |
| A15 | CH-026 | FieldSpec type exists | low | Schema validation can't implement |
| A16 | CH-026 | Schemas are static | high | Acceptable for v1 |
| A17 | CH-027 | get_current_agent() exists | low | Author field null/inconsistent |
| A18 | CH-027 | Provenance is immutable | high | No enforcement mechanism |
| A19 | CH-027 | inputs field captures all inputs | medium | Manual tracking error-prone |
| A20 | CH-027 | AssetRef available before storage | medium | Circular dependency |

---

## Critical Structural Conflict

### CH-023 vs CH-027: Incompatible Asset Structures

**CH-023 defines:**
```python
@dataclass
class Asset:
    type: str
    produced_by: str
    source_work: str
    version: int
    timestamp: datetime
    author: str
```

**CH-027 defines:**
```python
@dataclass
class Asset:
    provenance: Provenance  # Wrapper!
    content: Any
```

Where Provenance has the same fields PLUS `inputs` and `piped_from`.

**These are incompatible.** Must reconcile:
- Option A: Merge Provenance fields into CH-023 base class
- Option B: CH-023 Asset embeds Provenance (CH-027 pattern)

**Recommendation:** Option A - flat structure is cleaner.

---

## Chapter-Specific Issues

### CH-023: Lifecycle Asset Types

**Gaps:**
- Asset ID generation undefined
- Error handling on lifecycle failure
- Immutability not enforced

**Missing Types:**
- Finding, Decision, TestResults, CriterionResult, PrioritizedItem

### CH-024: Asset Versioning

**Gaps:**
- Concurrent versioning undefined
- Asset deletion policy undefined
- AssetRef.asset_id generation undefined

**Windows Issue:**
```
latest.md -> v3.md  # Symlink fails without admin
```
Use file-based reference or max-version query instead.

### CH-025: Asset Piping

**Gaps:**
- Work ID propagation in multi-work pipelines
- Store-then-pipe combination (either/or?)
- Pipe failure handling/rollback

**Conflict with CH-004:**
- CH-004: `cycle_runner.chain()`
- CH-025: `asset.pipe()`

Two chaining mechanisms. Should unify.

**Circular Dependency:**
Asset.pipe() calls CycleRunner. Asset is returned by CycleRunner. Need mediator pattern.

### CH-026: Asset Schemas

**Gaps:**
- Nested type validation undefined
- FieldSpec type not defined
- Schema path should use ConfigLoader
- Optional field defaults undefined

**Redundancy with CH-023:**
CH-023 has typed dataclasses. CH-026 has YAML schemas. These are duplicative.

**Recommendation:** Use Pydantic for both runtime validation and schema.

### CH-027: Asset Provenance

**Gaps:**
- Input tracking automation
- get_assets_by_work() implementation undefined
- Provenance vs Asset base class reconciliation

---

## Missing Definitions

| Missing | Needed By |
|---------|-----------|
| asset_id generation | CH-024, CH-025, CH-027 |
| FieldSpec type | CH-026 |
| Finding, Decision, etc. | CH-023, CH-026 |
| get_current_agent() | CH-027 |

---

## Interface Inconsistencies

| Issue | Chapters | Description |
|-------|----------|-------------|
| Asset structure | CH-023, CH-027 | Flat fields vs Provenance wrapper |
| Version metadata | CH-023, CH-024 | previous_version not in base class |
| Chaining mechanism | CH-025, CH-004 | pipe() vs chain() |
| Schema validation | CH-023, CH-026 | Dataclasses vs YAML schemas |

---

## Recommendations

### Priority 1 (Blocking)

1. **Reconcile Asset structure**: Merge CH-027 Provenance fields into CH-023 base class
2. **Define asset_id generation**: Add to Asset base class (UUID or deterministic)

### Priority 2 (High)

3. **Remove symlink dependency**: Use get_latest() query
4. **Single chaining mechanism**: Choose asset.pipe(), remove cycle_runner.chain()
5. **Define FieldSpec or use Pydantic**: Unify typing and validation

### Priority 3 (Medium)

6. **Error handling**: Specify failure behavior in all chapters
7. **Concurrent access**: CH-024 needs locking or optimistic versioning
8. **Input tracking**: CH-027 inputs field needs automation

---

*Critique generated: 2026-02-03*
*Verdict: REVISE*
