# generated: 2026-01-29
# System Auto: last updated on: 2026-01-29T18:35:25
# Chapter: CorpusLoader

## Definition

**Chapter ID:** CH-001
**Arc:** pipeline
**Status:** Planned
**Work Item:** WORK-031
**Implementation:** `.claude/haios/modules/corpus_loader.py`

---

## Problem

RequirementExtractor takes a `corpus_path` and discovers files via `rglob("*.md")`. This is functional but limited:

1. **No filtering:** Returns all markdown files, including irrelevant ones
2. **No configuration:** Hardcoded pattern, no corpus definition
3. **No multi-source:** Can't combine docs from multiple directories

**Current state:**
```python
# RequirementExtractor._discover_files()
return list(self.corpus_path.rglob("*.md"))  # Too broad
```

**Gap:** Pipeline portability requires arbitrary corpus definition, not hardcoded discovery.

---

## Agent Need

> "I need to define a corpus as a set of documents from multiple paths with filtering, so I can extract requirements from exactly the documents I specify."

---

## Requirements

### R1: Corpus Definition Schema

```yaml
corpus:
  name: "haios-requirements"
  version: "1.0"
  sources:
    - path: docs/specs
      pattern: "*.md"
      include_subdirs: true
      filters:
        - type: "TRD"
    - path: .claude/haios/manifesto/L4
      pattern: "*.md"
  exclude:
    - "**/archive/**"
    - "**/deprecated/**"
```

### R2: CorpusLoader Interface

```python
class CorpusLoader:
    def __init__(self, corpus_config: Path | dict):
        """Initialize with corpus definition."""

    def discover(self) -> List[Path]:
        """Return all files matching corpus definition."""

    def filter_by_type(self, doc_type: str) -> List[Path]:
        """Return files matching specific document type."""
```

### R3: RequirementExtractor Integration

CorpusLoader becomes the file discovery mechanism for RequirementExtractor:

```python
# Current
extractor = RequirementExtractor(corpus_path)
files = extractor._discover_files()  # Uses rglob

# Target
loader = CorpusLoader(corpus_config)
extractor = RequirementExtractor(loader)
files = loader.discover()  # Uses corpus definition
```

### R4: CLI Integration

```bash
python .claude/haios/modules/cli.py corpus-list <corpus_config>
python .claude/haios/modules/cli.py extract-requirements --corpus <corpus_config>
```

---

## Success Criteria

- [ ] Corpus schema defined (YAML)
- [ ] CorpusLoader class implements discover() and filter_by_type()
- [ ] Multi-source corpus definition works
- [ ] Exclusion patterns work
- [ ] RequirementExtractor accepts CorpusLoader
- [ ] CLI commands work
- [ ] Tests verify discovery with sample corpus

---

## Non-Goals

- Document classification (that's RequirementExtractor's job)
- Content parsing (that's RequirementExtractor's job)
- Caching discovered files

---

## Dependencies

- **RequirementExtractor (CH-002):** Consumer of CorpusLoader output
- **S26:** Pipeline architecture (stage interfaces)

---

## References

- @.claude/haios/modules/requirement_extractor.py (consumer)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (stage interface)
