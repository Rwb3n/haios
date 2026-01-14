# generated: 2025-11-27
# System Auto: last updated on: 2025-12-01 13:32:52
# Cognitive Memory System - Vision Anchor

> **Progressive Disclosure:** [Quick Reference](README.md) -> [Strategic Overview](epistemic_state.md) -> **Vision (YOU ARE HERE)**
>
> **Navigation:** [Operations](OPERATIONS.md) | [MCP](MCP_INTEGRATION.md) | [Full Spec](COGNITIVE_MEMORY_SYSTEM_SPEC.md)

---

> **IMPORTANT - Canonical Vision:** [Vision Interpretation Session](vision/2025-11-30-VISION-INTERPRETATION-SESSION.md)
> The document above is the **authoritative source** for HAIOS vision (Session 16+). This document (VISION_ANCHOR) describes the technical pillars. Read both.

---

> **Purpose:** This document captures the core architectural vision for the Cognitive Memory System. It should be read by any agent working on this project to understand the WHY behind the implementation.

> **Cold Start:** READ THIS DOCUMENT to understand the architectural foundation before implementing.

---

## The Two Pillars

The Cognitive Memory System is built on two Google research innovations:

### 1. LangExtract: Structured Knowledge Extraction

**Paper/Library:** [google/langextract](https://github.com/google/langextract)

**What it does:**
- Extracts structured information from unstructured text using LLMs
- Uses few-shot examples to define extraction schemas
- Maps every extraction to its exact source location (source grounding)
- Output format: `{extraction_class, extraction_text, attributes}`

**Our usage:** `haios_etl/extraction.py`
- Extracts entities: User, Agent, ADR, Filepath, AntiPattern
- Extracts concepts: Directive, Critique, Proposal, Decision
- Uses Gemini 2.5 Flash Lite for extraction

### 2. ReasoningBank: Experience-Based Learning

**Paper:** [ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory](https://arxiv.org/abs/2509.25140) (Google Research, Sept 2025)

**What it does:**
- Stores **learned strategies**, not execution logs
- Memory item structure: `{title, description, content}`
- Learns from BOTH successes AND failures
- LLM extracts "what made this work?" or "what to avoid?"
- Retrieves relevant strategies at inference time
- Injects strategies into system prompt for decision guidance

**Results:** +34% retrieval success, -16% tool interactions

---

## The Vision: How They Work Together

```
                    ┌─────────────────────────────────┐
                    │        User Query               │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │     ReasoningBank Lookup        │
                    │  "Have we tried this before?"   │
                    │  → Retrieve learned strategies  │
                    │  → Inject into system prompt    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │       Execute with Guidance     │
                    │  → LangExtract for extraction   │
                    │  → Memory search for retrieval  │
                    │  → Apply learned strategies     │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │      Strategy Extraction        │
                    │  LLM asks:                      │
                    │  Success: "Why did this work?"  │
                    │  Failure: "What to avoid?"      │
                    │  → Stores {title,desc,content}  │
                    └─────────────────────────────────┘
```

---

## Current Implementation Gap

| Aspect | Vision (Paper) | Current Reality |
|--------|----------------|-----------------|
| **Extraction** | LangExtract with learning | LangExtract works, no learning |
| **Memory Content** | `{title, description, content}` | `{query, approach, outcome}` |
| **What's Stored** | Learned strategies | Execution metadata |
| **Success Processing** | LLM extracts generalizable strategy | Records `outcome='success'` only |
| **Failure Processing** | LLM extracts preventive lesson | Records `outcome='failure'` only |
| **Prompt Injection** | Strategies injected into prompt | Returns metadata in response |
| **Retrieval** | Top-k, no threshold | Top-10 with 0.8 threshold |

**Root Cause:** We store WHAT HAPPENED, not WHAT WE LEARNED.

---

## The Fix: Align with Paper Architecture

### Step 1: Add Strategy Extraction

After each operation, use LLM to extract:

**For Success:**
```
Analyze this successful task:
Query: {query}
Approach: {approach}
Results: {results_summary}

Extract a transferable reasoning strategy.
Output: {title, description, content}
```

**For Failure:**
```
Analyze this failed task:
Query: {query}
Approach: {approach}
Error: {outcome_details}

Extract a preventive lesson.
Output: {title, description, content}
```

### Step 2: Store Strategies, Not Logs

New columns for `reasoning_traces`:
```sql
ALTER TABLE reasoning_traces ADD COLUMN strategy_title TEXT;
ALTER TABLE reasoning_traces ADD COLUMN strategy_description TEXT;
ALTER TABLE reasoning_traces ADD COLUMN strategy_content TEXT;
```

### Step 3: Inject into Prompts

When retrieving past experience, format for system prompt:
```python
relevant_strategies = [
    f"Strategy: {s['title']}\n{s['content']}"
    for s in past_attempts[:3]
]
```

### Step 4: Switch to Top-K

Paper uses top-k (k=1 default), not similarity threshold.
Let the LLM decide relevance, not a hardcoded 0.8 cutoff.

---

## Anti-Pattern Warning

> "All agents have suffered the anti-pattern of incentive to complete rather than question their actions as part of the system."

This means:
1. **Don't rush to implement** - understand the vision first
2. **Question assumptions** - is this the right approach?
3. **Preserve context** - future sessions need this knowledge
4. **Ask when uncertain** - operator feedback > guessing

---

## Context Persistence Strategy

To maintain this vision across context windows:

1. **This document** - `docs/VISION_ANCHOR.md` - core concepts
2. **CLAUDE.md** - add reference to this file in Key References
3. **Checkpoints** - session summaries reference this
4. **Plan files** - link back to this vision

---

## Key Files (Updated)

| File | Purpose | Vision Alignment |
|------|---------|------------------|
| `haios_etl/extraction.py` | LangExtract integration | ALIGNED (extraction works) |
| `haios_etl/retrieval.py` | ReasoningBank traces | GAP (stores metadata, not strategies) |
| `haios_etl/mcp_server.py` | MCP tools | GAP (2/12 tools, no prompt injection) |
| `docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md` | Full vision | Reference (aspirational) |
| `docs/specs/TRD-ETL-v2.md` | ETL implementation | Subset (MVP scope) |

---

## Sources

- [ReasoningBank Paper](https://arxiv.org/abs/2509.25140)
- [LangExtract GitHub](https://github.com/google/langextract)
- [MarkTechPost Analysis](https://www.marktechpost.com/2025/10/01/google-ai-proposes-reasoningbank-a-strategy-level-i-agent-memory-framework-that-makes-llm-agents-self-evolve-at-test-time/)

---

**Document Version:** 1.0
**Created:** 2025-11-27
**Status:** Reference - Read on cold start
