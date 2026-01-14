# FORESIGHT Schemas

## Proposed Data Structures for Predictive Self-Modeling

Status: Draft Proposal

---

## World Model

### Transition Pattern

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum


class TransitionSource(Enum):
    OBSERVED = "observed"       # Directly witnessed
    INFERRED = "inferred"       # Deduced from patterns
    TOLD = "told"               # Explicitly communicated
    HYPOTHESIZED = "hypothesized"  # Speculative


@dataclass
class TransitionPattern:
    """
    A learned pattern about how the world changes.
    
    Represents: "In context C, action A leads to state S with probability P"
    """
    
    id: str
    
    # Domain and scope
    domain: str                     # "web_navigation", "code_editing", "conversation"
    subdomain: Optional[str] = None # More specific category
    
    # The pattern itself
    preconditions: List[str]        # What must be true for this to apply
    action: str                     # What action triggers this transition
    postconditions: List[str]       # What becomes true after
    
    # Alternative outcomes (for stochastic environments)
    alternative_outcomes: List[Dict] = field(default_factory=list)
    # Each dict: {"postconditions": [...], "probability": float, "conditions": [...]}
    
    # Reliability metrics
    reliability: float = 0.5        # P(postconditions | preconditions, action)
    sample_size: int = 0            # Number of observations
    last_validated: Optional[datetime] = None
    
    # Provenance
    source: TransitionSource = TransitionSource.HYPOTHESIZED
    source_evidence: List[str] = field(default_factory=list)  # References
    
    # Known exceptions
    contradictions: List[str] = field(default_factory=list)
    exception_conditions: List[str] = field(default_factory=list)
    
    # Embedding for retrieval
    embedding: Optional[List[float]] = None
    
    def confidence_interval(self, alpha: float = 0.05) -> tuple:
        """Wilson score interval for reliability estimate."""
        if self.sample_size == 0:
            return (0.0, 1.0)
        
        from math import sqrt
        
        n = self.sample_size
        p = self.reliability
        z = 1.96  # 95% confidence
        
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2*n)) / denominator
        margin = z * sqrt((p*(1-p) + z**2/(4*n)) / n) / denominator
        
        return (max(0, center - margin), min(1, center + margin))
    
    def update(self, outcome_matched: bool):
        """Update reliability based on new observation."""
        self.sample_size += 1
        # Exponential moving average with decay
        alpha = min(0.3, 2.0 / (self.sample_size + 1))
        observed = 1.0 if outcome_matched else 0.0
        self.reliability = (1 - alpha) * self.reliability + alpha * observed
        self.last_validated = datetime.now()


@dataclass
class EntityBehaviorModel:
    """
    Model of how a specific entity (user, system) behaves.
    """
    
    entity_id: str
    entity_type: str                # "user", "system", "service"
    
    # Behavioral patterns
    response_patterns: List[Dict] = field(default_factory=list)
    # Each: {"trigger": str, "likely_response": str, "probability": float}
    
    # Temporal patterns
    active_hours: Optional[Dict] = None  # Hour -> activity probability
    response_latency: Optional[Dict] = None  # Context -> expected delay
    
    # Preferences (linked to declarative memory)
    known_preferences: List[str] = field(default_factory=list)  # Preference IDs
    
    # Reliability
    model_accuracy: float = 0.5
    last_updated: datetime = None
```

---

## Self Model

### Competence Entry

```python
class ConfidenceLevel(Enum):
    VERY_LOW = 1    # <20% accuracy
    LOW = 2         # 20-40% accuracy
    MEDIUM = 3      # 40-60% accuracy
    HIGH = 4        # 60-80% accuracy
    VERY_HIGH = 5   # >80% accuracy


@dataclass
class BayesianPrior:
    """
    Beta distribution prior for competence estimation.
    Solves the "cold start" problem by anchoring estimates to baseline LLM capabilities.
    
    The Beta distribution is parameterized by α (successes) and β (failures).
    Mean = α / (α + β)
    Variance decreases as α + β increases (more confidence with more data).
    """
    
    # Prior parameters (from baseline LLM benchmarks or domain defaults)
    alpha_prior: float = 3.0        # Pseudo-successes (prior belief)
    beta_prior: float = 1.0         # Pseudo-failures (prior belief)
    
    # Observed data
    successes: int = 0              # Actual observed successes
    failures: int = 0               # Actual observed failures
    
    # Source of prior
    prior_source: str = "default"   # "benchmark", "expert", "default"
    prior_confidence: float = 0.5   # How much we trust the prior
    
    @property
    def alpha(self) -> float:
        """Total alpha (prior + observed)."""
        return self.alpha_prior + self.successes
    
    @property
    def beta(self) -> float:
        """Total beta (prior + observed)."""
        return self.beta_prior + self.failures
    
    @property
    def mean(self) -> float:
        """Expected value: E[x] = α / (α + β)."""
        return self.alpha / (self.alpha + self.beta)
    
    @property
    def variance(self) -> float:
        """Variance of the Beta distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    @property
    def std(self) -> float:
        """Standard deviation."""
        from math import sqrt
        return sqrt(self.variance)
    
    @property
    def sample_size(self) -> int:
        """Total observations."""
        return self.successes + self.failures
    
    @property
    def effective_sample_size(self) -> float:
        """Effective sample size including prior weight."""
        return self.alpha + self.beta
    
    def update(self, success: bool) -> None:
        """Update posterior with new observation."""
        if success:
            self.successes += 1
        else:
            self.failures += 1
    
    def confidence_interval(self, alpha_level: float = 0.05) -> tuple:
        """
        Compute credible interval using Beta quantiles.
        Returns (lower, upper) bounds.
        """
        from scipy.stats import beta as beta_dist
        lower = beta_dist.ppf(alpha_level / 2, self.alpha, self.beta)
        upper = beta_dist.ppf(1 - alpha_level / 2, self.alpha, self.beta)
        return (lower, upper)
    
    def probability_above(self, threshold: float) -> float:
        """P(competence > threshold). Useful for go/no-go decisions."""
        from scipy.stats import beta as beta_dist
        return 1 - beta_dist.cdf(threshold, self.alpha, self.beta)
    
    @classmethod
    def from_benchmark(cls, benchmark_score: float, confidence: float = 0.7) -> 'BayesianPrior':
        """
        Create prior from a benchmark score (e.g., MMLU domain score).
        
        Higher confidence = stronger prior (more pseudo-observations).
        """
        # Scale pseudo-observations by confidence
        # At confidence=0.7, we use ~10 pseudo-observations
        pseudo_n = int(confidence * 15)
        alpha_prior = benchmark_score * pseudo_n
        beta_prior = (1 - benchmark_score) * pseudo_n
        
        return cls(
            alpha_prior=max(alpha_prior, 0.5),
            beta_prior=max(beta_prior, 0.5),
            prior_source="benchmark",
            prior_confidence=confidence
        )
    
    @classmethod
    def uninformative(cls) -> 'BayesianPrior':
        """Jeffreys prior: Beta(0.5, 0.5) - minimal prior assumption."""
        return cls(alpha_prior=0.5, beta_prior=0.5, prior_source="jeffreys")
    
    @classmethod
    def optimistic(cls) -> 'BayesianPrior':
        """Optimistic prior: assume competence until proven otherwise."""
        return cls(alpha_prior=3.0, beta_prior=1.0, prior_source="optimistic")
    
    @classmethod
    def pessimistic(cls) -> 'BayesianPrior':
        """Pessimistic prior: assume incompetence until proven otherwise."""
        return cls(alpha_prior=1.0, beta_prior=3.0, prior_source="pessimistic")


@dataclass
class CompetenceEntry:
    """
    Self-assessment of capability in a specific domain.
    
    Uses Bayesian calibration to solve the "cold start" problem:
    - Single failure doesn't crash confidence to zero
    - Prior beliefs (from benchmarks) anchor estimates
    - Uncertainty decreases with more observations
    """
    
    id: str
    
    # What capability this describes
    capability: str                 # "python_debugging", "legal_interpretation"
    domain: str                     # Where this applies
    subdomain: Optional[str] = None
    
    # BAYESIAN COMPETENCE MODEL (replaces raw estimated_accuracy)
    competence_model: BayesianPrior = field(default_factory=BayesianPrior.optimistic)
    
    # Granular breakdown by difficulty (each has its own Bayesian model)
    accuracy_by_difficulty: Dict[str, BayesianPrior] = field(default_factory=dict)
    # {"easy": BayesianPrior(...), "medium": BayesianPrior(...), "hard": BayesianPrior(...)}
    
    # Known failure modes
    failure_modes: List[str] = field(default_factory=list)
    failure_mode_frequencies: Dict[str, int] = field(default_factory=dict)
    
    # Resource requirements
    typical_steps: Optional[int] = None
    typical_tokens: Optional[int] = None
    typical_duration_seconds: Optional[float] = None
    
    # Calibration tracking
    last_calibrated: Optional[datetime] = None
    calibration_history: List[Dict] = field(default_factory=list)
    # Each: {"date": datetime, "predicted": float, "actual": float, "difficulty": str}
    
    # Qualitative notes
    notes: str = ""
    
    @property
    def estimated_accuracy(self) -> float:
        """Posterior mean estimate of accuracy."""
        return self.competence_model.mean
    
    @property
    def confidence_in_estimate(self) -> float:
        """
        Confidence in our estimate (inverse of uncertainty).
        Ranges from 0 (no data) to ~0.95 (many observations).
        """
        # Map standard deviation to confidence
        # Lower std = higher confidence
        max_std = 0.25  # Std of uniform distribution
        current_std = self.competence_model.std
        return max(0.0, min(0.95, 1 - (current_std / max_std)))
    
    @property
    def sample_size(self) -> int:
        """Number of actual observations (not including prior)."""
        return self.competence_model.sample_size
    
    def calibration_error(self) -> Optional[float]:
        """Calculate mean absolute calibration error."""
        if not self.calibration_history:
            return None
        errors = [abs(h["predicted"] - h["actual"]) for h in self.calibration_history]
        return sum(errors) / len(errors)
    
    def update_from_outcome(
        self, 
        predicted_success: float, 
        actual_success: bool,
        difficulty: str = "medium"
    ):
        """
        Update competence estimate from a new outcome using Bayesian update.
        
        Key improvement: A single failure no longer crashes confidence to zero.
        Instead, it shifts the posterior slightly based on prior strength.
        """
        # Update main competence model
        self.competence_model.update(actual_success)
        
        # Update difficulty-specific model if exists
        if difficulty in self.accuracy_by_difficulty:
            self.accuracy_by_difficulty[difficulty].update(actual_success)
        else:
            # Create new difficulty model with current posterior as prior
            self.accuracy_by_difficulty[difficulty] = BayesianPrior(
                alpha_prior=self.competence_model.alpha_prior,
                beta_prior=self.competence_model.beta_prior
            )
            self.accuracy_by_difficulty[difficulty].update(actual_success)
        
        # Track failure mode if applicable
        if not actual_success:
            self._track_failure_mode(difficulty)
        
        # Record calibration point
        self.calibration_history.append({
            "date": datetime.now(),
            "predicted": predicted_success,
            "actual": 1.0 if actual_success else 0.0,
            "difficulty": difficulty,
            "posterior_mean": self.estimated_accuracy,
            "posterior_std": self.competence_model.std
        })
        
        self.last_calibrated = datetime.now()
    
    def _track_failure_mode(self, context: str):
        """Track failure mode frequency."""
        mode = f"failure_in_{context}"
        self.failure_mode_frequencies[mode] = self.failure_mode_frequencies.get(mode, 0) + 1
    
    def should_attempt(self, required_accuracy: float = 0.5) -> tuple:
        """
        Decide whether to attempt a task based on competence.
        
        Returns: (should_attempt: bool, confidence: float, reasoning: str)
        """
        prob_above = self.competence_model.probability_above(required_accuracy)
        
        if prob_above > 0.7:
            return (True, prob_above, f"High confidence ({prob_above:.0%}) of meeting {required_accuracy:.0%} threshold")
        elif prob_above > 0.4:
            return (True, prob_above, f"Moderate confidence ({prob_above:.0%}), proceed with caution")
        else:
            return (False, prob_above, f"Low confidence ({prob_above:.0%}), recommend external help")
    
    def get_credible_interval(self, alpha: float = 0.05) -> tuple:
        """Get 95% (default) credible interval for competence."""
        return self.competence_model.confidence_interval(alpha)
    
    def inject_into_prompt(self) -> str:
        """
        Generate prompt injection for "humble" self-awareness.
        Per reviewer recommendation: explicitly inject competence into prompts.
        """
        lower, upper = self.get_credible_interval()
        
        if self.estimated_accuracy < 0.4:
            tone = "You have LIMITED competence"
            instruction = "Verify all assumptions and suggest external review."
        elif self.estimated_accuracy < 0.7:
            tone = "You have MODERATE competence"
            instruction = "Double-check critical steps and flag uncertainties."
        else:
            tone = "You have HIGH competence"
            instruction = "Proceed confidently but remain open to correction."
        
        failure_warning = ""
        if self.failure_modes:
            top_modes = sorted(
                self.failure_mode_frequencies.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            failure_warning = f"\nKnown failure modes: {', '.join(m for m, _ in top_modes)}"
        
        return f"""[COMPETENCE AWARENESS: {self.domain}/{self.capability}]
{tone} in this domain (estimated: {self.estimated_accuracy:.0%}, range: {lower:.0%}-{upper:.0%}).
Based on {self.sample_size} observations.
{instruction}{failure_warning}
"""


@dataclass
class ResourceModel:
    """
    Model of resource requirements for different task types.
    """
    
    task_type: str
    domain: str
    
    # Step estimates
    mean_steps: float
    std_steps: float
    min_steps: int
    max_steps: int
    
    # Token estimates
    mean_input_tokens: float
    mean_output_tokens: float
    
    # Time estimates
    mean_duration_seconds: float
    
    # Sample size
    n_observations: int = 0
    
    def estimate_steps(self, difficulty: str = "medium") -> tuple:
        """Return (expected, lower_bound, upper_bound) for steps."""
        multipliers = {"easy": 0.7, "medium": 1.0, "hard": 1.5}
        m = multipliers.get(difficulty, 1.0)
        expected = self.mean_steps * m
        lower = max(self.min_steps, expected - 2 * self.std_steps)
        upper = min(self.max_steps, expected + 2 * self.std_steps)
        return (expected, lower, upper)
```

---

## Goal Network

### Goal Entry

```python
class GoalStatus(Enum):
    ACTIVE = "active"           # Currently being pursued
    SUSPENDED = "suspended"     # Paused, waiting for something
    COMPLETED = "completed"     # Successfully achieved
    ABANDONED = "abandoned"     # Deliberately stopped
    FAILED = "failed"           # Could not be achieved


class GoalPriority(Enum):
    CRITICAL = 1.0      # Must be done
    HIGH = 0.8          # Very important
    MEDIUM = 0.5        # Normal importance
    LOW = 0.3           # Nice to have
    BACKGROUND = 0.1    # Do if nothing else


@dataclass
class GoalEntry:
    """
    A persistent goal the agent is trying to achieve.
    """
    
    id: str
    
    # Goal specification
    goal_state: str                     # Description of desired end state
    success_criteria: List[str]         # How to know when achieved
    
    # Priority and timing
    priority: GoalPriority = GoalPriority.MEDIUM
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # Status
    status: GoalStatus = GoalStatus.ACTIVE
    progress: float = 0.0               # Estimated completion (0-1)
    
    # Hierarchy
    parent_goal_id: Optional[str] = None
    subgoal_ids: List[str] = field(default_factory=list)
    
    # Dependencies and blockers
    blocking_on: List[str] = field(default_factory=list)  # What's preventing progress
    blocking_type: Dict[str, str] = field(default_factory=dict)
    # {"missing_info": "Need X data", "missing_skill": "Can't do Y"}
    
    # Prospective memory (triggers)
    trigger_conditions: List[str] = field(default_factory=list)
    # "When user mentions X", "When file Y is modified"
    
    # History
    last_worked: Optional[datetime] = None
    work_sessions: List[Dict] = field(default_factory=list)
    # Each: {"start": datetime, "end": datetime, "progress_delta": float}
    
    # Reasoning
    rationale: str = ""                 # Why this goal exists
    notes: str = ""                     # Additional context
    
    def is_blocked(self) -> bool:
        return len(self.blocking_on) > 0
    
    def days_until_deadline(self) -> Optional[float]:
        if self.deadline is None:
            return None
        delta = self.deadline - datetime.now()
        return delta.total_seconds() / 86400
    
    def urgency_score(self) -> float:
        """Calculate urgency based on priority and deadline."""
        base = self.priority.value
        
        if self.deadline:
            days = self.days_until_deadline()
            if days <= 0:
                return 1.0  # Overdue
            elif days <= 1:
                return base * 1.5
            elif days <= 7:
                return base * 1.2
        
        return base


@dataclass
class SubgoalDecomposition:
    """
    Result of decomposing a goal into subgoals.
    """
    
    parent_goal_id: str
    subgoals: List[GoalEntry]
    decomposition_rationale: str
    dependencies: Dict[str, List[str]]  # subgoal_id -> [depends_on_ids]
    estimated_total_effort: float       # Aggregate estimate
```

---

## Metamemory

### Metamemory Entry

```python
@dataclass
class FeelingOfKnowing:
    """
    Estimate of whether information exists in memory.
    """
    
    query_pattern: str              # Pattern this applies to
    
    # Estimates
    feeling_of_knowing: float       # P(info exists) - 0 to 1
    estimated_retrieval_quality: float  # If retrieved, how accurate?
    estimated_retrieval_latency: float  # Expected time to retrieve (ms)
    
    # Likely sources
    likely_sources: List[str]       # Which stores probably have info
    source_confidence: Dict[str, float]  # source -> confidence
    
    # Access patterns
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    # Calibration
    reliability_history: List[float] = field(default_factory=list)
    # History of whether FOK was accurate
    
    def calibration_accuracy(self) -> Optional[float]:
        """How often is this FOK estimate accurate?"""
        if not self.reliability_history:
            return None
        return sum(self.reliability_history) / len(self.reliability_history)


@dataclass
class SourceMonitoring:
    """
    Tracking where information came from.
    """
    
    memory_id: str                  # Which memory this applies to
    
    # Source information
    source_type: str                # "observed", "inferred", "told", "imagined"
    source_confidence: float        # How sure about the source
    source_details: str             # Specific source info
    
    # Reliability based on source
    source_reliability: float       # How reliable is this source type
    
    # Potential confusions
    potential_source_confusion: List[str] = field(default_factory=list)
    # Other possible sources this could be confused with


@dataclass
class BeliefRevisionTrigger:
    """
    Conditions under which beliefs should be reconsidered.
    """
    
    belief_id: str                  # Which belief this monitors
    
    # Trigger conditions
    time_based: Optional[float] = None  # Reconsider after N seconds
    contradiction_threshold: int = 3     # Reconsider after N contradictions
    confidence_floor: float = 0.3        # Reconsider if confidence drops below
    
    # Trigger state
    contradictions_seen: int = 0
    last_reconsidered: Optional[datetime] = None
    
    def should_trigger(self, current_confidence: float) -> bool:
        if current_confidence < self.confidence_floor:
            return True
        if self.contradictions_seen >= self.contradiction_threshold:
            return True
        if self.time_based and self.last_reconsidered:
            elapsed = (datetime.now() - self.last_reconsidered).total_seconds()
            if elapsed > self.time_based:
                return True
        return False
```

---

## Simulation Results

```python
@dataclass
class SimulationResult:
    """
    Result of running the world model forward.
    """
    
    # What was simulated
    action: str
    initial_context: Dict
    
    # Predicted outcome
    predicted_state: Dict
    confidence: float               # Overall confidence in prediction
    
    # Uncertainty breakdown
    uncertainty_sources: Dict[str, float]  # source -> contribution
    # {"world_model": 0.3, "incomplete_context": 0.2}
    
    # Alternative outcomes
    alternatives: List[Dict] = field(default_factory=list)
    # Each: {"state": Dict, "probability": float, "conditions": str}
    
    # Reasoning trace
    reasoning: str = ""             # How prediction was made
    
    # Utilities (if goal-directed)
    utility_estimate: Optional[float] = None
    goal_progress_estimate: Optional[float] = None


@dataclass
class IntrospectionResult:
    """
    Result of querying the self-model.
    """
    
    task_description: str
    
    # Competence assessment
    estimated_accuracy: float
    confidence_in_estimate: float
    
    # Risk assessment
    known_failure_modes: List[str]
    failure_mode_probabilities: Dict[str, float]
    
    # Resource estimates
    expected_steps: float
    expected_duration_seconds: float
    
    # Recommendation
    recommendation: str             # "attempt", "ask_for_help", "decline"
    recommendation_rationale: str


@dataclass
class AnticipationResult:
    """
    Result of backward-chaining from a goal.
    """
    
    goal_id: str
    
    # Identified gaps
    knowledge_gaps: List[str]
    skill_gaps: List[str]
    resource_gaps: List[str]
    
    # Gap sources
    gap_analysis: Dict[str, str]    # gap -> why it's needed
    
    # Acquisition plan
    acquisition_plan: List[Dict]
    # Each: {"gap": str, "strategy": str, "estimated_effort": float}
    
    # Feasibility
    overall_feasibility: float      # 0-1 estimate of achievability
    blocking_gaps: List[str]        # Gaps that truly block progress
```

---

## Database Schema

```sql
-- World model transitions
CREATE TABLE world_transitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(100) NOT NULL,
    subdomain VARCHAR(100),
    preconditions JSONB NOT NULL,
    action TEXT NOT NULL,
    postconditions JSONB NOT NULL,
    alternative_outcomes JSONB,
    reliability FLOAT DEFAULT 0.5,
    sample_size INT DEFAULT 0,
    last_validated TIMESTAMP WITH TIME ZONE,
    source VARCHAR(50) DEFAULT 'hypothesized',
    source_evidence JSONB,
    contradictions JSONB,
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Self model competencies
CREATE TABLE self_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability VARCHAR(200) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    subdomain VARCHAR(100),
    estimated_accuracy FLOAT DEFAULT 0.5,
    confidence_in_estimate FLOAT DEFAULT 0.5,
    failure_modes JSONB,
    typical_steps INT,
    typical_duration_seconds FLOAT,
    sample_size INT DEFAULT 0,
    last_calibrated TIMESTAMP WITH TIME ZONE,
    calibration_history JSONB,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Goal network
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_state TEXT NOT NULL,
    success_criteria JSONB NOT NULL,
    priority FLOAT DEFAULT 0.5,
    deadline TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active',
    progress FLOAT DEFAULT 0.0,
    parent_goal_id UUID REFERENCES goals(id),
    blocking_on JSONB,
    trigger_conditions JSONB,
    last_worked TIMESTAMP WITH TIME ZONE,
    rationale TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Metamemory
CREATE TABLE metamemory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_pattern TEXT NOT NULL,
    feeling_of_knowing FLOAT DEFAULT 0.5,
    estimated_retrieval_quality FLOAT DEFAULT 0.5,
    likely_sources JSONB,
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INT DEFAULT 0,
    reliability_history JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_transitions_domain ON world_transitions(domain);
CREATE INDEX idx_transitions_embedding ON world_transitions USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_competencies_capability ON self_competencies(capability);
CREATE INDEX idx_competencies_domain ON self_competencies(domain);
CREATE INDEX idx_goals_status ON goals(status);
CREATE INDEX idx_goals_parent ON goals(parent_goal_id);
CREATE INDEX idx_metamemory_pattern ON metamemory(query_pattern);
```

---

*Draft schemas for FORESIGHT proposal, December 2024*
*Status: Specification - requires implementation and validation*
