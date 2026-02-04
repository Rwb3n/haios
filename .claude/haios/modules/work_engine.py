# generated: 2026-01-03
# System Auto: last updated on: 2026-02-04T21:10:45
"""
WorkEngine Module (E2-242, E2-279 refactored)

Stateless owner of WORK.md files. Provides:
- get_work(id): Parse WORK.md into WorkState
- create_work(id, title, ...): Create new work item directory
- transition(id, to_node): Validate and execute DAG transition
- get_ready(): List unblocked work items
- archive(id): Move to archive directory
- add_memory_refs(id, refs): Link concepts to work item

Delegated to extracted modules (E2-279):
- cascade() -> CascadeEngine
- _create_portal(), _update_portal(), link_spawned_items() -> PortalManager
- spawn_tree(), format_tree() -> SpawnTree
- backfill(), backfill_all() -> BackfillEngine

L4 Invariants:
- MUST be the ONLY writer to WORK.md files
- MUST validate transitions via GovernanceLayer
- MUST update node_history with timestamps on every transition
- MUST call MemoryBridge.auto_link after memory operations

Usage:
    from work_engine import WorkEngine, WorkState, InvalidTransitionError
    from governance_layer import GovernanceLayer

    governance = GovernanceLayer()
    engine = WorkEngine(governance=governance)

    # Get work item
    work = engine.get_work("E2-242")

    # Transition to new node
    work = engine.transition("E2-242", "plan")

    # Get ready items
    ready = engine.get_ready()
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import shutil
import yaml

# Import sibling modules
# Use conditional import to support both package and standalone usage
try:
    from .governance_layer import GovernanceLayer
except ImportError:
    from governance_layer import GovernanceLayer

# Import ConfigLoader for centralized paths (WORK-080)
try:
    from ..lib.config import ConfigLoader
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
    from config import ConfigLoader

# TYPE_CHECKING imports for delegation (avoid circular imports at runtime)
if TYPE_CHECKING:
    from .cascade_engine import CascadeEngine, CascadeResult
    from .portal_manager import PortalManager
    from .spawn_tree import SpawnTree
    from .backfill_engine import BackfillEngine


class InvalidTransitionError(Exception):
    """Raised when a DAG transition is invalid."""

    pass


class WorkNotFoundError(Exception):
    """Raised when work item doesn't exist."""

    pass


class WorkIDUnavailableError(Exception):
    """Raised when work item ID exists with terminal status (E2-304, REQ-VALID-001)."""

    pass


@dataclass
class WorkState:
    """Typed work item state from parsed WORK.md.

    WORK-001: Extended with universal work item fields for pipeline portability.
    WORK-066: Added queue_position and cycle_phase per four-dimensional model.
    """

    id: str
    title: str
    status: str
    current_node: str  # DEPRECATED: use cycle_phase (kept for backward compat)
    type: str = "feature"  # WORK-001: feature|investigation|bug|chore|spike
    queue_position: str = "backlog"  # WORK-066: backlog|in_progress|done
    cycle_phase: str = "backlog"  # WORK-066: renamed from current_node
    blocked_by: List[str] = field(default_factory=list)
    node_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_refs: List[int] = field(default_factory=list)
    requirement_refs: List[str] = field(default_factory=list)  # WORK-001: Links to source requirements
    source_files: List[str] = field(default_factory=list)  # WORK-001: Provenance
    acceptance_criteria: List[str] = field(default_factory=list)  # WORK-001: Verifiable statements
    artifacts: List[str] = field(default_factory=list)  # WORK-001: Build outputs
    extensions: Dict[str, Any] = field(default_factory=dict)  # WORK-001: Project-specific fields
    path: Optional[Path] = None
    priority: str = "medium"  # E2-290: For queue ordering


@dataclass
class QueueConfig:
    """Queue configuration from work_queues.yaml (E2-290)."""

    name: str
    type: str  # fifo, priority, batch, chapter_aligned
    items: Any  # Work IDs list or "auto"
    allowed_cycles: List[str] = field(default_factory=list)
    phases: Optional[List[str]] = None  # For batch type


# Trigger statuses for cascade (shared constant)
TRIGGER_STATUSES = {"complete", "completed", "done", "closed", "accepted"}


class WorkEngine:
    """
    Stateless work item management module.

    Owns all WORK.md file operations, validates transitions via
    GovernanceLayer, and integrates with MemoryBridge for auto-linking.

    Delegated operations (E2-279):
    - cascade() delegated to CascadeEngine
    - Portal operations delegated to PortalManager
    - spawn_tree() delegated to SpawnTree
    - backfill() delegated to BackfillEngine
    """

    def __init__(
        self,
        governance: GovernanceLayer,
        memory: Optional[Any] = None,  # MemoryBridge
        base_path: Optional[Path] = None,
    ):
        """
        Initialize WorkEngine.

        Args:
            governance: GovernanceLayer for transition validation
            memory: Optional MemoryBridge for auto-linking
            base_path: Base path for work directories (for testing)
        """
        self._governance = governance
        self._memory = memory
        self._base_path = base_path or Path(".")

        # Lazy-loaded delegated modules (E2-279)
        self._cascade_engine: Optional["CascadeEngine"] = None
        self._portal_manager: Optional["PortalManager"] = None
        self._spawn_tree: Optional["SpawnTree"] = None
        self._backfill_engine: Optional["BackfillEngine"] = None

    @property
    def active_dir(self) -> Path:
        """Path to active work items directory (WORK-080: via ConfigLoader)."""
        config = ConfigLoader.get()
        return self._base_path / config.get_path("work_active")

    @property
    def archive_dir(self) -> Path:
        """Path to archived work items directory (WORK-080: via ConfigLoader)."""
        config = ConfigLoader.get()
        return self._base_path / config.get_path("work_archive")

    # =========================================================================
    # Core Work Item Operations (E2-242)
    # =========================================================================

    def get_work(self, id: str) -> Optional[WorkState]:
        """
        Get work item by ID.

        Args:
            id: Work item ID (e.g., "E2-242")

        Returns:
            WorkState if found, None otherwise
        """
        path = self._find_work_file(id)
        if path is None:
            return None
        return self._parse_work_file(path)

    def _validate_id_available(self, id: str) -> None:
        """
        Validate that work ID is available for creation (E2-304, REQ-VALID-001).

        Raises WorkIDUnavailableError if ID exists with terminal status.
        Allows overwriting active/draft items for backward compatibility.

        Args:
            id: Work item ID to validate

        Raises:
            WorkIDUnavailableError: If ID exists with status complete/archived
        """
        TERMINAL_STATUSES = {"complete", "archived"}

        work = self.get_work(id)
        if work is None:
            return  # ID available

        if work.status in TERMINAL_STATUSES:
            raise WorkIDUnavailableError(
                f"Work item {id} already exists with status '{work.status}'. "
                "Use a different ID."
            )
        # Allow overwriting active items (backward compat)

    def create_work(
        self,
        id: str,
        title: str,
        milestone: Optional[str] = None,
        priority: str = "medium",
        category: str = "implementation",
    ) -> Path:
        """
        Create new work item with directory structure.

        Args:
            id: Work item ID
            title: Work item title
            milestone: Optional milestone assignment
            priority: Priority level (low, medium, high)
            category: Category (implementation, investigation, etc.)

        Returns:
            Path to created WORK.md

        Raises:
            WorkIDUnavailableError: If ID exists with terminal status (E2-304)
        """
        # REQ-VALID-001: Validate ID availability against terminal statuses
        self._validate_id_available(id)

        work_dir = self.active_dir / id
        work_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (work_dir / "plans").mkdir(exist_ok=True)
        (work_dir / "references").mkdir(exist_ok=True)  # E2-277: Portal directory

        # Create initial REFS.md portal (delegated)
        self._create_portal(id, work_dir / "references" / "REFS.md")

        # Generate WORK.md
        work_path = work_dir / "WORK.md"
        now = datetime.now()
        frontmatter = {
            "template": "work_item",
            "id": id,
            "title": title,
            "status": "active",
            "owner": "Hephaestus",
            "created": now.strftime("%Y-%m-%d"),
            "closed": None,
            "milestone": milestone,
            "priority": priority,
            "category": category,
            "blocked_by": [],
            "blocks": [],
            "current_node": "backlog",
            "node_history": [
                {"node": "backlog", "entered": now.isoformat(), "exited": None}
            ],
            "memory_refs": [],
            "documents": {"plans": [], "investigations": [], "checkpoints": []},
        }
        content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n# WORK-{id}: {title}\n"
        work_path.write_text(content, encoding="utf-8")
        return work_path

    def transition(self, id: str, to_node: str) -> WorkState:
        """
        Transition work item to new DAG node.

        Validates via GovernanceLayer, updates node_history with timestamps.

        Args:
            id: Work item ID
            to_node: Target node

        Returns:
            Updated WorkState

        Raises:
            WorkNotFoundError: If work item doesn't exist
            InvalidTransitionError: If transition is invalid
        """
        work = self.get_work(id)
        if work is None:
            raise WorkNotFoundError(f"Work item {id} not found")

        from_node = work.current_node

        # L4 Invariant: Validate transitions via GovernanceLayer
        if not self._governance.validate_transition(from_node, to_node):
            raise InvalidTransitionError(
                f"Invalid transition: {from_node} -> {to_node}"
            )

        # Update node_history
        now = datetime.now().isoformat()
        if work.node_history:
            work.node_history[-1]["exited"] = now
        work.node_history.append({"node": to_node, "entered": now, "exited": None})
        work.current_node = to_node

        # Write changes (L4 Invariant: WorkEngine is ONLY writer)
        self._write_work_file(work)
        return work

    def get_ready(self) -> List[WorkState]:
        """
        Get all unblocked, active work items from active directory.

        Returns:
            List of WorkState with empty blocked_by and status in ('active', 'in_progress')
        """
        ready = []
        if not self.active_dir.exists():
            return ready

        # WORK-002 (Session 208): Query by tag, not location
        # Only include items with active statuses, exclude terminal states
        terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}

        for subdir in self.active_dir.iterdir():
            if subdir.is_dir():
                work_md = subdir / "WORK.md"
                if work_md.exists():
                    work = self._parse_work_file(work_md)
                    # INV-070: Filter out complete items
                    # WORK-002: Also filter archived, dismissed, invalid, deferred
                    if work and not work.blocked_by and work.status not in terminal_statuses:
                        ready.append(work)
        return ready

    # ========== Pause Point Methods (WORK-085, REQ-LIFECYCLE-002) ==========

    def is_at_pause_point(self, work_id: str) -> bool:
        """
        Check if work item is at valid pause point per S27 Breath Model.

        Pause points are the exhale-complete phases where work can safely stop
        without being considered incomplete. Per REQ-LIFECYCLE-002.

        Args:
            work_id: Work item ID (e.g., "INV-001", "WORK-085")

        Returns:
            True if work is at pause phase, False otherwise
        """
        work = self.get_work(work_id)
        if work is None:
            return False

        # Import PAUSE_PHASES from cycle_runner
        try:
            from .cycle_runner import PAUSE_PHASES
        except ImportError:
            from cycle_runner import PAUSE_PHASES

        # Map work type to lifecycle
        type_to_lifecycle = {
            "investigation": "investigation",
            "design": "design",
            "feature": "implementation",
            "implementation": "implementation",
            "bug": "implementation",
            "chore": "implementation",
            "spike": "investigation",
            "validation": "validation",
            "triage": "triage",
        }
        lifecycle = type_to_lifecycle.get(work.type, "implementation")

        # Check if current_node is a pause phase for this lifecycle
        pause_phases = PAUSE_PHASES.get(lifecycle, [])
        return work.current_node in pause_phases

    # ========== Queue Methods (E2-290) ==========

    def _get_queue_config_path(self) -> Path:
        """Get path to queue config file (WORK-080: via ConfigLoader)."""
        config = ConfigLoader.get()
        return config.get_path("work_queues")

    def load_queues(self) -> Dict[str, QueueConfig]:
        """
        Load queue configuration from work_queues.yaml.

        Returns:
            Dict mapping queue name to QueueConfig
        """
        config_path = self._get_queue_config_path()
        if not config_path.exists():
            # Default queue if no config exists
            return {"default": QueueConfig("default", "priority", "auto", [])}

        with open(config_path) as f:
            config = yaml.safe_load(f)

        queues = {}
        for name, q in config.get("queues", {}).items():
            queues[name] = QueueConfig(
                name=name,
                type=q.get("type", "priority"),
                items=q.get("items", "auto"),
                allowed_cycles=q.get("allowed_cycles", []),
                phases=q.get("phases"),
            )
        return queues

    def get_queue(self, queue_name: str = "default") -> List[WorkState]:
        """
        Get ordered work items from a specific queue.

        Args:
            queue_name: Name of queue to retrieve (default: "default")

        Returns:
            List of WorkState ordered according to queue type

        Session 211 fixes:
        - Bug 1: Filter completed items for explicit item lists (not just auto)
        - Bug 2: FIFO with explicit items preserves YAML order
        """
        queues = self.load_queues()
        if queue_name not in queues:
            return self.get_ready()  # Fallback to flat list

        q = queues[queue_name]

        # Terminal statuses to filter out (same as get_ready)
        terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}

        # Get items
        is_explicit_list = q.items != "auto" and q.items != ["auto"]
        if not is_explicit_list:
            items = self.get_ready()
        else:
            items = []
            for work_id in q.items:
                if self._work_exists(work_id):
                    work = self.get_work(work_id)
                    # Session 211 Bug 1 fix: Filter terminal statuses for explicit lists
                    if work and work.status not in terminal_statuses:
                        items.append(work)

        # Sort by queue type
        if q.type == "priority":
            # Sort by priority (high first), then by id
            priority_order = {"high": 0, "medium": 1, "low": 2}
            items.sort(key=lambda x: (priority_order.get(x.priority, 1), x.id))
        elif q.type == "fifo":
            # Session 211 Bug 2 fix: For explicit lists, preserve YAML order
            # For auto lists, sort by creation date
            if not is_explicit_list:
                items.sort(
                    key=lambda x: x.node_history[0]["entered"] if x.node_history else ""
                )
            # Explicit FIFO lists already in correct order from the loop above

        return items

    def get_next(self, queue_name: str = "default") -> Optional[WorkState]:
        """
        Get next item from queue head.

        Args:
            queue_name: Name of queue (default: "default")

        Returns:
            First WorkState from queue, or None if empty
        """
        queue = self.get_queue(queue_name)
        return queue[0] if queue else None

    def is_cycle_allowed(self, queue_name: str, cycle_name: str) -> bool:
        """
        Check if cycle is allowed for this queue (cycle-locking).

        Args:
            queue_name: Name of queue to check
            cycle_name: Name of cycle to verify

        Returns:
            True if cycle is allowed, False if blocked
        """
        queues = self.load_queues()
        if queue_name not in queues:
            return True  # No queue = no restrictions

        q = queues[queue_name]
        if not q.allowed_cycles:
            return True  # Empty list = all allowed

        return cycle_name in q.allowed_cycles

    def _work_exists(self, work_id: str) -> bool:
        """Check if work item exists."""
        work_dir = self.active_dir / work_id
        return (work_dir / "WORK.md").exists()

    # ========== End Queue Methods ==========

    def close(self, id: str) -> Path:
        """
        Close work item: set status=complete, closed date.

        Per ADR-041 "status over location": work items stay in docs/work/active/
        until epoch cleanup. The status field determines state, not directory path.

        Args:
            id: Work item ID

        Returns:
            Path to WORK.md (stays in active/)

        Raises:
            WorkNotFoundError: If work item doesn't exist
        """
        work = self.get_work(id)
        if work is None:
            raise WorkNotFoundError(f"Work item {id} not found")

        # Update status and closed date
        work.status = "complete"
        self._write_work_file(work)

        # Set closed date in frontmatter
        self._set_closed_date(work.path, datetime.now().strftime("%Y-%m-%d"))

        # ADR-041: No move to archive - status field determines state
        return work.path

    def _set_closed_date(self, path: Path, date: str) -> None:
        """Set the closed date in work file frontmatter."""
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return
        fm = yaml.safe_load(parts[1]) or {}
        fm["closed"] = date
        new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
        path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")

    def archive(self, id: str) -> Path:
        """
        Move work item to archive directory.

        Preserves entire directory structure (plans/, observations.md, etc.).

        Args:
            id: Work item ID

        Returns:
            Path to archived WORK.md

        Raises:
            WorkNotFoundError: If work item doesn't exist
        """
        source_dir = self.active_dir / id
        if not source_dir.exists():
            raise WorkNotFoundError(f"Work item {id} not found in active/")

        dest_dir = self.archive_dir / id
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Move entire directory (preserves plans/, etc.)
        shutil.move(str(source_dir), str(dest_dir))
        return dest_dir / "WORK.md"

    def add_memory_refs(self, id: str, concept_ids: List[int]) -> None:
        """
        Add memory references to work item.

        L4 Invariant: Calls MemoryBridge.auto_link after memory operations.

        Args:
            id: Work item ID
            concept_ids: List of concept IDs to link
        """
        work = self.get_work(id)
        if work is None:
            return

        # Extend memory_refs (dedup)
        existing = set(work.memory_refs)
        for cid in concept_ids:
            if cid not in existing:
                work.memory_refs.append(cid)

        self._write_work_file(work)

        # E2-277: Update portal with memory refs (delegated)
        self._update_portal(id, {"memory_refs": work.memory_refs})

        # L4 Invariant: Call MemoryBridge if available
        if self._memory:
            self._memory.auto_link(id, concept_ids)

    # =========================================================================
    # Queue Position Methods (WORK-066: Four-Dimensional Model)
    # =========================================================================

    def set_queue_position(self, id: str, position: str) -> Optional[WorkState]:
        """
        Set queue_position for work item (WORK-066).

        Uses unified write path via _write_work_file() per critique A1.

        Args:
            id: Work item ID
            position: New position (backlog, in_progress, done)

        Returns:
            Updated WorkState, or None if not found

        Raises:
            ValueError: If position is not valid
        """
        VALID_POSITIONS = {"backlog", "in_progress", "done"}
        if position not in VALID_POSITIONS:
            raise ValueError(
                f"Invalid queue_position: {position}. Must be one of {VALID_POSITIONS}"
            )

        work = self.get_work(id)
        if work is None:
            return None

        # Update in-memory state
        work.queue_position = position

        # Persist via unified write path (A1 mitigation)
        self._write_work_file(work)

        return work

    def get_in_progress(self) -> List[WorkState]:
        """
        Get all work items with queue_position: in_progress (WORK-066).

        Used by survey-cycle to enforce single in_progress constraint.

        Returns:
            List of WorkState with queue_position == "in_progress"
        """
        result = []
        if not self.active_dir.exists():
            return result

        for subdir in self.active_dir.iterdir():
            if subdir.is_dir():
                work_md = subdir / "WORK.md"
                if work_md.exists():
                    work = self._parse_work_file(work_md)
                    if work and work.queue_position == "in_progress":
                        result.append(work)
        return result

    def add_document_link(self, id: str, doc_type: str, doc_path: str) -> None:
        """
        Link a document to the work item.

        Updates both cycle_docs (current node's doc) and documents section.

        Args:
            id: Work item ID
            doc_type: Document type (plan, investigation, checkpoint)
            doc_path: Path to the document being linked
        """
        path = self._find_work_file(id)
        if path is None:
            raise WorkNotFoundError(f"Work item {id} not found")

        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        fm = yaml.safe_load(parts[1]) or {}

        # Map doc_type to documents key (plural)
        type_map = {"plan": "plans", "investigation": "investigations", "checkpoint": "checkpoints"}
        docs_key = type_map.get(doc_type, f"{doc_type}s")

        # Update documents section
        fm.setdefault("documents", {}).setdefault(docs_key, [])
        if doc_path not in fm["documents"][docs_key]:
            fm["documents"][docs_key].append(doc_path)

        # Update cycle_docs for current node
        current_node = fm.get("current_node", "backlog")
        fm.setdefault("cycle_docs", {})[current_node] = doc_path

        # Write back
        new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
        path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _find_work_file(self, id: str) -> Optional[Path]:
        """Find WORK.md for given ID."""
        # Directory structure (primary)
        dir_path = self.active_dir / id / "WORK.md"
        if dir_path.exists():
            return dir_path

        # Check archive
        archive_path = self.archive_dir / id / "WORK.md"
        if archive_path.exists():
            return archive_path

        return None

    def _parse_work_file(self, path: Path) -> Optional[WorkState]:
        """Parse WORK.md into WorkState.

        WORK-001: Extended to parse universal work item fields with backward compat.
        - type falls back to category field for legacy items
        - New fields default to empty list/dict if missing

        WORK-066: Parse queue_position and cycle_phase with backward compat.
        - queue_position defaults to "backlog" if missing
        - cycle_phase falls back to current_node for legacy items
        """
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        fm = yaml.safe_load(parts[1]) or {}
        # WORK-066: Parse current_node first for cycle_phase fallback
        current_node_val = fm.get("current_node", "backlog")
        return WorkState(
            id=fm.get("id", ""),
            title=fm.get("title", ""),
            status=fm.get("status", ""),
            current_node=current_node_val,  # DEPRECATED: kept for backward compat
            # WORK-001: type with fallback to category for backward compat
            type=fm.get("type", fm.get("category", "feature")),
            # WORK-066: New queue_position and cycle_phase fields
            queue_position=fm.get("queue_position", "backlog"),
            cycle_phase=fm.get("cycle_phase", current_node_val),  # Falls back to current_node
            blocked_by=fm.get("blocked_by", []) or [],
            node_history=fm.get("node_history", []),
            memory_refs=fm.get("memory_refs", []) or [],
            # WORK-001: Universal work item fields
            requirement_refs=fm.get("requirement_refs", []) or [],
            source_files=fm.get("source_files", []) or [],
            acceptance_criteria=fm.get("acceptance_criteria", []) or [],
            artifacts=fm.get("artifacts", []) or [],
            extensions=fm.get("extensions", {}) or {},
            path=path,
            priority=fm.get("priority", "medium"),  # E2-290: Queue ordering
        )

    def _write_work_file(self, work: WorkState) -> None:
        """
        Write WorkState back to WORK.md.

        L4 Invariant: WorkEngine is the ONLY writer to WORK.md files.
        WORK-066: Unified write path for queue_position and cycle_phase (A1 mitigation).
        """
        if work.path is None:
            return

        content = work.path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        fm = yaml.safe_load(parts[1]) or {}
        fm["current_node"] = work.current_node
        fm["node_history"] = work.node_history
        fm["memory_refs"] = work.memory_refs
        fm["status"] = work.status
        # WORK-066: Persist queue_position and cycle_phase (unified write path per A1)
        fm["queue_position"] = work.queue_position
        fm["cycle_phase"] = work.cycle_phase
        fm["last_updated"] = datetime.now().isoformat()

        new_fm = yaml.dump(
            fm, default_flow_style=False, sort_keys=False, allow_unicode=True
        )
        work.path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")

    # =========================================================================
    # Delegated Methods (E2-279: Backward Compatibility)
    # =========================================================================

    def _get_portal_manager(self) -> "PortalManager":
        """Lazy-load PortalManager."""
        if self._portal_manager is None:
            # E2-255 pattern: support both package and standalone usage
            try:
                from .portal_manager import PortalManager
            except ImportError:
                from portal_manager import PortalManager

            self._portal_manager = PortalManager(
                base_path=self._base_path, work_engine=self
            )
        return self._portal_manager

    def _create_portal(self, id: str, refs_path: Path) -> None:
        """Delegate to PortalManager."""
        self._get_portal_manager().create_portal(id, refs_path)

    def _update_portal(self, id: str, updates: Dict[str, Any]) -> None:
        """Delegate to PortalManager."""
        self._get_portal_manager().update_portal(id, updates)

    def link_spawned_items(
        self, spawned_by: str, ids: List[str], milestone: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Delegate to PortalManager."""
        return self._get_portal_manager().link_spawned_items(spawned_by, ids, milestone)

    def cascade(self, id: str, new_status: str, dry_run: bool = False) -> "CascadeResult":
        """
        Delegate to CascadeEngine.

        Args:
            id: Work item ID
            new_status: New status (triggers cascade if in TRIGGER_STATUSES)
            dry_run: If True, don't write events

        Returns:
            CascadeResult with cascade effects
        """
        if self._cascade_engine is None:
            # E2-255 pattern: support both package and standalone usage
            try:
                from .cascade_engine import CascadeEngine
            except ImportError:
                from cascade_engine import CascadeEngine

            self._cascade_engine = CascadeEngine(
                work_engine=self, base_path=self._base_path
            )
        return self._cascade_engine.cascade(id, new_status, dry_run)

    def spawn_tree(self, root_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """Delegate to SpawnTree."""
        if self._spawn_tree is None:
            # E2-255 pattern: support both package and standalone usage
            try:
                from .spawn_tree import SpawnTree
            except ImportError:
                from spawn_tree import SpawnTree

            self._spawn_tree = SpawnTree(base_path=self._base_path)
        return self._spawn_tree.spawn_tree(root_id, max_depth)

    @staticmethod
    def format_tree(tree: Dict[str, Any], use_ascii: bool = False) -> str:
        """Delegate to SpawnTree."""
        # E2-255 pattern: support both package and standalone usage
        try:
            from .spawn_tree import SpawnTree
        except ImportError:
            from spawn_tree import SpawnTree

        return SpawnTree.format_tree(tree, use_ascii)

    def backfill(self, id: str, force: bool = False) -> bool:
        """Delegate to BackfillEngine."""
        if self._backfill_engine is None:
            # E2-255 pattern: support both package and standalone usage
            try:
                from .backfill_engine import BackfillEngine
            except ImportError:
                from backfill_engine import BackfillEngine

            self._backfill_engine = BackfillEngine(
                work_engine=self, base_path=self._base_path
            )
        return self._backfill_engine.backfill(id, force)

    def backfill_all(self, force: bool = False) -> Dict[str, List[str]]:
        """Delegate to BackfillEngine."""
        if self._backfill_engine is None:
            # E2-255 pattern: support both package and standalone usage
            try:
                from .backfill_engine import BackfillEngine
            except ImportError:
                from backfill_engine import BackfillEngine

            self._backfill_engine = BackfillEngine(
                work_engine=self, base_path=self._base_path
            )
        return self._backfill_engine.backfill_all(force)
