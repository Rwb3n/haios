# generated: 2026-01-29
# System Auto: last updated on: 2026-01-29T19:32:28
"""
Tests for CorpusLoader Module (WORK-031, CH-001)

TDD tests written BEFORE implementation per implementation-cycle DO phase.
Tests verify:
- T1: Load corpus config from YAML file
- T2: Discover files from single source
- T3: Discover files from multiple sources
- T4: Exclusion patterns work
- T5: Filter by document type
- T6: Subdirectory inclusion control
- T7: RequirementExtractor accepts CorpusLoader
- T8: Backward compatibility - Path still works
"""
import pytest
from pathlib import Path

import sys
from pathlib import Path

# Add modules path for imports
modules_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
if str(modules_path) not in sys.path:
    sys.path.insert(0, str(modules_path))

# Import CorpusLoader
try:
    from corpus_loader import CorpusLoader
except ImportError:
    CorpusLoader = None

# Import RequirementExtractor for integration tests
try:
    from requirement_extractor import RequirementExtractor
except ImportError:
    RequirementExtractor = None


@pytest.fixture
def corpus_loader_available():
    """Skip tests if CorpusLoader not yet implemented."""
    if CorpusLoader is None:
        pytest.skip("CorpusLoader not yet implemented")


@pytest.fixture
def requirement_extractor_available():
    """Skip tests if RequirementExtractor not available."""
    if RequirementExtractor is None:
        pytest.skip("RequirementExtractor not available")


class TestCorpusLoaderConfig:
    """Tests for corpus configuration loading."""

    def test_load_corpus_from_yaml(self, tmp_path, corpus_loader_available):
        """T1: CorpusLoader loads configuration from YAML file."""
        config_file = tmp_path / "corpus.yaml"
        config_file.write_text("""
corpus:
  name: test-corpus
  version: "1.0"
  sources:
    - path: docs/specs
      pattern: "*.md"
""")
        loader = CorpusLoader(config_file)
        assert loader.config["corpus"]["name"] == "test-corpus"

    def test_load_corpus_from_dict(self, tmp_path, corpus_loader_available):
        """CorpusLoader accepts dict config directly."""
        config = {"corpus": {"name": "dict-corpus", "sources": []}}
        loader = CorpusLoader(config, base_path=tmp_path)
        assert loader.config["corpus"]["name"] == "dict-corpus"


class TestCorpusLoaderDiscover:
    """Tests for file discovery."""

    def test_discover_single_source(self, tmp_path, corpus_loader_available):
        """T2: discover() returns files matching pattern from single source."""
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "spec.md").touch()
        (tmp_path / "docs" / "readme.txt").touch()

        config = {"corpus": {"sources": [{"path": "docs", "pattern": "*.md"}]}}
        loader = CorpusLoader(config, base_path=tmp_path)
        files = loader.discover()

        assert len(files) == 1
        assert files[0].name == "spec.md"

    def test_discover_multiple_sources(self, tmp_path, corpus_loader_available):
        """T3: discover() aggregates files from multiple sources."""
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

    def test_exclusion_patterns(self, tmp_path, corpus_loader_available):
        """T4: discover() excludes files matching exclusion patterns."""
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

    def test_include_subdirs_false(self, tmp_path, corpus_loader_available):
        """T6: include_subdirs=false limits discovery to direct children."""
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


class TestCorpusLoaderFilter:
    """Tests for document type filtering."""

    def test_filter_by_type(self, tmp_path, corpus_loader_available):
        """T5: filter_by_type() returns only files matching doc type filter."""
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "TRD-spec.md").touch()
        (tmp_path / "docs" / "ADR-001.md").touch()

        config = {"corpus": {"sources": [
            {"path": "docs", "pattern": "*.md"}
        ]}}
        loader = CorpusLoader(config, base_path=tmp_path)
        files = loader.filter_by_type("TRD")

        assert len(files) == 1
        assert "TRD" in files[0].name


class TestRequirementExtractorIntegration:
    """Tests for RequirementExtractor integration with CorpusLoader."""

    def test_requirement_extractor_with_corpus_loader(
        self, tmp_path, corpus_loader_available, requirement_extractor_available
    ):
        """T7: RequirementExtractor works with CorpusLoader as file source."""
        # Use 'specs' in path to trigger TRDParser (it checks for 'specs' in path)
        (tmp_path / "specs").mkdir()
        spec_file = tmp_path / "specs" / "TRD-test.md"
        spec_file.write_text("| R0 | Must do something | MUST |")

        config = {"corpus": {"name": "test", "sources": [{"path": "specs", "pattern": "*.md"}]}}
        loader = CorpusLoader(config, base_path=tmp_path)
        extractor = RequirementExtractor(loader)
        result = extractor.extract()

        assert len(result.requirements) >= 1
        # Verify source_corpus uses corpus name, not "None"
        assert result.source_corpus == "test"

    def test_requirement_extractor_path_backward_compat(
        self, tmp_path, requirement_extractor_available
    ):
        """T8: RequirementExtractor still accepts Path for backward compatibility."""
        # Use 'specs' in path to trigger TRDParser
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()
        (specs_dir / "TRD-test.md").write_text("| R0 | Test | MUST |")

        extractor = RequirementExtractor(specs_dir)
        result = extractor.extract()

        assert len(result.requirements) >= 1
        # Verify source_corpus uses path string
        assert "specs" in result.source_corpus
