# generated: 2026-01-26
# System Auto: last updated on: 2026-01-29T19:31:46
"""
RequirementExtractor Module (WORK-015, CH-002)

Extracts structured requirements from TRDs, L4 manifesto, and prose documents
into a unified RequirementSet data structure with full provenance tracking.

Interface (per CH-002):
    extractor = RequirementExtractor(corpus_path)
    result: RequirementSet = extractor.extract()

Parsers:
    - TRDParser: R0-R8 style tables (docs/specs/)
    - ManifestoParser: REQ-{DOMAIN}-{NNN} patterns (manifesto/L4/)
    - NaturalLanguageParser: RFC 2119 keywords (fallback)

L4 Requirements:
    - CH-002 R1: Multi-parser architecture
    - CH-002 R2: RequirementSet schema
    - CH-002 R3: Provenance tracking (file, line_range, confidence)
    - CH-002 R4: Traceability links
    - CH-002 R5: CLI integration
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Protocol, Union
import logging
import re

logger = logging.getLogger(__name__)

# Import CorpusLoader (WORK-031)
try:
    from .corpus_loader import CorpusLoader
except ImportError:
    try:
        from corpus_loader import CorpusLoader
    except ImportError:
        CorpusLoader = None  # type: ignore


# =============================================================================
# Enums
# =============================================================================

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


# =============================================================================
# Data Classes
# =============================================================================

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


# =============================================================================
# Parser Protocol and Implementations
# =============================================================================

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

            # Normalize strength to enum key
            strength_key = strength.upper().replace(' ', '_')
            try:
                strength_enum = RequirementStrength[strength_key]
            except KeyError:
                strength_enum = RequirementStrength.SHOULD

            requirements.append(Requirement(
                id=req_id.upper(),
                description=description.strip(),
                source=RequirementSource(
                    file=str(file_path),
                    line_range=str(line_num),
                    document_type=DocumentType.TRD
                ),
                strength=strength_enum,
                type=RequirementType.FEATURE,
                confidence=1.0  # Table extraction is high confidence
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
                type=RequirementType.GOVERNANCE,
                confidence=1.0  # Table extraction is high confidence
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
                if keyword in ['MUST', 'SHALL']:
                    strength = RequirementStrength.MUST
                elif keyword == 'SHOULD':
                    strength = RequirementStrength.SHOULD
                elif keyword == 'MAY':
                    strength = RequirementStrength.MAY
                else:
                    strength = RequirementStrength.SHOULD

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


# =============================================================================
# RequirementExtractor Main Class
# =============================================================================

class RequirementExtractor:
    """Main extractor that orchestrates parsing across a corpus.

    Usage (legacy):
        extractor = RequirementExtractor(Path("docs/specs"))
        result = extractor.extract()
        print(f"Found {len(result.requirements)} requirements")

    Usage (with CorpusLoader - WORK-031):
        loader = CorpusLoader(config_path)
        extractor = RequirementExtractor(loader)
        result = extractor.extract()
    """

    VERSION = "1.1.0"  # Bumped for CorpusLoader integration (WORK-031)

    def __init__(self, corpus: Union[Path, 'CorpusLoader']):
        """Initialize with corpus path or CorpusLoader.

        Args:
            corpus: Either a Path (legacy) or CorpusLoader instance.
        """
        # Duck-type check for CorpusLoader (avoids import dependency)
        if hasattr(corpus, 'discover'):
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

        # Fix A5: Handle source_corpus when CorpusLoader is used (WORK-031)
        if self.loader:
            source = self.loader._parsed.name  # Get corpus name from config
        else:
            source = str(self.corpus_path)

        return RequirementSet(
            source_corpus=source,
            extracted_at=datetime.now(),
            extractor_version=self.VERSION,
            requirements=all_requirements,
            traceability=[]  # Populated by consumer, not extractor
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
        # Delegate to CorpusLoader if available (WORK-031)
        if self.loader:
            return self.loader.discover()
        # Legacy path-based discovery
        if self.corpus_path and self.corpus_path.is_file():
            return [self.corpus_path]
        if self.corpus_path:
            return list(self.corpus_path.rglob("*.md"))
        return []
