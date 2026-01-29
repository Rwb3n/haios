# generated: 2026-01-29
# System Auto: last updated on: 2026-01-29T19:30:29
"""
CorpusLoader Module (WORK-031, CH-001)

Provides YAML-configurable file discovery for RequirementExtractor.
Enables Pipeline to work on arbitrary document corpora.

Interface (per CH-001):
    loader = CorpusLoader(corpus_config)
    files = loader.discover()
    filtered = loader.filter_by_type("TRD")

L4 Requirements:
    - CH-001 R1: Corpus Definition Schema (YAML format)
    - CH-001 R2: CorpusLoader Interface (discover, filter_by_type)
    - CH-001 R3: RequirementExtractor Integration
    - CH-001 R4: CLI Integration

Design fixes from critique (Session 258):
    - A3: Use PurePath.match() instead of fnmatch for ** support
    - A4: Try/except around relative_to() for edge cases
"""
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import Dict, List, Optional, Union
import yaml
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

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


# =============================================================================
# CorpusLoader Class
# =============================================================================

class CorpusLoader:
    """Load and discover files from a configured corpus.

    Usage:
        # From YAML file
        loader = CorpusLoader(Path("corpus.yaml"))
        files = loader.discover()

        # From dict config
        config = {"corpus": {"sources": [{"path": "docs", "pattern": "*.md"}]}}
        loader = CorpusLoader(config, base_path=Path("."))
        files = loader.discover()

        # Filter by document type
        trds = loader.filter_by_type("TRD")
    """

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
            # Validate required 'path' field
            if "path" not in src:
                logger.warning("Source missing required 'path' field, skipping")
                continue
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
        (A3 critique fix)
        """
        if not self._parsed.exclude:
            return files

        result = []
        for f in files:
            try:
                rel_path = f.relative_to(self.base_path)
            except ValueError:
                # File not under base_path (e.g., symlink) - skip exclusion check
                # (A4 critique fix)
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
