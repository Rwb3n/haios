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
from typing import Dict, Optional

# Work item statuses considered "complete"
COMPLETE_STATUSES = {"complete", "completed", "done", "closed", "archived"}

# ARC.md chapter statuses considered "complete"
ARC_COMPLETE_STATUSES = {"complete", "completed", "done"}


class StatusPropagator:
    """
    Upstream status propagation from work item closure to ARC.md chapter rows.

    All I/O is injectable via base_path for testing.
    Production use auto-detects project root from __file__.

    # TODO(CH-044): Replace active dir scan with HierarchyQueryEngine.get_chapter_work_items()
    # when CH-044 is implemented.
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
            - action: "no_hierarchy" | "chapter_incomplete" | "chapter_completed" | "arc_completed"
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

        if not self.is_chapter_complete(chapter_id):
            return {
                "action": "chapter_incomplete",
                "work_id": work_id,
                "chapter": chapter_id,
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

    def is_chapter_complete(self, chapter_id: str) -> bool:
        """
        Check if all work items assigned to chapter_id are complete.

        Scans all active work items and checks status of those with
        matching chapter field. Returns False for unfunded chapters
        (no work items found).

        Args:
            chapter_id: Chapter ID (e.g., "CH-045")

        Returns:
            True if all chapter work items have complete status, False otherwise.
        """
        active_dir = self._base_path / "docs" / "work" / "active"
        if not active_dir.exists():
            return False
        chapter_items = []
        for work_path in active_dir.iterdir():
            if not work_path.is_dir():
                continue
            work_file = work_path / "WORK.md"
            if not work_file.exists():
                continue
            content = work_file.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            fm = yaml.safe_load(parts[1]) or {}
            if fm.get("chapter") == chapter_id:
                chapter_items.append(fm.get("status", "active"))
        if not chapter_items:
            return False  # No items = not complete (unfunded)
        return all(s.lower() in COMPLETE_STATUSES for s in chapter_items)

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
