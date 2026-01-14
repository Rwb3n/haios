# HAIOS Memory Layer Mapping

## Integrating Three-Paradigm Memory with HAIOS Orchestrator

Status: Architecture Sketch  
Context: Application to HAIOS Agent Orchestration System

**Dependencies:** This document uses types defined in:
- `schemas/unified-memory.md`: UnifiedMemory, Task, Query, Response, Outcome
- `schemas/hindsight-schemas.md`: MemoryUnit, Entity
- `schemas/reasoningbank-schemas.md`: MemoryItem
- `schemas/foresight-schemas.md`: TransitionPattern, GoalEntry

---

## HAIOS Architecture Context

HAIOS is an AI agent orchestration system designed for autonomous business operations. Key characteristics:

- **Multi-agent coordination**: Multiple specialized agents working together
- **Long-lived operations**: Persistent tasks spanning sessions
- **Business context**: User preferences, project state, domain knowledge
- **Self-improvement**: Agents should get better over time

---

## Memory Layer Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           HAIOS ORCHESTRATOR                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                     MEMORY INTEGRATION LAYER                     │  │
│   │                                                                  │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │  │
│   │  │ DECLARATIVE │  │ PROCEDURAL  │  │ PREDICTIVE  │             │  │
│   │  │ (HINDSIGHT) │  │(ReasonBank) │  │ (FORESIGHT) │             │  │
│   │  │             │  │             │  │             │             │  │
│   │  │ User prefs  │  │ Task skills │  │ World model │             │  │
│   │  │ Domain facts│  │ Failure     │  │ Self model  │             │  │
│   │  │ Entity state│  │   lessons   │  │ Goal network│             │  │
│   │  │ Project ctx │  │ Strategies  │  │ Metamemory  │             │  │
│   │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │  │
│   │         │                │                │                     │  │
│   │         └────────────────┼────────────────┘                     │  │
│   │                          │                                      │  │
│   │                          ▼                                      │  │
│   │              ┌───────────────────────┐                         │  │
│   │              │    MEMORY ROUTER      │                         │  │
│   │              │                       │                         │  │
│   │              │ Routes queries to     │                         │  │
│   │              │ appropriate paradigm  │                         │  │
│   │              └───────────────────────┘                         │  │
│   │                                                                  │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│   ┌──────────────────────────────────────────────────────────────────┐ │
│   │                        AGENT POOL                                 │ │
│   │                                                                   │ │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │ │
│   │   │  Code   │  │   Web   │  │ Document│  │ Research│           │ │
│   │   │  Agent  │  │  Agent  │  │  Agent  │  │  Agent  │           │ │
│   │   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │ │
│   │        │            │            │            │                  │ │
│   │        └────────────┴────────────┴────────────┘                  │ │
│   │                          │                                        │ │
│   │                          ▼                                        │ │
│   │              ┌───────────────────────┐                           │ │
│   │              │   SHARED MEMORY BUS   │                           │ │
│   │              │                       │                           │ │
│   │              │ Agent-specific +      │                           │ │
│   │              │ orchestrator memory   │                           │ │
│   │              └───────────────────────┘                           │ │
│   │                                                                   │ │
│   └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Paradigm Assignments

### Declarative Memory (HINDSIGHT-style)

**Purpose in HAIOS:** Store facts about users, projects, and domains

| Content Type | Network | Example |
|-------------|---------|---------|
| User preferences | Opinion | "User prefers brief responses" (0.85) |
| User background | Observation | "User is Salesforce analyst at L&P" |
| Project facts | World | "Project Alpha uses Python 3.11" |
| Interaction history | Experience | "Helped user debug Lead object query" |
| Domain knowledge | World | "Salesforce Lead object has 27k records" |
| Entity states | World | "User's certification exam is scheduled" |

**HAIOS-Specific Extensions:**
```python
# Project-scoped facts
class ProjectContext:
    project_id: str
    facts: List[MemoryUnit]  # Facts relevant to this project
    entities: List[Entity]    # Project-specific entities
    
# Cross-project user model
class UserModel:
    user_id: str
    preferences: List[MemoryUnit]  # From Opinion network
    background: MemoryUnit         # From Observation network
    interaction_history: List[MemoryUnit]  # From Experience network
```

### Procedural Memory (ReasoningBank-style)

**Purpose in HAIOS:** Store learned strategies and failure lessons

| Content Type | Source | Example |
|-------------|--------|---------|
| Task strategies | Success trajectories | "For Salesforce queries, check object relationships first" |
| Failure lessons | Failed trajectories | "Avoid bulk DML in triggers without governor limit checks" |
| Workflow patterns | Repeated successes | "Documentation tasks: outline → draft → review → finalize" |
| Domain heuristics | Experience | "When user mentions 'attribution gap', investigate Lead Source" |

**HAIOS-Specific Extensions:**
```python
# Agent-specific skills
class AgentSkills:
    agent_type: str              # "code", "web", "document"
    skills: List[MemoryItem]     # Learned strategies
    
# Cross-agent shared knowledge
class SharedProcedures:
    domain: str                  # "salesforce", "documentation"
    procedures: List[MemoryItem]
    applicable_agents: List[str]
```

### Predictive Memory (FORESIGHT)

**Purpose in HAIOS:** Enable proactive orchestration and self-improvement

| Component | HAIOS Application |
|-----------|-------------------|
| World Model | Predict user needs, task outcomes, environment states |
| Self Model | Know which agent is best for each task type |
| Goal Network | Track persistent user projects and objectives |
| Metamemory | Know what knowledge HAIOS has about user/domain |

**HAIOS-Specific Extensions:**
```python
# Agent competence tracking
class AgentCompetence:
    agent_type: str
    task_domain: str
    estimated_accuracy: float
    failure_modes: List[str]
    
# User behavior prediction
class UserBehaviorModel:
    user_id: str
    patterns: List[TransitionPattern]  # "After X, user usually asks Y"
    active_hours: Dict[int, float]     # Probability by hour
    
# Persistent project goals
class ProjectGoal:
    project_id: str
    goals: List[GoalEntry]
    blocking_on: List[str]            # Cross-project blockers
```

---

## Orchestrator Decision Points

### 1. Agent Selection

**Question:** Which agent should handle this task?

**Memory Consultation:**
```python
def select_agent(task: Task, memory: Memory) -> Agent:
    # Declarative: What do we know about this task type?
    task_context = memory.declarative.recall(task.context)
    
    # Predictive: Which agent is most competent?
    agent_competencies = memory.predictive.get_agent_competencies(task.type)
    
    # Procedural: What strategies work for this task type?
    applicable_strategies = memory.procedural.recall(task.query)
    
    # Select based on competence + strategy availability
    best_agent = rank_agents(
        agents=available_agents,
        competencies=agent_competencies,
        strategies=applicable_strategies,
        context=task_context
    )
    
    return best_agent
```

### 2. Context Injection

**Question:** What context should the selected agent receive?

**Memory Consultation:**
```python
def prepare_context(task: Task, agent: Agent, memory: Memory) -> Context:
    context = Context()
    
    # Declarative: User preferences and project facts
    context.user_preferences = memory.declarative.recall(
        query="user preferences",
        bank="opinion"
    )
    context.project_facts = memory.declarative.recall(
        query=task.project_id,
        bank="world"
    )
    
    # Procedural: Applicable strategies
    context.strategies = memory.procedural.recall(
        query=task.description,
        domain=agent.domain
    )
    
    # Predictive: Goal context (what's the bigger picture?)
    context.active_goals = memory.predictive.get_relevant_goals(task)
    
    return context
```

### 3. Post-Task Learning

**Question:** What should HAIOS learn from this interaction?

**Memory Updates:**
```python
def post_task_learning(
    task: Task, 
    agent: Agent, 
    outcome: Outcome,
    memory: Memory
):
    # Declarative: Record the experience
    memory.declarative.retain(
        bank="experience",
        text=f"Agent {agent.type} completed {task.type}: {outcome.summary}",
        entities=[task.project_id, agent.id]
    )
    
    # Declarative: Update beliefs if outcome reveals new info
    if outcome.reveals_preferences:
        memory.declarative.update_opinion(
            topic=outcome.preference_topic,
            evidence=outcome.evidence,
            direction="reinforce" if outcome.confirmed else "weaken"
        )
    
    # Procedural: Extract strategies from trajectory
    memory.procedural.extract(
        trajectory=outcome.trajectory,
        success=outcome.succeeded,
        failure_reason=outcome.failure_reason if not outcome.succeeded else None
    )
    
    # Predictive: Update agent competence
    memory.predictive.update_competence(
        agent=agent,
        task_type=task.type,
        success=outcome.succeeded
    )
    
    # Predictive: Update goal progress
    if task.goal_id:
        memory.predictive.update_goal_progress(
            goal_id=task.goal_id,
            progress_delta=outcome.goal_progress
        )
```

### 4. Proactive Suggestions

**Question:** What should HAIOS proactively suggest?

**Memory Consultation:**
```python
def generate_proactive_suggestions(user_id: str, memory: Memory) -> List[Suggestion]:
    suggestions = []
    
    # Predictive: Check for goals nearing deadline
    urgent_goals = memory.predictive.get_urgent_goals(user_id)
    for goal in urgent_goals:
        suggestions.append(Suggestion(
            type="deadline_reminder",
            content=f"Goal '{goal.goal_state}' is due in {goal.days_until_deadline():.0f} days",
            priority=goal.urgency_score()
        ))
    
    # Predictive: Check for blocked goals with resolutions
    blocked_goals = memory.predictive.get_blocked_goals(user_id)
    for goal in blocked_goals:
        # Check if blocker can now be resolved
        for blocker in goal.blocking_on:
            if memory.declarative.has_knowledge(blocker):
                suggestions.append(Suggestion(
                    type="blocker_resolved",
                    content=f"Blocker '{blocker}' for goal '{goal.goal_state}' may be resolvable",
                    priority=goal.priority.value
                ))
    
    # Declarative + Predictive: Anticipate based on patterns
    predicted_needs = memory.predictive.predict_user_needs(user_id)
    for need in predicted_needs:
        if need.confidence > 0.7:
            suggestions.append(Suggestion(
                type="anticipated_need",
                content=need.description,
                priority=need.confidence
            ))
    
    return sorted(suggestions, key=lambda s: s.priority, reverse=True)
```

---

## Multi-Agent Memory Sharing

### Shared vs. Agent-Specific Memory

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MEMORY SCOPE HIERARCHY                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   GLOBAL SHARED                                                         │
│   ═════════════                                                         │
│   • User preferences (all agents should respect)                       │
│   • Project facts (shared context)                                     │
│   • Goal network (orchestrator-level)                                  │
│   • World model (environment dynamics)                                 │
│                                                                         │
│   DOMAIN SHARED                                                         │
│   ═════════════                                                         │
│   • Domain strategies (e.g., "Salesforce" strategies)                  │
│   • Domain entities (e.g., Salesforce objects)                         │
│   • Domain competencies (which agents handle which domains)            │
│                                                                         │
│   AGENT-SPECIFIC                                                        │
│   ══════════════                                                        │
│   • Agent strategies (how THIS agent does things)                      │
│   • Agent competencies (THIS agent's strengths/weaknesses)             │
│   • Agent failure modes (THIS agent's known issues)                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Memory Conflict Resolution

When agents have conflicting beliefs or strategies:

```python
def resolve_memory_conflict(
    memories: List[MemoryItem], 
    conflict_type: str
) -> MemoryItem:
    
    if conflict_type == "belief":
        # Use confidence-weighted resolution
        weighted = [(m, m.confidence) for m in memories]
        return max(weighted, key=lambda x: x[1])[0]
    
    elif conflict_type == "strategy":
        # Use success-rate-weighted resolution
        weighted = [(m, m.success_rate() or 0.5) for m in memories]
        return max(weighted, key=lambda x: x[1])[0]
    
    elif conflict_type == "fact":
        # Most recent wins (with recency weighting)
        return max(memories, key=lambda m: m.mention_time)
```

---

## Implementation Priorities

### Phase 1: Declarative Foundation
1. Implement user preference storage (Opinion network)
2. Implement project fact storage (World network)
3. Implement interaction logging (Experience network)
4. Build basic retrieval with embedding similarity

### Phase 2: Procedural Layer
1. Add trajectory logging
2. Implement success/failure extraction
3. Build strategy retrieval for agent context injection
4. Add failure lesson application

### Phase 3: Predictive Layer
1. Add agent competence tracking
2. Implement goal network for persistent tasks
3. Build user behavior prediction
4. Add proactive suggestion generation

### Phase 4: Full Integration
1. Cross-paradigm query routing
2. Multi-agent memory sharing
3. Conflict resolution
4. Closed-loop learning validation

---

## Success Metrics for HAIOS

| Metric | Target | Measurement |
|--------|--------|-------------|
| User preference consistency | >95% | Same response to preference-sensitive queries |
| Agent selection accuracy | >85% | Right agent chosen first try |
| Strategy transfer success | >70% | Strategies help on new tasks |
| Goal completion rate | >80% | Persistent goals eventually completed |
| Proactive suggestion relevance | >60% | Users act on suggestions |
| Error repetition rate | <5% | Same error made twice |
| Context retrieval latency | <200ms | Time to assemble agent context |

---

## Open Questions for HAIOS Implementation

1. **Memory persistence**: File-based, SQLite, or PostgreSQL?
2. **Embedding model**: OpenAI, Gemini, or local?
3. **User data isolation**: How to separate multi-user deployments?
4. **Memory limits**: Maximum items per paradigm?
5. **Forgetting policy**: When/how to prune old memories?
6. **Human oversight**: How to expose memory for user inspection/correction?

---

*Architecture sketch for HAIOS integration, December 2024*
*Status: Requires validation against HAIOS implementation details*
