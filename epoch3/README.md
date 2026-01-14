# Agent Memory Architecture

## A Unified Framework for Cognitive Agent Memory Systems

This corpus documents a three-paradigm model for agent memory, synthesizing insights from recent research (HINDSIGHT, ReasoningBank) and proposing a novel predictive layer (FORESIGHT) to close the cognitive loop.

---

## Core Thesis

Modern AI agents require three complementary memory systems:

| Paradigm | Function | Question Answered | Temporal Focus |
|----------|----------|-------------------|----------------|
| **Declarative** (HINDSIGHT-style) | What does the agent know/believe? | "What is true?" | Past-oriented |
| **Procedural** (ReasoningBank-style) | What should the agent do? | "What works?" | Past→Future transfer |
| **Predictive** (FORESIGHT - proposed) | What will happen if...? | "What will occur?" | Future-oriented |

No single paradigm suffices. Declarative memory without procedural guidance produces knowledgeable but ineffective agents. Procedural memory without world models produces reactive but not anticipatory agents. The three paradigms form a closed loop enabling genuine self-improvement.

---

## Corpus Structure

```
/agent-memory-architecture/
│
├── README.md                         # This file
│
├── /literature/
│   ├── hindsight-analysis.md         # HINDSIGHT paper breakdown
│   └── reasoningbank-analysis.md     # ReasoningBank paper breakdown
│
├── /architecture/
│   ├── three-paradigm-model.md       # Unified framework specification
│   ├── foresight-spec.md             # Novel predictive layer proposal
│   ├── integration-patterns.md       # Composition and data flow
│   └── v1.1-enhancements.md          # Phase 2 optimizations (Strategy Compressor, FoK Regressor)
│
├── /schemas/
│   ├── hindsight-schemas.md          # Data structures from HINDSIGHT
│   ├── reasoningbank-schemas.md      # Data structures from ReasoningBank
│   ├── foresight-schemas.md          # Proposed predictive schemas
│   └── unified-memory.md             # Integration layer types
│
└── /haios-integration/
    └── memory-layer-mapping.md       # Application to HAIOS orchestrator
```

---

## Key Contributions

### From Literature Analysis
- Systematic comparison of declarative vs. procedural memory approaches
- Identification of failure learning as critical gap in most systems
- Understanding of memory-scaling synergies (MaTTS)

### Novel Proposals
- **FORESIGHT**: Predictive self-modeling layer with world models, self-models, goal networks, and metamemory
- **Metamemory**: The capacity to know what the agent knows (retrieval confidence, source monitoring)
- **Three-paradigm integration architecture**: Closed-loop design enabling genuine agent self-evolution
- **Bayesian Competence Calibration**: Beta distribution priors solving the "cold start" problem for self-model accuracy estimates

### Phase 2 Enhancements (v1.1)
- **Strategy Compressor**: DBSCAN clustering + LLM abstraction for procedural memory consolidation
- **FoK Regressor**: Lightweight classifier for fast-path routing (skip memory when unlikely to help)

---

## Source Documents

| Paper | Authors | Key Contribution |
|-------|---------|------------------|
| HINDSIGHT | Vectorize.io (arXiv:2512.12818) | Four-network epistemic memory with opinion evolution |
| ReasoningBank | Google Cloud AI Research (arXiv:2509.25140) | Procedural memory with failure learning + MaTTS |

---

## Reading Order

**For conceptual understanding:**
1. `architecture/three-paradigm-model.md` - The unified framework
2. `architecture/foresight-spec.md` - The novel proposal
3. `architecture/integration-patterns.md` - How they compose

**For implementation reference:**
1. `schemas/` directory - Data structure specifications
2. `haios-integration/memory-layer-mapping.md` - Practical application

**For academic context:**
1. `literature/hindsight-analysis.md`
2. `literature/reasoningbank-analysis.md`

---

## Status

| Document | Status | Notes |
|----------|--------|-------|
| Literature analyses | Complete | Based on full paper review |
| Three-paradigm model | Complete | Synthesis framework |
| FORESIGHT spec | Complete | Includes Bayesian calibration |
| Schemas (paradigm-specific) | Complete | Ready for implementation |
| Schemas (unified-memory) | Complete | Integration layer types |
| Integration patterns | Complete | Cross-paradigm flows |
| v1.1 Enhancements | Specified | Strategy Compressor, FoK Regressor |
| HAIOS integration | Sketch | Requires architecture alignment |

---

## License and Attribution

This corpus synthesizes published research with original analysis. Source papers retain their original licenses. Novel proposals (FORESIGHT, integration patterns) are original work.

---

*Generated: December 2024*
*Context: HAIOS Agent Orchestration Architecture Development*
