# generated: 2026-02-16
# WORK-034: Upstream Status Propagation on Work Closure
"""
Upstream Status Propagation (WORK-034).

Propagates work item closure status to chapter rows in ARC.md.
When all work items for a chapter are complete, updates the chapter
status in the parent arc's ARC.md file. Checks arc completion and
logs StatusPropagation events.

Usage:
    from status_propagator import StatusPropagator

    # Injected (testing):
    propagator = StatusPropagator(base_path=tmp_path)

    # Disk-loading (production):
    propagator = StatusPropagator()

    result = propagator.propagate("WORK-034")
    # result = {"action": "chapter_completed", "chapter": "CH-045", ...}

Integration: close-work-cycle ARCHIVE phase calls propagate() after just close-work.
"""
import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Work item statuses considered "complete"
COMPLETE_STATUSES = {"complete", "completed", "done", "closed", "archived"}

# ARC.md chapter statuses considered "complete"
ARC_COMPLETE_STATUSES = {"complete", "completed", "done"}


class StatusPropagator:
    """
    Upstream status propagation from work item closure to ARC.md chapter rows.

    All I/O is injectable via base_path for testing.
    Production use auto-detects project root from __file__.

    CH-044 resolved: Uses HierarchyQueryEngine for chapter work item queries.
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        events_file: Optional[Path] = None,
    ):
        self._base_path = base_path or Path(__file__).parent.parent.parent.parent
        self._events_file = events_file or (
            self._base_path / ".claude" / "haios" / "governance-events.jsonl"
        )
        # Lazy import to avoid circular dependency issues
        from hierarchy_engine import HierarchyQueryEngine

        self._hierarchy = HierarchyQueryEngine(base_path=self._base_path)

    def propagate(self, work_id: str) -> dict:
        """
        Main entry point. Propagates status for a closed work item.

        1. Reads chapter/arc from work item frontmatter
        2. Checks if all chapter work items are complete
        3. Updates ARC.md chapter status row
        4. Checks if entire arc is complete
        5. Logs StatusPropagation event

        Args:
            work_id: Work item ID (e.g., "WORK-034")

        Returns:
            dict with keys:
            - action: "no_hierarchy" | "chapter_incomplete" | "chapter_criteria_unmet" | "chapter_completed" | "arc_completed"
            - work_id: The work item ID
            - chapter: Chapter ID (if hierarchy exists)
            - arc: Arc name (if hierarchy exists)
            - arc_updated: bool (if chapter completed)
            - arc_complete: bool (if chapter completed)
        """
        ctx = self.get_hierarchy_context(work_id)
        if ctx is None:
            return {"action": "no_hierarchy", "work_id": work_id}

        chapter_id = ctx["chapter"]
        arc_name = ctx["arc"]

        # Check work item completion first
        items = self._hierarchy.get_work(chapter_id)
        all_items_complete = (
            bool(items) and all(item.status.lower() in COMPLETE_STATUSES for item in items)
        )

        if not all_items_complete:
            return {
                "action": "chapter_incomplete",
                "work_id": work_id,
                "chapter": chapter_id,
            }

        # Check exit criteria (WORK-239: two-predicate conjunction)
        criteria = self._check_exit_criteria(chapter_id, arc_name)
        if criteria is not None and not criteria["all_checked"]:
            return {
                "action": "chapter_criteria_unmet",
                "work_id": work_id,
                "chapter": chapter_id,
                "arc": arc_name,
                "unchecked_items": criteria["unchecked_items"],
                "criteria_checked": criteria["checked"],
                "criteria_total": criteria["total"],
            }

        update_result = self.update_arc_chapter_status(arc_name, chapter_id, "Complete")
        arc_complete = self.is_arc_complete(arc_name)
        action = "arc_completed" if arc_complete else "chapter_completed"
        self._log_event(work_id, chapter_id, arc_name, action)

        return {
            "action": action,
            "work_id": work_id,
            "chapter": chapter_id,
            "arc": arc_name,
            "arc_updated": update_result["updated"],
            "arc_complete": arc_complete,
        }

    def get_hierarchy_context(self, work_id: str) -> Optional[Dict]:
        """
        Read chapter and arc fields from work item frontmatter.

        Args:
            work_id: Work item ID (e.g., "WORK-034")

        Returns:
            {"chapter": "CH-045", "arc": "engine-functions"} or None
        """
        work_file = self._base_path / "docs" / "work" / "active" / work_id / "WORK.md"
        if not work_file.exists():
            return None
        content = work_file.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        fm = yaml.safe_load(parts[1]) or {}
        chapter = fm.get("chapter")
        arc = fm.get("arc")
        if not chapter or not arc:
            return None
        return {"chapter": chapter, "arc": arc}

    def is_chapter_complete(self, chapter_id: str, arc_name: Optional[str] = None) -> bool:
        """
        Check if chapter is complete: all work items done AND exit criteria checked.

        Two-predicate conjunction (WORK-222 / WORK-239):
        1. All work items assigned to chapter have complete status
        2. All exit criteria checkboxes in CHAPTER.md are checked

        Graceful degradation (L3.6): if CHAPTER.md or exit criteria section
        is missing, falls back to work-item-count-only predicate.

        Args:
            chapter_id: Chapter ID (e.g., "CH-045")
            arc_name: Arc directory name (optional). When provided, enables
                      exit criteria validation by locating CHAPTER.md.

        Returns:
            True if chapter is complete, False otherwise.
        """
        # Predicate 1: All work items complete
        items = self._hierarchy.get_work(chapter_id)
        if not items:
            return False  # No items = not complete (unfunded)
        if not all(item.status.lower() in COMPLETE_STATUSES for item in items):
            return False

        # Predicate 2: Exit criteria (when arc_name available)
        if arc_name is not None:
            criteria = self._check_exit_criteria(chapter_id, arc_name)
            if criteria is not None and not criteria["all_checked"]:
                return False

        return True

    def _check_exit_criteria(self, chapter_id: str, arc_name: str) -> Optional[Dict]:
        """
        Parse exit criteria checkboxes from CHAPTER.md.

        Locates CHAPTER.md via arcs_dir/arc_name/chapters/CH-XXX-*/CHAPTER.md
        convention, then parses the ## Exit Criteria section for markdown
        checkboxes (- [ ] / - [x]).

        Args:
            chapter_id: Chapter ID (e.g., "CH-045")
            arc_name: Arc directory name (e.g., "infrastructure")

        Returns:
            {"all_checked": bool, "total": int, "checked": int, "unchecked_items": list[str]}
            or None if CHAPTER.md not found or no exit criteria section.
        """
        chapter_file = self._find_chapter_file(chapter_id, arc_name)
        if chapter_file is None:
            return None

        content = chapter_file.read_text(encoding="utf-8")

        # Find ## Exit Criteria section
        lines = content.split("\n")
        in_section = False
        criteria: List[tuple] = []

        for line in lines:
            if re.match(r"^##\s+Exit Criteria", line):
                in_section = True
                continue
            if in_section and re.match(r"^##\s+", line):
                break  # Next section starts
            if in_section:
                m = re.match(r"^- \[([ x])\] (.+)$", line)
                if m:
                    checked = m.group(1) == "x"
                    criteria.append((checked, m.group(2).strip()))

        if not criteria:
            return None  # No exit criteria found

        checked_count = sum(1 for c, _ in criteria if c)
        unchecked_items = [desc for c, desc in criteria if not c]

        return {
            "all_checked": checked_count == len(criteria),
            "total": len(criteria),
            "checked": checked_count,
            "unchecked_items": unchecked_items,
        }

    def _find_chapter_file(self, chapter_id: str, arc_name: str) -> Optional[Path]:
        """
        Locate CHAPTER.md for a given chapter ID and arc.

        Convention: {arcs_dir}/{arc_name}/chapters/{chapter_id}-{Name}/CHAPTER.md

        Args:
            chapter_id: Chapter ID (e.g., "CH-045")
            arc_name: Arc directory name (e.g., "infrastructure")

        Returns:
            Path to CHAPTER.md, or None if not found.
        """
        haios_path = self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        if not haios_path.exists():
            return None
        haios_config = yaml.safe_load(haios_path.read_text(encoding="utf-8"))
        arcs_dir = haios_config.get("epoch", {}).get("arcs_dir", "")
        if not arcs_dir:
            return None

        chapters_dir = self._base_path / arcs_dir / arc_name / "chapters"
        if not chapters_dir.exists():
            return None

        # Scan for directory starting with chapter_id
        for d in chapters_dir.iterdir():
            if d.is_dir() and d.name.startswith(f"{chapter_id}-"):
                chapter_file = d / "CHAPTER.md"
                if chapter_file.exists():
                    return chapter_file

        return None

    def update_arc_chapter_status(
        self, arc_name: str, chapter_id: str, new_status: str
    ) -> dict:
        """
        Update the chapter row in ARC.md status table.

        Finds the ARC.md file via haios.yaml epoch.arcs_dir, locates the
        chapter row by ID in the markdown table, and replaces the status cell.

        Args:
            arc_name: Arc directory name (e.g., "engine-functions")
            chapter_id: Chapter ID (e.g., "CH-045")
            new_status: New status value (e.g., "Complete")

        Returns:
            {"updated": True} on success, {"updated": False, "reason": str} on failure.
        """
        haios_path = self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        if not haios_path.exists():
            return {"updated": False, "reason": "haios_config_not_found"}
        haios_config = yaml.safe_load(haios_path.read_text(encoding="utf-8"))
        arcs_dir = haios_config.get("epoch", {}).get("arcs_dir", "")
        arc_file = self._base_path / arcs_dir / arc_name / "ARC.md"
        if not arc_file.exists():
            return {"updated": False, "reason": "arc_file_not_found"}

        content = arc_file.read_text(encoding="utf-8")
        # Line-by-line approach: find the chapter row, replace last cell (Status)
        lines = content.split("\n")
        found = False
        for i, line in enumerate(lines):
            if re.match(rf"\s*\|\s*{re.escape(chapter_id)}\s*\|", line):
                cells = line.split("|")
                # cells: ['', ' CH-XXX ', ' Title ', ..., ' Status ', '']
                # Find last non-empty cell (Status) and replace it
                for j in range(len(cells) - 1, -1, -1):
                    if cells[j].strip():
                        cells[j] = f" {new_status} "
                        break
                lines[i] = "|".join(cells)
                found = True
                break
        if not found:
            return {"updated": False, "reason": "chapter_row_not_found"}

        arc_file.write_text("\n".join(lines), encoding="utf-8")
        return {"updated": True}

    def is_arc_complete(self, arc_name: str) -> bool:
        """
        Check if all chapters in ARC.md have Complete status.

        Parses the chapter table and checks every status cell.
        Returns False if no chapters found or any chapter is not complete.

        Args:
            arc_name: Arc directory name (e.g., "infrastructure")

        Returns:
            True if all chapter rows have complete status, False otherwise.
        """
        haios_path = self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        if not haios_path.exists():
            return False
        haios_config = yaml.safe_load(haios_path.read_text(encoding="utf-8"))
        arcs_dir = haios_config.get("epoch", {}).get("arcs_dir", "")
        arc_file = self._base_path / arcs_dir / arc_name / "ARC.md"
        if not arc_file.exists():
            return False
        content = arc_file.read_text(encoding="utf-8")
        # Parse chapter rows by splitting cells — more reliable than regex across lines
        statuses = []
        for line in content.split("\n"):
            if re.match(r"\s*\|\s*CH-\d+", line):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if cells:
                    statuses.append(cells[-1])  # Last cell = Status
        if not statuses:
            return False
        return all(s.lower() in ARC_COMPLETE_STATUSES for s in statuses)

    def _log_event(
        self, work_id: str, chapter: str, arc: str, action: str
    ) -> None:
        """
        Append StatusPropagation event to governance-events.jsonl.

        Args:
            work_id: Work item ID
            chapter: Chapter ID
            arc: Arc name
            action: Action type (chapter_completed, arc_completed)
        """
        event = {
            "type": "StatusPropagation",
            "work_id": work_id,
            "chapter": chapter,
            "arc": arc,
            "action": action,
            "timestamp": datetime.now().isoformat(),
        }
        self._events_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
