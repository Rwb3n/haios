# generated: 2026-01-26
# System Auto: last updated on: 2026-01-29T19:34:55
"""
Tests for RequirementExtractor module (WORK-015, CH-002).

Tests cover:
- TRDParser: R0-R8 table extraction
- ManifestoParser: REQ-{DOMAIN}-{NNN} pattern extraction
- NaturalLanguageParser: RFC 2119 keyword extraction
- RequirementExtractor: Parser selection, provenance tracking
- RequirementSet: Schema conformance (including traceability, confidence)
"""
import pytest
from datetime import datetime
from pathlib import Path
import sys

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))

from requirement_extractor import (
    RequirementExtractor,
    RequirementSet,
    Requirement,
    RequirementSource,
    RequirementStrength,
    RequirementType,
    DocumentType,
    TraceabilityLink,
    TRDParser,
    ManifestoParser,
    NaturalLanguageParser,
)


class TestTRDParser:
    """Tests for TRDParser - extracts R0-R8 style requirement tables."""

    def test_trd_parser_extracts_r_table(self):
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
        assert reqs[1].id == "R1"
        assert reqs[1].strength == RequirementStrength.SHOULD

    def test_trd_parser_handles_no_table(self):
        """TRDParser returns empty list when no R table found."""
        parser = TRDParser()
        reqs = parser.parse("No table here", Path("test.md"))
        assert reqs == []

    def test_trd_parser_can_parse_trd_files(self):
        """TRDParser can_parse returns True for TRD files."""
        parser = TRDParser()
        assert parser.can_parse(Path("docs/specs/TRD-foo.md")) is True
        assert parser.can_parse(Path("docs/specs/something.md")) is True
        assert parser.can_parse(Path("random/file.md")) is False


class TestManifestoParser:
    """Tests for ManifestoParser - extracts REQ-{DOMAIN}-{NNN} patterns."""

    def test_manifesto_parser_extracts_req_pattern(self):
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
        assert reqs[1].id == "REQ-CONTEXT-001"

    def test_manifesto_parser_can_parse_manifesto_files(self):
        """ManifestoParser can_parse returns True for manifesto files."""
        parser = ManifestoParser()
        assert parser.can_parse(Path("manifesto/L4/requirements.md")) is True
        assert parser.can_parse(Path(".claude/haios/manifesto/L4/test.md")) is True
        assert parser.can_parse(Path("docs/specs/TRD-foo.md")) is False


class TestNaturalLanguageParser:
    """Tests for NaturalLanguageParser - extracts RFC 2119 keyword statements."""

    def test_nl_parser_extracts_must_statements(self):
        """NaturalLanguageParser extracts 'must allow' and 'should' statements."""
        content = "The system must allow users to log in. Users should be able to reset passwords."
        parser = NaturalLanguageParser()
        reqs = parser.parse(content, Path("requirements.md"))
        assert len(reqs) >= 2
        assert any("log in" in r.description for r in reqs)

    def test_nl_parser_sets_lower_confidence(self):
        """NaturalLanguageParser sets confidence=0.7 for NLP extraction (CH-002 R3)."""
        content = "The system must allow users to authenticate."
        parser = NaturalLanguageParser()
        reqs = parser.parse(content, Path("requirements.md"))
        assert len(reqs) >= 1
        assert reqs[0].confidence == 0.7

    def test_nl_parser_can_parse_markdown(self):
        """NaturalLanguageParser can_parse returns True for any .md file."""
        parser = NaturalLanguageParser()
        assert parser.can_parse(Path("any/file.md")) is True
        assert parser.can_parse(Path("file.txt")) is False


class TestRequirementExtractor:
    """Tests for RequirementExtractor main class."""

    def test_extractor_selects_correct_parser(self):
        """RequirementExtractor selects parser based on file path."""
        extractor = RequirementExtractor(Path("test_corpus"))

        # TRD files get TRDParser
        parser = extractor._select_parser(Path("docs/specs/TRD-foo.md"))
        assert isinstance(parser, TRDParser)

        # Manifesto files get ManifestoParser
        parser = extractor._select_parser(Path("manifesto/L4/requirements.md"))
        assert isinstance(parser, ManifestoParser)

        # Other .md files get NaturalLanguageParser
        parser = extractor._select_parser(Path("random/file.md"))
        assert isinstance(parser, NaturalLanguageParser)

    def test_extractor_tracks_provenance(self, tmp_path):
        """Extracted requirements include source file and line range."""
        # Create test TRD file
        test_file = tmp_path / "TRD-test.md"
        test_file.write_text("""# Test TRD

| #  | Requirement | Criticality |
| -- | ----------- | ----------- |
| R0 | Test requirement | MUST |
""")
        extractor = RequirementExtractor(tmp_path)
        reqs = extractor.extract_from_file(test_file)
        assert len(reqs) > 0
        assert all(r.source.file for r in reqs)
        assert all(r.source.document_type for r in reqs)

    def test_extractor_extract_returns_requirement_set(self, tmp_path):
        """extract() returns a complete RequirementSet."""
        # Create test file
        test_file = tmp_path / "TRD-test.md"
        test_file.write_text("| R0 | Test | MUST |")

        extractor = RequirementExtractor(tmp_path)
        result = extractor.extract()

        assert isinstance(result, RequirementSet)
        assert result.source_corpus == str(tmp_path)
        assert result.extractor_version == "1.1.0"  # Bumped in WORK-031


class TestRequirementSetSchema:
    """Tests for RequirementSet and Requirement schema conformance."""

    def test_requirement_set_schema(self):
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

    def test_requirement_confidence_field(self):
        """Requirement has confidence field per CH-002 R3."""
        req = Requirement(
            id="TEST-001",
            description="Test requirement",
            source=RequirementSource(file="test.md"),
            confidence=0.7
        )
        assert req.confidence == 0.7  # CH-002 R3: NLP has lower confidence

    def test_traceability_link_schema(self):
        """TraceabilityLink conforms to CH-002 R4 schema."""
        link = TraceabilityLink(
            req_id="REQ-TEST-001",
            work_items=["WORK-015"],
            artifacts=["requirement_extractor.py"],
            memory_refs=[82430]
        )
        assert link.req_id == "REQ-TEST-001"
        assert "WORK-015" in link.work_items


class TestRealFileExtraction:
    """Integration tests with real HAIOS files."""

    @pytest.mark.skipif(
        not Path("docs/specs/TRD-ETL-v2.md").exists(),
        reason="Real TRD file not available"
    )
    def test_extract_from_real_trd(self):
        """Extract requirements from real TRD-ETL-v2.md."""
        extractor = RequirementExtractor(Path("."))
        reqs = extractor.extract_from_file(Path("docs/specs/TRD-ETL-v2.md"))
        # TRD-ETL-v2.md has R0-R8 requirements
        assert len(reqs) >= 8
        assert any(r.id == "R0" for r in reqs)

    @pytest.mark.skipif(
        not Path(".claude/haios/manifesto/L4/functional_requirements.md").exists(),
        reason="Real manifesto file not available"
    )
    def test_extract_from_real_manifesto(self):
        """Extract requirements from real functional_requirements.md."""
        extractor = RequirementExtractor(Path("."))
        reqs = extractor.extract_from_file(
            Path(".claude/haios/manifesto/L4/functional_requirements.md")
        )
        # functional_requirements.md has REQ-* patterns
        assert len(reqs) >= 10
        assert any("REQ-TRACE" in r.id for r in reqs)
