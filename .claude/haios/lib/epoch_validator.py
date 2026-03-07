# generated: 2026-02-16
# WORK-154: Epoch Transition Validation and Queue Config Sync
"""
Epoch Transition Validator (WORK-154).

Validates consistency between:
1. work_queues.yaml queue names vs haios.yaml active_arcs
2. EPOCH.md work item status tables vs actual WORK.md statuses

Integrates into ColdstartOrchestrator as [PHASE: VALIDATION].

Usage:
    from epoch_validator import EpochValidator

    # Injected (testing):
    validator = EpochValidator(haios_config=haios, queue_config=queues)

    # Disk-loading (production):
    validator = EpochValidator()

    result = validator.validate()  # Returns formatted warnings string or ""
"""
from pathlib import Path
from typing import Dict, List, Optional
import re
import yaml
import logging

logger = logging.getLogger(__name__)

# Queues that are not arc-specific (exempt from arc matching).
# Note: 'parked' is a top-level key in work_queues.yaml, not under 'queues:',
# so it is structurally excluded. Only 'default' needs runtime exemption.
EXEMPT_QUEUES = {"default"}

# Work item statuses considered "complete" (triggers drift if EPOCH.md disagrees)
COMPLETE_STATUSES = {"complete", "completed", "done", "closed", "archived"}

# EPOCH.md status values considered "complete-equivalent" (no drift if matched)
EPOCH_COMPLETE_LABELS = {"complete", "completed", "done", "closed"}

# Headings that mark the end of active arc tables in EPOCH.md
STOP_HEADINGS = {"### Completed", "### Deferred"}


class EpochValidator:
    """
    Epoch transition consistency validator.

    Validates queue config against active_arcs and EPOCH.md status
    against actual WORK.md statuses. All inputs are injectable for
    testing; disk I/O is the fallback for production use.
    """

    def __init__(
        self,
        haios_config: Optional[Dict] = None,
        queue_config: Optional[Dict] = None,
        epoch_content: Optional[str] = None,
        work_statuses: Optional[Dict[str, str]] = None,
        base_path: Optional[Path] = None,
    ):
        """
        Initialize with injected configs or load from disk.

        Args:
            haios_config: Parsed haios.yaml dict (or None to load from disk)
            queue_config: Parsed work_queues.yaml dict (or None to load from disk)
            epoch_content: Raw EPOCH.md content string (or None to load from disk)
            work_statuses: Dict of {work_id: status} (or None to scan from disk)
            base_path: Project root path (default: auto-detect from __file__)
        """
        self._base_path = base_path or Path(__file__).parent.parent.parent.parent
        self._haios_config = haios_config or self._load_haios_config()
        self._queue_config = queue_config or self._load_queue_config()
        self._epoch_content = epoch_content or self._load_epoch_content()
        self._work_statuses = work_statuses  # Lazy-loaded in validate_epoch_status

    # =========================================================================
    # Disk Loading (fallback for production)
    # =========================================================================

    def _load_haios_config(self) -> Dict:
        """Load haios.yaml from disk."""
        path = self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load haios.yaml: {e}")
            return {}

    def _load_queue_config(self) -> Dict:
        """Load work_queues.yaml from disk."""
        path = self._base_path / ".claude" / "haios" / "config" / "work_queues.yaml"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load work_queues.yaml: {e}")
            return {}

    def _load_epoch_content(self) -> str:
        """Load EPOCH.md content from disk using haios.yaml epoch_file path."""
        epoch_file = self._haios_config.get("epoch", {}).get("epoch_file", "")
        if not epoch_file:
            return ""
        path = self._base_path / epoch_file
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to load EPOCH.md: {e}")
            return ""

    def _load_work_status(self, work_id: str) -> Optional[str]:
        """Load single work item status via raw YAML parsing (no WorkEngine dependency)."""
        path = self._base_path / "docs" / "work" / "active" / work_id / "WORK.md"
        if not path.exists():
            # Check archive
            path = self._base_path / "docs" / "work" / "archive" / work_id / "WORK.md"
        if not path.exists():
            return None
        try:
            content = path.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None
            fm = yaml.safe_load(parts[1]) or {}
            return fm.get("status")
        except Exception as e:
            logger.warning(f"Failed to read {work_id}: {e}")
            return None

    # =========================================================================
    # Validation Methods
    # =========================================================================

    def validate_queue_config(self) -> Dict[str, List[str]]:
        """
        Check queue names against active_arcs.

        Returns:
            {"warnings": [stale queue msgs], "info": [missing arc msgs]}
        """
        result: Dict[str, List[str]] = {"warnings": [], "info": []}

        active_arcs = set(
            self._haios_config.get("epoch", {}).get("active_arcs", [])
        )
        queue_names = set(self._queue_config.get("queues", {}).keys())

        # Check for stale queues (queue exists but not in active_arcs)
        for queue_name in queue_names:
            if queue_name in EXEMPT_QUEUES:
                continue
            if queue_name not in active_arcs:
                result["warnings"].append(
                    f"Queue '{queue_name}' is not in active_arcs — may be stale from prior epoch"
                )

        # Check for missing queues (active arc with no dedicated queue)
        for arc in active_arcs:
            if arc not in queue_names:
                result["info"].append(
                    f"Active arc '{arc}' has no dedicated queue in work_queues.yaml"
                )

        return result

    def validate_epoch_status(self) -> Dict[str, List[str]]:
        """
        Check EPOCH.md work item references against actual statuses.

        Parses active arc table rows, extracts all WORK-\\d{3} IDs per row
        (handles multi-item cells like 'WORK-152, WORK-155').
        Stops parsing at Completed/Deferred headings.

        Returns:
            {"drift": [drift messages]}
        """
        result: Dict[str, List[str]] = {"drift": []}

        if not self._epoch_content:
            return result

        # Split content at stop headings to only parse active sections
        active_content = self._epoch_content
        for heading in STOP_HEADINGS:
            idx = active_content.find(heading)
            if idx != -1:
                active_content = active_content[:idx]

        # Read arc chapter data via arc_frontmatter if arcs_dir resolvable,
        # else fall back to inline table parsing from EPOCH.md content
        try:
            from arc_frontmatter import get_chapters as get_arc_chapters
            _arc_fm_available = True
        except ImportError:
            try:
                from .arc_frontmatter import get_chapters as get_arc_chapters
                _arc_fm_available = True
            except ImportError:
                _arc_fm_available = False

        # A5 critique fix: derive arcs_dir from self._haios_config
        arcs_dir_str = self._haios_config.get("epoch", {}).get("arcs_dir", "")
        arcs_dir = self._base_path / arcs_dir_str if arcs_dir_str else None

        # Build chapter data from ARC.md frontmatter if available
        # Guard: only use frontmatter path when base_path was explicitly set
        # (not defaulting to real project root in test mode).
        # When work_statuses is injected, caller owns the data — use EPOCH.md fallback.
        arc_chapters_map = {}  # chapter_id -> {"work_items": [...], "status": str}
        _use_frontmatter = (_arc_fm_available and arcs_dir and arcs_dir.exists()
                            and self._work_statuses is None)
        if _use_frontmatter:
            for arc_dir in arcs_dir.iterdir():
                if not arc_dir.is_dir():
                    continue
                arc_file = arc_dir / "ARC.md"
                if arc_file.exists():
                    for ch in get_arc_chapters(arc_file):
                        arc_chapters_map[ch["id"]] = ch

        # Process: prefer arc_frontmatter data, fall back to EPOCH.md table parsing
        # WORK-272: Chapter-level drift detection — only flag when ALL work items
        # in a chapter are complete but the chapter status hasn't been promoted.
        # Previously flagged per-item, producing false positives for chapters
        # that legitimately contain a mix of complete and incomplete items.
        if arc_chapters_map:
            for ch_id, ch_data in arc_chapters_map.items():
                work_ids = re.findall(r"WORK-\d{3}", " ".join(ch_data.get("work_items", [])))
                epoch_status = ch_data["status"].lower()
                if not work_ids:
                    continue
                # Collect statuses for ALL work items in the chapter
                statuses = {}
                for work_id in work_ids:
                    if self._work_statuses is not None:
                        actual_status = self._work_statuses.get(work_id)
                    else:
                        actual_status = self._load_work_status(work_id)
                    if actual_status is not None:
                        statuses[work_id] = actual_status.lower()
                # Only flag drift when ALL chapter work items are complete
                # but the chapter status is not
                if (
                    statuses
                    and all(s in COMPLETE_STATUSES for s in statuses.values())
                    and epoch_status not in EPOCH_COMPLETE_LABELS
                ):
                    ids_str = ", ".join(sorted(statuses.keys()))
                    result["drift"].append(
                        f"DRIFT: All work items in {ch_id} are complete "
                        f"({ids_str}) but chapter status is "
                        f"'{ch_data['status']}' in ARC.md"
                    )
        else:
            # Legacy fallback: parse EPOCH.md table rows directly
            for line in active_content.split("\n"):
                line_stripped = line.strip()
                if not line_stripped.startswith("|"):
                    continue
                if "CH-ID" in line_stripped or "---" in line_stripped:
                    continue
                work_ids = re.findall(r"WORK-\d{3}", line_stripped)
                if not work_ids:
                    continue
                cells = [c.strip() for c in line_stripped.split("|") if c.strip()]
                if len(cells) < 4:
                    continue
                epoch_status = cells[-1].lower()
                # Collect statuses for ALL work items in this chapter row
                statuses = {}
                for work_id in work_ids:
                    if self._work_statuses is not None:
                        actual_status = self._work_statuses.get(work_id)
                    else:
                        actual_status = self._load_work_status(work_id)
                    if actual_status is not None:
                        statuses[work_id] = actual_status.lower()
                # Only flag drift when ALL work items are complete
                if (
                    statuses
                    and all(s in COMPLETE_STATUSES for s in statuses.values())
                    and epoch_status not in EPOCH_COMPLETE_LABELS
                ):
                    ch_id = cells[0] if cells else "unknown"
                    ids_str = ", ".join(sorted(statuses.keys()))
                    result["drift"].append(
                        f"DRIFT: All work items in {ch_id} are complete "
                        f"({ids_str}) but chapter status is "
                        f"'{cells[-1]}' in EPOCH.md"
                    )

        return result

    # =========================================================================
    # Main Validation Entry Point
    # =========================================================================

    def validate(self) -> str:
        """
        Run all validations and return formatted output.

        Returns:
            Formatted warning string, or empty string if no issues found.
            Empty string causes coldstart to skip [PHASE: VALIDATION].
        """
        messages = []

        # Queue config validation
        queue_result = self.validate_queue_config()
        for warning in queue_result["warnings"]:
            messages.append(f"WARNING: {warning}")
        for info in queue_result["info"]:
            messages.append(f"INFO: {info}")

        # Epoch status validation
        status_result = self.validate_epoch_status()
        for drift in status_result["drift"]:
            messages.append(drift)

        if not messages:
            return ""

        return "=== EPOCH VALIDATION ===\n" + "\n".join(messages)
