# Rhiza Agent: Scientific Research Mining System

## Purpose
Transform low-trust AI research outputs → high-trust architectural insights for HAIOS evolution.

## Core Loop
```
SCAN(landscape) → TRIAGE(relevance) → EXTRACT(insights) → VALIDATE(evidence)
```

## Quick Start
```bash
# Prerequisites: Docker services running (n8n, NocoDB)
cd agents/rhiza_agent

# Install dependencies
pip install -r requirements.txt

# Run deterministic router test
python deterministic_router.py

# Execute builder/validator pattern demo
python builder_validator_pattern.py
```

## Architecture Patterns

### 1. Three-Phase Protocol
```yaml
Phase_1_Strategic_Triage:
  input: research_categories[]
  process: compare_against_canon()
  output: priority_topics_ranked[]

Phase_2_Tactical_Ingestion:
  input: selected_topic
  process: categorize_papers(tier_1|2|3)
  output: triage_report{relevance_tiers}

Phase_3_Crystal_Seed_Extraction:
  input: tier_1_paper
  process: deep_analysis() → map_to_haios()
  output: crystal_seed_proposal{concepts, impacts}
```

### 2. Security Model
```
Builder ≠ Validator  # Separation of duties
Router = Rules_Only  # No LLM decisions
Evidence = SHA256    # Cryptographic proof
Sandbox = Enforced   # Resource isolation
```

### 3. Data Flow
```
arXiv → [BUILDER] → artifact{signature} → [VALIDATOR] → report{verified}
         ↓                                   ↓
         sandbox_A                          sandbox_B
         (external_access)                  (internal_only)
```

## Component Map

### Core Systems
- `deterministic_router.py` - Rule-based workflow selection
- `builder_validator_pattern.py` - Separation of duties enforcement
- `security_sandbox_config.yaml` - Agent isolation rules

### Legacy Reference
- `legacy/adapters/` - Original implementations (not security-compliant)

### Schemas (Data Contracts)
- `schemas/research_evidence_schema.json` - Evidence artifact structure

### Documentation
- `RHIZA_BLUEPRINT.md` - Full implementation guide
- `THIRD_PARTY_EVALUATION.md` - Security analysis of patterns

## Key Invariants

1. **No Self-Validation**: Builder_ID ≠ Validator_ID
2. **Deterministic Routing**: scope → workflow (no LLM)
3. **Evidence Chain**: Every step hashed & signed
4. **Immutable Artifacts**: `_locked: true`

## Agent Configuration

### Builder Agent
```yaml
role: BUILDER
permissions: [read_external, write_artifacts]
sandbox:
  memory: 512MB
  timeout: 300s
  network: [arxiv.org, localhost:8080]
forbidden: [validate_own_work, access_validator_code]
```

### Validator Agent  
```yaml
role: VALIDATOR
permissions: [read_artifacts, write_validations]
sandbox:
  memory: 256MB
  timeout: 120s
  network: [localhost:8080]  # NocoDB only
forbidden: [create_artifacts, external_network]
```

## Workflow Patterns

### Chain (Sequential)
```python
SINGLE_PAPER: fetch → extract → analyze → artifact
```

### Parallel (Concurrent)
```python
TOPIC_SURVEY: fetch_many → parallel(analyze[]) → aggregate
```

### Triage (Routing)
```python
STRATEGIC_SCAN: scan → categorize{t1,t2,t3} → route_by_tier
```

## Database Tables

### raw_research_artifacts
Primary storage for ingested papers with cryptographic integrity.
```sql
artifact_id (PK) | paper_id | content | evidence_chain[] | signature
```

### concept_extraction_reports
Validated insights from crystal seed extraction.
```sql
report_id (PK) | artifact_id (FK) | concepts[] | validator_signature
```

## Error Codes
```
0 = Success
1 = Recoverable (retry)
2 = Security violation (abort)
```

## Integration Points

### n8n Workflows
- `Rhiza_Main_Orchestration` - Phase routing
- `Rhiza_Ingestion_Pipeline` - Paper processing

### NocoDB Access
```python
NOCODB_API_URL = "http://nocodb:8080/api/v1"
# Tables: raw_research_artifacts, concept_extraction_reports
```

## Monitoring Metrics
- `agent_execution_time{agent_type, action}`
- `validation_failures{failure_type}`
- `security_violations{violation_type}`

## Development Workflow

1. **Modify Core Logic**: Edit phase implementations
2. **Update Schemas**: Maintain in `schemas/`
3. **Test Locally**: Use pattern demo scripts
4. **Deploy to n8n**: Import workflow JSONs
5. **Monitor**: Check Grafana dashboards

## Security Checklist
- [ ] Builder/Validator IDs different?
- [ ] Evidence chain complete?
- [ ] Signatures valid?
- [ ] Sandbox limits enforced?
- [ ] No LLM routing?

## Common Patterns

### Adding New Source
```python
1. Create adapter in adapters/
2. Add to deterministic router rules
3. Update evidence schema if needed
4. Test with builder/validator pattern
```

### Debugging Failed Validation
```python
1. Check validation_report.issues[]
2. Verify evidence_chain integrity
3. Confirm builder permissions
4. Review audit logs with trace_id
```

## Future AI Agent Instructions

When extending Rhiza:
1. **Maintain invariants** - Never allow self-validation
2. **Use deterministic routing** - Add rules, not LLM calls
3. **Generate evidence** - Every decision needs proof
4. **Respect sandboxes** - Security > convenience
5. **Follow patterns** - Chain/Parallel/Triage only

## References
- ADR-OS-041: Rhiza Protocol specification
- HAIOS Trust Engine principles
- Distributed systems requirements (ADRs 023-029)