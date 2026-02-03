# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:35:31
# Chapter: Asset Versioning

## Definition

**Chapter ID:** CH-024
**Arc:** assets
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-023
**Work Items:** None

---

## Current State (Verified)

No asset versioning exists:
- Files are overwritten on edit
- No AssetStore class
- No version directories

**What exists:**
- Git provides implicit versioning of files
- Work items have `node_history` for state changes

**What doesn't exist:**
- AssetStore class
- Version-based storage layout
- get_version(), get_latest(), list_versions() methods
- AssetRef type

**Windows Consideration (per critique):**
Symlinks require admin privileges on Windows. Use file-based "latest" tracking instead:
```python
# Instead of symlinks
def get_latest(asset_id: str) -> Asset:
    versions = list_versions(asset_id)
    return versions[-1]  # Highest version number
```

---

## Problem

No asset versioning. Need append-only versioning with version history queryable.

---

## Agent Need

> "I need assets to be versioned so edits create new versions while preserving old ones, enabling history tracking and rollback if needed."

---

## Requirements

### R1: Append-Only Versioning (REQ-ASSET-002)

Edit creates new version, old preserved:

```
findings_v1.md  # Original
findings_v2.md  # After revision
findings_v3.md  # After second revision
```

Or directory-based:
```
findings/
  v1.md
  v2.md
  v3.md
  latest.md -> v3.md  # Symlink to latest
```

### R2: Version Metadata

Each version tracks:
```yaml
---
version: 2
previous_version: 1
created_from: WORK-001
created_at: 2026-02-03T01:00:00
change_summary: "Added batch mode findings"
---
```

### R3: Version Operations

```python
# Create new version
new_asset = asset_store.create_version(asset, changes)
# asset.version=1 preserved, new_asset.version=2 created

# Get specific version
v1 = asset_store.get_version(asset_id, version=1)

# Get latest
latest = asset_store.get_latest(asset_id)

# List versions
versions = asset_store.list_versions(asset_id)
```

---

## Interface

### AssetStore Class

```python
class AssetStore:
    """Manage versioned asset storage."""

    def store(self, asset: Asset) -> AssetRef:
        """Store asset, returns reference."""

    def create_version(self, asset: Asset, changes: str) -> Asset:
        """Create new version from existing asset."""

    def get_version(self, ref: AssetRef, version: int) -> Asset:
        """Get specific version."""

    def get_latest(self, ref: AssetRef) -> Asset:
        """Get latest version."""

    def list_versions(self, ref: AssetRef) -> List[VersionInfo]:
        """List all versions with metadata."""
```

### AssetRef

```python
@dataclass
class AssetRef:
    """Reference to versioned asset."""
    asset_id: str      # Unique identifier
    asset_type: str    # findings, specification, etc.
    work_id: str       # Source work item
    path: Path         # Storage location
```

### Storage Layout

```
assets/
  WORK-001/
    findings/
      v1.md
      v2.md
    specification/
      v1.md
  WORK-002/
    findings/
      v1.md
```

### Version Diff

```python
def diff_versions(ref: AssetRef, v1: int, v2: int) -> str:
    """Get diff between two versions."""
```

---

## Success Criteria

- [ ] AssetStore class implemented
- [ ] store() creates v1
- [ ] create_version() creates v(n+1), preserves v(n)
- [ ] get_version() retrieves specific version
- [ ] get_latest() retrieves highest version
- [ ] Version metadata in frontmatter
- [ ] Storage layout works
- [ ] Unit tests for versioning operations
- [ ] Integration test: create → edit → verify both versions exist

---

## Non-Goals

- Automatic merging (versions are independent)
- Branch-based versioning (linear only)
- Compression/deduplication (future optimization)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ASSET-002)
- @.claude/haios/epochs/E2_5/arcs/assets/CH-023-LifecycleAssetTypes.md (asset types)
