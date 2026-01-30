# generated: 2026-01-30
# System Auto: last updated on: 2026-01-30T17:42:25
"""
PipelineOrchestrator Module (WORK-033, CH-006)

Pipeline state machine that wires INGEST and PLAN stages together.
Drives the doc-to-product pipeline per S26 architecture.

Interface:
    orchestrator = PipelineOrchestrator(corpus_config, base_path)
    result = orchestrator.run()  # Full pipeline
    # Or step-by-step:
    req_set = orchestrator.ingest()
    work_plan = orchestrator.plan()

State Machine (per S26):
    IDLE -> INGESTING -> PLANNING -> COMPLETE
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

# Import sibling modules (follow existing pattern from planner_agent.py)
try:
    from .corpus_loader import CorpusLoader
    from .requirement_extractor import RequirementExtractor, RequirementSet
    from .planner_agent import PlannerAgent, WorkPlan
except ImportError:
    from corpus_loader import CorpusLoader
    from requirement_extractor import RequirementExtractor, RequirementSet
    from planner_agent import PlannerAgent, WorkPlan

logger = logging.getLogger(__name__)


class PipelineState(Enum):
    """Pipeline execution states per S26."""
    IDLE = auto()
    INGESTING = auto()
    PLANNING = auto()
    BUILDING = auto()   # Future: CH-004
    VALIDATING = auto() # Future: CH-005
    COMPLETE = auto()
    ERROR = auto()


class InvalidStateError(Exception):
    """Raised when operation called in invalid state."""
    pass


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    requirement_set: RequirementSet
    work_plan: WorkPlan
    state_history: List[PipelineState]
    completed_at: datetime


class PipelineOrchestrator:
    """Pipeline state machine per S26.

    Responsibilities:
    1. Initialize pipeline with corpus config
    2. Call stages in sequence (INGEST -> PLAN)
    3. Track state transitions
    4. Store intermediate results
    """

    VERSION = "1.0.0"

    # Valid state transitions
    TRANSITIONS = {
        PipelineState.IDLE: [PipelineState.INGESTING],
        PipelineState.INGESTING: [PipelineState.PLANNING, PipelineState.ERROR],
        PipelineState.PLANNING: [PipelineState.COMPLETE, PipelineState.ERROR],
        PipelineState.COMPLETE: [],
        PipelineState.ERROR: [PipelineState.IDLE],  # Allow reset
    }

    def __init__(
        self,
        corpus_config: Union[Path, Dict],
        base_path: Optional[Path] = None
    ):
        """Initialize orchestrator with corpus configuration.

        Args:
            corpus_config: Path to YAML file or dict with corpus definition.
            base_path: Base directory for resolving paths.
        """
        self.corpus_config = corpus_config
        self.base_path = Path(base_path) if base_path else Path.cwd()

        # State machine
        self._state = PipelineState.IDLE
        self._state_history: List[PipelineState] = [PipelineState.IDLE]

        # Stage results (populated during execution)
        self._requirement_set: Optional[RequirementSet] = None
        self._work_plan: Optional[WorkPlan] = None

    @property
    def state(self) -> PipelineState:
        """Current pipeline state."""
        return self._state

    @property
    def state_history(self) -> List[PipelineState]:
        """History of state transitions."""
        return self._state_history.copy()

    @property
    def requirement_set(self) -> Optional[RequirementSet]:
        """RequirementSet from INGEST stage (None if not run)."""
        return self._requirement_set

    @property
    def work_plan(self) -> Optional[WorkPlan]:
        """WorkPlan from PLAN stage (None if not run)."""
        return self._work_plan

    def _transition(self, new_state: PipelineState) -> None:
        """Transition to new state if valid."""
        if new_state not in self.TRANSITIONS.get(self._state, []):
            raise InvalidStateError(
                f"Cannot transition from {self._state.name} to {new_state.name}"
            )
        self._state = new_state
        self._state_history.append(new_state)
        logger.info(f"Pipeline state: {new_state.name}")

    def ingest(self) -> RequirementSet:
        """Execute INGEST stage: Corpus -> Requirements.

        Returns:
            RequirementSet with extracted requirements.

        Raises:
            InvalidStateError: If not in IDLE state.
        """
        self._transition(PipelineState.INGESTING)

        try:
            # Load corpus
            loader = CorpusLoader(self.corpus_config, base_path=self.base_path)

            # Extract requirements
            extractor = RequirementExtractor(loader)
            self._requirement_set = extractor.extract()

            logger.info(f"INGEST complete: {len(self._requirement_set.requirements)} requirements")
            self._transition(PipelineState.PLANNING)
            return self._requirement_set

        except Exception as e:
            logger.error(f"INGEST failed: {e}")
            # A9 defensive fix: Preserve original error if transition fails
            try:
                self._transition(PipelineState.ERROR)
            except InvalidStateError:
                logger.warning(f"Could not transition to ERROR state")
            raise

    def plan(self) -> WorkPlan:
        """Execute PLAN stage: Requirements -> WorkPlan.

        Returns:
            WorkPlan with suggested work items.

        Raises:
            InvalidStateError: If not in PLANNING state.
        """
        if self._state != PipelineState.PLANNING:
            raise InvalidStateError(
                f"plan() requires PLANNING state, current: {self._state.name}"
            )

        try:
            planner = PlannerAgent(self._requirement_set)
            self._work_plan = planner.plan()

            logger.info(f"PLAN complete: {len(self._work_plan.work_items)} work items")
            self._transition(PipelineState.COMPLETE)
            return self._work_plan

        except Exception as e:
            logger.error(f"PLAN failed: {e}")
            # A9 defensive fix: Preserve original error if transition fails
            try:
                self._transition(PipelineState.ERROR)
            except InvalidStateError:
                logger.warning(f"Could not transition to ERROR state")
            raise

    def run(self) -> PipelineResult:
        """Execute full pipeline: INGEST -> PLAN.

        Returns:
            PipelineResult with all outputs.
        """
        self.ingest()
        self.plan()

        return PipelineResult(
            requirement_set=self._requirement_set,
            work_plan=self._work_plan,
            state_history=self._state_history.copy(),
            completed_at=datetime.now(),
        )
