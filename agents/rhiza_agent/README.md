# Rhiza Research Mining Agent

A three-phase system for automated research discovery and analysis, designed to mine academic papers for insights relevant to HAiOS architecture evolution.

## Current Architecture: v3 Claude-as-a-Service

We've pivoted to a Claude-as-a-Service architecture that provides:
- Automatic HAiOS context loading from CLAUDE.md
- Centralized LLM governance
- Simplified adapter code
- Mock support for testing

**Architecture**: `Python Adapter → MCP Client → Claude Server → Anthropic API`

## Quick Start

### Testing with Mock LLM (No API Key Required)
```bash
# Test the complete pipeline
./test/test_v3_complete.sh

# Test individual phases
python3 adapters/phase1_strategic_triage_v3.py  # Strategic triage (v3)
python3 adapters/phase2_tactical_ingestion_v3.py   # Tactical ingestion (v3)
python3 adapters/phase3_crystal_seed_v3.py         # Crystal seed extraction (v3)
```

### Deploy with Docker (Requires API Key)
```bash
# Start all services including Claude server
docker compose --profile rhiza-v3 up -d

# Import n8n workflow
# 1. Open http://localhost:5678
# 2. Import n8n_workflows/rhiza_mvp_linear.json
# 3. Configure execution paths
```

## Project Structure

```
rhiza_agent/
├── adapters/               # Phase implementations
│   ├── mcp_client.py      # Claude MCP client
│   ├── phase1_*.py        # Strategic triage (3 versions)
│   ├── phase2_*.py        # Tactical ingestion
│   ├── phase3_*.py        # Crystal seed extraction
│   └── archive/           # Old adapter versions
├── claude-server/          # Claude MCP server Docker setup
├── n8n_workflows/          # Workflow automation
├── reports/                # Generated outputs (organized by phase)
│   ├── phase1_priorities/ # Strategic triage results
│   ├── phase2_triage/     # Paper categorization results
│   └── phase3_crystal_seeds/ # Crystal seed proposals
├── test/                   # Test suites and scripts
├── archive/                # Old/deprecated files
├── CHANGELOG.md           # Development history
├── rhiza_blueprint_v3.md  # Current architecture
└── rhiza_agent_status.md  # Project status
```

## Three-Phase Pipeline

### Phase 1: Strategic Triage
- Fetches papers from arXiv by category
- Identifies high-priority research themes using LLM
- Outputs: Priority themes with relevance scores

### Phase 2: Tactical Ingestion  
- Analyzes papers against priority themes
- Categorizes into Tier 1/2/3 by relevance
- Uses deterministic keyword matching

### Phase 3: Crystal Seed Extraction
- Deep analysis of Tier 1 papers
- Extracts actionable concepts
- Proposes integration strategies

## Development Status

- **MVP**: ✅ Complete and validated
- **v3 Architecture**: 🚧 Phase 1 complete, Phases 2-3 pending
- **Production**: ❌ Needs credentials, monitoring, security

See `rhiza_agent_status.md` for detailed progress.

## Key Documents

- `rhiza_blueprint_v3.md` - Claude-as-a-Service architecture
- `CHANGELOG.md` - Complete development timeline
- `rhiza_agent_status.md` - Current status and next steps

## Environment Variables

```bash
# For real LLM usage
export ANTHROPIC_API_KEY="your-key"
export USE_MOCK_LLM=false

# For NocoDB integration
export NOCODB_API_TOKEN="your-token"
export NOCODB_BASE_URL="http://localhost:8081"
```

## Next Steps

1. Complete v3 adapter refactoring
2. Test NocoDB integration
3. Deploy n8n workflow
4. Add monitoring and logging