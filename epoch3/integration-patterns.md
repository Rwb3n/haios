# Integration Patterns

## Cross-Paradigm Data Flows and Composition

This document specifies how the three memory paradigms (Declarative, Procedural, Predictive) interact to form a complete cognitive memory system.

**Dependencies:** This document uses types defined in:
- `schemas/hindsight-schemas.md`: MemoryUnit, MemoryBank, Entity
- `schemas/reasoningbank-schemas.md`: MemoryItem, Trajectory, TrajectoryOutcome
- `schemas/foresight-schemas.md`: GoalEntry, SimulationResult, IntrospectionResult, AnticipationResult, CompetenceEntry
- `schemas/unified-memory.md`: UnifiedMemory, Task, Query, Response, Outcome, GoalProgress, LearningPriority

**Note:** `Strategy` is a type alias for `MemoryItem` to improve readability in procedural contexts.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED MEMORY SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                       QUERY ROUTER                               │  │
│   │                                                                  │  │
│   │  Analyzes incoming queries and routes to appropriate paradigm(s)│  │
│   │                                                                  │  │
│   └──────────────────────────┬──────────────────────────────────────┘  │
│                              │                                          │
│          ┌───────────────────┼───────────────────┐                     │
│          │                   │                   │                     │
│          ▼                   ▼                   ▼                     │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐             │
│   │ DECLARATIVE │     │ PROCEDURAL  │     │ PREDICTIVE  │             │
│   │             │     │             │     │             │             │
│   │  Facts      │◄───►│  Strategies │◄───►│  World Model│             │
│   │  Beliefs    │     │  Lessons    │     │  Self Model │             │
│   │  Entities   │     │  Skills     │     │  Goals      │             │
│   │             │     │             │     │  Metamemory │             │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘             │
│          │                   │                   │                     │
│          └───────────────────┼───────────────────┘                     │
│                              │                                          │
│                              ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      RESPONSE SYNTHESIZER                        │  │
│   │                                                                  │  │
│   │  Combines outputs from all paradigms into coherent response     │  │
│   │                                                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Query Routing Logic

### Query Classification

```python
from enum import Enum
from typing import Set

# Type alias: Strategy = MemoryItem (from reasoningbank_schemas)
# See schemas/unified-memory.md for full type definitions

class Paradigm(Enum):
    DECLARATIVE = "declarative"
    PROCEDURAL = "procedural"
    PREDICTIVE = "predictive"


def classify_query(query: str) -> Set[Paradigm]:
    """Determine which paradigms should handle a query."""
    
    paradigms = set()
    
    # Declarative indicators
    if requires_factual_knowledge(query):
        paradigms.add(Paradigm.DECLARATIVE)
    if references_entities(query):
        paradigms.add(Paradigm.DECLARATIVE)
    if asks_about_beliefs_or_preferences(query):
        paradigms.add(Paradigm.DECLARATIVE)
    
    # Procedural indicators
    if asks_how_to_do_something(query):
        paradigms.add(Paradigm.PROCEDURAL)
    if similar_to_past_tasks(query):
        paradigms.add(Paradigm.PROCEDURAL)
    if involves_multi_step_execution(query):
        paradigms.add(Paradigm.PROCEDURAL)
    
    # Predictive indicators
    if asks_about_future_outcomes(query):
        paradigms.add(Paradigm.PREDICTIVE)
    if requires_planning(query):
        paradigms.add(Paradigm.PREDICTIVE)
    if asks_about_capabilities(query):
        paradigms.add(Paradigm.PREDICTIVE)
    if involves_goal_tracking(query):
        paradigms.add(Paradigm.PREDICTIVE)
    
    # Default: use all if unclear
    if not paradigms:
        paradigms = {Paradigm.DECLARATIVE, Paradigm.PROCEDURAL, Paradigm.PREDICTIVE}
    
    return paradigms
```

### Routing Examples

| Query Type | Paradigms Used | Rationale |
|------------|---------------|-----------|
| "What is the user's preferred language?" | Declarative | Fact retrieval |
| "How do I navigate paginated results?" | Procedural | Strategy retrieval |
| "What will happen if I submit this form?" | Predictive | Outcome simulation |
| "Help me complete my project" | All three | Facts + strategies + goals |
| "Am I good at SQL queries?" | Predictive + Declarative | Self-model + evidence |
| "What did we discuss yesterday?" | Declarative | Experience retrieval |

---

## Cross-Paradigm Data Flows

### Flow 1: Declarative → Procedural

**Purpose:** Ground strategies in factual knowledge

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DECLARATIVE                              PROCEDURAL                    │
│                                                                         │
│  Facts about environment    ─────────►   Strategy applicability        │
│  "This is a paginated list"              "Use pagination strategy"     │
│                                                                         │
│  Entity states              ─────────►   Strategy parameterization     │
│  "User prefers brief"                    "Use concise variant"         │
│                                                                         │
│  Historical context         ─────────►   Strategy selection            │
│  "User struggled with X"                 "Avoid X-related strategies"  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
def retrieve_strategy(task: Task, memory: UnifiedMemory) -> Strategy:
    # Get relevant facts from declarative memory
    facts = memory.declarative.recall(task.context)
    
    # Filter strategies based on factual preconditions
    candidates = memory.procedural.recall(task.query)
    applicable = [s for s in candidates if s.preconditions_met(facts)]
    
    # Rank by historical success in similar contexts
    ranked = rank_by_context_similarity(applicable, facts)
    
    return ranked[0] if ranked else None
```

### Flow 2: Procedural → Declarative

**Purpose:** Successful strategies become known patterns

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PROCEDURAL                               DECLARATIVE                   │
│                                                                         │
│  Strategy succeeded         ─────────►   Experience record             │
│  "Pagination strategy                    "I successfully used          │
│   worked for task X"                      pagination on 2024-12-15"    │
│                                                                         │
│  Pattern discovered         ─────────►   World knowledge               │
│  "Filtering before                       "This site requires           │
│   pagination works better"                filtering before pagination" │
│                                                                         │
│  Failure lesson             ─────────►   Belief update                 │
│  "Strategy X fails                       "Strategy X is unreliable     │
│   in context Y"                           in context Y" (conf: 0.8)    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
def record_strategy_outcome(
    strategy: Strategy, 
    outcome: Outcome,
    memory: UnifiedMemory
):
    # Record experience
    memory.declarative.retain(
        bank="experience",
        text=f"Used strategy '{strategy.title}' for {outcome.task_type}: "
             f"{'succeeded' if outcome.success else 'failed'}",
        confidence=1.0,
        entities=[outcome.task_id]
    )
    
    # If pattern discovered, add to world knowledge
    if outcome.reveals_pattern:
        memory.declarative.retain(
            bank="world",
            text=outcome.pattern_description,
            confidence=outcome.pattern_confidence
        )
```

### Flow 3: Declarative → Predictive

**Purpose:** Ground predictions in observed facts

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DECLARATIVE                              PREDICTIVE                    │
│                                                                         │
│  Entity states              ─────────►   World model conditioning      │
│  "Button is disabled"                    "Click will fail"             │
│                                                                         │
│  Historical patterns        ─────────►   Transition probabilities      │
│  "User usually asks                      P(follow_up | code_help)=0.7  │
│   follow-up questions"                                                 │
│                                                                         │
│  Belief confidence          ─────────►   Prediction uncertainty        │
│  "Preference unclear                     "Low confidence in            │
│   (conf: 0.4)"                            personalization prediction"  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
def simulate_with_facts(
    action: str,
    context: Dict,
    memory: UnifiedMemory
) -> SimulationResult:
    # Retrieve relevant facts
    facts = memory.declarative.recall(context)
    
    # Get applicable transition patterns
    transitions = memory.predictive.world_model.get_transitions(
        action=action,
        preconditions=extract_preconditions(facts)
    )
    
    # Weight predictions by fact confidence
    weighted_outcomes = []
    for transition in transitions:
        fact_confidence = get_supporting_fact_confidence(transition, facts)
        weighted_outcomes.append({
            "outcome": transition.postconditions,
            "probability": transition.reliability * fact_confidence,
            "uncertainty_source": "fact_confidence" if fact_confidence < 0.8 else "model"
        })
    
    return SimulationResult(
        predicted_state=most_likely(weighted_outcomes),
        confidence=max_probability(weighted_outcomes),
        alternatives=weighted_outcomes
    )
```

### Flow 4: Predictive → Declarative

**Purpose:** Validated predictions become beliefs

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PREDICTIVE                               DECLARATIVE                   │
│                                                                         │
│  Prediction validated       ─────────►   Belief strengthened           │
│  "Predicted X, X occurred"               confidence += α               │
│                                                                         │
│  Prediction failed          ─────────►   Belief weakened/revised       │
│  "Predicted X, Y occurred"               confidence -= α               │
│                                                                         │
│  New pattern discovered     ─────────►   World fact added              │
│  "A always leads to B"                   "A causes B" (factual)        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
def update_beliefs_from_prediction(
    prediction: SimulationResult,
    actual_outcome: Outcome,
    memory: UnifiedMemory
):
    prediction_correct = prediction.matches(actual_outcome)
    
    if prediction_correct:
        # Reinforce supporting beliefs
        for belief_id in prediction.supporting_beliefs:
            memory.declarative.reinforce_opinion(belief_id)
        
        # If pattern is now highly reliable, promote to fact
        if prediction.source_pattern.reliability > 0.95:
            memory.declarative.retain(
                bank="world",
                text=prediction.source_pattern.as_fact(),
                confidence=prediction.source_pattern.reliability
            )
    else:
        # Weaken contradicted beliefs
        for belief_id in prediction.supporting_beliefs:
            memory.declarative.weaken_opinion(belief_id)
        
        # Record the contradiction
        memory.declarative.retain(
            bank="experience",
            text=f"Prediction failed: expected {prediction.predicted_state}, "
                 f"got {actual_outcome.state}",
            entities=[prediction.source_pattern.id]
        )
```

### Flow 5: Procedural → Predictive

**Purpose:** Strategy success rates inform self-model

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PROCEDURAL                               PREDICTIVE                    │
│                                                                         │
│  Strategy success rate      ─────────►   Competence estimate           │
│  "Strategy X: 85% success"               "Capability X: 0.85 accuracy" │
│                                                                         │
│  Failure mode identified    ─────────►   Self-model failure modes      │
│  "Strategy fails when Y"                 "Known risk: Y condition"     │
│                                                                         │
│  Strategy complexity        ─────────►   Resource model                │
│  "Strategy takes ~5 steps"               "Estimated cost: 5 steps"     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
def update_self_model_from_strategies(memory: UnifiedMemory):
    """Periodic sync: aggregate strategy performance into self-model."""
    
    for domain in memory.procedural.get_domains():
        strategies = memory.procedural.get_strategies_by_domain(domain)
        
        # Aggregate success rates
        total_applications = sum(s.application_count for s in strategies)
        total_successes = sum(s.success_when_applied for s in strategies)
        
        if total_applications > 0:
            accuracy = total_successes / total_applications
            
            # Update self-model competence
            memory.predictive.self_model.update_competence(
                capability=domain,
                estimated_accuracy=accuracy,
                sample_size=total_applications
            )
        
        # Aggregate failure modes
        failure_modes = {}
        for strategy in strategies:
            for mode in strategy.failure_modes:
                failure_modes[mode] = failure_modes.get(mode, 0) + 1
        
        memory.predictive.self_model.set_failure_modes(
            capability=domain,
            modes=list(failure_modes.keys()),
            frequencies=failure_modes
        )
```

### Flow 6: Predictive → Procedural

**Purpose:** Competence guides strategy selection

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PREDICTIVE                               PROCEDURAL                    │
│                                                                         │
│  Competence estimate        ─────────►   Strategy ranking              │
│  "Low skill in domain X"                 "Prefer simpler strategies"   │
│                                                                         │
│  Goal requirements          ─────────►   Strategy search               │
│  "Goal needs skill Y"                    "Retrieve Y-related strategies│
│                                                                         │
│  Risk assessment            ─────────►   Strategy filtering            │
│  "High-risk prediction"                  "Exclude risky strategies"    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
def select_strategy_with_competence(
    task: Task,
    memory: UnifiedMemory
) -> Strategy:
    # Get competence for task domain
    competence = memory.predictive.self_model.get_competence(task.domain)
    
    # Retrieve candidate strategies
    candidates = memory.procedural.recall(task.query)
    
    # Filter by risk tolerance based on competence
    if competence.estimated_accuracy < 0.5:
        # Low competence: prefer conservative strategies
        candidates = [s for s in candidates if s.risk_level != "high"]
    
    # Rank by expected utility given competence
    ranked = []
    for strategy in candidates:
        # Simulate outcome
        sim = memory.predictive.simulate(strategy, task.context)
        
        # Adjust by self-model confidence
        adjusted_confidence = sim.confidence * competence.confidence_in_estimate
        
        ranked.append((strategy, adjusted_confidence))
    
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[0][0] if ranked else None
```

---

## Composition Patterns

### Pattern 1: Fact-Grounded Strategy Execution

**Scenario:** Execute a task using facts, strategies, and outcome prediction

```python
def execute_grounded_strategy(task: Task, memory: UnifiedMemory) -> Outcome:
    """
    Full pipeline:
    1. Retrieve relevant facts (Declarative)
    2. Retrieve applicable strategies (Procedural)
    3. Simulate outcomes (Predictive)
    4. Select best strategy
    5. Execute
    6. Learn from outcome (all three paradigms)
    """
    
    # Step 1: Get facts
    context_facts = memory.declarative.recall(
        query=task.context,
        banks=["world", "experience", "observation"]
    )
    user_prefs = memory.declarative.recall(
        query="user preferences",
        banks=["opinion"]
    )
    
    # Step 2: Get strategies
    strategies = memory.procedural.recall(
        query=task.query,
        context=context_facts
    )
    
    # Step 3: Simulate outcomes for top candidates
    predictions = []
    for strategy in strategies[:5]:
        outcome = memory.predictive.simulate(
            action=strategy.to_action(),
            context={**context_facts, **user_prefs}
        )
        predictions.append((strategy, outcome))
    
    # Step 4: Select best (highest utility, adjusted for confidence)
    def score(pair):
        strategy, prediction = pair
        return prediction.utility * prediction.confidence
    
    best_strategy, expected_outcome = max(predictions, key=score)
    
    # Step 5: Execute
    actual_outcome = execute(best_strategy, task)
    
    # Step 6: Update all paradigms
    
    # Declarative: record experience
    memory.declarative.retain(
        bank="experience",
        text=f"Executed {best_strategy.title} for {task.type}: "
             f"{'success' if actual_outcome.succeeded else 'failure'}",
        entities=[task.id, best_strategy.id]
    )
    
    # Procedural: extract lessons
    memory.procedural.extract(
        trajectory=actual_outcome.trajectory,
        success=actual_outcome.succeeded,
        failure_reason=actual_outcome.failure_reason
    )
    
    # Predictive: update models
    memory.predictive.update(
        prediction=expected_outcome,
        outcome=actual_outcome
    )
    
    return actual_outcome
```

### Pattern 2: Goal-Directed Planning

**Scenario:** Achieve a persistent goal across sessions

```python
def pursue_goal(goal: GoalEntry, memory: UnifiedMemory) -> GoalProgress:
    """
    Plan and execute toward a goal:
    1. Decompose goal into subgoals (Predictive)
    2. Identify gaps (Predictive)
    3. Check knowledge availability (Declarative)
    4. Check strategy availability (Procedural)
    5. Execute achievable subgoals
    6. Update goal state
    """
    
    # Step 1: Decompose
    subgoals = memory.predictive.decompose_goal(goal)
    
    # Step 2: Identify gaps
    gaps = memory.predictive.anticipate(goal)
    
    # Step 3: Check declarative memory for knowledge gaps
    resolvable_knowledge_gaps = []
    for gap in gaps.knowledge_gaps:
        if memory.declarative.has_knowledge(gap):
            resolvable_knowledge_gaps.append(gap)
    
    # Remove resolvable gaps
    for gap in resolvable_knowledge_gaps:
        gaps.knowledge_gaps.remove(gap)
    
    # Step 4: Check procedural memory for skill gaps
    resolvable_skill_gaps = []
    for gap in gaps.skill_gaps:
        if memory.procedural.has_strategy_for(gap):
            resolvable_skill_gaps.append(gap)
    
    for gap in resolvable_skill_gaps:
        gaps.skill_gaps.remove(gap)
    
    # Step 5: Execute achievable subgoals
    progress = GoalProgress(goal_id=goal.id)
    
    for subgoal in subgoals:
        if not subgoal.is_blocked_by(gaps):
            # Convert subgoal to task and execute
            task = subgoal.to_task()
            outcome = execute_grounded_strategy(task, memory)
            
            progress.record_subgoal_outcome(subgoal, outcome)
    
    # Step 6: Update goal state
    goal.progress = progress.calculate_overall_progress()
    goal.blocking_on = [str(g) for g in gaps.all_gaps()]
    goal.last_worked = datetime.now()
    
    memory.predictive.update_goal(goal)
    
    return progress
```

### Pattern 3: Competence-Aware Help-Seeking

**Scenario:** Decide whether to attempt a task or ask for help

```python
from enum import Enum

class Decision(Enum):
    ATTEMPT = "attempt"
    ASK_FOR_HELP = "ask_for_help"
    ATTEMPT_WITH_CAVEAT = "attempt_with_caveat"
    DECLINE = "decline"


def should_attempt_or_ask(task: Task, memory: UnifiedMemory) -> Decision:
    """
    Determine the right approach:
    1. Assess competence (Predictive)
    2. Simulate outcomes (Predictive)
    3. Check past experiences (Declarative)
    4. Check available strategies (Procedural)
    5. Make decision
    """
    
    # Step 1: Assess competence
    competence = memory.predictive.introspect(task)
    
    # Step 2: Simulate outcomes
    attempt_outcome = memory.predictive.simulate(
        action="attempt_task",
        context={"task": task.description}
    )
    
    # Step 3: Check past experience
    similar_experiences = memory.declarative.recall(
        query=task.description,
        banks=["experience"],
        limit=10
    )
    
    past_attempts = [e for e in similar_experiences if "attempted" in e.text.lower()]
    past_successes = [e for e in past_attempts if "success" in e.text.lower()]
    past_success_rate = len(past_successes) / len(past_attempts) if past_attempts else 0.5
    
    # Step 4: Check for applicable strategies
    strategies = memory.procedural.recall(task.query)
    has_applicable_strategy = len(strategies) > 0
    best_strategy_success_rate = max(
        (s.success_rate() or 0.5 for s in strategies), 
        default=0.5
    )
    
    # Step 5: Weighted decision
    confidence_score = (
        competence.estimated_accuracy * 0.30 +
        past_success_rate * 0.25 +
        best_strategy_success_rate * 0.25 +
        attempt_outcome.confidence * 0.20
    )
    
    # Check for known failure modes
    failure_risk = 0.0
    for mode in competence.known_failure_modes:
        if mode_applies_to_task(mode, task):
            failure_risk += 0.1
    
    adjusted_confidence = confidence_score - failure_risk
    
    # Decision thresholds
    if adjusted_confidence > 0.75:
        return Decision.ATTEMPT
    elif adjusted_confidence > 0.5:
        return Decision.ATTEMPT_WITH_CAVEAT
    elif adjusted_confidence > 0.25:
        return Decision.ASK_FOR_HELP
    else:
        return Decision.DECLINE
```

### Pattern 4: Proactive Gap Detection

**Scenario:** Identify what the agent should learn next

```python
def identify_learning_priorities(memory: UnifiedMemory) -> List[LearningPriority]:
    """
    Analyze memory to find high-value learning opportunities:
    1. Find goals blocked by knowledge gaps
    2. Find recurring failure patterns
    3. Find low-confidence high-importance beliefs
    4. Rank by impact
    """
    
    priorities = []
    
    # 1. Goals blocked by knowledge gaps
    active_goals = memory.predictive.get_active_goals()
    for goal in active_goals:
        if goal.blocking_on:
            for blocker in goal.blocking_on:
                priorities.append(LearningPriority(
                    type="knowledge_gap",
                    description=blocker,
                    impact=goal.priority.value,
                    source_goal=goal.id
                ))
    
    # 2. Recurring failure patterns
    failure_experiences = memory.declarative.recall(
        query="failure",
        banks=["experience"],
        limit=50
    )
    
    failure_patterns = extract_patterns(failure_experiences)
    for pattern, count in failure_patterns.items():
        if count >= 3:  # Recurring
            priorities.append(LearningPriority(
                type="recurring_failure",
                description=f"Pattern: {pattern} (occurred {count} times)",
                impact=count * 0.1,
                source_experiences=[e.id for e in failure_experiences 
                                   if pattern in e.text]
            ))
    
    # 3. Low-confidence important beliefs
    uncertain_opinions = memory.declarative.get_opinions_below_confidence(0.5)
    for opinion in uncertain_opinions:
        # Check if this opinion affects active goals
        relevance = memory.predictive.opinion_relevance_to_goals(opinion)
        if relevance > 0.5:
            priorities.append(LearningPriority(
                type="uncertain_belief",
                description=f"Uncertain: {opinion.text} (conf: {opinion.confidence})",
                impact=relevance,
                source_belief=opinion.id
            ))
    
    # 4. Rank by impact
    priorities.sort(key=lambda p: p.impact, reverse=True)
    
    return priorities[:10]  # Top 10
```

---

## Response Synthesis

### Combining Multi-Paradigm Outputs

```python
def synthesize_response(query: Query, memory: UnifiedMemory) -> Response:
    """
    Combine outputs from multiple paradigms into coherent response.
    """
    
    paradigms = classify_query(query.text)
    outputs = {}
    
    # Parallel retrieval from relevant paradigms
    if Paradigm.DECLARATIVE in paradigms:
        outputs["facts"] = memory.declarative.recall(query.text)
        outputs["preferences"] = memory.declarative.recall(
            "user preferences", banks=["opinion"]
        )
    
    if Paradigm.PROCEDURAL in paradigms:
        outputs["strategies"] = memory.procedural.recall(query.text)
    
    if Paradigm.PREDICTIVE in paradigms:
        outputs["predictions"] = memory.predictive.simulate(query.as_action())
        outputs["goals"] = memory.predictive.get_relevant_goals(query.text)
        outputs["competence"] = memory.predictive.introspect(query.as_task())
    
    # Resolve conflicts
    resolved = resolve_conflicts(outputs)
    
    # Generate coherent response
    response = generate_response(query, resolved)
    
    return response


def resolve_conflicts(outputs: Dict) -> Dict:
    """
    Handle conflicts between paradigm outputs.
    """
    
    resolved = outputs.copy()
    
    # Fact contradicts prediction → trust fact, flag prediction
    if "facts" in outputs and "predictions" in outputs:
        for fact in outputs["facts"]:
            if contradicts(fact, outputs["predictions"]):
                resolved["predictions"].confidence *= 0.5
                resolved["predictions"].add_caveat(
                    f"Note: prediction may conflict with known fact: {fact.text}"
                )
    
    # Strategy contradicts self-model → trust self-model
    if "strategies" in outputs and "competence" in outputs:
        competence = outputs["competence"]
        filtered_strategies = []
        for strategy in outputs["strategies"]:
            # Deprioritize strategies in weak competence areas
            if strategy.domain in competence.weak_domains:
                strategy.priority *= 0.5
            filtered_strategies.append(strategy)
        resolved["strategies"] = sorted(
            filtered_strategies, 
            key=lambda s: s.priority, 
            reverse=True
        )
    
    # Multiple strategies applicable → use competence to rank
    if "strategies" in outputs and len(outputs["strategies"]) > 1:
        if "competence" in outputs:
            resolved["strategies"] = rank_by_competence(
                outputs["strategies"],
                outputs["competence"]
            )
    
    return resolved
```

---

## Learning Signals

### Post-Interaction Learning

```python
def post_interaction_learning(
    query: Query,
    response: Response,
    outcome: Outcome,
    memory: UnifiedMemory
):
    """
    Update all memory paradigms after an interaction.
    """
    
    # === DECLARATIVE LEARNING ===
    
    # Record the experience
    memory.declarative.retain(
        bank="experience",
        text=f"Handled query '{query.summary}': "
             f"{'successful' if outcome.succeeded else 'unsuccessful'}",
        mention_time=datetime.now(),
        entities=outcome.mentioned_entities
    )
    
    # Update beliefs if outcome reveals new information
    if outcome.reveals_preferences:
        for pref in outcome.revealed_preferences:
            existing = memory.declarative.find_opinion(pref.topic)
            if existing:
                if pref.confirms:
                    memory.declarative.reinforce_opinion(existing.id)
                else:
                    memory.declarative.weaken_opinion(existing.id)
            else:
                memory.declarative.retain(
                    bank="opinion",
                    text=pref.statement,
                    confidence=0.6  # Initial confidence
                )
    
    # === PROCEDURAL LEARNING ===
    
    # Extract strategies from trajectory
    if outcome.has_trajectory:
        memory.procedural.extract(
            trajectory=outcome.trajectory,
            success=outcome.succeeded,
            failure_reason=outcome.failure_reason if not outcome.succeeded else None
        )
    
    # Update strategy statistics
    if outcome.strategy_used:
        strategy = memory.procedural.get(outcome.strategy_used)
        strategy.application_count += 1
        if outcome.succeeded:
            strategy.success_when_applied += 1
        memory.procedural.save(strategy)
    
    # === PREDICTIVE LEARNING ===
    
    # Update world model
    if outcome.predictions_made:
        for prediction in outcome.predictions_made:
            matched = prediction.matches(outcome)
            memory.predictive.world_model.update(
                pattern_id=prediction.source_pattern_id,
                outcome_matched=matched
            )
    
    # Update self-model
    memory.predictive.self_model.update_from_outcome(
        capability=outcome.capability_used,
        predicted_success=outcome.predicted_success_probability,
        actual_success=outcome.succeeded
    )
    
    # Update goal progress
    if outcome.goal_id:
        goal = memory.predictive.get_goal(outcome.goal_id)
        goal.progress += outcome.progress_delta
        goal.last_worked = datetime.now()
        
        if outcome.succeeded and goal.progress >= 1.0:
            goal.status = GoalStatus.COMPLETED
        
        memory.predictive.save_goal(goal)
    
    # === CROSS-PARADIGM UPDATES ===
    
    # Novel failure mode discovered
    if not outcome.succeeded and outcome.is_novel_failure:
        # Add to self-model
        memory.predictive.self_model.add_failure_mode(
            capability=outcome.capability_used,
            mode=outcome.failure_reason
        )
        
        # Record as experience
        memory.declarative.retain(
            bank="experience",
            text=f"Discovered failure mode in {outcome.capability_used}: "
                 f"{outcome.failure_reason}",
            confidence=0.8
        )
    
    # High-confidence pattern discovered
    if outcome.pattern_discovered and outcome.pattern_confidence > 0.9:
        # Promote from world model to declarative fact
        memory.declarative.retain(
            bank="world",
            text=outcome.pattern_description,
            confidence=outcome.pattern_confidence
        )
```

---

## Conflict Resolution Matrix

| Conflict Type | Resolution Strategy | Rationale |
|--------------|---------------------|-----------|
| Fact contradicts prediction | Trust fact, update world model | Facts are observed; predictions are inferred |
| Strategy contradicts self-model | Trust self-model, deprioritize strategy | Self-model aggregates more evidence |
| Goal conflicts with facts | Flag to user, suspend goal | User should resolve real-world conflicts |
| Multiple strategies applicable | Rank by (competence × success_rate) | Balance historical performance with current ability |
| Uncertain prediction | Widen confidence interval, seek more facts | Epistemic humility |
| Belief contradicts new evidence | Apply opinion evolution rules | Gradual belief update, not sudden reversal |
| Old fact contradicts new fact | Prefer more recent, check source reliability | Temporal recency with source weighting |

---

## Performance Considerations

### Latency Budget

| Operation | Target Latency | Strategy |
|-----------|---------------|----------|
| Query classification | <10ms | Rule-based, no ML |
| Declarative retrieval | <50ms | Parallel vector + keyword search |
| Procedural retrieval | <30ms | Single embedding search |
| Predictive simulation | <100ms | Cached world model lookups |
| Response synthesis | <50ms | Template-based generation |
| Total | <250ms | Parallel where possible |

### Caching Strategy

```python
class MemoryCache:
    """LRU cache for frequent memory accesses."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    # Cache user preferences (accessed every query)
    # Cache active goals (accessed frequently)
    # Cache recent strategies (likely to be reused)
    # Don't cache: world facts (too diverse), predictions (context-dependent)
```

---

*Integration patterns for three-paradigm memory system, December 2024*
