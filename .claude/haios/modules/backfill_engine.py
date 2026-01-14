# generated: 2026-01-09
# System Auto: last updated on: 2026-01-09T21:54:50
"""
BackfillEngine Module (E2-279)

Backlog content backfill for work items. Provides:
- backfill(id): Backfill single work item from backlog.md
- backfill_all(): Backfill all active work items

Extracted from WorkEngine as part of E2-279 decomposition per ADR-041 svelte criteria.

L4 Invariants:
- MUST NOT create new work items (uses WorkEngine.get_work to find)
- MUST write updates via WorkEngine pattern (direct file write ok since no state)

Usage:
    from backfill_engine import BackfillEngine
    from work_engine import WorkEngine
    from governance_layer import GovernanceLayer

    work_engine = WorkEngine(GovernanceLayer(), base_path=Path("."))
    backfill = BackfillEngine(work_engine=work_engine, base_path=Path("."))
    backfill.backfill("E2-001")
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import re
import yaml

if TYPE_CHECKING:
    from work_engine import WorkEngine

# Constants
WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
PM_DIR = Path("docs/pm")


class BackfillEngine:
    """
    Backlog content backfill for work items.

    Parses backlog.md and backlog_archive.md to extract context, deliverables,
    and metadata for work items, then updates the work files.
    """

    def __init__(
        self,
        work_engine: "WorkEngine",
        base_path: Optional[Path] = None,
    ):
        """
        Initialize BackfillEngine.

        Args:
            work_engine: WorkEngine instance for work file access
            base_path: Base path for file operations (default: cwd)
        """
        self._work_engine = work_engine
        self._base_path = base_path or Path(".")

    @property
    def active_dir(self) -> Path:
        """Path to active work items directory."""
        return self._base_path / ACTIVE_DIR

    def backfill(self, id: str, force: bool = False) -> bool:
        """
        Backfill work file from backlog.md/backlog_archive.md.

        Args:
            id: Work item ID
            force: Re-process even if placeholders not found

        Returns:
            True if updated, False if not found or no changes
        """
        work = self._work_engine.get_work(id)
        if work is None or work.path is None:
            return False

        # Try backlog.md first, then archive
        backlog_path = self._base_path / PM_DIR / "backlog.md"
        archive_path = self._base_path / PM_DIR / "backlog_archive.md"

        parsed = None
        for source in [backlog_path, archive_path]:
            if source.exists():
                content = source.read_text(encoding="utf-8")
                parsed = self._parse_backlog_entry(id, content)
                if parsed:
                    break

        if not parsed:
            return False

        # Check if work file has placeholders or force mode
        work_content = work.path.read_text(encoding="utf-8")
        if "[Problem and root cause]" not in work_content and not force:
            return False

        # Update work file
        new_content = self._update_work_file_content(work_content, parsed, force)
        work.path.write_text(new_content, encoding="utf-8")
        return True

    def backfill_all(self, force: bool = False) -> Dict[str, List[str]]:
        """
        Backfill all active work items.

        Returns:
            Dict with 'success', 'not_found', 'no_changes' lists
        """
        results: Dict[str, List[str]] = {"success": [], "not_found": [], "no_changes": []}

        if not self.active_dir.exists():
            return results

        for work_dir in self.active_dir.iterdir():
            if not work_dir.is_dir():
                continue
            work_file = work_dir / "WORK.md"
            if not work_file.exists():
                continue

            work_id = work_dir.name

            # Check if already has content
            content = work_file.read_text(encoding="utf-8")
            if "[Problem and root cause]" not in content and not force:
                results["no_changes"].append(work_id)
                continue

            if self.backfill(work_id, force=force):
                results["success"].append(work_id)
            else:
                results["not_found"].append(work_id)

        return results

    def _parse_backlog_entry(self, backlog_id: str, content: str) -> Optional[Dict[str, Any]]:
        """Parse backlog entry and extract fields."""
        # Pattern: ### [STATUS] ID: Title
        pattern = rf"^### \[[^\]]*\] {re.escape(backlog_id)}:.*?(?=^### |\Z)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if not match:
            return None

        entry = match.group(0)
        result: Dict[str, Any] = {
            "context": "",
            "deliverables": [],
            "milestone": None,
            "spawned_by": None,
            "memory_refs": [],
        }

        # Context
        ctx = re.search(r"\*\*Context:\*\*\s*(.+?)(?=\n- \*\*|\n\n|\Z)", entry, re.DOTALL)
        if ctx:
            result["context"] = ctx.group(1).strip()

        # Milestone
        mile = re.search(r"\*\*Milestone:\*\*\s*(\S+)", entry)
        if mile:
            result["milestone"] = mile.group(1)

        # Spawned By
        spawn = re.search(r"\*\*Spawned By:\*\*\s*(.+?)(?=\n|$)", entry)
        if spawn:
            result["spawned_by"] = spawn.group(1).strip()

        # Deliverables (checklist items)
        result["deliverables"] = re.findall(r"^\s*-\s*\[[ x]\]\s*(.+)$", entry, re.MULTILINE)

        # Memory refs
        mem = re.search(r"\*\*Memory:\*\*\s*(.+?)(?=\n|$)", entry)
        if mem:
            mem_str = mem.group(1).strip()
            # Range: "Concepts 64641-64652"
            rng = re.search(r"(\d+)-(\d+)", mem_str)
            if rng:
                start, end = int(rng.group(1)), int(rng.group(2))
                result["memory_refs"] = list(range(start, end + 1))
            else:
                result["memory_refs"] = [int(x) for x in re.findall(r"\d+", mem_str)]

        return result

    def _update_work_file_content(
        self, content: str, parsed: Dict[str, Any], force: bool
    ) -> str:
        """Update work file content with parsed backlog data."""
        # Update Context section
        if parsed["context"]:
            if "[Problem and root cause]" in content:
                content = content.replace(
                    "[Problem and root cause]", f"**Problem:** {parsed['context']}"
                )
            elif force:
                content = re.sub(
                    r"\*\*Problem:\*\*.*?(?=\n---|\n\n##)",
                    f"**Problem:** {parsed['context']}",
                    content,
                    count=1,
                    flags=re.DOTALL,
                )

        # Update Deliverables section
        if parsed["deliverables"]:
            old_deliv = "- [ ] [Deliverable 1]\n- [ ] [Deliverable 2]"
            new_deliv = "\n".join(f"- [ ] {d}" for d in parsed["deliverables"])
            content = content.replace(old_deliv, new_deliv)

        # Update frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            if parsed["milestone"]:
                fm["milestone"] = parsed["milestone"]
            if parsed["spawned_by"]:
                fm["spawned_by"] = parsed["spawned_by"]
            if parsed["memory_refs"]:
                fm["memory_refs"] = parsed["memory_refs"]
            new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
            content = f"---\n{new_fm}---{parts[2]}"

        return content
