# generated: 2025-11-27
# System Auto: last updated on: 2025-11-27 23:50:01
# HAIOS Agent Principles & Architecture

> **Navigation:** [README](README.md) | [CLAUDE.md](CLAUDE.md) | [GEMINI.md](GEMINI.md) | [ADMIN.md](ADMIN.md) | [Strategic Overview](docs/epistemic_state.md) | [Vision Anchor](docs/VISION_ANCHOR.md)

---

## Quick Reference

| Principle | Summary |
|-----------|---------|
| **Evidence-Based** | Actions proven by verifiable artifacts |
| **Durable Context** | Knowledge lives within artifacts, not conversations |
| **Separation of Duties** | Creation vs validation by different agents |
| **Structured Mistrust** | Assume predictable failure modes |
| **Precision Context** | Load only what's needed, when needed |

---

## Architecture & Critical Patterns

### Core Principles (The Three Pillars)
1. **Evidence-Based Development**: Actions are only complete when proven by separate, verifiable artifacts
2. **Durable, Co-located Context**: Critical knowledge lives directly within artifacts via EmbeddedAnnotationBlocks
3. **Separation of Duties**: Different agent personas handle creation vs validation to prevent conflicts of interest

### Operational Philosophy
- **Evidence over Declaration**: Never trust claims without verifiable proof
- **Structured Mistrust**: Assume agents will fail in predictable ways
- **Theory of Constraints**: Human attention is the bottleneck - optimize for it
- **Precision Context Loading**: Give agents only what they need, when they need it
- **Immutable Canon**: Once hardened, architectural decisions cannot regress

### Distributed Systems Requirements (ADRs 023-029)
- **Idempotency**: All state-changing operations MUST be idempotent
- **Asynchronous messaging** for phase transitions
- **Zero-Trust security** for agent communication
- **Vector clocks** for event ordering
- **Partition tolerance** with split-brain handling

### File Operations
- Use atomic operations for concurrent access safety
- JSON schemas validate all artifacts
- EmbeddedAnnotationBlock for self-describing data

---

## Key Documentation

> **Progressive Disclosure:** Start with Quick Reference, then Strategic Overview, then Detailed Docs

| Level | Document | Purpose |
|-------|----------|---------|
| 1 | [README.md](README.md) | Project overview, quick start |
| 2 | [docs/epistemic_state.md](docs/epistemic_state.md) | Strategic state, knowns/unknowns |
| 3 | [docs/VISION_ANCHOR.md](docs/VISION_ANCHOR.md) | Architectural vision (ReasoningBank + LangExtract) |
| 4 | [docs/specs/TRD-ETL-v2.md](docs/specs/TRD-ETL-v2.md) | Technical requirements |
| 5 | [docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md](docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md) | Full system specification |

### Agent Personas
- [CLAUDE.md](CLAUDE.md) - Builder/Executor (implementation)
- [GEMINI.md](GEMINI.md) - Architect/Planner (design)
- [ADMIN.md](ADMIN.md) - Administrator (operations)

### Schema Definitions
- `docs/schema/` - JSON schemas for all data structures
- All artifacts must pass schema validation

### Key Architectural Evolutions
- **Phase 1 (ADRs 001-020)**: Established deterministic kernel
- **Phase 2 (ADRs 021-032)**: Added distributed systems reality
- **Phase 3 (ADRs 033-039)**: Governance engine with Plan Validation Gateway

---

## Development Standards

### Code Requirements
- Comprehensive error scenario testing
- Distributed failure scenario coverage
- Structured logging with trace_id
- Reference ADR numbers in commits
- JSON-schema validation for all data

### Agent Patterns
1. **2A System (Architect Dialogue)**: Evaluator-optimizer pattern with feedback loops
2. **Rhiza Agent**: Three-phase research mining (Strategic Triage -> Tactical Ingestion -> Crystal Seed Extraction)
3. **Plan Validation Gateway**: Semantic, economic, and behavioral linting
4. **Argus Protocol**: Real-time monitoring and safety enforcement

---

## Project Structure
```
haios/
├── haios_etl/     # ETL pipeline implementation
├── tests/         # Test suite (48 tests)
├── docs/          # Documentation
│   ├── specs/     # Technical specifications
│   ├── checkpoints/ # Session snapshots
│   └── plans/     # Implementation plans
├── scripts/       # Utility scripts
└── HAIOS-RAW/     # Source corpus (625 files)
```

---

## Implementation Notes

### Critical Lessons from Development
- The cost of the construct-validate-fail-remediate loop is high
- Early quality control (CRITIQUE phase) is essential
- Test pyramid completion is critical for trust
- Idempotency must be built in from the start
- Use atomic I/O operations with file locking
- Path sandboxing for security
- Topological sort for plan dependencies

### Economic Model
HAIOS serves as a **Vertical Model Context Protocol (MCP) Foundry**:
- Creates high-value, domain-specific MCP servers
- Does NOT compete with foundation models or CLI agents
- Value proposition is in handling regulatory compliance, security, and domain complexity
- Designed to be provider-agnostic and leverage best-in-class execution agents

### Integration Points
- **Claude Code**: Validates durable context approach, serves as primary builder/executor

---

**See also:** [CLAUDE.md](CLAUDE.md) for implementation | [GEMINI.md](GEMINI.md) for architecture | [ADMIN.md](ADMIN.md) for operations

*Last Updated: 2025-11-27*
