---
template: implementation_plan
status: complete
date: 2026-01-29
backlog_id: WORK-031
title: CorpusLoader Module Implementation
author: Hephaestus
lifecycle_phase: plan
session: 247
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-29T19:45:21'
---
# Implementation Plan: CorpusLoader Module Implementation

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

CorpusLoader module will provide YAML-configurable file discovery that enables RequirementExtractor to work on arbitrary document corpora instead of hardcoded paths.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `requirement_extractor.py`, `cli.py` |
| Lines of code affected | ~30 | Integration in RequirementExtractor (lines 355-363) |
| New files to create | 3 | `corpus_loader.py`, `test_corpus_loader.py`, `corpus/haios-requirements.yaml` |
| Tests to write | 8 | Based on acceptance criteria |
| Dependencies | 1 | `requirement_extractor.py` consumes CorpusLoader |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only RequirementExtractor consumes this |
| Risk of regression | Low | Adding new module, not modifying existing behavior |
| External dependencies | Low | No external APIs, pure file system operations |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests First | 30 min | High |
| CorpusLoader Implementation | 45 min | High |
| CLI Integration | 20 min | High |
| RequirementExtractor Wiring | 15 min | High |
| **Total** | ~2 hr | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/requirement_extractor.py:355-363
def _discover_files(self) -> List[Path]:
    """Discover markdown files in corpus.

    Returns:
        List of markdown file paths.
    """
    if self.corpus_path.is_file():
        return [self.corpus_path]
    return list(self.corpus_path.rglob("*.md"))
```

**Behavior:** RequirementExtractor discovers files via hardcoded `rglob("*.md")` pattern.

**Result:** Returns ALL markdown files in directory - no filtering, no configuration, no multi-source support.

### Desired State

```python
# .claude/haios/modules/corpus_loader.py - NEW
class CorpusLoader:
    def __init__(self, corpus_config: Path | dict):
        """Initialize with corpus definition."""
        self.config = self._load_config(corpus_config)

    def discover(self) -> List[Path]:
        """Return all files matching corpus definition."""
        # Aggregates from multiple sources, applies filters and exclusions

    def filter_by_type(self, doc_type: str) -> List[Path]:
        """Return files matching specific document type."""

# .claude/haios/modules/requirement_extractor.py - MODIFIED
class RequirementExtractor:
    def __init__(self, corpus: Path | CorpusLoader):
        """Accept either path (legacy) or CorpusLoader."""
        if isinstance(corpus, CorpusLoader):
            self.loader = corpus
            self.corpus_path = None
        else:
            self.loader = None
            self.corpus_path = Path(corpus)
```

**Behavior:** RequirementExtractor accepts CorpusLoader which provides configurable file discovery.

**Result:** Corpus defined via YAML - multiple sources, patterns, filters, exclusions all configurable.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Load Corpus Config from YAML
```python
def test_load_corpus_from_yaml(tmp_path):
    """CorpusLoader loads configuration from YAML file."""
    config_file = tmp_path / "corpus.yaml"
    config_file.write_text("""
corpus:
  name: test-corpus
  sources:
    - path: docs/specs
      pattern: "*.md"
""")
    loader = CorpusLoader(config_file)
    assert loader.config["corpus"]["name"] == "test-corpus"
```

### Test 2: Discover Files from Single Source
```python
def test_discover_single_source(tmp_path):
    """discover() returns files matching pattern from single source."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "spec.md").touch()
    (tmp_path / "docs" / "readme.txt").touch()

    config = {"corpus": {"sources": [{"path": "docs", "pattern": "*.md"}]}}
    loader = CorpusLoader(config, base_path=tmp_path)
    files = loader.discover()

    assert len(files) == 1
    assert files[0].name == "spec.md"
```

### Test 3: Discover Files from Multiple Sources
```python
def test_discover_multiple_sources(tmp_path):
    """discover() aggregates files from multiple sources."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "specs").mkdir()
    (tmp_path / "docs" / "doc.md").touch()
    (tmp_path / "specs" / "trd.md").touch()

    config = {"corpus": {"sources": [
        {"path": "docs", "pattern": "*.md"},
        {"path": "specs", "pattern": "*.md"}
    ]}}
    loader = CorpusLoader(config, base_path=tmp_path)
    files = loader.discover()

    assert len(files) == 2
```

### Test 4: Exclusion Patterns Work
```python
def test_exclusion_patterns(tmp_path):
    """discover() excludes files matching exclusion patterns."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "archive").mkdir()
    (tmp_path / "docs" / "spec.md").touch()
    (tmp_path / "docs" / "archive" / "old.md").touch()

    config = {"corpus": {
        "sources": [{"path": "docs", "pattern": "*.md", "include_subdirs": True}],
        "exclude": ["**/archive/**"]
    }}
    loader = CorpusLoader(config, base_path=tmp_path)
    files = loader.discover()

    assert len(files) == 1
    assert "archive" not in str(files[0])
```

### Test 5: Filter by Document Type
```python
def test_filter_by_type(tmp_path):
    """filter_by_type() returns only files matching doc type filter."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-spec.md").touch()
    (tmp_path / "docs" / "ADR-001.md").touch()

    config = {"corpus": {"sources": [
        {"path": "docs", "pattern": "*.md", "filters": [{"type": "TRD"}]}
    ]}}
    loader = CorpusLoader(config, base_path=tmp_path)
    files = loader.filter_by_type("TRD")

    assert len(files) == 1
    assert "TRD" in files[0].name
```

### Test 6: Subdirectory Inclusion Control
```python
def test_include_subdirs_false(tmp_path):
    """include_subdirs=false limits discovery to direct children."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "sub").mkdir()
    (tmp_path / "docs" / "top.md").touch()
    (tmp_path / "docs" / "sub" / "nested.md").touch()

    config = {"corpus": {"sources": [
        {"path": "docs", "pattern": "*.md", "include_subdirs": False}
    ]}}
    loader = CorpusLoader(config, base_path=tmp_path)
    files = loader.discover()

    assert len(files) == 1
    assert files[0].name == "top.md"
```

### Test 7: RequirementExtractor Accepts CorpusLoader
```python
def test_requirement_extractor_with_corpus_loader(tmp_path):
    """RequirementExtractor works with CorpusLoader as file source."""
    (tmp_path / "docs").mkdir()
    spec_file = tmp_path / "docs" / "spec.md"
    spec_file.write_text("| R0 | Must do something | MUST |")

    config = {"corpus": {"sources": [{"path": "docs", "pattern": "*.md"}]}}
    loader = CorpusLoader(config, base_path=tmp_path)
    extractor = RequirementExtractor(loader)
    result = extractor.extract()

    assert len(result.requirements) >= 1
```

### Test 8: Backward Compatibility - Path Still Works
```python
def test_requirement_extractor_path_backward_compat(tmp_path):
    """RequirementExtractor still accepts Path for backward compatibility."""
    (tmp_path / "spec.md").write_text("| R0 | Test | MUST |")

    extractor = RequirementExtractor(tmp_path)
    result = extractor.extract()

    assert len(result.requirements) >= 1
```

---

## Detailed Design

### Exact Code Change

**File 1: NEW `.claude/haios/modules/corpus_loader.py`**

```python
"""
CorpusLoader Module (WORK-031, CH-001)

Provides YAML-configurable file discovery for RequirementExtractor.
Enables Pipeline to work on arbitrary document corpora.

Interface (per CH-001):
    loader = CorpusLoader(corpus_config)
    files = loader.discover()
    filtered = loader.filter_by_type("TRD")
"""
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class CorpusSource:
    """Single source definition within a corpus."""
    path: str
    pattern: str = "*.md"
    include_subdirs: bool = True
    filters: List[Dict] = field(default_factory=list)


@dataclass
class CorpusConfig:
    """Parsed corpus configuration."""
    name: str
    version: str
    sources: List[CorpusSource]
    exclude: List[str] = field(default_factory=list)


class CorpusLoader:
    """Load and discover files from a configured corpus."""

    def __init__(
        self,
        corpus_config: Union[Path, Dict],
        base_path: Optional[Path] = None
    ):
        """Initialize with corpus definition.

        Args:
            corpus_config: Path to YAML file or dict with corpus definition.
            base_path: Base directory for resolving relative paths.
                       Defaults to current working directory.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.config = self._load_config(corpus_config)
        self._parsed = self._parse_config()

    def _load_config(self, config: Union[Path, Dict]) -> Dict:
        """Load configuration from path or use dict directly."""
        if isinstance(config, dict):
            return config
        with open(config, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _parse_config(self) -> CorpusConfig:
        """Parse raw config dict into typed CorpusConfig."""
        corpus = self.config.get("corpus", self.config)
        sources = []
        for src in corpus.get("sources", []):
            sources.append(CorpusSource(
                path=src["path"],
                pattern=src.get("pattern", "*.md"),
                include_subdirs=src.get("include_subdirs", True),
                filters=src.get("filters", [])
            ))
        return CorpusConfig(
            name=corpus.get("name", "unnamed"),
            version=corpus.get("version", "1.0"),
            sources=sources,
            exclude=corpus.get("exclude", [])
        )

    def discover(self) -> List[Path]:
        """Return all files matching corpus definition.

        Returns:
            List of absolute file paths matching all sources,
            with exclusions applied.
        """
        all_files = []
        for source in self._parsed.sources:
            source_path = self.base_path / source.path
            if not source_path.exists():
                logger.warning(f"Source path does not exist: {source_path}")
                continue

            if source.include_subdirs:
                files = list(source_path.rglob(source.pattern))
            else:
                files = list(source_path.glob(source.pattern))

            all_files.extend(files)

        # Apply exclusions
        return self._apply_exclusions(all_files)

    def _apply_exclusions(self, files: List[Path]) -> List[Path]:
        """Filter out files matching exclusion patterns.

        Uses PurePath.match() which supports ** recursive glob patterns,
        unlike fnmatch which treats * as single-directory only.
        """
        if not self._parsed.exclude:
            return files

        from pathlib import PurePath
        result = []
        for f in files:
            try:
                rel_path = f.relative_to(self.base_path)
            except ValueError:
                # File not under base_path (e.g., symlink) - skip exclusion check
                result.append(f)
                continue
            excluded = any(
                PurePath(rel_path).match(pattern)
                for pattern in self._parsed.exclude
            )
            if not excluded:
                result.append(f)
        return result

    def filter_by_type(self, doc_type: str) -> List[Path]:
        """Return files matching specific document type.

        Args:
            doc_type: Document type to filter (e.g., "TRD", "ADR").

        Returns:
            List of files where filename contains doc_type.
        """
        all_files = self.discover()
        return [f for f in all_files if doc_type.upper() in f.name.upper()]
```

**File 2: MODIFY `.claude/haios/modules/requirement_extractor.py` lines 280-303**

**Current Code:**
```python
# Lines 280-303
class RequirementExtractor:
    """Main extractor that orchestrates parsing across a corpus.

    Usage:
        extractor = RequirementExtractor(Path("docs/specs"))
        result = extractor.extract()
        print(f"Found {len(result.requirements)} requirements")
    """

    VERSION = "1.0.0"

    def __init__(self, corpus_path: Path):
        """Initialize with corpus root path.

        Args:
            corpus_path: Root directory to scan for documents.
        """
        self.corpus_path = Path(corpus_path)
        self.parsers: List[Parser] = [
            TRDParser(),
            ManifestoParser(),
            NaturalLanguageParser()  # Fallback, must be last
        ]
```

**Changed Code:**
```python
# Lines 280-310 - MODIFIED
# Import at top of file
try:
    from .corpus_loader import CorpusLoader
except ImportError:
    from corpus_loader import CorpusLoader


class RequirementExtractor:
    """Main extractor that orchestrates parsing across a corpus.

    Usage (legacy):
        extractor = RequirementExtractor(Path("docs/specs"))
        result = extractor.extract()

    Usage (with CorpusLoader):
        loader = CorpusLoader(config_path)
        extractor = RequirementExtractor(loader)
        result = extractor.extract()
    """

    VERSION = "1.1.0"  # Bumped for CorpusLoader integration

    def __init__(self, corpus: Union[Path, 'CorpusLoader']):
        """Initialize with corpus path or CorpusLoader.

        Args:
            corpus: Either a Path (legacy) or CorpusLoader instance.
        """
        if hasattr(corpus, 'discover'):  # Duck-type CorpusLoader
            self.loader = corpus
            self.corpus_path = None
        else:
            self.loader = None
            self.corpus_path = Path(corpus)
        self.parsers: List[Parser] = [
            TRDParser(),
            ManifestoParser(),
            NaturalLanguageParser()  # Fallback, must be last
        ]
```

**File 3: MODIFY `.claude/haios/modules/requirement_extractor.py` lines 305-326 (extract method)**

**Current Code:**
```python
def extract(self) -> RequirementSet:
    """Extract all requirements from corpus."""
    all_requirements = []
    for file_path in self._discover_files():
        # ... extraction logic ...
    return RequirementSet(
        source_corpus=str(self.corpus_path),  # <-- BUG: None when loader used
        extracted_at=datetime.now(),
        # ...
    )
```

**Changed Code:**
```python
def extract(self) -> RequirementSet:
    """Extract all requirements from corpus."""
    all_requirements = []
    for file_path in self._discover_files():
        # ... extraction logic ...

    # Fix A5: Handle source_corpus when CorpusLoader is used
    if self.loader:
        source = self.loader._parsed.name  # Get corpus name from config
    else:
        source = str(self.corpus_path)

    return RequirementSet(
        source_corpus=source,  # <-- FIXED: Uses corpus name or path
        extracted_at=datetime.now(),
        # ...
    )
```

**File 4: MODIFY `.claude/haios/modules/requirement_extractor.py` lines 355-363 (_discover_files)**

**Current Code:**
```python
def _discover_files(self) -> List[Path]:
    """Discover markdown files in corpus.

    Returns:
        List of markdown file paths.
    """
    if self.corpus_path.is_file():
        return [self.corpus_path]
    return list(self.corpus_path.rglob("*.md"))
```

**Changed Code:**
```python
def _discover_files(self) -> List[Path]:
    """Discover markdown files in corpus.

    Returns:
        List of markdown file paths.
    """
    if self.loader:
        return self.loader.discover()
    # Legacy path-based discovery
    if self.corpus_path.is_file():
        return [self.corpus_path]
    return list(self.corpus_path.rglob("*.md"))
```

### Call Chain Context

```
RequirementExtractor.extract()
    |
    +-> _discover_files()      # <-- What we're changing
    |       |
    |       +-> CorpusLoader.discover()  # NEW delegation
    |       |       Returns: List[Path]
    |       |
    |       +-> (legacy) rglob("*.md")   # Backward compat
    |           Returns: List[Path]
    |
    +-> extract_from_file(path)
            Returns: List[Requirement]
```

### Function/Component Signatures

```python
class CorpusLoader:
    def __init__(
        self,
        corpus_config: Union[Path, Dict],
        base_path: Optional[Path] = None
    ):
        """
        Initialize with corpus definition.

        Args:
            corpus_config: Path to YAML file or dict config.
            base_path: Root for resolving relative paths.

        Raises:
            FileNotFoundError: If YAML config path doesn't exist.
            yaml.YAMLError: If config is invalid YAML.
        """

    def discover(self) -> List[Path]:
        """
        Return all files matching corpus definition.

        Returns:
            List of absolute paths, exclusions applied.
        """

    def filter_by_type(self, doc_type: str) -> List[Path]:
        """
        Return files matching document type filter.

        Args:
            doc_type: Type string (e.g., "TRD", "ADR").

        Returns:
            Subset of discover() matching type.
        """
```

### Behavior Logic

**Current Flow:**
```
RequirementExtractor(path)
    → _discover_files()
        → rglob("*.md")  # ALL markdown files
            → [file1.md, file2.md, archive/old.md, ...]
```

**New Flow:**
```
RequirementExtractor(CorpusLoader) or RequirementExtractor(path)
    → _discover_files()
        ├─ Has loader? YES → loader.discover()
        │                       → Aggregate from sources
        │                       → Apply exclusions
        │                       → [filtered files]
        │
        └─ Has loader? NO  → (legacy) rglob("*.md")
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Duck-typing for CorpusLoader | Check `hasattr(corpus, 'discover')` | Avoids import dependency in type check, supports any object with discover() method |
| base_path parameter | Optional, defaults to cwd | Enables test isolation with tmp_path fixtures |
| YAML config format | Nested `corpus:` key | Matches existing HAIOS config patterns (haios.yaml) |
| Exclusion via PurePath.match() | Use pathlib instead of fnmatch | fnmatch does NOT support `**` recursive patterns (A3 critique fix) |
| Sibling import pattern | try/except conditional | Matches work_engine.py pattern (lines 49-54) |
| Version bump | 1.0.0 → 1.1.0 | Backward-compatible addition per semver |
| source_corpus from loader | Use `self.loader._parsed.name` | Fix A5: extract() used str(None) when corpus_path was None |
| relative_to() safety | try/except ValueError | Handle symlinks or absolute paths gracefully (A4 critique) |

### Input/Output Examples

**Current behavior with path:**
```
extractor = RequirementExtractor(Path("docs"))
files = extractor._discover_files()
# Returns: ALL .md files including archive, deprecated, etc.
# Count: 847 files in HAIOS docs/
```

**New behavior with CorpusLoader:**
```yaml
# .claude/haios/config/corpus/haios-requirements.yaml
corpus:
  name: haios-requirements
  version: "1.0"
  sources:
    - path: docs/specs
      pattern: "*.md"
    - path: .claude/haios/manifesto/L4
      pattern: "*.md"
  exclude:
    - "**/archive/**"
    - "**/deprecated/**"
```

```python
loader = CorpusLoader(Path(".claude/haios/config/corpus/haios-requirements.yaml"))
extractor = RequirementExtractor(loader)
files = extractor._discover_files()
# Returns: Only TRDs and L4 manifesto files, excluding archive
# Count: ~15 files (targeted)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Source path doesn't exist | Log warning, skip source | Not tested (logging only) |
| Empty corpus (no files match) | Return empty list | Implicit in other tests |
| Config is dict not file | Accept directly | Test 2-6 use dict configs |
| Relative vs absolute paths | base_path resolves relatives | All tests use tmp_path |
| File passed to RequirementExtractor | Legacy single-file mode | Test 8 (backward compat) |

### Open Questions

**Q: Should CorpusLoader cache discovered files?**

No - CH-001 Non-Goals explicitly states "Caching discovered files" is out of scope. Each discover() call re-scans the filesystem.

**Q: Should filter_by_type use filters config or filename matching?**

Filename matching for simplicity. The `filters` in source config can be extended later, but MVP uses simple string-in-filename check.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in work item - all design choices resolved in plan -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | - | - | No blocking operator decisions identified |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_corpus_loader.py`
- [ ] Add all 8 tests from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Implement CorpusLoader Class
- [ ] Create `.claude/haios/modules/corpus_loader.py`
- [ ] Implement `__init__`, `_load_config`, `_parse_config`
- [ ] Implement `discover()` method
- [ ] Implement `_apply_exclusions()` method
- [ ] Implement `filter_by_type()` method
- [ ] Tests 1-6 pass (green)

### Step 3: Integrate with RequirementExtractor
- [ ] Add CorpusLoader import to requirement_extractor.py (lines 29-32)
- [ ] Modify `__init__` to accept Union[Path, CorpusLoader] (lines 291-304)
- [ ] Modify `_discover_files()` to delegate to loader (lines 355-363)
- [ ] Bump VERSION to "1.1.0"
- [ ] Tests 7-8 pass (green)

### Step 4: Add CLI Commands
- [ ] Add `corpus-list` command to cli.py
- [ ] Add `--corpus` option to `extract-requirements` command
- [ ] Test CLI commands manually

### Step 5: Create Example Corpus Config
- [ ] Create `.claude/haios/config/corpus/` directory
- [ ] Create `haios-requirements.yaml` example config
- [ ] Verify it works with real HAIOS corpus

### Step 6: Integration Verification
- [ ] All tests pass: `pytest tests/test_corpus_loader.py -v`
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)
- [ ] Verify existing requirement_extractor tests still pass

### Step 7: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with corpus_loader.py entry
- [ ] **MUST:** Verify README content matches actual module state

### Step 8: Runtime Consumer Verification (MUST)
- [ ] Verify CorpusLoader has runtime consumer (RequirementExtractor)
- [ ] Verify import works: `python -c "from .claude.haios.modules.corpus_loader import CorpusLoader"`

> **ADR-033 DoD:** Tests pass AND runtime consumer exists. CorpusLoader's consumer is RequirementExtractor.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment - CorpusLoader interface differs from CH-001 | Medium | Verified interface matches CH-001 R2 exactly |
| Integration regression - RequirementExtractor breaks | Medium | Test 8 verifies backward compat with Path |
| Scope creep - Adding caching or advanced features | Low | CH-001 Non-Goals explicitly excludes caching |
| fnmatch patterns behave differently than expected | Low | Use simple patterns, test with real exclusions |
| Import failures in different contexts | Low | Use try/except pattern from work_engine.py |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-031/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `.claude/haios/modules/corpus_loader.py` - CorpusLoader class | [ ] | File exists, class defined |
| Corpus schema definition (YAML format specification) | [ ] | Example config shows format |
| `discover()` method returns filtered file list | [ ] | Test 2-4 pass |
| `filter_by_type()` method for document type filtering | [ ] | Test 5 passes |
| Multi-source corpus definition support | [ ] | Test 3 passes |
| Exclusion pattern support | [ ] | Test 4 passes |
| CLI command: `corpus-list <corpus_config>` | [ ] | CLI help shows command |
| CLI integration: `extract-requirements --corpus <corpus_config>` | [ ] | CLI help shows option |
| Unit tests: `tests/test_corpus_loader.py` | [ ] | 8 tests exist |
| Example corpus config: `.claude/haios/config/corpus/haios-requirements.yaml` | [ ] | File exists |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/corpus_loader.py` | CorpusLoader class with discover(), filter_by_type() | [ ] | |
| `.claude/haios/modules/requirement_extractor.py` | Accepts CorpusLoader, VERSION="1.1.0" | [ ] | |
| `tests/test_corpus_loader.py` | 8 tests covering all acceptance criteria | [ ] | |
| `.claude/haios/config/corpus/haios-requirements.yaml` | Valid corpus definition | [ ] | |
| `.claude/haios/modules/README.md` | **MUST:** Lists corpus_loader.py | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_corpus_loader.py -v
# Expected: 8 tests passed
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
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @.claude/haios/epochs/E2_3/arcs/pipeline/CH-001-corpus-loader.md (chapter spec)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (pipeline architecture)
- @.claude/haios/modules/requirement_extractor.py (consumer module)
- @.claude/haios/modules/work_engine.py (sibling import pattern reference)

---
