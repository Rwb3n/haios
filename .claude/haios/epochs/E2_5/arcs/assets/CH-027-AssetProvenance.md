# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:36:39
# Chapter: Asset Provenance

## Definition

**Chapter ID:** CH-027
**Arc:** assets
**Status:** Planned
**Implementation Type:** CREATE NEW (integrated into CH-023 Asset base class)
**Depends:** CH-023
**Work Items:** None

---

## Current State (Verified)

No provenance tracking exists:
- No Provenance class
- No provenance frontmatter in output files
- No `get_current_agent()` function

**What exists:**
- Work items have `memory_refs` for concept links
- governance-events.jsonl tracks some agent actions
- No asset-level provenance

**What doesn't exist:**
- Provenance fields in any class
- piped_from tracking
- get_provenance_chain() function
- get_assets_by_work() function

---

## Structure Decision (Aligns with CH-023)

**Per CH-023 decision:** Provenance fields are FLAT in Asset base class, not wrapped.

```python
# CORRECT (flat structure per CH-023)
@dataclass
class Asset:
    asset_id: str
    type: str
    produced_by: str
    source_work: str
    version: int
    timestamp: datetime
    author: str
    inputs: List[str] = field(default_factory=list)
    piped_from: Optional[AssetRef] = None

# REJECTED (wrapper structure)
@dataclass
class Asset:
    provenance: Provenance  # NO - flat fields instead
    content: Any
```

This chapter defines the FIELDS; CH-023 defines the CLASS STRUCTURE.

---

## Problem

Assets have no provenance. Need provenance fields for traceability.

---

## Agent Need

> "I need every asset to have provenance metadata so I can trace who made it, when, from what source, and which lifecycle produced it."

---

## Requirements

### R1: Provenance Frontmatter (REQ-ASSET-005)

Every asset has frontmatter:

```yaml
---
asset_type: findings
produced_by: investigation
source_work: WORK-001
version: 1
timestamp: 2026-02-03T01:00:00
author: Hephaestus
inputs:
  - question.md
piped_from: null  # or asset_ref if piped
---
```

### R2: Provenance Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| asset_type | string | Yes | findings, specification, etc. |
| produced_by | string | Yes | Lifecycle that created this |
| source_work | string | Yes | WORK-XXX that produced this |
| version | int | Yes | Version number |
| timestamp | datetime | Yes | Creation timestamp |
| author | string | Yes | Agent/human who created |
| inputs | list | No | Input files/assets used |
| piped_from | AssetRef | No | Previous asset if piped |

### R3: Provenance Chain

For piped assets, chain is traceable:

```yaml
# findings.md
---
asset_type: findings
piped_from: null
---

# specification.md
---
asset_type: specification
piped_from:
  asset_id: findings-001
  version: 1
---

# artifact metadata
---
asset_type: artifact
piped_from:
  asset_id: spec-001
  version: 2
---
```

Full chain: findings → specification → artifact

---

## Interface

### Provenance Fields (Flat in Asset Base Class)

Per CH-023 decision, provenance fields are directly on Asset:

```python
@dataclass
class Asset:
    """Base class with provenance fields."""
    # Identity
    asset_id: str
    type: str

    # Provenance fields (not wrapped)
    produced_by: str
    source_work: str
    version: int
    timestamp: datetime
    author: str
    inputs: List[str] = field(default_factory=list)
    piped_from: Optional[AssetRef] = None

    def provenance_to_frontmatter(self) -> str:
        """Serialize provenance fields to YAML frontmatter."""
        return yaml.dump({
            'asset_id': self.asset_id,
            'asset_type': self.type,
            'produced_by': self.produced_by,
            'source_work': self.source_work,
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'author': self.author,
            'inputs': self.inputs,
            'piped_from': self.piped_from.to_dict() if self.piped_from else None,
        })

    def to_markdown(self) -> str:
        """Serialize with provenance frontmatter."""
        return f"---\n{self.provenance_to_frontmatter()}---\n\n{self.content_to_markdown()}"
```

**NOTE:** No separate Provenance class needed. Fields live directly on Asset.

### Provenance Queries

```python
def get_provenance_chain(asset_ref: AssetRef) -> List[Provenance]:
    """Get full provenance chain for asset."""
    chain = []
    current = asset_store.get_latest(asset_ref)
    while current.provenance.piped_from:
        chain.append(current.provenance)
        current = asset_store.get_latest(current.provenance.piped_from)
    chain.append(current.provenance)
    return list(reversed(chain))

def get_assets_by_work(work_id: str) -> List[AssetRef]:
    """Get all assets produced by a work item."""
```

### Automatic Provenance

CycleRunner sets provenance automatically:

```python
def run(work_id: str, lifecycle: str, input: Asset = None) -> Asset:
    # ... run lifecycle ...

    output = create_asset(lifecycle_output)
    output.provenance = Provenance(
        asset_type=LIFECYCLE_ASSET_TYPES[lifecycle],
        produced_by=lifecycle,
        source_work=work_id,
        version=1,
        timestamp=datetime.now(),
        author=get_current_agent(),
        piped_from=input.ref if input else None
    )
    return output
```

---

## Success Criteria

- [ ] Provenance dataclass defined
- [ ] All assets include provenance frontmatter
- [ ] Provenance auto-populated by CycleRunner
- [ ] piped_from tracks input asset
- [ ] get_provenance_chain() works
- [ ] get_assets_by_work() works
- [ ] Parsing from markdown works
- [ ] Unit tests for provenance operations
- [ ] Integration test: pipe chain → verify full provenance

---

## Non-Goals

- Cryptographic verification (trust-based)
- External provenance standards (internal format)
- Provenance editing (immutable once set)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ASSET-005)
- @.claude/haios/epochs/E2_5/arcs/assets/CH-023-LifecycleAssetTypes.md (asset structure)
- @.claude/haios/epochs/E2_5/arcs/assets/CH-025-AssetPiping.md (piping context)
