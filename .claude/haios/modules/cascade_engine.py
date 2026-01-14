# generated: 2026-01-08
# System Auto: last updated on: 2026-01-09T00:00:20
"""
CascadeEngine Module (E2-279)

Stateless cascade manager for work item completion effects. Provides:
- cascade(id, status): Run cascade for completed item
- Unblock dependents, notify related, track milestone

Extracted from WorkEngine as part of E2-279 decomposition per ADR-041 svelte criteria.

L4 Invariants:
- MUST NOT modify work files directly (uses WorkEngine for reads)
- MUST emit cascade events to haios-events.jsonl

Usage:
    from cascade_engine import CascadeEngine, CascadeResult
    from work_engine import WorkEngine
    from governance_layer import GovernanceLayer

    engine = CascadeEngine(work_engine=WorkEngine(GovernanceLayer()), base_path=Path("."))
    result = engine.cascade("E2-001", "complete")
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import json
import yaml

if TYPE_CHECKING:
    from work_engine import WorkEngine

# Constants (shared with work_engine.py)
WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"

# Trigger statuses for cascade
TRIGGER_STATUSES = {"complete", "completed", "done", "closed", "accepted"}


@dataclass
class CascadeResult:
    """Result of cascade operation (E2-251)."""

    unblocked: List[str] = field(default_factory=list)  # IDs now READY
    still_blocked: List[str] = field(default_factory=list)  # IDs with remaining blockers
    related: List[str] = field(default_factory=list)  # IDs to review
    milestone_delta: Optional[int] = None  # Progress change (+N%)
    substantive_refs: List[str] = field(default_factory=list)  # Files referencing ID
    message: str = ""  # Formatted cascade report


class CascadeEngine:
    """
    Stateless cascade manager for work item completion effects.

    Handles cascade checks when work items complete:
    1. UNBLOCK - Items blocked by completed item
    2. RELATED - Bidirectional related items
    3. MILESTONE - Progress delta
    4. SUBSTANTIVE - CLAUDE.md/README references
    """

    def __init__(
        self,
        work_engine: "WorkEngine",
        base_path: Optional[Path] = None,
    ):
        """
        Initialize CascadeEngine.

        Args:
            work_engine: WorkEngine instance for work item access
            base_path: Base path for work directories (for testing)
        """
        self._work_engine = work_engine
        self._base_path = base_path or Path(".")

    @property
    def active_dir(self) -> Path:
        """Path to active work items directory."""
        return self._base_path / ACTIVE_DIR

    @property
    def archive_dir(self) -> Path:
        """Path to archived work items directory."""
        return self._base_path / ARCHIVE_DIR

    def cascade(self, id: str, new_status: str, dry_run: bool = False) -> CascadeResult:
        """
        Run cascade for completed item.

        Checks:
        1. UNBLOCK - Items blocked by this item
        2. RELATED - Bidirectional related items
        3. MILESTONE - Progress delta (read from haios-status.json)
        4. SUBSTANTIVE - CLAUDE.md/README references

        Args:
            id: Work item ID (e.g., "E2-100")
            new_status: New status (must be in TRIGGER_STATUSES)
            dry_run: If True, don't write events or refresh status

        Returns:
            CascadeResult with all cascade effects
        """
        # Only trigger on completion statuses
        if new_status.lower() not in TRIGGER_STATUSES:
            return CascadeResult(
                message=f"Status '{new_status}' does not trigger cascade"
            )

        # Run all cascade checks
        unblocked, still_blocked = self._get_unblocked_items(id)
        related = self._get_related_items(id)
        milestone_delta = self._get_milestone_delta(id)
        substantive = self._get_substantive_refs(id)

        # Build message
        message = self._format_cascade_message(
            id, new_status, unblocked, still_blocked, related, milestone_delta, substantive
        )

        # Write cascade event (if not dry run)
        if not dry_run and (unblocked or related):
            self._write_cascade_event(id, unblocked, related, milestone_delta)

        return CascadeResult(
            unblocked=unblocked,
            still_blocked=still_blocked,
            related=related,
            milestone_delta=milestone_delta,
            substantive_refs=substantive,
            message=message,
        )

    def _get_unblocked_items(self, completed_id: str) -> tuple[List[str], List[str]]:
        """
        Find items blocked by completed_id and check if now unblocked.

        Returns:
            Tuple of (unblocked_ids, still_blocked_ids)
        """
        unblocked = []
        still_blocked = []

        if not self.active_dir.exists():
            return unblocked, still_blocked

        for work_dir in self.active_dir.iterdir():
            if not work_dir.is_dir():
                continue
            work_file = work_dir / "WORK.md"
            if not work_file.exists():
                continue

            work = self._parse_work_file(work_file)
            if work is None:
                continue

            # Only process if blocked by completed_id
            blocked_by = work.get("blocked_by", []) or []
            if completed_id not in blocked_by:
                continue

            # Skip if already complete
            status = work.get("status", "")
            if status.lower() in TRIGGER_STATUSES:
                continue

            # Check remaining blockers
            remaining = [
                b for b in blocked_by
                if b != completed_id and not self._is_item_complete(b)
            ]

            work_id = work.get("id", work_dir.name)
            if len(remaining) == 0:
                unblocked.append(work_id)
            else:
                still_blocked.append(work_id)

        return unblocked, still_blocked

    def _is_item_complete(self, item_id: str) -> bool:
        """Check if a work item is complete."""
        work = self._work_engine.get_work(item_id)
        if work is None:
            return False
        return work.status.lower() in TRIGGER_STATUSES

    def _get_related_items(self, completed_id: str) -> List[str]:
        """
        Find items with bidirectional related relationship.

        Returns:
            List of related item IDs
        """
        related = []
        seen = set()

        if not self.active_dir.exists():
            return related

        # Get completed item's related list (outbound)
        completed_work = self._work_engine.get_work(completed_id)
        outbound_related = []
        if completed_work and completed_work.path:
            content = completed_work.path.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1]) or {}
                outbound_related = fm.get("related", []) or []
                if isinstance(outbound_related, str):
                    outbound_related = [outbound_related]

        # Scan all work items
        for work_dir in self.active_dir.iterdir():
            if not work_dir.is_dir():
                continue
            work_file = work_dir / "WORK.md"
            if not work_file.exists():
                continue

            content = work_file.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            fm = yaml.safe_load(parts[1]) or {}
            item_id = fm.get("id", "")
            item_status = fm.get("status", "")
            item_related = fm.get("related", []) or []

            if item_id == completed_id or not item_id:
                continue
            if item_status.lower() in TRIGGER_STATUSES:
                continue

            if isinstance(item_related, str):
                item_related = [item_related]

            # Inbound: item lists completed_id
            if completed_id in item_related and item_id not in seen:
                seen.add(item_id)
                related.append(item_id)

            # Outbound: completed item lists this item
            if item_id in outbound_related and item_id not in seen:
                seen.add(item_id)
                related.append(item_id)

        return related

    def _get_milestone_delta(self, completed_id: str) -> Optional[int]:
        """Get milestone progress delta from haios-status.json."""
        status_file = self._base_path / ".claude" / "haios-status.json"
        if not status_file.exists():
            return None

        try:
            status = json.loads(status_file.read_text(encoding="utf-8"))
            milestones = status.get("milestones", {})

            for milestone in milestones.values():
                items = milestone.get("items", [])
                if completed_id in items:
                    prior = milestone.get("prior_progress", 0)
                    current = milestone.get("progress", 0)
                    complete = list(milestone.get("complete", []))
                    if completed_id not in complete:
                        complete.append(completed_id)
                    total = len(items)
                    new_progress = round(len(complete) / total * 100) if total > 0 else 0
                    return new_progress - current
        except Exception:
            pass

        return None

    def _get_substantive_refs(self, completed_id: str) -> List[str]:
        """Check CLAUDE.md and READMEs for references."""
        refs = []
        check_files = [
            self._base_path / "CLAUDE.md",
            self._base_path / "README.md",
            self._base_path / "docs" / "README.md",
        ]

        for file_path in check_files:
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if completed_id in content:
                        refs.append(str(file_path.relative_to(self._base_path)))
                except Exception:
                    continue

        return refs

    def _format_cascade_message(
        self,
        completed_id: str,
        new_status: str,
        unblocked: List[str],
        still_blocked: List[str],
        related: List[str],
        milestone_delta: Optional[int],
        substantive: List[str],
    ) -> str:
        """Build formatted cascade report."""
        lines = ["--- Cascade (Heartbeat) ---", f"{completed_id} status: {new_status}", ""]

        if unblocked or still_blocked:
            lines.append("[UNBLOCK]")
            for item_id in unblocked:
                lines.append(f"  - {item_id} is now READY (was blocked_by: {completed_id})")
            for item_id in still_blocked:
                lines.append(f"  - {item_id} still has other blockers")
            lines.append("")

        if related:
            lines.append("[RELATED - REVIEW REQUIRED]")
            for item_id in related:
                lines.append(f"  - {item_id}")
            lines.append("")

        if milestone_delta and milestone_delta > 0:
            lines.append(f"[MILESTONE] Progress: +{milestone_delta}%")
            lines.append("")

        if substantive:
            lines.append("[SUBSTANTIVE]")
            for ref in substantive:
                lines.append(f"  - {ref} references {completed_id}")
            lines.append("")

        if unblocked:
            lines.append(f"Action: {unblocked[0]} is next in sequence.")
        elif not unblocked and not related:
            lines.append("No dependents affected.")

        lines.append("--- End Cascade ---")
        return "\n".join(lines)

    def _write_cascade_event(
        self,
        source_id: str,
        unblocked: List[str],
        related: List[str],
        milestone_delta: Optional[int],
    ) -> None:
        """Write cascade event to haios-events.jsonl."""
        events_file = self._base_path / ".claude" / "haios-events.jsonl"
        effects = []
        for item_id in unblocked:
            effects.append(f"unblock:{item_id}")
        if related:
            effects.append(f"related:{len(related)}")
        if milestone_delta:
            effects.append(f"milestone:+{milestone_delta}")

        event = {
            "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "type": "cascade",
            "source": source_id,
            "effects": effects,
        }

        try:
            with open(events_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass  # Best effort

    def _parse_work_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """Parse WORK.md frontmatter into dict."""
        try:
            content = path.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None
            return yaml.safe_load(parts[1]) or {}
        except Exception:
            return None
