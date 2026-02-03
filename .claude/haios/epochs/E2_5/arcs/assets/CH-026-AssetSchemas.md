# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:36:09
# Chapter: Asset Schemas

## Definition

**Chapter ID:** CH-026
**Arc:** assets
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-023
**Work Items:** None

---

## Current State (Verified)

No asset schemas exist:
- No `config/schemas/` directory
- No schema validation in codebase
- No AssetSchema class

**What exists:**
- Pydantic is not currently used in HAIOS
- YAML validation via yaml.safe_load() only

**What doesn't exist:**
- Schema files (findings.yaml, specification.yaml, etc.)
- AssetSchema class
- FieldSpec type
- validate() method

**Schema Approach (per critique):**

Option A: YAML schemas + custom validation
Option B: Pydantic models (recommended)

**DECISION:** Use Pydantic for schema validation.

Rationale: Pydantic provides both runtime validation and type hints. Asset dataclasses become Pydantic models. Single source of truth.

```python
from pydantic import BaseModel

class FindingsAsset(BaseModel):
    asset_id: str
    type: Literal["findings"] = "findings"
    question: str
    findings: List[Finding]
    conclusion: str
    evidence: List[str] = []
```

No separate YAML schemas needed - Pydantic model IS the schema.

---

## Problem

No schema validation for assets. Need validation before storage.

---

## Agent Need

> "I need asset schemas to validate that each asset type has required fields and correct structure, catching invalid assets before they're stored."

---

## Requirements

### R1: Lifecycle-Specific Schemas (REQ-ASSET-004)

Each asset type has schema:

```yaml
# findings_schema.yaml
type: findings
required_fields:
  - question
  - findings
  - conclusion
optional_fields:
  - evidence
  - methodology
  - limitations
```

### R2: Schema Validation

Assets validated before storage:

```python
def store(asset: Asset) -> AssetRef:
    schema = load_schema(asset.type)
    validation = schema.validate(asset)
    if not validation.valid:
        raise SchemaValidationError(validation.errors)
    # ... proceed with storage
```

### R3: Schema Definitions

**Findings Schema:**
```yaml
type: findings
required_fields:
  question: string
  findings: list[Finding]
  conclusion: string
optional_fields:
  evidence: list[string]
  methodology: string
  next_steps: list[string]
```

**Specification Schema:**
```yaml
type: specification
required_fields:
  requirements: list[string]
  interface: string
  success_criteria: list[string]
optional_fields:
  design_decisions: list[Decision]
  non_goals: list[string]
  open_questions: list[string]
```

**Artifact Schema:**
```yaml
type: artifact
required_fields:
  files_created: list[path]
  entry_point: path
optional_fields:
  files_modified: list[path]
  dependencies_added: list[string]
  test_results: TestResults
```

**Verdict Schema:**
```yaml
type: verdict
required_fields:
  passed: boolean
  criteria_results: list[CriterionResult]
optional_fields:
  evidence: list[string]
  recommendations: list[string]
```

**PriorityList Schema:**
```yaml
type: priority_list
required_fields:
  items: list[PrioritizedItem]
optional_fields:
  rationale: string
  excluded: list[string]
```

---

## Interface

### Schema Files

```
config/schemas/
  findings.yaml
  specification.yaml
  artifact.yaml
  verdict.yaml
  priority_list.yaml
```

### Schema Class

```python
@dataclass
class AssetSchema:
    type: str
    required_fields: Dict[str, FieldSpec]
    optional_fields: Dict[str, FieldSpec]

    @classmethod
    def load(cls, schema_path: Path) -> "AssetSchema":
        """Load schema from YAML file."""

    def validate(self, asset: Asset) -> ValidationResult:
        """Validate asset against schema."""
        errors = []
        for field, spec in self.required_fields.items():
            if not hasattr(asset, field):
                errors.append(f"Missing required field: {field}")
            elif not spec.validate(getattr(asset, field)):
                errors.append(f"Invalid value for {field}")
        return ValidationResult(valid=len(errors)==0, errors=errors)
```

### Validation Integration

```python
# In AssetStore.store()
def store(self, asset: Asset) -> AssetRef:
    # Load and validate against schema
    schema = AssetSchema.load(f"schemas/{asset.type}.yaml")
    result = schema.validate(asset)
    if not result.valid:
        raise SchemaValidationError(result.errors)

    # Proceed with storage
    ...
```

---

## Success Criteria

- [ ] 5 schema files created (one per asset type)
- [ ] AssetSchema class loads YAML schemas
- [ ] validate() checks required fields
- [ ] validate() checks field types
- [ ] AssetStore validates before storing
- [ ] Invalid assets rejected with clear errors
- [ ] Unit tests for schema validation
- [ ] Integration test: invalid asset → rejection with error message

---

## Non-Goals

- Complex type validation (basic types only)
- Schema evolution/migration (future work)
- Cross-asset validation (schemas are per-asset)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ASSET-004)
- @.claude/haios/epochs/E2_5/arcs/assets/CH-023-LifecycleAssetTypes.md (asset types to schema)
