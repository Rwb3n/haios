# generated: 2026-01-25
# System Auto: last updated on: 2026-01-25T22:39:21
# Chapter: RequirementExtractor

## Definition

**Chapter ID:** CH-002
**Arc:** pipeline
**Status:** Active
**Work Item:** WORK-015
**Implementation:** `.claude/haios/modules/requirement_extractor.py`
**Investigation:** @docs/work/active/INV-019/investigations/001-requirements-synthesis.md

---

## Problem

HAIOS has requirements scattered across multiple document formats:
- TRDs use R0-R8 tables with ID/Description/Strength
- L4 manifesto uses REQ-{DOMAIN}-{NNN} with derives_from traceability
- Natural language docs use "must allow" statements

No unified extraction tool exists. Requirements are manually enumerated, not auto-extracted.

**Current state:**
```
TRDs: 54 RFC 2119 keywords, not structured
L4: 13 formal REQs, manually maintained
Prose: "must allow" statements, not extracted
```

**Gap:** Pipeline PLAN stage needs structured RequirementSet as input. No extractor produces it.

---

## Agent Need

> "I need requirements extracted from a corpus of documents in a structured format I can reason about and trace to work items."

---

## Requirements

### R1: Multi-Parser Architecture

Extract requirements from different document types:

| Parser | Input | Output |
|--------|-------|--------|
| TRDParser | R0-R8 tables | Requirement with id, description, strength |
| ManifestoParser | REQ-{DOMAIN}-{NNN} | Requirement with derives_from, implemented_by |
| NaturalLanguageParser | "must allow" statements | Requirement (inferred strength) |

### R2: RequirementSet Schema

Output conforms to schema (from INV-019):

```yaml
requirement_set:
  source_corpus: string
  extracted_at: datetime
  extractor_version: string

requirements:
  - id: string                # REQ-{DOMAIN}-{NNN}
    source:
      file: string
      line_range: string
      document_type: enum[TRD, ADR, manifesto, spec]
    type: enum[feature, constraint, interface, behavior, governance]
    strength: enum[MUST, SHOULD, MAY, MUST_NOT, SHOULD_NOT]
    description: string
    derives_from: list[string]
    acceptance_criteria: list[string]
    dependencies: list[string]
    implemented_by: string
    status: enum[proposed, accepted, implemented, verified, deprecated]
```

### R3: Provenance Tracking

Every extracted requirement MUST include:
- Source file path
- Line range where found
- Document type
- Extraction confidence (if NLP-based)

### R4: Traceability Links

Output includes traceability section:

```yaml
traceability:
  - req_id: string
    work_items: list[string]
    artifacts: list[string]
    memory_refs: list[int]
```

### R5: CLI Integration

Extractor callable via cli.py:

```bash
python .claude/haios/modules/cli.py extract-requirements <corpus_path>
```

---

## Interface

**Module contract:**
```python
# .claude/haios/modules/requirement_extractor.py

class RequirementExtractor:
    def __init__(self, corpus_path: Path):
        """Initialize with corpus root path."""

    def extract(self) -> RequirementSet:
        """Extract all requirements from corpus."""

    def extract_from_file(self, file_path: Path) -> List[Requirement]:
        """Extract requirements from single file."""

# Parser interface
class Parser(Protocol):
    def can_parse(self, file_path: Path) -> bool:
        """Return True if parser handles this file type."""

    def parse(self, content: str, file_path: Path) -> List[Requirement]:
        """Extract requirements from content."""
```

---

## Success Criteria

- [ ] TRDParser extracts R0-R8 style tables
- [ ] ManifestoParser extracts REQ-{DOMAIN}-{NNN} pattern
- [ ] NaturalLanguageParser extracts "must allow" statements
- [ ] Output conforms to RequirementSet schema
- [ ] Provenance tracked (file, line_range, doc_type)
- [ ] CLI command `extract-requirements` works
- [ ] Tests verify extraction from sample docs

---

## Non-Goals

- Full NLP requirement extraction (use pattern matching first)
- Requirement validation (that's CH-005)
- Work item generation from requirements (that's CH-003)
- Caching extracted requirements

---

## Dependencies

- **CH-001 (CorpusLoader):** Provides file list to extract from
- **INV-019:** Investigation findings (schema, architecture)
- **S26:** Pipeline architecture (stage interfaces)

---

## References

- @docs/work/active/INV-019/investigations/001-requirements-synthesis.md (design source)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (stage interface)
- @.claude/haios/manifesto/L4/functional_requirements.md (L4 pattern example)
- @docs/specs/TRD-ETL-v2.md (TRD pattern example)
