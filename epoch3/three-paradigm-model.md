# Three-Paradigm Model for Agent Memory

## Overview

This document presents a unified framework for understanding agent memory systems, synthesizing insights from recent research and proposing a complete cognitive architecture.

**Related Documents:**
- Detailed specifications: `foresight-spec.md`, `integration-patterns.md`
- Schema definitions: `schemas/hindsight-schemas.md`, `schemas/reasoningbank-schemas.md`, `schemas/foresight-schemas.md`, `schemas/unified-memory.md`
- Literature analysis: `literature/hindsight-analysis.md`, `literature/reasoningbank-analysis.md`

---

## The Three Paradigms

Modern AI agents require three complementary memory systems that mirror distinctions in cognitive science:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     THREE-PARADIGM MODEL                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   DECLARATIVE              PROCEDURAL              PREDICTIVE           │
│   (HINDSIGHT-style)        (ReasoningBank-style)   (FORESIGHT-proposed) │
│                                                                         │
│   ┌─────────────┐          ┌─────────────┐         ┌─────────────┐     │
│   │   Facts     │          │   Skills    │         │ World Model │     │
│   │   Beliefs   │          │  Strategies │         │ Self Model  │     │
│   │   Entities  │          │   Lessons   │         │ Goal Network│     │
│   └─────────────┘          └─────────────┘         └─────────────┘     │
│                                                                         │
│   "What is true?"          "What works?"           "What will happen?" │
│                                                                         │
│   Past-oriented            Past→Future             Future-oriented      │
│                            transfer                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Paradigm 1: Declarative Memory

### Function
Stores factual knowledge, beliefs, and entity states. Answers "What does the agent know?"

### Characteristics
- **Epistemic clarity**: Distinguishes observed facts from inferred beliefs
- **Entity-centric**: Organizes knowledge around entities and relationships
- **Temporal awareness**: Tracks when things happened vs. when discussed
- **Confidence tracking**: Beliefs have strength that evolves with evidence

### Exemplar System: HINDSIGHT

| Network | Content | Example |
|---------|---------|---------|
| World (W) | Objective external facts | "Paris is France's capital" |
| Experience (B) | Agent's own actions | "I helped debug the code" |
| Opinion (O) | Beliefs with confidence | "User prefers concise style" (0.8) |
| Observation (S) | Entity summaries | "User is a software engineer" |

### Failure Modes Without This Paradigm
- Forgetting user preferences across sessions
- Mixing up entities (calling user by wrong name)
- Treating inferences as facts
- Inability to track what has changed over time

---

## Paradigm 2: Procedural Memory

### Function
Stores skills, strategies, and lessons learned. Answers "What should the agent do?"

### Characteristics
- **Abstraction**: Extracts generalizable patterns from specific experiences
- **Failure-aware**: Learns from both successful and failed attempts
- **Transferable**: Strategies apply across similar but not identical tasks
- **Evolving**: Progresses from procedural to compositional strategies

### Exemplar System: ReasoningBank

| Component | Content | Example |
|-----------|---------|---------|
| Title | Strategy identifier | "Navigation Strategy" |
| Description | One-sentence summary | "When searching paginated data..." |
| Content | Actionable guidance | "1. Detect pagination mode; 2. Examine all items; 3. Use fallbacks..." |

### Strategy Evolution (Emergent)

```
Level 1: Procedural     → "Click 'Next Page' links"
Level 2: Self-Check     → "Re-verify element identifiers"
Level 3: Adaptive       → "Use search/filters, ensure completeness"
Level 4: Compositional  → "Cross-reference with task requirements"
```

### Failure Modes Without This Paradigm
- Repeating same mistakes across tasks
- Not improving with experience
- Rediscovering already-learned strategies
- Inefficient exploration of solution space

---

## Paradigm 3: Predictive Memory (Proposed)

### Function
Models future states, agent capabilities, and goal structures. Answers "What will happen if...?"

### Characteristics
- **Generative**: Can simulate outcomes before committing to actions
- **Self-aware**: Tracks own competencies and failure modes
- **Goal-directed**: Maintains persistent intentions across sessions
- **Calibrated**: Knows what it doesn't know

### Proposed Components

| Component | Content | Example |
|-----------|---------|---------|
| World Model | Environment dynamics | "Clicking X leads to state Y" |
| Self Model | Competence estimates | "Reliable at Python, unreliable at legal" |
| Goal Network | Persistent intentions | "Complete project by deadline" |
| Metamemory | Retrieval confidence | "I might have info on this topic" |

### Failure Modes Without This Paradigm
- Purely reactive (no anticipation)
- Overconfident or underconfident predictions
- No persistent goals across sessions
- Cannot estimate resource requirements
- Doesn't know when to ask for help

---

## Paradigm Interactions

The three paradigms form a closed loop:

```
                              PREDICTIVE
                           (World + Self Model)
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             │             ▼
              Simulates           │       Models own
              outcomes            │       competence
                    │             │             │
                    │             │             │
        ┌───────────┴─────────────┴─────────────┴───────────┐
        │                                                   │
        ▼                                                   ▼
   DECLARATIVE ◄──────────────────────────────────────► PROCEDURAL
   (Facts/Beliefs)         Grounds              (Skills/Strategies)
        │                predictions                  │
        │                in facts                     │
        │                                             │
        │         Strategies informed                 │
        │         by factual knowledge                │
        │                                             │
        └──────────────────┬──────────────────────────┘
                           │
                           ▼
                      PREDICTIVE
                   (Model update from
                    observed outcomes)
```

### Information Flows

| From | To | Flow Content |
|------|-----|-------------|
| Declarative → Procedural | Facts constrain applicable strategies |
| Procedural → Declarative | Successful strategies become known patterns |
| Declarative → Predictive | Facts ground world model predictions |
| Predictive → Declarative | Predictions become beliefs when validated |
| Procedural → Predictive | Skill success rates feed self-model |
| Predictive → Procedural | Competence estimates guide strategy selection |

---

## Gap Analysis

### What HINDSIGHT Provides
- ✓ Epistemic separation (W, B, O, S networks)
- ✓ Entity resolution and linking
- ✓ Bi-temporal modeling
- ✓ Opinion evolution with confidence
- ✗ No skill/procedure learning
- ✗ No failure analysis
- ✗ No future modeling

### What ReasoningBank Provides
- ✓ Strategy abstraction and transfer
- ✓ Failure learning (unique contribution)
- ✓ Memory-scaling synergy (MaTTS)
- ✓ Emergent strategy complexity
- ✗ No fact/belief distinction
- ✗ No entity modeling
- ✗ No future modeling

### What Neither Provides (FORESIGHT Gap)
- ✗ World model for outcome simulation
- ✗ Self-model for competence tracking
- ✗ Goal network for persistent intentions
- ✗ Metamemory for knowing what you know
- ✗ Proactive gap detection

---

## Design Principles

### Principle 1: Structural Epistemic Separation
Don't mix facts, beliefs, and summaries in the same store. Use different networks or clearly typed records.

### Principle 2: Explicit Failure Learning
Design memory systems to handle failed trajectories, not just successful ones.

### Principle 3: Multi-Modal Retrieval
No single retrieval method dominates. Combine vector, keyword, graph, and temporal.

### Principle 4: Confidence Evolution
Beliefs should strengthen or weaken based on evidence, not remain static.

### Principle 5: Future-Oriented Modeling
Agents need to simulate outcomes before acting, not just react to inputs.

### Principle 6: Calibrated Uncertainty
Agents should know what they don't know and track retrieval confidence.

---

## Implementation Roadmap

### Phase 1: Declarative Foundation
Implement HINDSIGHT-style four-network memory with entity resolution.

**Deliverables:**
- World/Experience/Opinion/Observation networks
- Entity resolution pipeline
- Multi-modal retrieval with RRF
- Opinion evolution rules

### Phase 2: Procedural Layer
Add ReasoningBank-style strategy memory with failure learning.

**Deliverables:**
- Memory item schema (title/description/content)
- Success/failure trajectory processing
- Strategy extraction prompts
- Embedding-based retrieval

### Phase 3: Predictive Layer
Implement FORESIGHT world/self/goal models.

**Deliverables:**
- World model transition patterns
- Self-model competence tracking
- Goal network with subgoals and triggers
- Metamemory confidence estimates

### Phase 4: Integration
Connect all three paradigms with proper information flows.

**Deliverables:**
- Cross-paradigm query routing
- Prediction grounding in facts
- Strategy selection based on competence
- Closed-loop learning from outcomes

---

## Success Metrics

| Paradigm | Metric | Target |
|----------|--------|--------|
| Declarative | Fact retrieval accuracy | >90% on LongMemEval |
| Declarative | Entity resolution precision | >95% |
| Procedural | Task success rate improvement | >10% vs no-memory |
| Procedural | Step efficiency gain | >15% fewer steps |
| Predictive | Prediction calibration | <10% Brier score |
| Predictive | Goal completion rate | >80% of persistent goals |
| Integrated | Cross-session consistency | <5% contradiction rate |

---

## Open Research Questions

1. **Optimal abstraction level**: How abstract should procedural memories be?
2. **Consolidation strategies**: When to merge, prune, or forget memories?
3. **Cross-domain transfer**: Do memories help across different task types?
4. **Negative transfer**: Can accumulated memories hurt performance?
5. **Human interpretability**: Should memory items be human-readable?
6. **Computational scaling**: How to handle millions of memory items?
7. **Multi-agent memory**: How to share memories across agent instances?

---

*Framework synthesized from HINDSIGHT (arXiv:2512.12818) and ReasoningBank (arXiv:2509.25140), December 2024*
