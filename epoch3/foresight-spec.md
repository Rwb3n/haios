# FORESIGHT: Predictive Self-Modeling Layer

## Specification Document

### Status: Complete (v1.0)
### Version: 1.0

**Key Update (v1.0):** Self-model now uses Bayesian calibration via `BayesianPrior` class to solve the cold-start problem. Single failures shift competence estimates slightly rather than crashing to zero.

**Dependencies:**
- Schema definitions: `schemas/foresight-schemas.md`
- Integration: `integration-patterns.md`, `schemas/unified-memory.md`
- Related paradigms: `schemas/hindsight-schemas.md` (Declarative), `schemas/reasoningbank-schemas.md` (Procedural)

---

## Motivation

Existing agent memory systems are fundamentally **reactive**:
- HINDSIGHT stores what happened (past-oriented)
- ReasoningBank stores what worked (past→future transfer)

Neither system models:
- What **will** happen if the agent takes action X
- What the agent is **capable** of doing well
- What the agent is **trying** to achieve over time
- What the agent **knows it doesn't know**

FORESIGHT closes this loop with predictive self-modeling.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FORESIGHT                                     │
│                    Predictive Self-Modeling Layer                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      WORLD MODEL                                 │  │
│   │                                                                  │  │
│   │  Environment dynamics: "If I click X, page state becomes Y"     │  │
│   │  Entity behavior models: "User tends to ask follow-ups about Z" │  │
│   │  Causal structure: "A causes B under conditions C"              │  │
│   │                                                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                 │                                       │
│                                 ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      SELF MODEL                                  │  │
│   │                                                                  │  │
│   │  Competence map: "I'm reliable at X, unreliable at Y"           │  │
│   │  Uncertainty tracking: "Confidence in this prediction: 0.3"     │  │
│   │  Resource model: "This will take ~N steps / tokens"             │  │
│   │  Failure modes: "I tend to miss edge cases in domain Z"         │  │
│   │                                                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                 │                                       │
│                                 ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    GOAL NETWORK                                  │  │
│   │                                                                  │  │
│   │  Persistent intentions: "Complete project X by deadline"        │  │
│   │  Subgoal decomposition: "To do A, first need B and C"           │  │
│   │  Prospective triggers: "When X happens, do Y"                   │  │
│   │  Gap detection: "Missing information needed for goal G"         │  │
│   │                                                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                 │                                       │
│                                 ▼                                       │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                     METAMEMORY                                   │  │
│   │                                                                  │  │
│   │  Feeling of knowing: "I probably have info on this"             │  │
│   │  Retrieval confidence: "This memory is likely accurate"         │  │
│   │  Source monitoring: "Did I observe this or infer it?"           │  │
│   │  Belief revision triggers: "Time to update this model"          │  │
│   │                                                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Operations

### 1. SIMULATE(action, context) → predicted_outcome + confidence

Runs the world model forward to predict outcomes.

```
SIMULATE(action, context):
    1. Query Declarative memory for relevant facts
    2. Query Procedural memory for applicable strategies
    3. Retrieve matching world model transitions
    4. Generate predicted outcome distribution
    5. Return (most_likely_outcome, confidence, alternatives)
```

**Use cases:**
- "What happens if I click this button?"
- "How will the user respond to this message?"
- "What state will the code be in after this edit?"

### 2. INTROSPECT(task) → competence_estimate + failure_modes

Queries the self-model to assess capability.

```
INTROSPECT(task):
    1. Extract task domain and requirements
    2. Match to self-model competence entries
    3. Retrieve historical performance data
    4. Identify known failure modes for this domain
    5. Return (estimated_accuracy, known_risks, confidence_in_estimate)
```

**Use cases:**
- "Am I good at this type of task?"
- "What might go wrong if I try this?"
- "Should I attempt this or ask for help?"

### 3. ANTICIPATE(goal_state) → required_knowledge + required_skills

Backward chains from goals to identify gaps.

```
ANTICIPATE(goal_state):
    1. Decompose goal into subgoals
    2. For each subgoal:
       a. Check Declarative memory for required knowledge
       b. Check Procedural memory for required skills
       c. Identify gaps
    3. Generate acquisition plan for gaps
    4. Return (knowledge_gaps, skill_gaps, acquisition_plan)
```

**Use cases:**
- "What do I need to know to complete this project?"
- "What skills am I missing for this task?"
- "What should I learn next?"

### 4. UPDATE(prediction, outcome) → model_delta

Updates models based on prediction-outcome comparison.

```
UPDATE(prediction, outcome):
    1. Compare predicted vs actual outcome
    2. Calculate prediction error
    3. If significant error:
       a. Update world model transition probabilities
       b. Adjust self-model competence estimates
       c. Generate learning signal for Procedural memory
    4. Return (updated_world_model, updated_self_model, learning_signal)
```

**Use cases:**
- "My prediction was wrong - update my model"
- "I succeeded at something I expected to fail - I'm better than I thought"
- "This strategy didn't work here - adjust competence estimate"

---

## Component Specifications

### World Model

```
WorldModelEntry:
    domain: str                    # "web_navigation", "code_editing", etc.
    transition_pattern: str        # "action X in state S → state S'"
    preconditions: list[str]       # What must be true for this to apply
    reliability: float             # How often this pattern holds (0-1)
    sample_size: int               # Number of observations
    last_validated: timestamp      # When this was last confirmed
    contradictions: list[str]      # Known exceptions or failures
    source: str                    # "observed" | "inferred" | "told"
```

**Example entries:**
```yaml
- domain: web_navigation
  transition_pattern: "click(submit_button) → form_submitted"
  preconditions: ["form_valid", "button_enabled"]
  reliability: 0.95
  sample_size: 47
  last_validated: 2024-12-15
  contradictions: ["fails if network timeout"]
  source: observed

- domain: user_behavior  
  transition_pattern: "provide_code_fix → user_asks_explanation"
  preconditions: ["code_is_complex"]
  reliability: 0.7
  sample_size: 23
  last_validated: 2024-12-14
  contradictions: ["expert users often skip explanation"]
  source: inferred
```

### Self Model

```
SelfModelEntry:
    capability: str                # "temporal_reasoning", "entity_resolution"
    domain: str                    # Where this capability applies
    estimated_accuracy: float      # Calibrated from outcomes (0-1)
    confidence_in_estimate: float  # How sure about the accuracy estimate
    failure_modes: list[str]       # Known ways this capability fails
    sample_size: int               # Number of measured attempts
    last_calibrated: timestamp     # When accuracy was last updated
    notes: str                     # Qualitative observations
```

**Example entries:**
```yaml
- capability: python_debugging
  domain: code_editing
  estimated_accuracy: 0.85
  confidence_in_estimate: 0.9
  failure_modes: 
    - "misses async/await issues"
    - "overconfident on complex inheritance"
  sample_size: 156
  last_calibrated: 2024-12-15
  notes: "Strong on standard patterns, weaker on advanced concurrency"

- capability: legal_interpretation
  domain: document_analysis
  estimated_accuracy: 0.45
  confidence_in_estimate: 0.6
  failure_modes:
    - "misses jurisdiction-specific nuances"
    - "overrelies on pattern matching"
  sample_size: 12
  last_calibrated: 2024-12-10
  notes: "Should recommend consulting lawyer for anything substantive"
```

### Goal Network

```
GoalEntry:
    id: str                        # Unique identifier
    goal_state: str                # Desired end state description
    priority: float                # Importance weight (0-1)
    deadline: timestamp | None     # When this should be complete
    status: GoalStatus             # active | suspended | completed | abandoned
    parent_goal: str | None        # ID of parent goal (for subgoals)
    subgoals: list[str]            # IDs of child goals
    blocking_on: list[str]         # Knowledge/skill gaps preventing progress
    trigger_conditions: list[str]  # Prospective memory triggers
    progress: float                # Estimated completion (0-1)
    last_worked: timestamp         # When agent last made progress
    notes: str                     # Context and rationale

GoalStatus = Enum:
    ACTIVE                         # Currently being pursued
    SUSPENDED                      # Paused, waiting for something
    COMPLETED                      # Successfully achieved
    ABANDONED                      # Deliberately stopped pursuing
```

**Example goal tree:**
```yaml
- id: project_alpha
  goal_state: "Complete Project Alpha documentation"
  priority: 0.8
  deadline: 2024-12-31
  status: active
  parent_goal: null
  subgoals: [alpha_architecture, alpha_api, alpha_examples]
  blocking_on: []
  trigger_conditions: ["user mentions 'Project Alpha'"]
  progress: 0.4
  last_worked: 2024-12-15

- id: alpha_architecture
  goal_state: "Document system architecture"
  priority: 0.9
  deadline: 2024-12-20
  status: active
  parent_goal: project_alpha
  subgoals: []
  blocking_on: ["need clarification on microservice boundaries"]
  trigger_conditions: []
  progress: 0.6
  last_worked: 2024-12-15
```

### Metamemory

```
MetamemoryEntry:
    query_pattern: str             # Type of query this applies to
    feeling_of_knowing: float      # Confidence that info exists (0-1)
    estimated_retrieval_quality: float  # Expected accuracy if retrieved
    likely_sources: list[str]      # Which memory stores probably have info
    last_accessed: timestamp       # When this topic was last retrieved
    access_count: int              # How often this is queried
    reliability_history: list[float]  # Past retrieval accuracy
```

**Example entries:**
```yaml
- query_pattern: "user preferences for *"
  feeling_of_knowing: 0.9
  estimated_retrieval_quality: 0.85
  likely_sources: ["declarative.opinion", "declarative.observation"]
  last_accessed: 2024-12-15
  access_count: 47
  reliability_history: [0.9, 0.85, 0.88, 0.92]

- query_pattern: "historical events before 1900"
  feeling_of_knowing: 0.7
  estimated_retrieval_quality: 0.5
  likely_sources: ["declarative.world"]
  last_accessed: 2024-12-10
  access_count: 3
  reliability_history: [0.6, 0.4]
```

---

## Integration Points

### With Declarative Memory (HINDSIGHT-style)

```
FORESIGHT                         DECLARATIVE
    │                                  │
    │  Query facts for simulation      │
    ├─────────────────────────────────►│
    │                                  │
    │  Return relevant facts           │
    │◄─────────────────────────────────┤
    │                                  │
    │  Store validated predictions     │
    ├─────────────────────────────────►│
    │  as new beliefs                  │
    │                                  │
    │  Report contradictions to        │
    │◄─────────────────────────────────┤
    │  update world model              │
```

### With Procedural Memory (ReasoningBank-style)

```
FORESIGHT                         PROCEDURAL
    │                                  │
    │  Query strategies for context    │
    ├─────────────────────────────────►│
    │                                  │
    │  Return applicable strategies    │
    │◄─────────────────────────────────┤
    │                                  │
    │  Report strategy success/fail    │
    ├─────────────────────────────────►│
    │  to update procedural memory     │
    │                                  │
    │  Strategy selection based on     │
    │◄─────────────────────────────────┤
    │  self-model competence           │
```

---

## Enabled Capabilities

| Capability | Without FORESIGHT | With FORESIGHT |
|------------|-------------------|----------------|
| Planning | Reactive | Proactive |
| Risk assessment | Post-hoc | Pre-hoc simulation |
| Resource estimation | Implicit | Explicit modeling |
| Uncertainty handling | Overconfident | Calibrated |
| Multi-step reasoning | Emergent from LLM | Explicit goal decomposition |
| Help-seeking | Threshold-based | Competence-aware |
| Persistent goals | Session-limited | Cross-session |
| Learning prioritization | Reactive | Gap-directed |

---

## Implementation Considerations

### Storage Requirements

| Component | Estimated Size | Growth Rate |
|-----------|---------------|-------------|
| World Model | 10K-100K entries | Slow (stabilizes) |
| Self Model | 100-1K entries | Very slow |
| Goal Network | 10-100 active | User-dependent |
| Metamemory | 1K-10K patterns | Moderate |

### Computational Costs

| Operation | Complexity | Typical Latency |
|-----------|-----------|-----------------|
| SIMULATE | O(world_model_size) | 50-200ms |
| INTROSPECT | O(self_model_size) | 10-50ms |
| ANTICIPATE | O(goal_depth × subgoals) | 100-500ms |
| UPDATE | O(1) amortized | 20-100ms |

### Failure Modes

1. **Model drift**: World model becomes stale if not updated
2. **Overconfidence**: Self-model accuracy estimates too high
3. **Goal explosion**: Too many subgoals to manage effectively
4. **Cold start**: No predictions possible until models populated

---

## Validation Approach

### World Model Validation
- Compare predictions to observed outcomes
- Track Brier score over time
- Flag entries with declining reliability

### Self Model Validation
- Compare competence estimates to actual success rates
- Calibration plots (predicted vs actual accuracy)
- Failure mode coverage (did we predict this failure?)

### Goal Network Validation
- Goal completion rates
- Deadline adherence
- Gap detection accuracy (did blocking_on correctly identify issues?)

### Metamemory Validation
- Feeling-of-knowing vs actual retrieval success
- Source monitoring accuracy
- Retrieval confidence calibration

---

## Open Questions

1. **Granularity**: How specific should world model entries be?
2. **Forgetting**: When to remove stale entries?
3. **Generalization**: How to transfer models across domains?
4. **Bootstrapping**: How to initialize models for new domains?
5. **Multi-agent**: How to share models across agent instances?
6. **Human oversight**: How to make models interpretable and correctable?

---

## Next Steps

1. Define detailed schemas (see `/schemas/foresight-schemas.md`)
2. Implement core operations in prototype
3. Build validation framework
4. Integrate with existing Declarative/Procedural layers
5. Evaluate on benchmark tasks

---

*Draft specification, December 2024*
*Status: Proposal - requires implementation and validation*
