# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:35:44
# Chapter: Asset Piping

## Definition

**Chapter ID:** CH-025
**Arc:** assets
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-023, Lifecycles:CH-004
**Work Items:** None

---

## Current State (Verified)

No asset piping exists:
- No Asset.pipe() method
- No VALID_PIPES constraint map
- CycleRunner has no `input` parameter

**What exists:**
- CycleRunner validates phases
- CH-004 defines CycleRunner.chain() for explicit chaining
- Lifecycle outputs stored as files

**What doesn't exist:**
- Asset.pipe() method
- Asset.store() method
- CycleRunner.run(input=...) parameter
- VALID_PIPES type compatibility map

**Unify Chaining Mechanisms (per critique):**
CH-004 proposes `cycle_runner.chain()`. CH-025 proposes `asset.pipe()`.

**DECISION:** Use `asset.pipe()` only. Remove `cycle_runner.chain()` from CH-004.

Rationale: Assets carry data; chaining is about data flow. The asset should own the piping.

---

## Problem

No asset piping. Need pipe() method with type compatibility validation.

---

## Agent Need

> "I need to pipe assets directly from one lifecycle to another, like Unix pipes, so Investigation findings can flow directly into Design."

---

## Requirements

### R1: Pipe or Store (REQ-ASSET-003)

Assets can be:
1. Piped to next lifecycle (direct flow)
2. Stored standalone (no downstream)

```python
# Pipe: output feeds directly to next
spec = investigation | design  # Findings → Spec

# Store: output saved, nothing downstream
investigation > findings_file  # Findings → file
```

### R2: Pipe Syntax

```python
# Python API
findings = cycle_runner.run(work_id, "investigation")
spec = cycle_runner.run(work_id, "design", input=findings)

# Or fluent
spec = (
    cycle_runner
    .run(work_id, "investigation")
    .pipe("design")
)
```

### R3: Type Compatibility

Piping validates type compatibility:

| From | To | Valid | Reason |
|------|-----|-------|--------|
| Findings | Design | Yes | Findings inform spec |
| Specification | Implementation | Yes | Spec guides code |
| Artifact | Validation | Yes | Code needs testing |
| Findings | Implementation | No | Findings don't directly guide code |

```python
VALID_PIPES = {
    "findings": ["design"],
    "specification": ["implementation"],
    "artifact": ["validation"],
    "verdict": [],  # Terminal
    "priority_list": ["design", "investigation"],  # Can spawn either
}
```

---

## Interface

### Piping API

```python
class Asset:
    def pipe(self, to_lifecycle: str) -> Asset:
        """Pipe this asset to another lifecycle."""
        if to_lifecycle not in VALID_PIPES[self.type]:
            raise InvalidPipeError(f"Cannot pipe {self.type} to {to_lifecycle}")
        return cycle_runner.run(
            work_id=self.source_work,
            lifecycle=to_lifecycle,
            input=self
        )

    def store(self, path: Path = None) -> AssetRef:
        """Store asset to filesystem."""
        return asset_store.store(self, path)
```

### Store API

```python
# Explicit store
ref = findings.store()  # Uses default path

# Store with custom path
ref = findings.store(Path("docs/investigations/user-auth-findings.md"))
```

### CycleRunner Changes

```python
def run(
    work_id: str,
    lifecycle: str,
    input: Asset = None  # Optional piped input
) -> Asset:
    """
    Run lifecycle.

    Args:
        work_id: Work item ID
        lifecycle: Lifecycle to run
        input: Optional asset from previous lifecycle (piping)
    """
```

### Chaining Example

```python
# Full pipeline
verdict = (
    cycle_runner.run(work_id, "investigation")
    .pipe("design")
    .pipe("implementation")
    .pipe("validation")
)

# Or stored at each step
findings = cycle_runner.run(work_id, "investigation")
findings.store()

spec = findings.pipe("design")
spec.store()

artifact = spec.pipe("implementation")
artifact.store()
```

---

## Success Criteria

- [ ] Asset.pipe() method implemented
- [ ] Asset.store() method implemented
- [ ] Type compatibility enforced
- [ ] CycleRunner accepts input parameter
- [ ] Piped input available within lifecycle
- [ ] Invalid pipes raise error
- [ ] Unit tests for valid pipes
- [ ] Unit tests for invalid pipes
- [ ] Integration test: investigation → design → implementation chain

---

## Non-Goals

- Parallel pipes (sequential only)
- Pipe branching (one output, one destination)
- Automatic pipe detection (explicit only)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ASSET-003)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-004-CallerChaining.md (caller decides piping)
