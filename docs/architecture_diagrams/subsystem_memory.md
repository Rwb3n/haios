# Subsystem: Cognitive Memory Engine

```text
┌─────────────────────────────────────────────────────────────┐
│                  COGNITIVE MEMORY ENGINE                    │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   EXTRACTION LAYER                  │   │
│   │                                                     │   │
│   │ ┌────────────────┐              ┌─────────────────┐ │   │
│   │ │  LangExtract   │              │  ReasoningBank  │ │   │
│   │ │ (Entity &      │              │ (Strategy/Trace │ │   │
│   │ │  Concept data) │              │  extraction)    │ │   │
│   │ └───────┬────────┘              └────────┬────────┘ │   │
│   └─────────┼────────────────────────────────┼──────────┘   │
│             │                                │              │
│             v                                v              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                    STORAGE LAYER                    │   │
│   │                                                     │   │
│   │        haios_memory.db (SQLite w/ Embeddings)       │   │
│   │   • 9,000+ Entities                                 │   │
│   │   • 81,000+ Concepts (Episteme, Techne, Doxa)       │   │
│   │   • Reasoning Traces (Strategies)                   │   │
│   └─────────────────────────┬───────────────────────────┘   │
│                             │                               │
│                             v                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  MAINTENANCE LAYER                  │   │
│   │                                                     │   │
│   │ ┌────────────────┐              ┌─────────────────┐ │   │
│   │ │  Synthesis Hub │              │  Cross-Pollinate│ │   │
│   │ │ (Cluster sim-  │              │ (Inject traces  │ │   │
│   │ │  ilar concepts)│              │  into Prompts)  │ │   │
│   │ └────────────────┘              └─────────────────┘ │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Description
The **Cognitive Memory Engine** is the heart of HAIOS's cross-session persistence:
- **Extraction Layer**: Translates unstructured chat/document data into structured records using `google/langextract` methods and parses experiential success/failure out of reasoning blocks via `ReasoningBank` architectures.
- **Storage Layer**: A local SQLite database supporting Vector embeddings for semantic retrieval. Applies the Episteme (Truth), Techne (Skill), Doxa (Opinion) ontological taxonomy.
- **Maintenance Layer**: Cleans the database by clustering redundant nodes (Synthesis Hub) and proactively feeding identified effective strategies back into the agent context (Cross-Pollination/Prompt Injection).
