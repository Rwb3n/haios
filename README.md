# generated: 2025-11-30
# System Auto: last updated on: 2026-01-14T20:28:18
```

        ██╗  ██╗ █████╗ ██╗ ██████╗ ███████╗
        ██║  ██║██╔══██╗██║██╔═══██╗██╔════╝
        ███████║███████║██║██║   ██║███████╗
        ██╔══██║██╔══██║██║██║   ██║╚════██║
        ██║  ██║██║  ██║██║╚██████╔╝███████║
        ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝

   ╔══════════════════════════════════════════════════════════════════════╗
   ║  ░▒▓█ HYBRID AI OPERATING SYSTEM █▓▒░                                ║
   ║                                                                      ║
   ║     "Where silicon dreams meet carbon intuition"                     ║
   ║                                                                      ║
   ║  ┌─────────────────────────────────────────────────────────────┐     ║
   ║  │  ◈ COGNITIVE MEMORY ENGINE                    [ONLINE]      │    ║
   ║  │  ◈ TRUST RATCHET                             [ENGAGED]      │    ║
   ║  │  ◈ REASONINGBANK                             [VERIFIED]     │    ║
   ║  │  ◈ KNOWLEDGE REFINEMENT                      [COMPLETE]     │    ║
   ║  │  ◈ MEMORY SYNTHESIS                          [OPERATIONAL]  │    ║
   ║  │  ◈ MCP INTERFACE                             [ONLINE]       │    ║
   ║  └─────────────────────────────────────────────────────────────┘     ║
   ║                                                                      ║
   ║     ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄       ║
   ║     █ EPOCH 2.2 ─── SCHEMA v3 ─── 190 SESSIONS ─── ACTIVE █       ║
   ║     ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀       ║
   ║                                                                      ║
   ╚══════════════════════════════════════════════════════════════════════╝

            ┌──────────────┐                    ┌──────────────┐
            │   EXTRACT    │───── neural ─────▶│   REASON     │
            │   ◇◆◇◆◇◆  │      pathways     │   ◆◇◆◇◆◇  │
            └──────────────┘                    └──────────────┘
                   │                                   │
                   │          ┌──────────────┐         │
                   └────────▶│   REMEMBER   │◀────────┘
                              │   ▓▓▓▓▓▓▓▓   │
                              │   ░░░░░░░░   │
                              └──────────────┘
                                     │
                              ╔══════╧══════╗
                              ║  TRUST  ▲   ║
                              ║  ENGINE ║   ║
                              ╚═════════════╝

   ─────────────────────────────────────────────────────────────────────────
```

# HAIOS: A Trust Engine for AI Agents

> **H**ybrid **AI** **O**perating **S**ystem

## What is this?

HAIOS is an experimental **governance and memory system for AI agents**, built as a Claude Code plugin. It explores how to make AI assistants more reliable through:

- **Persistent Memory** - Knowledge that compounds across sessions (81k+ concepts stored)
- **Governance Hooks** - Enforcement points that guide agent behavior
- **Work Item Tracking** - Structured workflows with audit trails
- **Layered Architecture** - Immutable principles (L0-L3) guiding dynamic execution (L4+)

This is a personal research project exploring AI agent reliability, context management, and human-AI collaboration patterns. It's opinionated, evolving, and very much a work in progress.

> **For Claude Code users:** The `.claude/` directory contains the plugin infrastructure - hooks, skills, commands, and agents that extend Claude Code's capabilities.

---

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (requires Google Gemini API Key)
# Create .env file with: GOOGLE_API_KEY=your_key_here
```

### 2. Run ETL Pipeline
Process the raw corpus to build the memory database:
```bash
python -m haios_etl.cli process HAIOS-RAW
```

### 3. Check Status
View system statistics and processing health:
```bash
python -m haios_etl.cli status
```

---

## Documentation Navigation

**Progressive Disclosure** - Start at the top, dive deeper as needed.

| Priority | Document | Purpose |
|----------|----------|---------|
| **CRITICAL** | **[Vision Interpretation](docs/vision/2025-11-30-VISION-INTERPRETATION-SESSION.md)** | **MANDATORY FIRST READ.** Canonical vision definition. |
| **0** | **[You Are Here]** | High-level overview and quick start. |
| **1** | **[Strategic Map](docs/README.md)** | Documentation map, cold start guide. |
| **2** | **[Epistemic State](docs/epistemic_state.md)** | Current system state, knowns, unknowns. |
| **3** | **[Technical Specs](docs/specs/TRD-ETL-v2.md)** | Deep dive into system requirements and design. |
| **4** | **[Operations](docs/OPERATIONS.md)** | Runbooks for maintaining and troubleshooting the system. |
| **Code**| **[ETL Package](haios_etl/README.md)** | Technical documentation for the `haios_etl` Python package. |

---

## Architecture Overview

HAIOS operates in five implemented phases:

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 3 | **ETL** | COMPLETE | Extract entities/concepts from docs via Gemini LLM |
| 4 | **ReasoningBank** | COMPLETE | Strategy extraction + experience learning (loop CLOSED) |
| 5 | **Scale** | COMPLETE | MCP integration, WAL optimization, 116.93 req/s |
| 6 | **Governance Suite** | OPERATIONAL | Hooks, Commands, Templates, PM Directory |
| 8 | **Knowledge Layer** | COMPLETE | Greek Triad taxonomy, metadata tables |
| 9 | **Memory Synthesis** | OPERATIONAL | Cluster + synthesize + cross-pollinate |
| E2 | **Epoch 2** | ACTIVE | File lifecycle governance, staleness awareness |

### System Statistics (as of Session 190)
```
Sessions:         190 (since October 2025)
Entities:         9,000+ extracted
Concepts:         81,000+ stored
Hooks:            4 active (PreToolUse, PostToolUse, UserPromptSubmit, Stop)
Skills:           18 (cycles, bridges, utilities)
Agents:           7 subagents
Commands:         18 slash commands
MCP Tools:        13 exposed
Schema:           v3 (SQLite with embeddings)
```

### Key Features
- **Cognitive Memory Engine** - Structured knowledge extraction from unstructured docs
- **Trust Ratchet** - One-way progression from ambiguity to verified truth
- **Knowledge Refinement** - Greek Triad taxonomy (Episteme/Techne/Doxa) classification
- **ReasoningBank** - Strategy extraction + experience learning (per Google Research paper)
- **Memory Synthesis** - Cluster similar memories, extract meta-patterns, cross-pollinate
- **MCP Interface** - Ready for Claude Desktop and agent ecosystem integration

---

## Navigation

| Destination | Purpose |
|-------------|---------|
| [Vision Interpretation](docs/vision/2025-11-30-VISION-INTERPRETATION-SESSION.md) | **MANDATORY** - Canonical vision definition |
| [Strategic Overview](docs/epistemic_state.md) | Current system state, knowns, unknowns |
| [Quick Reference](docs/README.md) | Documentation map, cold start guide |
| [Vision Anchor](docs/VISION_ANCHOR.md) | Technical architecture (ReasoningBank + LangExtract) |
| [MCP Integration](docs/MCP_INTEGRATION.md) | Connect to agent ecosystem |
| [Operations Manual](docs/OPERATIONS.md) | ETL and synthesis runbook |
| [Investigation Handoff](docs/handoff/2025-11-30-INVESTIGATION-HANDOFF-vision-gap-analysis.md) | Gap analysis mission |
| [ETL Package](haios_etl/README.md) | Module documentation |
| [Test Suite](tests/README.md) | 154 tests passing |
| [Anti-Patterns](docs/anti-patterns/) | Known failure modes to avoid |

---

## The Vision (Summary)

```
HAIOS exists to make the OPERATOR successful.

- Spaces    = Domains where operator wants to succeed
- Memory    = Engine that enables transformation AND tracks outcomes
- Epochs    = Refactoring cycles (RAW -> EPOCH2 -> EPOCH3 -> ...)
- Success   = Operator achieves real-world goals (not system metrics)
- Feedback  = Evidence from operator outcomes drives epoch transitions
```

**Key Insight:** System metrics (concepts extracted, query latency) are irrelevant. Only OPERATOR SUCCESS matters.

---

**Status:** Epoch 2.2 - The Refinement (Active)
**Last Updated:** 2026-01-14 (Session 190)
