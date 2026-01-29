# generated: 2026-01-29
# System Auto: last updated on: 2026-01-29T21:28:07
"""
PlannerAgent Module (WORK-032, CH-003)

PLAN stage component for the doc-to-product pipeline.
Transforms RequirementSet into WorkPlan with grouped work items,
dependency graph, and execution order.

Interface (per CH-003 R2):
    planner = PlannerAgent(requirements)
    groupings = planner.suggest_groupings()  # For operator review
    deps = planner.estimate_dependencies()   # Dependency graph
    plan = planner.plan()                    # Full WorkPlan

L4 Requirements:
    - CH-003 R1: WorkPlan Schema
    - CH-003 R2: PlannerAgent Interface
    - CH-003 R3: Grouping Heuristics (domain, strength)
    - CH-003 R4: CLI Integration
    - S26: Pipeline stage interface

Non-Goals (per CH-003):
    - Work item creation (that's WorkEngine's job)
    - Execution (that's BUILD stage)
    - Human-level design decisions (agent suggests, operator approves)
"""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
import logging
import re

# Import sibling modules (A5: follow existing pattern from requirement_extractor.py)
try:
    from .requirement_extractor import Requirement, RequirementSet, RequirementStrength
except ImportError:
    try:
        from requirement_extractor import Requirement, RequirementSet, RequirementStrength
    except ImportError:
        # Allow module to load even if requirement_extractor not available
        Requirement = None  # type: ignore
        RequirementSet = None  # type: ignore
        RequirementStrength = None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes (CH-003 R1: WorkPlan Schema)
# =============================================================================

@dataclass
class PlannedWorkItem:
    """A work item suggested by the planner.

    Uses WORK-PXXX prefix to distinguish from actual work items
    until operator approves and WorkEngine creates them.
    """
    id: str  # Suggested WORK-PXXX
    title: str
    type: str = "feature"
    requirement_refs: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: str = "medium"
    priority: str = "medium"


@dataclass
class RequirementGroup:
    """A group of requirements to become a single work item.

    Groups are formed by domain (REQ-TRACE-*, REQ-CONTEXT-*, etc.)
    and sorted by strength (MUST before SHOULD).
    """
    domain: str  # e.g., "TRACE", "CONTEXT", "GENERAL"
    requirements: List['Requirement'] = field(default_factory=list)
    suggested_title: str = ""

    def __post_init__(self):
        """Generate suggested title if not provided."""
        if not self.suggested_title and self.domain:
            self.suggested_title = f"Implement {self.domain} requirements"


@dataclass
class DependencyGraph:
    """Graph of dependencies between requirements/work items.

    Uses Kahn's algorithm for topological sort to determine execution order.
    Handles cycles gracefully with warning and partial ordering.
    """
    edges: List[Tuple[str, str]] = field(default_factory=list)
    nodes: Set[str] = field(default_factory=set)

    def add_edge(self, dependent: str, dependency: str):
        """Add a dependency edge: dependent depends on dependency."""
        self.edges.append((dependent, dependency))
        self.nodes.add(dependent)
        self.nodes.add(dependency)

    def topological_sort(self) -> List[str]:
        """Return nodes in dependency order using Kahn's algorithm.

        Returns:
            List of node IDs in execution order (dependencies first).
            If cycles detected, returns partial ordering with warning.
        """
        if not self.nodes:
            return []

        # Build adjacency list and in-degree count
        in_degree: Dict[str, int] = {node: 0 for node in self.nodes}
        adjacency: Dict[str, List[str]] = defaultdict(list)

        for dependent, dependency in self.edges:
            adjacency[dependency].append(dependent)
            in_degree[dependent] = in_degree.get(dependent, 0) + 1

        # Start with nodes that have no dependencies
        queue = [node for node in self.nodes if in_degree[node] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for dependent in adjacency[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles
        if len(result) != len(self.nodes):
            remaining = self.nodes - set(result)
            logger.warning(f"Cycle detected in dependencies. Remaining nodes: {remaining}")
            # Add remaining nodes at end (partial ordering)
            result.extend(remaining)

        return result


@dataclass
class WorkPlan:
    """Output of the PLAN stage per S26.

    Contains work items, execution order, and dependency graph
    for operator review before WorkEngine creates actual work items.
    """
    source_requirements: 'RequirementSet'
    created_at: datetime
    planner_version: str
    work_items: List[PlannedWorkItem] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    dependency_graph: DependencyGraph = field(default_factory=DependencyGraph)


# =============================================================================
# PlannerAgent Class (CH-003 R2)
# =============================================================================

class PlannerAgent:
    """PLAN stage component per S26.

    Transforms RequirementSet into WorkPlan by:
    1. Grouping requirements by domain
    2. Estimating dependencies from derives_from links
    3. Generating work items with topological ordering

    Usage:
        planner = PlannerAgent(requirements)
        groupings = planner.suggest_groupings()  # Operator reviews
        plan = planner.plan()  # Or with approved groupings
    """

    VERSION = "1.0.0"

    # Pattern to extract domain from requirement ID: REQ-{DOMAIN}-{NNN}
    DOMAIN_PATTERN = re.compile(r'^REQ-([A-Z]+)-\d+$', re.IGNORECASE)

    def __init__(self, requirements: 'RequirementSet'):
        """Initialize with requirements to plan.

        Args:
            requirements: RequirementSet from RequirementExtractor.
        """
        self.requirements = requirements
        self._work_id_counter = 0

    def suggest_groupings(self) -> List[RequirementGroup]:
        """Suggest how requirements could be grouped into work items.

        Groups by domain (REQ-TRACE-*, REQ-CONTEXT-*, etc.).
        Requirements without a domain segment go to GENERAL.
        Within each group, MUST requirements sort before SHOULD.

        Returns:
            List of RequirementGroup for operator review.
        """
        groups: Dict[str, List[Requirement]] = defaultdict(list)

        for req in self.requirements.requirements:
            domain = self._extract_domain(req.id)
            groups[domain].append(req)

        # Sort requirements within each group by strength (MUST first)
        result = []
        for domain, reqs in sorted(groups.items()):
            sorted_reqs = sorted(
                reqs,
                key=lambda r: self._strength_priority(r.strength)
            )
            result.append(RequirementGroup(
                domain=domain,
                requirements=sorted_reqs,
            ))

        return result

    def estimate_dependencies(self) -> DependencyGraph:
        """Estimate dependencies from derives_from links.

        Builds a graph where an edge (A, B) means A depends on B.

        Returns:
            DependencyGraph with edges and topological sort capability.
        """
        graph = DependencyGraph()

        for req in self.requirements.requirements:
            graph.nodes.add(req.id)
            for dep_id in req.derives_from:
                graph.add_edge(req.id, dep_id)

        return graph

    def plan(
        self,
        approved_groupings: Optional[List[RequirementGroup]] = None
    ) -> WorkPlan:
        """Generate work plan from requirements.

        Args:
            approved_groupings: Optional operator-approved groupings.
                If not provided, uses suggest_groupings().

        Returns:
            WorkPlan with work items and execution order.
        """
        # Use approved groupings or generate suggestions
        groupings = approved_groupings or self.suggest_groupings()

        # Build dependency graph
        dep_graph = self.estimate_dependencies()

        # Create work items from groups
        work_items = []
        req_to_work: Dict[str, str] = {}  # Map requirement ID to work item ID

        for group in groupings:
            work_id = self._next_work_id()

            # Collect requirement IDs and acceptance criteria
            req_refs = [r.id for r in group.requirements]
            criteria = []
            for req in group.requirements:
                criteria.extend(req.acceptance_criteria)

            # Determine priority from requirement strengths
            has_must = any(
                r.strength == RequirementStrength.MUST
                for r in group.requirements
            ) if RequirementStrength else False
            priority = "high" if has_must else "medium"

            # Estimate effort from requirement count
            effort = "small" if len(group.requirements) <= 2 else (
                "medium" if len(group.requirements) <= 5 else "large"
            )

            work_item = PlannedWorkItem(
                id=work_id,
                title=group.suggested_title,
                type="feature",
                requirement_refs=req_refs,
                acceptance_criteria=criteria,
                dependencies=[],  # Filled below
                estimated_effort=effort,
                priority=priority,
            )
            work_items.append(work_item)

            # Track mapping for dependency resolution
            for req_id in req_refs:
                req_to_work[req_id] = work_id

        # Convert requirement dependencies to work item dependencies
        work_dep_graph = DependencyGraph()
        for work_item in work_items:
            work_dep_graph.nodes.add(work_item.id)

            for req_id in work_item.requirement_refs:
                # Find requirements this req depends on
                req = next(
                    (r for r in self.requirements.requirements if r.id == req_id),
                    None
                )
                if req:
                    for dep_req_id in req.derives_from:
                        dep_work_id = req_to_work.get(dep_req_id)
                        if dep_work_id and dep_work_id != work_item.id:
                            work_item.dependencies.append(dep_work_id)
                            work_dep_graph.add_edge(work_item.id, dep_work_id)

        # Compute execution order via topological sort
        execution_order = work_dep_graph.topological_sort()

        return WorkPlan(
            source_requirements=self.requirements,
            created_at=datetime.now(),
            planner_version=self.VERSION,
            work_items=work_items,
            execution_order=execution_order,
            dependency_graph=work_dep_graph,
        )

    def _extract_domain(self, req_id: str) -> str:
        """Extract domain from requirement ID.

        Args:
            req_id: Requirement ID like "REQ-TRACE-001".

        Returns:
            Domain string ("TRACE") or "GENERAL" if no domain found.
        """
        match = self.DOMAIN_PATTERN.match(req_id)
        if match:
            return match.group(1).upper()
        return "GENERAL"

    def _strength_priority(self, strength) -> int:
        """Return sort priority for requirement strength (lower = higher priority)."""
        if strength is None:
            return 99

        # Map strength to priority (MUST=0, SHOULD=1, MAY=2, etc.)
        priority_map = {
            "MUST": 0,
            "MUST_NOT": 0,
            "SHOULD": 1,
            "SHOULD_NOT": 1,
            "MAY": 2,
        }

        # Handle enum or string
        strength_str = strength.value if hasattr(strength, 'value') else str(strength)
        return priority_map.get(strength_str, 99)

    def _next_work_id(self) -> str:
        """Generate next planned work item ID."""
        self._work_id_counter += 1
        return f"WORK-P{self._work_id_counter:03d}"
