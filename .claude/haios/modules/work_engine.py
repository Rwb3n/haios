# generated: 2026-01-03
# System Auto: last updated on: 2026-01-09T22:06:03
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

# TYPE_CHECKING imports for delegation (avoid circular imports at runtime)
if TYPE_CHECKING:
    from .cascade_engine import CascadeEngine, CascadeResult
    from .portal_manager import PortalManager
    from .spawn_tree import SpawnTree
    from .backfill_engine import BackfillEngine

WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"


class InvalidTransitionError(Exception):
    """Raised when a DAG transition is invalid."""

    pass


class WorkNotFoundError(Exception):
    """Raised when work item doesn't exist."""

    pass


@dataclass
class WorkState:
    """Typed work item state from parsed WORK.md."""

    id: str
    title: str
    status: str
    current_node: str
    blocked_by: List[str] = field(default_factory=list)
    node_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_refs: List[int] = field(default_factory=list)
    path: Optional[Path] = None


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
        """Path to active work items directory."""
        return self._base_path / ACTIVE_DIR

    @property
    def archive_dir(self) -> Path:
        """Path to archived work items directory."""
        return self._base_path / ARCHIVE_DIR

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
        """
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
        Get all unblocked work items from active directory.

        Returns:
            List of WorkState with empty blocked_by
        """
        ready = []
        if not self.active_dir.exists():
            return ready

        for subdir in self.active_dir.iterdir():
            if subdir.is_dir():
                work_md = subdir / "WORK.md"
                if work_md.exists():
                    work = self._parse_work_file(work_md)
                    if work and not work.blocked_by:
                        ready.append(work)
        return ready

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
        """Parse WORK.md into WorkState."""
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        fm = yaml.safe_load(parts[1]) or {}
        return WorkState(
            id=fm.get("id", ""),
            title=fm.get("title", ""),
            status=fm.get("status", ""),
            current_node=fm.get("current_node", "backlog"),
            blocked_by=fm.get("blocked_by", []) or [],
            node_history=fm.get("node_history", []),
            memory_refs=fm.get("memory_refs", []) or [],
            path=path,
        )

    def _write_work_file(self, work: WorkState) -> None:
        """
        Write WorkState back to WORK.md.

        L4 Invariant: WorkEngine is the ONLY writer to WORK.md files.
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
