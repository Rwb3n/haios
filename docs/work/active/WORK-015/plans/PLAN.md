---
template: implementation_plan
status: complete
date: 2026-01-26
backlog_id: WORK-015
title: RequirementExtractor Module Implementation
author: Hephaestus
lifecycle_phase: plan
session: 243
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-26T18:42:40'
---
# Implementation Plan: RequirementExtractor Module Implementation

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

A RequirementExtractor module that extracts structured requirements from TRDs, L4 manifesto, and prose documents into a unified RequirementSet data structure with full provenance tracking.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `cli.py` (add extract-requirements command) |
| Lines of code affected | ~20 | CLI integration |
| New files to create | 2 | `requirement_extractor.py`, `tests/test_requirement_extractor.py` |
| Tests to write | 8 | 3 parsers x 2 tests + 2 extractor tests |
| Dependencies | 0 | New module, no existing consumers |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only CLI integration, standalone module |
| Risk of regression | Low | New module, no existing code modified |
| External dependencies | Low | No external APIs, pure file parsing |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Data classes + Parser protocol | 30 min | High |
| TRDParser implementation | 30 min | High |
| ManifestoParser implementation | 20 min | High |
| NaturalLanguageParser implementation | 30 min | Med |
| RequirementExtractor main class | 20 min | High |
| CLI integration | 15 min | High |
| Tests | 45 min | Med |
| **Total** | ~3 hr | |

---

## Current State vs Desired State

### Current State

No RequirementExtractor module exists. Requirements are scattered across multiple document formats:

**TRD Format (docs/specs/TRD-ETL-v2.md:61-72):**
```markdown
| #  | Requirement | Criticality |
| -- | ----------- | ----------- |
| R0 | This TRD covers ONLY the ETL pipeline... | MUST |
| R1 | The ETL pipeline MUST parse text files... | MUST |
```

**L4 Manifesto Format (.claude/haios/manifesto/L4/functional_requirements.md:15-21):**
```markdown
| ID | Domain | Description | Derives From | Implemented By |
|----|--------|-------------|--------------|----------------|
| REQ-TRACE-001 | Traceability | Work items include... | L3.7, L3.11 | WORK.md template |
```

**Natural Language (agent_user_requirements.md):**
```markdown
The system must allow multiple agents to share context.
Users should be able to query memory semantically.
```

**Behavior:** Manual requirement enumeration, no automated extraction.

**Result:** Pipeline PLAN stage has no structured input.

### Desired State

```python
# .claude/haios/modules/requirement_extractor.py
from requirement_extractor import RequirementExtractor

extractor = RequirementExtractor(Path("docs/specs"))
result: RequirementSet = extractor.extract()

# result.requirements contains:
# [Requirement(id="R0", strength=MUST, source=RequirementSource(file="TRD-ETL-v2.md", line_range="63")), ...]
```

**Behavior:** Automated extraction from TRDs, L4 manifesto, and prose documents.

**Result:** Structured RequirementSet available for pipeline PLAN stage input.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: TRDParser extracts R-table requirements
```python
def test_trd_parser_extracts_r_table():
    """TRDParser extracts R0-R8 style requirement tables."""
    content = """
| #  | Requirement | Criticality |
| -- | ----------- | ----------- |
| R0 | System MUST do X | MUST |
| R1 | System SHOULD do Y | SHOULD |
"""
    parser = TRDParser()
    reqs = parser.parse(content, Path("TRD-test.md"))
    assert len(reqs) == 2
    assert reqs[0].id == "R0"
    assert reqs[0].strength == RequirementStrength.MUST
    assert reqs[1].strength == RequirementStrength.SHOULD
```

### Test 2: TRDParser handles no table
```python
def test_trd_parser_handles_no_table():
    """TRDParser returns empty list when no R table found."""
    parser = TRDParser()
    reqs = parser.parse("No table here", Path("test.md"))
    assert reqs == []
```

### Test 3: ManifestoParser extracts REQ pattern
```python
def test_manifesto_parser_extracts_req_pattern():
    """ManifestoParser extracts REQ-{DOMAIN}-{NNN} patterns."""
    content = """
| ID | Domain | Description | Derives From |
|----|--------|-------------|--------------|
| REQ-TRACE-001 | Traceability | Work items include traces_to | L3.7 |
| REQ-CONTEXT-001 | Context | Coldstart MUST inject | L3.3 |
"""
    parser = ManifestoParser()
    reqs = parser.parse(content, Path("functional_requirements.md"))
    assert len(reqs) == 2
    assert reqs[0].id == "REQ-TRACE-001"
    assert "Traceability" in reqs[0].description or reqs[0].source.file
```

### Test 4: NaturalLanguageParser extracts must/should
```python
def test_nl_parser_extracts_must_statements():
    """NaturalLanguageParser extracts 'must allow' and 'should' statements."""
    content = "The system must allow users to log in. Users should be able to reset passwords."
    parser = NaturalLanguageParser()
    reqs = parser.parse(content, Path("requirements.md"))
    assert len(reqs) >= 2
    assert any("log in" in r.description for r in reqs)
```

### Test 5: RequirementExtractor selects correct parser
```python
def test_extractor_selects_correct_parser():
    """RequirementExtractor selects parser based on file path."""
    extractor = RequirementExtractor(Path("test_corpus"))

    # TRD files get TRDParser
    parser = extractor._select_parser(Path("docs/specs/TRD-foo.md"))
    assert isinstance(parser, TRDParser)

    # Manifesto files get ManifestoParser
    parser = extractor._select_parser(Path("manifesto/L4/requirements.md"))
    assert isinstance(parser, ManifestoParser)
```

### Test 6: RequirementExtractor tracks provenance
```python
def test_extractor_tracks_provenance():
    """Extracted requirements include source file and line range."""
    extractor = RequirementExtractor(Path("."))
    # Use a real file for integration
    reqs = extractor.extract_from_file(Path("docs/specs/TRD-ETL-v2.md"))
    assert len(reqs) > 0
    assert all(r.source.file for r in reqs)
    assert all(r.source.document_type for r in reqs)
```

### Test 7: RequirementSet schema conformance
```python
def test_requirement_set_schema():
    """RequirementSet conforms to INV-019 + CH-002 schema."""
    req_set = RequirementSet(
        source_corpus="test",
        extracted_at=datetime.now(),
        extractor_version="1.0.0",
        requirements=[],
        traceability=[]  # CH-002 R4: Traceability field required
    )
    assert req_set.source_corpus == "test"
    assert req_set.extractor_version == "1.0.0"
    assert hasattr(req_set, 'traceability')  # CH-002 R4

def test_requirement_confidence_field():
    """Requirement has confidence field per CH-002 R3."""
    req = Requirement(
        id="TEST-001",
        description="Test requirement",
        source=RequirementSource(file="test.md"),
        confidence=0.7
    )
    assert req.confidence == 0.7  # CH-002 R3: NLP has lower confidence
```

### Test 8: CLI command works
```python
def test_cli_extract_requirements(tmp_path):
    """CLI extract-requirements command produces output."""
    # Create test file
    test_file = tmp_path / "TRD-test.md"
    test_file.write_text("| # | Requirement | Criticality |\n| R0 | Test | MUST |")

    # Run CLI (via subprocess or direct call)
    result = run_cli(["extract-requirements", str(tmp_path)])
    assert result.returncode == 0
    # Verify output contains requirements
```

---

## Detailed Design

<!-- Pattern verified from memory_bridge.py: dataclasses, logging, optional imports with try/except -->

### Data Classes (per INV-019 schema)

**File:** `.claude/haios/modules/requirement_extractor.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Protocol
import logging
import re

logger = logging.getLogger(__name__)


class RequirementStrength(Enum):
    """RFC 2119 requirement strength levels."""
    MUST = "MUST"
    SHOULD = "SHOULD"
    MAY = "MAY"
    MUST_NOT = "MUST_NOT"
    SHOULD_NOT = "SHOULD_NOT"


class RequirementType(Enum):
    """Requirement type classification."""
    FEATURE = "feature"
    CONSTRAINT = "constraint"
    INTERFACE = "interface"
    BEHAVIOR = "behavior"
    GOVERNANCE = "governance"


class DocumentType(Enum):
    """Source document type."""
    TRD = "TRD"
    ADR = "ADR"
    MANIFESTO = "manifesto"
    SPEC = "spec"


class RequirementStatus(Enum):
    """Requirement lifecycle status."""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"


@dataclass
class RequirementSource:
    """Provenance information for a requirement."""
    file: str
    line_range: Optional[str] = None
    document_type: DocumentType = DocumentType.SPEC


@dataclass
class Requirement:
    """A single extracted requirement."""
    id: str
    description: str
    source: RequirementSource
    strength: RequirementStrength = RequirementStrength.SHOULD
    type: RequirementType = RequirementType.FEATURE
    derives_from: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    implemented_by: Optional[str] = None
    status: RequirementStatus = RequirementStatus.PROPOSED
    confidence: float = 1.0  # CH-002 R3: 1.0 for table extraction, 0.7 for NLP


@dataclass
class TraceabilityLink:
    """Traceability from requirement to artifacts (CH-002 R4)."""
    req_id: str
    work_items: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    memory_refs: List[int] = field(default_factory=list)


@dataclass
class RequirementSet:
    """Collection of extracted requirements with metadata."""
    source_corpus: str
    extracted_at: datetime
    extractor_version: str
    requirements: List[Requirement] = field(default_factory=list)
    traceability: List[TraceabilityLink] = field(default_factory=list)  # CH-002 R4
```

### Parser Protocol and Implementations

```python
class Parser(Protocol):
    """Protocol for requirement parsers."""

    def can_parse(self, file_path: Path) -> bool:
        """Return True if this parser handles the file type."""
        ...

    def parse(self, content: str, file_path: Path) -> List[Requirement]:
        """Extract requirements from content."""
        ...


class TRDParser:
    """Extracts requirements from TRD R0-R8 tables.

    Pattern: | # | Requirement | Criticality |
             | R0 | Description | MUST |
    """

    # Regex: Captures R-number, description, and strength from table rows
    PATTERN = re.compile(
        r'\|\s*(R\d+)\s*\|\s*([^|]+)\s*\|\s*(MUST|SHOULD|MAY|MUST_NOT|SHOULD_NOT)\s*\|',
        re.IGNORECASE
    )

    def can_parse(self, file_path: Path) -> bool:
        """TRD files: path contains 'TRD' or 'specs/'."""
        path_str = str(file_path).lower()
        return 'trd' in path_str or 'specs' in path_str

    def parse(self, content: str, file_path: Path) -> List[Requirement]:
        """Extract R0-R8 style requirements."""
        requirements = []
        for match in self.PATTERN.finditer(content):
            req_id, description, strength = match.groups()
            line_num = content[:match.start()].count('\n') + 1

            requirements.append(Requirement(
                id=req_id.upper(),
                description=description.strip(),
                source=RequirementSource(
                    file=str(file_path),
                    line_range=str(line_num),
                    document_type=DocumentType.TRD
                ),
                strength=RequirementStrength[strength.upper().replace(' ', '_')],
                type=RequirementType.FEATURE
            ))
        return requirements


class ManifestoParser:
    """Extracts requirements from L4 manifesto REQ-{DOMAIN}-{NNN} patterns.

    Pattern: | REQ-TRACE-001 | Traceability | Description | L3.7 |
    """

    # Regex: Captures REQ-DOMAIN-NNN pattern from tables
    PATTERN = re.compile(
        r'\|\s*(REQ-[A-Z]+-\d{3})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|',
        re.IGNORECASE
    )

    def can_parse(self, file_path: Path) -> bool:
        """Manifesto files: path contains 'manifesto' or 'L4'."""
        path_str = str(file_path).lower()
        return 'manifesto' in path_str or '/l4/' in path_str or '\\l4\\' in path_str

    def parse(self, content: str, file_path: Path) -> List[Requirement]:
        """Extract REQ-{DOMAIN}-{NNN} pattern requirements."""
        requirements = []
        for match in self.PATTERN.finditer(content):
            req_id, domain, description = match.groups()
            line_num = content[:match.start()].count('\n') + 1

            requirements.append(Requirement(
                id=req_id.upper(),
                description=description.strip(),
                source=RequirementSource(
                    file=str(file_path),
                    line_range=str(line_num),
                    document_type=DocumentType.MANIFESTO
                ),
                strength=RequirementStrength.MUST,  # L4 requirements are MUST by default
                type=RequirementType.GOVERNANCE
            ))
        return requirements


class NaturalLanguageParser:
    """Extracts requirements from prose with RFC 2119 keywords.

    Pattern: "must allow", "should be able to", "shall"
    """

    # Regex: Captures sentences with RFC 2119 keywords
    PATTERN = re.compile(
        r'([^.]*\b(must|should|shall|may)\s+(not\s+)?(allow|be able to|enable|support|provide|have|include)[^.]*\.)',
        re.IGNORECASE
    )

    def can_parse(self, file_path: Path) -> bool:
        """Fallback parser for any markdown file."""
        return file_path.suffix.lower() == '.md'

    def parse(self, content: str, file_path: Path) -> List[Requirement]:
        """Extract natural language requirements."""
        requirements = []
        for i, match in enumerate(self.PATTERN.finditer(content)):
            sentence = match.group(1).strip()
            keyword = match.group(2).upper()
            negation = match.group(3)
            line_num = content[:match.start()].count('\n') + 1

            # Determine strength from keyword
            if negation:
                strength = RequirementStrength.MUST_NOT if keyword == 'MUST' else RequirementStrength.SHOULD_NOT
            else:
                strength = RequirementStrength[keyword] if keyword in ['MUST', 'SHOULD', 'MAY'] else RequirementStrength.SHOULD

            requirements.append(Requirement(
                id=f"NL-{file_path.stem.upper()}-{i+1:03d}",  # Auto-generated ID
                description=sentence,
                source=RequirementSource(
                    file=str(file_path),
                    line_range=str(line_num),
                    document_type=DocumentType.SPEC
                ),
                strength=strength,
                type=RequirementType.BEHAVIOR,
                confidence=0.7  # CH-002 R3: NLP extraction has lower confidence
            ))
        return requirements
```

### RequirementExtractor Main Class

```python
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

    def extract(self) -> RequirementSet:
        """Extract all requirements from corpus.

        Returns:
            RequirementSet with all discovered requirements.
        """
        all_requirements = []
        for file_path in self._discover_files():
            try:
                requirements = self.extract_from_file(file_path)
                all_requirements.extend(requirements)
                logger.debug(f"Extracted {len(requirements)} from {file_path}")
            except Exception as e:
                logger.warning(f"Failed to extract from {file_path}: {e}")

        return RequirementSet(
            source_corpus=str(self.corpus_path),
            extracted_at=datetime.now(),
            extractor_version=self.VERSION,
            requirements=all_requirements
        )

    def extract_from_file(self, file_path: Path) -> List[Requirement]:
        """Extract requirements from a single file.

        Args:
            file_path: Path to the file to parse.

        Returns:
            List of extracted requirements.
        """
        content = file_path.read_text(encoding='utf-8')
        parser = self._select_parser(file_path)
        return parser.parse(content, file_path)

    def _select_parser(self, file_path: Path) -> Parser:
        """Select appropriate parser for file.

        Args:
            file_path: Path to check.

        Returns:
            First parser that can handle the file.
        """
        for parser in self.parsers:
            if parser.can_parse(file_path):
                return parser
        return self.parsers[-1]  # NaturalLanguageParser as ultimate fallback

    def _discover_files(self) -> List[Path]:
        """Discover markdown files in corpus.

        Returns:
            List of markdown file paths.
        """
        if self.corpus_path.is_file():
            return [self.corpus_path]
        return list(self.corpus_path.rglob("*.md"))
```

### CLI Integration

**File:** `.claude/haios/modules/cli.py` (add to existing)

```python
# Add to existing CLI commands
def extract_requirements(corpus_path: str) -> None:
    """Extract requirements from a corpus of documents.

    Args:
        corpus_path: Path to corpus root directory or single file.
    """
    from requirement_extractor import RequirementExtractor
    import json

    extractor = RequirementExtractor(Path(corpus_path))
    result = extractor.extract()

    # Output as JSON for pipeline consumption
    output = {
        "source_corpus": result.source_corpus,
        "extracted_at": result.extracted_at.isoformat(),
        "extractor_version": result.extractor_version,
        "requirement_count": len(result.requirements),
        "requirements": [
            {
                "id": r.id,
                "description": r.description,
                "strength": r.strength.value,
                "type": r.type.value,
                "source": {
                    "file": r.source.file,
                    "line_range": r.source.line_range,
                    "document_type": r.source.document_type.value
                }
            }
            for r in result.requirements
        ]
    }
    print(json.dumps(output, indent=2))
```

### Call Chain Context

```
Pipeline Orchestrator (future)
    |
    +-> RequirementExtractor.extract()      # <-- This module
    |       Returns: RequirementSet
    |
    +-> PlannerAgent.plan(RequirementSet)   # Future CH-003
            Returns: WorkPlan
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Parser selection order | TRD -> Manifesto -> NaturalLanguage | Specific parsers first, fallback last; prevents NL parser from grabbing TRD content |
| Auto-generated IDs for NL | NL-{FILENAME}-{NNN} | NL requirements lack explicit IDs; generated IDs enable traceability |
| L4 requirements default to MUST | Hardcoded strength | L4 manifesto requirements are governance constraints, should be treated as MUST |
| Provenance via line numbers | Count newlines before match | Simple, accurate, no external dependencies |
| JSON CLI output | Structured JSON to stdout | Machine-parseable for pipeline integration; human-readable with indent |
| Confidence field (CH-002 R3) | 1.0 for table, 0.7 for NLP | NLP extraction is less reliable; consumers can filter by confidence |
| Traceability field (CH-002 R4) | List[TraceabilityLink] in RequirementSet | Enables future linking to work items, artifacts, memory refs |

### Input/Output Examples

**Real Example - TRD-ETL-v2.md:**
```
Input: docs/specs/TRD-ETL-v2.md
  Contains: 8 R0-R8 requirements in table format

Output RequirementSet:
  - Requirement(id="R0", description="This TRD covers ONLY the ETL pipeline...", strength=MUST)
  - Requirement(id="R1", description="The ETL pipeline MUST parse text files...", strength=MUST)
  - ... (8 total)
```

**Real Example - functional_requirements.md:**
```
Input: .claude/haios/manifesto/L4/functional_requirements.md
  Contains: 15 REQ-{DOMAIN}-{NNN} patterns

Output RequirementSet:
  - Requirement(id="REQ-TRACE-001", description="Work items include traces_to field", strength=MUST)
  - Requirement(id="REQ-CONTEXT-001", description="Coldstart MUST inject prior session context", strength=MUST)
  - ... (15 total)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty file | Returns empty list | Test 2 |
| Malformed table | Skips non-matching rows | Implicit in regex |
| Non-UTF8 encoding | Raises UnicodeDecodeError, logged | Error handling |
| Missing corpus path | Raises FileNotFoundError | CLI validation |
| Duplicate IDs | Allowed (different sources may have same ID) | Test 6 |

### Open Questions

**Q: Should duplicate requirement IDs across files be merged or kept separate?**

Answer: Keep separate. Different documents may reference same conceptual requirement with different context. Deduplication is a consumer concern, not extractor concern.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in WORK-015 frontmatter. All design decisions made in CH-002 and INV-019. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Parser architecture | Single parser, Multi-parser | Multi-parser | INV-019: Different doc formats require specialized extraction (TRD tables vs REQ patterns vs prose) |
| Output format | YAML, JSON, Dataclass | Dataclass + JSON CLI | Dataclass for internal use, JSON for pipeline integration |
| ID generation for NL | Manual, Auto-generated | Auto-generated | Natural language lacks explicit IDs; NL-{FILE}-{NNN} enables traceability |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_requirement_extractor.py`
- [ ] Add tests 1-8 from Tests First section
- [ ] Run `pytest tests/test_requirement_extractor.py` - verify all fail (red)

### Step 2: Create Data Classes
- [ ] Create `.claude/haios/modules/requirement_extractor.py`
- [ ] Add enums: RequirementStrength, RequirementType, DocumentType, RequirementStatus
- [ ] Add dataclasses: RequirementSource, Requirement, RequirementSet
- [ ] Test 7 passes (green)

### Step 3: Implement TRDParser
- [ ] Add Parser protocol
- [ ] Implement TRDParser with regex for R0-R8 tables
- [ ] Tests 1, 2 pass (green)

### Step 4: Implement ManifestoParser
- [ ] Implement ManifestoParser with regex for REQ-{DOMAIN}-{NNN}
- [ ] Test 3 passes (green)

### Step 5: Implement NaturalLanguageParser
- [ ] Implement NaturalLanguageParser with RFC 2119 keyword detection
- [ ] Test 4 passes (green)

### Step 6: Implement RequirementExtractor
- [ ] Implement RequirementExtractor main class
- [ ] Add _select_parser, extract_from_file, extract, _discover_files
- [ ] Tests 5, 6 pass (green)

### Step 7: Add CLI Integration
- [ ] Add extract-requirements command to cli.py
- [ ] Test 8 passes (green)

### Step 8: Integration Verification
- [ ] All 8 tests pass
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)
- [ ] Demo: Extract from real TRD-ETL-v2.md

### Step 9: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with requirement_extractor.py
- [ ] **MUST:** Verify README lists the new module

### Step 10: Consumer Verification
- [ ] N/A - New module, no existing consumers
- [ ] Document intended consumer: Pipeline PLAN stage (CH-003)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex fails on edge cases | Med | Start with known patterns from real files; iterate on failures |
| Large files cause performance issues | Low | Add file size limit warning (>1MB); log and continue |
| Line range tracking inaccurate | Low | Use newline counting; verified against real files |
| Spec misalignment - wrong interface | High | MUST verify design matches CH-002 interface (done in plan) |
| Missing document types | Med | NaturalLanguageParser as fallback catches all .md files |
| Import pattern inconsistency | Low | Verified against memory_bridge.py sibling module |

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

**MUST** read `docs/work/active/WORK-015/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| TRDParser class that extracts R0-R8 requirement tables | [ ] | Class exists, test_trd_parser_* pass |
| ManifestoParser class that extracts REQ-{DOMAIN}-{NNN} patterns | [ ] | Class exists, test_manifesto_parser_* pass |
| NaturalLanguageParser class that extracts "must allow" statements | [ ] | Class exists, test_nl_parser_* pass |
| RequirementSet dataclass conforming to schema | [ ] | Dataclass exists, matches INV-019 schema |
| RequirementExtractor main class with extract() and extract_from_file() | [ ] | Class exists with both methods |
| CLI integration via cli.py extract-requirements command | [ ] | Command runs, outputs JSON |
| Tests covering all parsers with sample documents | [ ] | 8 tests pass |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/requirement_extractor.py` | All classes + RequirementExtractor | [ ] | |
| `tests/test_requirement_extractor.py` | 8 tests covering all parsers | [ ] | |
| `.claude/haios/modules/README.md` | **MUST:** Lists requirement_extractor.py | [ ] | |
| `.claude/haios/modules/cli.py` | extract-requirements command added | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_requirement_extractor.py -v
# Expected: 8 tests passed

# Demo command
python .claude/haios/modules/cli.py extract-requirements docs/specs/TRD-ETL-v2.md
# Expected: JSON output with R0-R8 requirements
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

- @.claude/haios/epochs/E2_3/arcs/pipeline/CH-002-requirement-extractor.md (chapter definition)
- @docs/work/active/INV-019/investigations/001-requirements-synthesis.md (schema design)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (pipeline interface)
- @.claude/haios/manifesto/L4/functional_requirements.md (L4 REQ pattern example)
- @docs/specs/TRD-ETL-v2.md (TRD R0-R8 pattern example)
- Memory: 82421, 82429 (multi-parser architecture decision)

---
