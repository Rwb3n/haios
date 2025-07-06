# Rhiza Agent Implementation Blueprint v2

## Overview

This is the refined blueprint for the Rhiza Scientific Research Mining Agent, incorporating lessons learned from initial implementation attempts and architectural feedback. This version emphasizes **iterative development**, **clear separation of concerns**, and **pragmatic simplicity over premature complexity**.

## Key Principles (v2)

1. **Start Simple, Iterate**: Build a working MVP first, then harden
2. **Clear Phase Separation**: Each phase has ONE job, does it well
3. **No Premature Security**: Functionality first, security in Stage 3
4. **Leverage Modern Tools**: Use Claude Code and existing infrastructure
5. **Evidence-Based Progress**: Each stage produces verifiable outputs

## Three-Phase Architecture (Clarified)

```
┌─────────────────────────────────────────────────────────────────┐
│                    RHIZA SYSTEM - SIMPLIFIED                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Phase 1: Strategic Triage                                        │
│  ┌─────────────────┐                                            │
│  │ Input: Research │──────▶ "What topics matter to HAiOS?"      │
│  │ Categories      │        (High-level themes only)             │
│  └─────────────────┘                                            │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────────────┐                                    │
│  │ Research Priorities      │                                    │
│  │ - Topic relevance scores │                                    │
│  │ - Strategic alignment    │                                    │
│  └─────────────────────────┘                                    │
│                                                                   │
│  Phase 2: Tactical Ingestion                                      │
│  ┌─────────────────┐                                            │
│  │ Input: Topic +  │──────▶ "Which papers in this topic?"       │
│  │ Paper List      │        (Deterministic categorization)       │
│  └─────────────────┘                                            │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────────────┐                                    │
│  │ Triage Report           │                                    │
│  │ - Tier 1: Must read     │                                    │
│  │ - Tier 2: Interesting   │                                    │
│  │ - Tier 3: Low relevance │                                    │
│  └─────────────────────────┘                                    │
│                                                                   │
│  Phase 3: Crystal Seed Extraction                                 │
│  ┌─────────────────┐                                            │
│  │ Input: Tier 1   │──────▶ "What can we learn from this?"      │
│  │ Paper           │        (Deep analysis & extraction)         │
│  └─────────────────┘                                            │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────────────┐                                    │
│  │ Crystal Seed Proposal   │                                    │
│  │ - Key concepts          │                                    │
│  │ - HAiOS applications    │                                    │
│  │ - Actionable insights   │                                    │
│  └─────────────────────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Stages (Lean & Iterative)

### Stage 1: MVP - Just Make It Work (Current Focus)

**Goal**: Prove data can flow through all three phases

#### Tasks:

1. **Fix Phase 1 Adapter** (Immediate)
   ```python
   # phase1_strategic_triage_v2.py
   # ONLY does: arXiv search → topic analysis → priorities report
   # NO deterministic routing, NO deep analysis
   ```

2. **Create Minimal Phase 2** (Next)
   ```python
   # phase2_tactical_ingestion.py
   # ONLY does: paper list → keyword matching → tier assignment
   # Simple rules, no LLM needed initially
   ```

3. **Create Minimal Phase 3** (Then)
   ```python
   # phase3_crystal_seed.py
   # ONLY does: paper content → concept extraction → proposal
   # Can use mock LLM for testing
   ```

4. **Simple n8n Workflow**
   ```yaml
   Workflow: Rhiza_MVP_Linear
   1. Manual Trigger (paper ID input)
   2. Execute Phase 1 (if needed)
   3. Execute Phase 2
   4. Execute Phase 3
   5. Save results to NocoDB
   ```

#### Success Criteria:
- Can process ONE paper from arXiv to crystal seed
- All data saved in NocoDB
- No crashes, basic error handling

### Stage 2: Workflow Hardening

**Goal**: Make it robust and scalable

#### Enhancements:
1. **Two-Queue Architecture**
   - Ingestion queue for new papers
   - Processing queue for analysis tasks

2. **arXiv Polling**
   ```python
   # poll_arxiv_new.py
   # Checks for new papers every N hours
   # Adds to ingestion queue
   ```

3. **Idempotency**
   - Check if paper already processed
   - Skip duplicate work
   - Update existing records

4. **Better n8n Workflows**
   - Separate workflows per phase
   - Error handling nodes
   - Retry logic

### Stage 3: Security Hardening (Future)

**Goal**: Production-ready security

#### Security Features:
1. **Integrity Hashing**
   - SHA-256 for all artifacts
   - Chain of evidence

2. **Builder/Validator Separation**
   - Separate processes
   - Cannot self-validate

3. **Resource Limits**
   - Memory caps
   - Timeout enforcement
   - Rate limiting

4. **Audit Trail**
   - All actions logged
   - Cryptographic signatures
   - Immutable records

### Stage 4: Integration & Polish

**Goal**: Full HAiOS integration

#### Final Features:
1. **Connect to HAiOS Core**
   - ADR update proposals
   - Architecture impact analysis

2. **UI Dashboard**
   - Review crystal seeds
   - Approve/reject proposals

3. **Advanced Analytics**
   - Trend detection
   - Citation analysis
   - Impact scoring

## Database Schema (Unchanged - Already Good)

The existing schema from v1 is well-designed and remains unchanged:
- `raw_research_artifacts`
- `concept_extraction_reports`
- `research_priorities`
- `triage_reports`

## Code Structure (Simplified)

```
agents/rhiza_agent/
├── adapters/
│   ├── phase1_strategic_triage_v2.py  # Refactored, focused
│   ├── phase2_tactical_ingestion.py   # New, simple
│   ├── phase3_crystal_seed.py         # New, simple
│   └── poll_arxiv_new.py              # Stage 2
├── tests/
│   ├── test_phase1.py
│   ├── test_phase2.py
│   └── test_phase3.py
├── database/                           # Stage 2
│   ├── models.py
│   └── queries.py
└── README.md                          # Setup instructions
```

## Key Corrections from v1

### What We're NOT Doing (Yet):
- ❌ Complex security architecture
- ❌ Cryptographic signatures everywhere
- ❌ Deterministic routers as separate components
- ❌ Loading entire ADR canon at runtime
- ❌ Monolithic prompts doing everything

### What We ARE Doing:
- ✅ One job per phase
- ✅ Simple keyword matching before LLM analysis
- ✅ Context provided by framework, not self-loaded
- ✅ Testable, modular components
- ✅ Iterative improvement

## Adapter Specifications (Minimal MVP)

### Phase 1: Strategic Triage (v2)
```python
class StrategicTriageAgent:
    """
    ONLY identifies high-priority research topics.
    Does NOT categorize papers or do deep analysis.
    """
    
    def analyze_research_landscape(self, categories: List[str]) -> Dict:
        # 1. Fetch recent papers from arXiv
        papers = self._fetch_recent_papers(categories)
        
        # 2. Ask LLM: "What themes are relevant to HAiOS?"
        # (Context about HAiOS provided by framework)
        priorities = self._identify_themes(papers)
        
        # 3. Save and return priorities
        return {
            "topics": priorities,
            "paper_count": len(papers),
            "timestamp": datetime.now()
        }
```

### Phase 2: Tactical Ingestion (NEW)
```python
class TacticalIngestionAgent:
    """
    Categorizes papers into tiers using simple rules.
    No LLM needed for MVP - just keyword matching.
    """
    
    def triage_papers(self, topic: str, papers: List[Dict]) -> Dict:
        tier_1, tier_2, tier_3 = [], [], []
        
        for paper in papers:
            relevance = self._calculate_relevance(paper, topic)
            
            if relevance > 0.8:
                tier_1.append(paper)
            elif relevance > 0.5:
                tier_2.append(paper)
            else:
                tier_3.append(paper)
        
        return {
            "topic": topic,
            "tier_1_papers": tier_1,
            "tier_2_papers": tier_2,
            "tier_3_papers": tier_3
        }
    
    def _calculate_relevance(self, paper: Dict, topic: str) -> float:
        # Simple keyword matching for MVP
        # Can enhance with LLM in Stage 2
        score = 0.0
        keywords = self._get_topic_keywords(topic)
        
        text = f"{paper['title']} {paper['abstract']}".lower()
        for keyword in keywords:
            if keyword in text:
                score += 0.2
        
        return min(score, 1.0)
```

### Phase 3: Crystal Seed Extraction (NEW)
```python
class CrystalSeedExtractor:
    """
    Extracts actionable insights from Tier 1 papers.
    This is where deep LLM analysis happens.
    """
    
    def extract_crystal_seed(self, paper: Dict) -> Dict:
        # 1. Get full paper content (if available)
        content = self._fetch_full_content(paper)
        
        # 2. Extract key concepts
        concepts = self._extract_concepts(content)
        
        # 3. Map to HAiOS applications
        applications = self._identify_applications(concepts)
        
        # 4. Generate proposal
        return {
            "paper_id": paper['id'],
            "concepts": concepts,
            "applications": applications,
            "proposal": self._generate_proposal(concepts, applications)
        }
```

## n8n Workflow (MVP)

```yaml
Workflow: Rhiza_MVP_Test
Nodes:
  1. Manual Trigger:
     - Input: categories (default: ["cs.AI", "cs.DC"])
     
  2. Execute Phase 1:
     - Command: python phase1_strategic_triage_v2.py
     - Args: --categories {{ $json.categories }}
     
  3. Parse Results:
     - Extract top topic from Phase 1 output
     
  4. Execute Phase 2:
     - Command: python phase2_tactical_ingestion.py
     - Args: --topic {{ $json.topic }}
     
  5. Get First Tier 1 Paper:
     - Extract paper_id from Phase 2 output
     
  6. Execute Phase 3:
     - Command: python phase3_crystal_seed.py
     - Args: --paper_id {{ $json.paper_id }}
     
  7. Save to NocoDB:
     - Table: concept_extraction_reports
     - Data: {{ $json.crystal_seed }}
```

## Testing Strategy (Simple)

### Unit Tests (Stage 1)
```python
# test_phase1.py
def test_fetch_papers():
    # Mock arXiv API
    # Assert correct parsing

def test_theme_identification():
    # Mock LLM response
    # Assert priorities extracted

# test_phase2.py
def test_keyword_matching():
    # Test relevance calculation
    # Assert correct tier assignment

# test_phase3.py
def test_concept_extraction():
    # Mock paper content
    # Assert concepts found
```

### Integration Test (Stage 1)
```bash
# Simple bash script
python phase1_strategic_triage_v2.py --categories cs.AI > phase1_out.json
python phase2_tactical_ingestion.py --topic "transformer architectures" > phase2_out.json
python phase3_crystal_seed.py --paper_id "2301.00001" > phase3_out.json

# Check outputs exist and are valid JSON
```

## Environment Setup (Minimal)

```bash
# .env
NOCODB_API_URL=http://localhost:8081/api/v1
NOCODB_API_TOKEN=your_token_here

# Optional for now
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here
```

## Success Metrics (Stage 1 MVP)

- [ ] Phase 1 returns research priorities
- [ ] Phase 2 categorizes papers into tiers
- [ ] Phase 3 extracts at least one concept
- [ ] Data persists in NocoDB
- [ ] No import errors
- [ ] Basic error handling works

## Migration Path from v1

1. **Rename current adapter**: `phase1_strategic_triage.py` → `phase1_strategic_triage_old.py`
2. **Create v2 adapter**: Strip out categorization logic, focus on theme identification
3. **Extract Phase 2 logic**: Take categorization code and create new `phase2_tactical_ingestion.py`
4. **Build Phase 3 fresh**: New file with simple concept extraction

## Key Decisions

1. **No complex routing**: Phases called in sequence for MVP
2. **Keyword matching first**: Simple rules before LLM analysis
3. **Mock LLM option**: Can test without API keys
4. **One paper test**: Prove concept with single paper flow
5. **Defer optimization**: Get working first, optimize later

## Next Immediate Actions

1. [ ] Refactor Phase 1 adapter per feedback
2. [ ] Create simple Phase 2 adapter
3. [ ] Create simple Phase 3 adapter
4. [ ] Build linear n8n workflow
5. [ ] Test with one arXiv paper
6. [ ] Document what works/fails

---

*This blueprint v2 represents a pragmatic, iterative approach to building Rhiza. It prioritizes working software over comprehensive documentation, simple solutions over complex architectures, and learning through building over planning in abstract.*