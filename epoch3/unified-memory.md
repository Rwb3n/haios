# Unified Memory Schemas

## Core Integration Types

These schemas define the types required by the integration layer to compose the three memory paradigms into a unified system.

---

## Core Interface

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Protocol
from enum import Enum

# Import from paradigm-specific schemas
# from .hindsight_schemas import MemoryUnit, MemoryBank, Entity, OpinionEvolution
# from .reasoningbank_schemas import MemoryItem, Trajectory, TrajectoryOutcome
# from .foresight_schemas import (
#     TransitionPattern, CompetenceEntry, GoalEntry, 
#     SimulationResult, IntrospectionResult, AnticipationResult
# )


# =============================================================================
# DECLARATIVE MEMORY INTERFACE
# =============================================================================

class DeclarativeMemory(Protocol):
    """
    Interface for HINDSIGHT-style declarative memory.
    Stores facts, beliefs, entities, and experiences.
    """
    
    def recall(
        self, 
        query: str, 
        banks: Optional[List[str]] = None,
        limit: int = 10
    ) -> List['MemoryUnit']:
        """Retrieve relevant facts from specified memory banks."""
        ...
    
    def retain(
        self, 
        bank: str,
        text: str,
        confidence: float = 1.0,
        entities: Optional[List[str]] = None,
        occurrence_start: Optional[datetime] = None,
        mention_time: Optional[datetime] = None
    ) -> 'MemoryUnit':
        """Store a new fact in the specified memory bank."""
        ...
    
    def has_knowledge(self, topic: str) -> bool:
        """Check if memory contains knowledge about a topic."""
        ...
    
    def find_opinion(self, topic: str) -> Optional['MemoryUnit']:
        """Find an opinion about a specific topic."""
        ...
    
    def reinforce_opinion(self, opinion_id: str) -> None:
        """Strengthen confidence in an opinion."""
        ...
    
    def weaken_opinion(self, opinion_id: str) -> None:
        """Reduce confidence in an opinion."""
        ...
    
    def get_opinions_below_confidence(self, threshold: float) -> List['MemoryUnit']:
        """Retrieve opinions with confidence below threshold."""
        ...
    
    def resolve_entity(self, mention: str, context: Dict) -> Optional['Entity']:
        """Resolve a mention to a canonical entity."""
        ...


# =============================================================================
# PROCEDURAL MEMORY INTERFACE
# =============================================================================

class ProceduralMemory(Protocol):
    """
    Interface for ReasoningBank-style procedural memory.
    Stores strategies, skills, and failure lessons.
    """
    
    def recall(
        self, 
        query: str, 
        context: Optional[Dict] = None,
        domain: Optional[str] = None,
        limit: int = 5
    ) -> List['MemoryItem']:
        """Retrieve relevant strategies for a query."""
        ...
    
    def extract(
        self, 
        trajectory: 'Trajectory',
        success: bool,
        failure_reason: Optional[str] = None
    ) -> List['MemoryItem']:
        """Extract memory items from a trajectory."""
        ...
    
    def has_strategy_for(self, skill_gap: str) -> bool:
        """Check if a strategy exists for a skill gap."""
        ...
    
    def get_domains(self) -> List[str]:
        """Get all domains with stored strategies."""
        ...
    
    def get_strategies_by_domain(self, domain: str) -> List['MemoryItem']:
        """Get all strategies for a domain."""
        ...
    
    def get(self, strategy_id: str) -> Optional['MemoryItem']:
        """Get a specific strategy by ID."""
        ...
    
    def save(self, item: 'MemoryItem') -> None:
        """Save or update a memory item."""
        ...


# =============================================================================
# PREDICTIVE MEMORY INTERFACE
# =============================================================================

class PredictiveMemory(Protocol):
    """
    Interface for FORESIGHT-style predictive memory.
    Contains world model, self model, goal network, and metamemory.
    """
    
    # World Model
    def simulate(
        self, 
        action: str, 
        context: Optional[Dict] = None
    ) -> 'SimulationResult':
        """Simulate outcome of an action."""
        ...
    
    # Self Model
    def introspect(self, task: 'Task') -> 'IntrospectionResult':
        """Assess competence for a task."""
        ...
    
    def get_agent_competencies(self, task_type: str) -> List['CompetenceEntry']:
        """Get competence entries for a task type."""
        ...
    
    def update_competence(
        self, 
        agent: Any, 
        task_type: str, 
        success: bool
    ) -> None:
        """Update competence based on outcome."""
        ...
    
    # Goal Network
    def get_active_goals(self) -> List['GoalEntry']:
        """Get all active goals."""
        ...
    
    def get_relevant_goals(self, query: str) -> List['GoalEntry']:
        """Get goals relevant to a query."""
        ...
    
    def get_urgent_goals(self, user_id: str) -> List['GoalEntry']:
        """Get goals nearing deadline."""
        ...
    
    def get_blocked_goals(self, user_id: str) -> List['GoalEntry']:
        """Get goals that are blocked."""
        ...
    
    def get_goal(self, goal_id: str) -> Optional['GoalEntry']:
        """Get a specific goal."""
        ...
    
    def save_goal(self, goal: 'GoalEntry') -> None:
        """Save or update a goal."""
        ...
    
    def update_goal(self, goal: 'GoalEntry') -> None:
        """Update goal state."""
        ...
    
    def update_goal_progress(self, goal_id: str, progress_delta: float) -> None:
        """Update goal progress."""
        ...
    
    def decompose_goal(self, goal: 'GoalEntry') -> List['GoalEntry']:
        """Decompose a goal into subgoals."""
        ...
    
    def anticipate(self, goal: 'GoalEntry') -> 'AnticipationResult':
        """Identify gaps for achieving a goal."""
        ...
    
    # Metamemory
    def opinion_relevance_to_goals(self, opinion: 'MemoryUnit') -> float:
        """Assess how relevant an opinion is to active goals."""
        ...
    
    def predict_user_needs(self, user_id: str) -> List['PredictedNeed']:
        """Predict user's upcoming needs."""
        ...
    
    # World Model Updates
    @property
    def world_model(self) -> 'WorldModel':
        """Access the world model."""
        ...
    
    @property
    def self_model(self) -> 'SelfModel':
        """Access the self model."""
        ...


# =============================================================================
# UNIFIED MEMORY
# =============================================================================

@dataclass
class UnifiedMemory:
    """
    The unified memory system combining all three paradigms.
    This is the primary interface used by the integration layer.
    """
    
    declarative: DeclarativeMemory
    procedural: ProceduralMemory
    predictive: PredictiveMemory
    
    # Configuration
    config: Optional['UnifiedMemoryConfig'] = None
    
    # Statistics
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    query_count: int = 0


@dataclass
class UnifiedMemoryConfig:
    """Configuration for the unified memory system."""
    
    # Retrieval settings
    default_declarative_limit: int = 10
    default_procedural_limit: int = 5
    
    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    
    # Cross-paradigm settings
    enable_cross_paradigm_learning: bool = True
    prediction_confidence_threshold: float = 0.5


# =============================================================================
# TASK AND QUERY TYPES
# =============================================================================

@dataclass
class Task:
    """
    A task to be executed by the agent.
    """
    
    id: str
    description: str
    type: str                           # "code", "web", "document", "research"
    domain: str                         # More specific domain
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Optional associations
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    priority: float = 0.5
    deadline: Optional[datetime] = None
    
    def to_query(self) -> 'Query':
        """Convert task to a query."""
        return Query(
            text=self.description,
            context=self.context,
            task_type=self.type,
            domain=self.domain
        )


@dataclass
class Query:
    """
    A query to the memory system.
    """
    
    text: str
    context: Dict[str, Any] = field(default_factory=dict)
    task_type: Optional[str] = None
    domain: Optional[str] = None
    
    # Query metadata
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    
    def as_action(self) -> str:
        """Convert query to an action string for simulation."""
        return f"respond_to: {self.text}"
    
    def as_task(self) -> Task:
        """Convert query to a task."""
        import uuid
        return Task(
            id=str(uuid.uuid4()),
            description=self.text,
            type=self.task_type or "general",
            domain=self.domain or "general",
            context=self.context
        )
    
    @property
    def summary(self) -> str:
        """Short summary of the query."""
        return self.text[:50] + "..." if len(self.text) > 50 else self.text


# =============================================================================
# RESPONSE AND OUTCOME TYPES
# =============================================================================

@dataclass
class Response:
    """
    A response generated by the agent.
    """
    
    content: str
    
    # Source information
    paradigms_used: List[str] = field(default_factory=list)
    facts_used: List[str] = field(default_factory=list)      # MemoryUnit IDs
    strategies_used: List[str] = field(default_factory=list)  # MemoryItem IDs
    
    # Confidence
    confidence: float = 1.0
    caveats: List[str] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    generation_time_ms: Optional[float] = None


class OutcomeStatus(Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    UNKNOWN = "unknown"


@dataclass
class Outcome:
    """
    The outcome of executing a task.
    """
    
    task_id: str
    status: OutcomeStatus
    
    # Result details
    result: Optional[str] = None
    error: Optional[str] = None
    
    # Trajectory (for procedural learning)
    trajectory: Optional['Trajectory'] = None
    
    # Predictions made (for predictive learning)
    predictions_made: List['SimulationResult'] = field(default_factory=list)
    predicted_success_probability: float = 0.5
    
    # What was used
    strategy_used: Optional[str] = None      # MemoryItem ID
    capability_used: Optional[str] = None    # Capability domain
    
    # What was learned
    reveals_preferences: bool = False
    revealed_preferences: List['RevealedPreference'] = field(default_factory=list)
    reveals_pattern: bool = False
    pattern_description: Optional[str] = None
    pattern_confidence: float = 0.0
    is_novel_failure: bool = False
    failure_reason: Optional[str] = None
    
    # Entities mentioned
    mentioned_entities: List[str] = field(default_factory=list)
    
    # Goal progress
    goal_id: Optional[str] = None
    progress_delta: float = 0.0
    goal_progress: float = 0.0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: datetime = field(default_factory=datetime.now)
    
    @property
    def succeeded(self) -> bool:
        return self.status in (OutcomeStatus.SUCCESS, OutcomeStatus.PARTIAL_SUCCESS)
    
    @property
    def has_trajectory(self) -> bool:
        return self.trajectory is not None
    
    @property
    def state(self) -> Dict:
        """Return outcome state for prediction comparison."""
        return {
            "status": self.status.value,
            "result": self.result,
            "error": self.error
        }
    
    @property
    def summary(self) -> str:
        if self.succeeded:
            return f"Success: {self.result or 'completed'}"
        else:
            return f"Failure: {self.failure_reason or self.error or 'unknown'}"


@dataclass
class RevealedPreference:
    """A preference revealed during an interaction."""
    
    topic: str
    statement: str
    confirms: bool              # True if confirms existing belief
    confidence: float = 0.6


# =============================================================================
# GOAL PROGRESS TRACKING
# =============================================================================

@dataclass
class SubgoalOutcome:
    """Outcome of working on a subgoal."""
    
    subgoal_id: str
    status: OutcomeStatus
    progress_delta: float
    notes: Optional[str] = None


@dataclass
class GoalProgress:
    """
    Progress report for a goal.
    """
    
    goal_id: str
    
    # Subgoal outcomes
    subgoal_outcomes: List[SubgoalOutcome] = field(default_factory=list)
    
    # Aggregate progress
    total_progress_delta: float = 0.0
    
    # Blockers encountered
    new_blockers: List[str] = field(default_factory=list)
    resolved_blockers: List[str] = field(default_factory=list)
    
    # Timing
    session_start: datetime = field(default_factory=datetime.now)
    session_end: Optional[datetime] = None
    
    def record_subgoal_outcome(self, subgoal: 'GoalEntry', outcome: Outcome):
        """Record outcome of working on a subgoal."""
        self.subgoal_outcomes.append(SubgoalOutcome(
            subgoal_id=subgoal.id,
            status=outcome.status,
            progress_delta=outcome.progress_delta
        ))
        self.total_progress_delta += outcome.progress_delta
    
    def calculate_overall_progress(self) -> float:
        """Calculate overall progress from subgoal outcomes."""
        if not self.subgoal_outcomes:
            return 0.0
        
        successful = sum(
            1 for o in self.subgoal_outcomes 
            if o.status == OutcomeStatus.SUCCESS
        )
        return successful / len(self.subgoal_outcomes)


# =============================================================================
# LEARNING PRIORITIES
# =============================================================================

class LearningPriorityType(Enum):
    KNOWLEDGE_GAP = "knowledge_gap"
    SKILL_GAP = "skill_gap"
    RECURRING_FAILURE = "recurring_failure"
    UNCERTAIN_BELIEF = "uncertain_belief"
    COMPETENCE_GAP = "competence_gap"


@dataclass
class LearningPriority:
    """
    A prioritized learning opportunity.
    """
    
    type: LearningPriorityType
    description: str
    impact: float                   # 0-1 importance score
    
    # Source information
    source_goal: Optional[str] = None
    source_experiences: List[str] = field(default_factory=list)
    source_belief: Optional[str] = None
    
    # Actionability
    suggested_action: Optional[str] = None
    estimated_effort: Optional[float] = None
    
    def __lt__(self, other: 'LearningPriority') -> bool:
        """Enable sorting by impact."""
        return self.impact < other.impact


# =============================================================================
# PREDICTION SUPPORT TYPES
# =============================================================================

@dataclass
class PredictedNeed:
    """A predicted user need."""
    
    description: str
    confidence: float
    trigger: Optional[str] = None   # What would trigger this need
    suggested_preparation: Optional[str] = None


# =============================================================================
# HELPER PROTOCOLS FOR COMPONENTS
# =============================================================================

class WorldModel(Protocol):
    """World model component interface."""
    
    def get_transitions(
        self, 
        action: str, 
        preconditions: List[str]
    ) -> List['TransitionPattern']:
        ...
    
    def update(self, pattern_id: str, outcome_matched: bool) -> None:
        ...


class SelfModel(Protocol):
    """
    Self model component interface.
    
    Uses Bayesian calibration (BayesianPrior) for competence tracking.
    See foresight-schemas.md for BayesianPrior and CompetenceEntry definitions.
    """
    
    def get_competence(self, domain: str) -> 'CompetenceEntry':
        """Get competence entry for a domain (creates with prior if not exists)."""
        ...
    
    def update_from_outcome(
        self, 
        capability: str, 
        predicted_success: float, 
        actual_success: bool,
        difficulty: str = "medium"
    ) -> None:
        """
        Update competence using Bayesian posterior update.
        Single failures shift estimate slightly rather than crashing to zero.
        """
        ...
    
    def add_failure_mode(self, capability: str, mode: str) -> None:
        """Record a known failure mode for a capability."""
        ...
    
    def reinforce(self, capability: str, success: bool) -> None:
        """Quick update without prediction tracking."""
        ...
    
    def set_failure_modes(
        self, 
        capability: str, 
        modes: List[str], 
        frequencies: Dict[str, int]
    ) -> None:
        """Bulk set failure modes and frequencies."""
        ...
    
    def should_attempt(
        self, 
        capability: str, 
        required_accuracy: float = 0.5
    ) -> tuple:
        """
        Decide whether to attempt based on P(competence > threshold).
        Returns: (should_attempt, confidence, reasoning)
        """
        ...
    
    def get_prompt_injection(self, capability: str) -> str:
        """
        Generate 'humble' prompt injection with competence awareness.
        Explicitly injects competence scores per reviewer recommendation.
        """
        ...
    
    def set_prior_from_benchmark(
        self, 
        capability: str, 
        benchmark_score: float,
        confidence: float = 0.7
    ) -> None:
        """
        Set Bayesian prior from external benchmark (e.g., MMLU score).
        Solves cold-start problem with informed priors.
        """
        ...
    
    @property
    def weak_domains(self) -> List[str]:
        """Domains where P(competence > 0.5) < 0.4."""
        ...
    
    @property
    def uncertain_domains(self) -> List[str]:
        """Domains with high variance (need more data)."""
        ...


# =============================================================================
# STRATEGY ALIAS
# =============================================================================

# Strategy is an alias for MemoryItem in the integration layer
# This makes the code more readable when discussing procedural patterns
Strategy = 'MemoryItem'  # Type alias - actual type from reasoningbank_schemas


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def extract_preconditions(facts: List['MemoryUnit']) -> List[str]:
    """Extract preconditions from a list of facts."""
    return [f.text for f in facts if f.confidence > 0.5]


def get_supporting_fact_confidence(
    transition: 'TransitionPattern', 
    facts: List['MemoryUnit']
) -> float:
    """Calculate confidence based on supporting facts."""
    if not facts:
        return 0.5
    
    relevant_facts = [
        f for f in facts 
        if any(pre in f.text.lower() for pre in transition.preconditions)
    ]
    
    if not relevant_facts:
        return 0.5
    
    return sum(f.confidence for f in relevant_facts) / len(relevant_facts)


def mode_applies_to_task(mode: str, task: Task) -> bool:
    """Check if a failure mode applies to a task."""
    mode_lower = mode.lower()
    return (
        task.domain.lower() in mode_lower or
        task.type.lower() in mode_lower or
        any(keyword in mode_lower for keyword in task.description.lower().split())
    )


def contradicts(fact: 'MemoryUnit', prediction: 'SimulationResult') -> bool:
    """Check if a fact contradicts a prediction."""
    # Simplified check - in practice would need semantic comparison
    fact_lower = fact.text.lower()
    pred_state = str(prediction.predicted_state).lower()
    
    negation_pairs = [
        ("not ", ""), ("isn't", "is"), ("won't", "will"),
        ("can't", "can"), ("false", "true"), ("fail", "succeed")
    ]
    
    for neg, pos in negation_pairs:
        if neg in fact_lower and pos in pred_state:
            return True
        if pos in fact_lower and neg in pred_state:
            return True
    
    return False


def rank_by_competence(
    strategies: List['MemoryItem'], 
    competence: 'IntrospectionResult'
) -> List['MemoryItem']:
    """Rank strategies by competence match."""
    def score(strategy: 'MemoryItem') -> float:
        # Higher score for strategies in domains we're competent at
        domain_match = 1.0 if strategy.domain not in competence.known_failure_modes else 0.5
        return (strategy.success_rate() or 0.5) * domain_match * competence.estimated_accuracy
    
    return sorted(strategies, key=score, reverse=True)
