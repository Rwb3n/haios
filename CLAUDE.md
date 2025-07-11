# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HAIOS (Hybrid AI Operating System) is a **Trust Engine** that transforms low-trust AI agent outputs into high-trust, verifiable artifacts. It operates as an orchestration layer managing multiple AI agents through a structured five-phase lifecycle: ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE.

The system implements a "Certainty Ratchet" architecture - a one-way mechanism that only allows movement from ambiguity toward verified truth. HAIOS positions itself as the "Admiralty" commanding fleets of commodity AI agents, focusing on governance, planning, and synthesis rather than direct task execution.

### MCP Server Configuration
The project includes MCP (Model Context Protocol) servers for enhanced Claude Code integration:
- **Filesystem Server**: Full access to the HAIOS project directory
- **Memory Server**: Knowledge graph for context persistence
- **SQLite Server**: Direct access to NocoDB and Langflow databases
- **Playwright Server**: Browser automation capabilities

Configure MCP servers:
```bash
./mcp-config.sh setup     # Add all HAIOS MCP servers
./mcp-config.sh remove    # Remove HAIOS MCP servers
./mcp-config.sh info      # Show configuration
claude mcp list           # List all configured servers
```

#### SQLite MCP Tool Usage Pattern
**CRITICAL**: SQLite MCP servers (`nocodb-sqlite`, `langflow-sqlite`) cannot be accessed directly by Claude Code. Use this pattern:

```
1. Use Task tool to delegate SQL queries to an agent
2. Agent accesses MCP servers and executes queries
3. Results returned in agent's final report

Example:
Task: "Query nocodb-sqlite to list all tables and show data from ingestion_queue"
```

**Quick Reference - NocoDB Tables**:
- `nc__b20___ingestion_queue` - Research paper processing queue
- `nc__b20___raw_research` - Raw research data storage
- `nc__b20___concept_reports` - Processed concept reports
- Research pipeline: ingestion_queue → raw_research → concept_reports

### Service URLs
- n8n (workflow automation): http://localhost:5678
- NocoDB (no-code database): http://localhost:8081
- Langflow (visual flow builder): http://localhost:7860

### Python Development (agents/rhiza_agent)
```bash
cd agents/rhiza_agent
pip install -r requirements.txt

# Test Rhiza MVP (v3 architecture)
./test_mvp_v3.sh

# Test individual phases
python3 adapters/phase1_strategic_triage_v3.py  # v3 with MCP
python3 adapters/phase2_tactical_ingestion.py   # v2 (v3 pending)
python3 adapters/phase3_crystal_seed.py         # v2 (v3 pending)
```

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

### Error Handling
```python
# Exit codes
0 = Success
1 = Errors (recoverable)
2 = Security violations (non-recoverable)

# All errors must:
- Include trace_id in structured logs
- Output to both structlog AND stderr
- Propagate security exceptions to engine level
```

### File Operations
- Use atomic operations for concurrent access safety
- JSON schemas validate all artifacts
- EmbeddedAnnotationBlock for self-describing data

## Key Documentation

### Must-Read for Contributors
1. `/docs/ADR/` - Architecture Decision Records (especially ADRs 023-029 for distributed systems)
2. `/docs/appendices/` - Core operational guides:
   - Appendix_A: Assumptions & Constraints
   - Appendix_B: Operational Principles & Error Handling
   - Appendix_F: Testing Guidelines (90% coverage target)
   - Appendix_H: CI/CD Policy
3. `/docs/source/Cody_Reports/` - Project evolution and architectural insights

### Schema Definitions
- `/docs/schema/` - JSON schemas for all data structures
- All artifacts must pass schema validation

### Key Architectural Evolutions
- **Phase 1 (ADRs 001-020)**: Established deterministic kernel
- **Phase 2 (ADRs 021-032)**: Added distributed systems reality
- **Phase 3 (ADRs 033-039)**: Governance engine with Plan Validation Gateway

## Development Standards

### Code Requirements
- Comprehensive error scenario testing
- Distributed failure scenario coverage
- Structured logging with trace_id
- Reference ADR numbers in commits
- JSON-schema validation for all data

### Agent System
- Multiple personas: CODING_ASSISTANT, TESTING_VALIDATOR, CRITIQUE_AGENT
- Dynamic registration in agent registry
- Strict role-based permissions
- No self-validation allowed

### Agent Patterns
1. **2A System (Architect Dialogue)**: Evaluator-optimizer pattern with feedback loops
2. **Rhiza Agent**: Three-phase research mining (Strategic Triage → Tactical Ingestion → Crystal Seed Extraction)
   - **v3 Architecture**: Uses Claude-as-a-Service (`Python → MCP Client → Claude Server → Anthropic API`)
   - Automatic CLAUDE.md context loading via claude-server
   - See `/agents/rhiza_agent/rhiza_blueprint_v3.md` for details
3. **Plan Validation Gateway**: Semantic, economic, and behavioral linting
4. **Argus Protocol**: Real-time monitoring and safety enforcement

## Project Structure
```
haios/
├── _legacy/        # Historical Python engine implementation
├── agents/         # Agent configurations and implementations
├── data/          # Docker volume data (gitignored)
├── docs/          # Comprehensive documentation
│   ├── ADR/       # Architecture Decision Records
│   ├── schema/    # JSON schema definitions
│   └── appendices/# Core operational guides
└── rawdata/       # Research artifacts
```

## Important Implementation Notes

### Critical Lessons from v3.1 Engine Development
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
- **n8n**: Workflow orchestration layer
- **NocoDB**: State management and persistence
- **Langflow**: Agent intelligence configuration

### Development Priorities
1. Integrate Claude Code as primary builder/executor agent
2. Implement the 2A System for clarification processing
3. Build Rhiza agent for automated research mining
4. Develop first Vertical MCP server as proof of concept