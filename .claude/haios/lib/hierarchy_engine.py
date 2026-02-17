# generated: 2026-02-17
# WORK-157: Hierarchy Query Engine (CH-044, engine-functions arc)
"""
Stateless hierarchy query engine for epoch/arc/chapter/work navigation.

Reads hierarchy from existing markdown files (EPOCH.md, ARC.md, WORK.md)
and haios.yaml config. All I/O injectable via base_path for testing.

Functions:
    get_arcs()      -> List[ArcInfo]
    get_chapters()  -> List[ChapterInfo]
    get_work()      -> List[WorkInfo]
    get_hierarchy() -> Optional[HierarchyChain]

Usage:
    from hierarchy_engine import HierarchyQueryEngine
    engine = HierarchyQueryEngine()                  # production
    engine = HierarchyQueryEngine(base_path=tmp_path)  # testing

Design decisions (WORK-157 plan):
    - lib/ not modules/ (no GovernanceLayer dependency, pure data reader)
    - haios.yaml read lazily (only in get_arcs(), not __init__) per A11 critique
    - try/except per file in get_work() per A9 critique
    - Epoch from work item extensions.epoch, fallback to config per A10 critique
    - ChapterInfo.work_items is INFORMATIONAL (from ARC.md table) per A4 critique
    - Column guard >= 6 for ARC.md table parsing per A2 critique
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# =========================================================================
# Data Types
# =========================================================================


@dataclass
class ArcInfo:
    """Arc metadata parsed from haios.yaml active_arcs + ARC.md."""

    name: str  # e.g., "engine-functions"
    theme: str  # From ARC.md ## Definition
    status: str  # From ARC.md ## Definition
    chapters: List[str] = field(default_factory=list)  # Chapter IDs from table


@dataclass
class ChapterInfo:
    """Chapter metadata parsed from ARC.md chapter table row.

    Note (A4 critique): work_items is INFORMATIONAL only (from ARC.md table).
    For authoritative chapter membership, use get_work(chapter_id).
    """

    id: str  # e.g., "CH-044"
    title: str  # e.g., "HierarchyQueryEngine"
    work_items: List[str] = field(default_factory=list)  # IDs from table cell
    status: str = ""  # e.g., "Planning", "Complete"
    arc: str = ""  # Parent arc name


@dataclass
class WorkInfo:
    """Lightweight work item metadata for hierarchy queries."""

    id: str  # e.g., "WORK-157"
    title: str = ""
    status: str = ""
    type: str = ""
    chapter: str = ""  # From frontmatter
    arc: str = ""  # From frontmatter


@dataclass
class HierarchyChain:
    """Full hierarchy chain from work item up to epoch."""

    work_id: str
    chapter: str = ""  # CH-XXX
    arc: str = ""  # Arc name
    epoch: str = ""  # e.g., "E2.7"


# =========================================================================
# Engine
# =========================================================================


class HierarchyQueryEngine:
    """
    Stateless hierarchy query engine for epoch/arc/chapter/work navigation.

    Reads hierarchy from existing markdown files (EPOCH.md, ARC.md, WORK.md)
    via haios.yaml path resolution. All I/O injectable via base_path for testing.

    Usage:
        engine = HierarchyQueryEngine()  # production (auto-detect project root)
        engine = HierarchyQueryEngine(base_path=tmp_path)  # testing
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize engine with project root path.

        haios.yaml is NOT read here (lazy loading, A11 critique).
        Only base_path and active_dir are resolved.

        Args:
            base_path: Project root. Default: auto-detect from __file__
                       (lib/ -> haios/ -> .claude/ -> project root).
        """
        if base_path is None:
            # Auto-detect: .claude/haios/lib/ -> project root
            base_path = Path(__file__).parent.parent.parent.parent
        self._base_path = base_path
        self._active_dir = base_path / "docs" / "work" / "active"

    # =====================================================================
    # Public API
    # =====================================================================

    def get_arcs(self) -> List[ArcInfo]:
        """
        Get all active arcs from haios.yaml epoch.active_arcs + ARC.md files.

        Reads haios.yaml for active_arcs list and arcs_dir path.
        For each arc, parses ARC.md for theme, status, and chapter list.

        Returns:
            List of ArcInfo, sorted by name. Empty list if no arcs_dir or
            config missing.
        """
        config = self._load_haios_config()
        epoch = config.get("epoch", {})
        active_arcs = epoch.get("active_arcs", [])
        arcs_dir_str = epoch.get("arcs_dir", "")

        if not arcs_dir_str or not active_arcs:
            return []

        arcs_dir = self._base_path / arcs_dir_str
        if not arcs_dir.exists():
            return []

        result = []
        for arc_name in active_arcs:
            arc_file = arcs_dir / arc_name / "ARC.md"
            if not arc_file.exists():
                continue

            metadata = self._parse_arc_metadata(arc_file)
            chapters = self._parse_arc_chapters(arc_file, arc_name)
            chapter_ids = [c.id for c in chapters]

            result.append(
                ArcInfo(
                    name=arc_name,
                    theme=metadata.get("theme", ""),
                    status=metadata.get("status", ""),
                    chapters=chapter_ids,
                )
            )

        return sorted(result, key=lambda a: a.name)

    def get_chapters(self, arc_name: str) -> List[ChapterInfo]:
        """
        Get chapters for a given arc from its ARC.md chapter table.

        Parses the markdown table under ## Chapters in ARC.md.
        Table format: | CH-ID | Title | Work Items | Requirements | Dependencies | Status |

        Args:
            arc_name: Arc directory name (e.g., "engine-functions")

        Returns:
            List of ChapterInfo. Empty list if arc not found.
        """
        config = self._load_haios_config()
        arcs_dir_str = config.get("epoch", {}).get("arcs_dir", "")

        if not arcs_dir_str:
            return []

        arc_file = self._base_path / arcs_dir_str / arc_name / "ARC.md"
        if not arc_file.exists():
            return []

        return self._parse_arc_chapters(arc_file, arc_name)

    def get_work(self, chapter_id: str) -> List[WorkInfo]:
        """
        Get work items assigned to a chapter by scanning active work items.

        Reads each WORK.md in docs/work/active/ and filters by chapter field.
        Includes ALL statuses (active, complete, etc.) for completeness queries.

        This is the AUTHORITATIVE source for chapter membership (A4 critique).
        ChapterInfo.work_items from ARC.md table is informational only.

        Args:
            chapter_id: Chapter ID (e.g., "CH-044")

        Returns:
            List of WorkInfo. Empty list if no items found.
        """
        if not self._active_dir.exists():
            return []

        result = []
        for work_dir in self._active_dir.iterdir():
            if not work_dir.is_dir():
                continue
            info = self._parse_work_info(work_dir)
            if info is not None and info.chapter == chapter_id:
                result.append(info)

        return sorted(result, key=lambda w: w.id)

    def get_hierarchy(self, work_id: str) -> Optional[HierarchyChain]:
        """
        Get full hierarchy chain for a work item (work -> chapter -> arc -> epoch).

        Reads work item frontmatter for chapter/arc fields.
        Resolves epoch from work item extensions.epoch first (A10 critique),
        falls back to haios.yaml epoch.current if not present.

        Args:
            work_id: Work item ID (e.g., "WORK-157")

        Returns:
            HierarchyChain if work item has chapter/arc fields, None otherwise.
        """
        work_dir = self._active_dir / work_id
        if not work_dir.exists():
            return None

        fm = self._parse_frontmatter(work_dir / "WORK.md")
        if fm is None:
            return None

        chapter = fm.get("chapter")
        arc = fm.get("arc")
        if not chapter or not arc:
            return None

        # A10 critique: epoch from work item extensions, fallback to config
        extensions = fm.get("extensions") or {}
        epoch = extensions.get("epoch", "")
        if not epoch:
            config = self._load_haios_config()
            epoch = config.get("epoch", {}).get("current", "")

        return HierarchyChain(
            work_id=work_id,
            chapter=chapter,
            arc=arc,
            epoch=epoch,
        )

    # =====================================================================
    # Private Helpers
    # =====================================================================

    def _load_haios_config(self) -> Dict:
        """Load haios.yaml from config directory. Returns empty dict on failure."""
        config_file = (
            self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        )
        if not config_file.exists():
            return {}
        try:
            with open(config_file, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
        """Extract theme and status from ARC.md definition section."""
        content = arc_file.read_text(encoding="utf-8")
        theme = ""
        status = ""
        for line in content.split("\n"):
            if line.startswith("**Theme:**"):
                theme = line.split("**Theme:**", 1)[1].strip()
            elif line.startswith("**Status:**"):
                status = line.split("**Status:**", 1)[1].strip()
        return {"theme": theme, "status": status}

    def _parse_arc_chapters(
        self, arc_file: Path, arc_name: str
    ) -> List[ChapterInfo]:
        """Parse chapter table rows from ARC.md.

        Note (A4 critique): ChapterInfo.work_items is INFORMATIONAL only
        (from ARC.md table). For authoritative chapter membership, use
        get_work(chapter_id) which scans WORK.md files.

        A2 critique: guard requires >= 6 columns (the documented table format).
        """
        content = arc_file.read_text(encoding="utf-8")
        chapters = []
        for line in content.split("\n"):
            # Match: | CH-XXX | Title | Work Items | Requirements | Dependencies | Status |
            if re.match(r"\s*\|\s*CH-\d+", line):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 6:  # A2: must be 6-column table
                    ch_id = cells[0]  # CH-044
                    title = cells[1]  # HierarchyQueryEngine
                    work_str = cells[2]  # "WORK-157" or "WORK-152, WORK-155"
                    status = cells[-1]  # Planning, Complete
                    # Parse work item IDs from cell
                    work_items = re.findall(r"WORK-\d+", work_str)
                    chapters.append(
                        ChapterInfo(
                            id=ch_id,
                            title=title,
                            work_items=work_items,
                            status=status,
                            arc=arc_name,
                        )
                    )
        return chapters

    def _parse_work_info(self, work_dir: Path) -> Optional[WorkInfo]:
        """Parse full WorkInfo from a WORK.md file.

        Extracts all 6 fields: id, title, status, type, chapter, arc.
        Returns None if file missing, malformed, or lacks chapter/arc fields.

        A5 critique: extracts ALL WorkInfo fields, not just chapter/arc.
        A9 critique: wrapped in try/except for malformed YAML tolerance.
        """
        fm = self._parse_frontmatter(work_dir / "WORK.md")
        if fm is None:
            return None

        chapter = fm.get("chapter")
        arc = fm.get("arc")
        if not chapter or not arc:
            return None

        return WorkInfo(
            id=fm.get("id", work_dir.name),
            title=fm.get("title", ""),
            status=fm.get("status", "active"),
            type=fm.get("type", ""),
            chapter=chapter,
            arc=arc,
        )

    def _parse_frontmatter(self, filepath: Path) -> Optional[Dict]:
        """Parse YAML frontmatter from a markdown file.

        Returns parsed dict or None if file missing/malformed.
        A9 critique: try/except for graceful degradation.
        """
        if not filepath.exists():
            return None
        try:
            content = filepath.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None
            return yaml.safe_load(parts[1]) or {}
        except Exception:
            return None  # A9: skip malformed files gracefully
