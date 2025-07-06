# Rhiza Agent Implementation Blueprint

## Overview

This blueprint provides a comprehensive, actionable plan to implement the Rhiza Scientific Research Mining Agent as specified in ADR-OS-041. It bridges the gap between architectural design and working implementation, providing step-by-step guidance for each component.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Security Architecture](#security-architecture)
3. [Database Setup](#database-setup)
4. [Phase 1: Strategic Triage](#phase-1-strategic-triage)
5. [Phase 2: Tactical Ingestion](#phase-2-tactical-ingestion)
6. [Phase 3: Crystal Seed Extraction](#phase-3-crystal-seed-extraction)
7. [n8n Workflow Implementation](#n8n-workflow-implementation)
8. [Integration & Testing](#integration--testing)
9. [Deployment Checklist](#deployment-checklist)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        RHIZA SYSTEM OVERVIEW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐  │
│  │   Trigger   │────▶│ Phase 1:     │────▶│ Research        │  │
│  │   (Manual/  │     │ Strategic    │     │ Priorities      │  │
│  │   Scheduled)│     │ Triage       │     │ Report          │  │
│  └─────────────┘     └──────────────┘     └─────────────────┘  │
│                                                      │           │
│                                                      ▼           │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐  │
│  │   arXiv     │────▶│ Phase 2:     │────▶│ Triage Report   │  │
│  │   API       │     │ Tactical     │     │ (Tier 1/2/3)    │  │
│  │             │     │ Ingestion    │     │                 │  │
│  └─────────────┘     └──────────────┘     └─────────────────┘  │
│                                                      │           │
│                                                      ▼           │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐  │
│  │   Full      │────▶│ Phase 3:     │────▶│ Crystal Seed    │  │
│  │   Paper     │     │ Crystal Seed │     │ Proposal        │  │
│  │   Text      │     │ Extraction   │     │                 │  │
│  └─────────────┘     └──────────────┘     └─────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Data Layer (NocoDB)                     │  │
│  │  • raw_research_artifacts                                  │  │
│  │  • concept_extraction_reports                              │  │
│  │  • research_priorities                                     │  │
│  │  • triage_reports                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Core Security Principles

1. **Separation of Duties**: Builder and Validator agents are strictly separated
2. **Deterministic Routing**: No LLM-based decisions for critical paths
3. **Evidence-Based Trust**: Every claim backed by cryptographic evidence
4. **Sandboxed Execution**: All agents run in restricted environments

### Security Components

#### 1. Deterministic Router
- Rule-based routing system (no LLM involvement)
- Explicit workflow selection based on research scope
- Enforced execution budgets and timeouts
- See: `deterministic_router.py`

#### 2. Builder/Validator Pattern
- **Builder Agents**: Execute research, cannot validate own work
- **Validator Agents**: Verify artifacts, cannot create research
- Cryptographic signatures for non-repudiation
- See: `builder_validator_pattern.py`

#### 3. Evidence Chain
- Every processing step creates evidence entry
- SHA-256 hashes for input/output verification
- Chronological ordering enforcement
- Immutable audit trail

#### 4. Security Sandbox
- Resource limits (CPU, memory, disk, network)
- Filesystem restrictions with allowed/denied paths
- Network domain whitelisting
- Process execution controls
- See: `security_sandbox_config.yaml`

### Security Enforcement

```yaml
Per-Agent Security:
  Builder:
    - Can read external sources (arXiv)
    - Can write to artifact storage
    - Cannot access validation code
    - 512MB memory, 5-minute timeout
    
  Validator:
    - Can read artifacts and schemas
    - Cannot access external network
    - Cannot execute builder code
    - 256MB memory, 2-minute timeout
    
Runtime Monitoring:
  - Real-time resource usage tracking
  - Anomaly detection for suspicious patterns
  - Automatic termination on violations
  - Comprehensive audit logging
```

### Input/Output Validation

1. **Input Sanitization**
   - Schema validation for all requests
   - HTML tag stripping
   - Special character escaping
   - Size limits (10MB input max)

2. **Output Verification**
   - Required fields validation
   - Forbidden content detection
   - Cryptographic signatures
   - Size limits (50MB output max)

## Database Setup

### Step 1: Create NocoDB Tables

Access NocoDB at http://localhost:8081 and create the following tables:

#### Table: `raw_research_artifacts`
```sql
-- Primary identification
artifact_id         VARCHAR(255) PRIMARY KEY
paper_id           VARCHAR(255) UNIQUE NOT NULL
schema_version     VARCHAR(10) DEFAULT '1.0'

-- Source tracking
source_name        VARCHAR(50) NOT NULL
source_url         TEXT NOT NULL
source_pdf_url     TEXT

-- Core metadata
title              TEXT NOT NULL
authors            JSON NOT NULL
abstract           TEXT NOT NULL
categories         JSON NOT NULL

-- Content
full_text          TEXT
extracted_sections JSON

-- System metadata
ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
integrity_hash     VARCHAR(64)
trace_id           VARCHAR(255)
_locked_payload    BOOLEAN DEFAULT TRUE

-- Indexes
INDEX idx_paper_id (paper_id)
INDEX idx_categories (categories)
INDEX idx_ingestion_timestamp (ingestion_timestamp)
```

#### Table: `concept_extraction_reports`
```sql
-- Primary identification
report_id          VARCHAR(255) PRIMARY KEY
source_artifact_id VARCHAR(255) NOT NULL FOREIGN KEY REFERENCES raw_research_artifacts(artifact_id)
schema_version     VARCHAR(10) DEFAULT '1.0'

-- Extraction metadata
extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
extraction_method   VARCHAR(50) NOT NULL
llm_model          VARCHAR(100)

-- Extracted concepts
concepts           JSON NOT NULL
-- Structure: [{
--   concept_id: string,
--   concept_type: "ALGORITHM" | "PROTOCOL" | "ARCHITECTURE" | "PATTERN" | "PRINCIPLE",
--   name: string,
--   description: string,
--   relevance_quote: string,
--   haios_applicability: string,
--   confidence_score: number
-- }]

-- Categorization
primary_category   VARCHAR(50)
keywords          JSON
relevance_tier    INTEGER CHECK (relevance_tier IN (1, 2, 3))

-- HAiOS integration
impacted_adrs     JSON
proposed_actions  JSON

-- System metadata
trace_id          VARCHAR(255)
status            VARCHAR(20) DEFAULT 'pending'

-- Indexes
INDEX idx_source_artifact (source_artifact_id)
INDEX idx_relevance_tier (relevance_tier)
INDEX idx_status (status)
```

#### Table: `research_priorities`
```sql
-- Identification
priority_id        VARCHAR(255) PRIMARY KEY
generation_counter INTEGER NOT NULL
created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- Priority data
topics            JSON NOT NULL
-- Structure: [{
--   topic: string,
--   relevance_score: number,
--   open_questions: [string],
--   impacted_adrs: [string],
--   rationale: string
-- }]

-- Metadata
corpus_source     VARCHAR(255)
analysis_window   VARCHAR(50)
operator_notes    TEXT
```

#### Table: `triage_reports`
```sql
-- Identification
report_id         VARCHAR(255) PRIMARY KEY
topic            VARCHAR(255) NOT NULL
generation_counter INTEGER NOT NULL
created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- Triage results
tier_1_papers    JSON
tier_2_papers    JSON
tier_3_papers    JSON

-- Analysis metadata
total_papers_analyzed INTEGER
analysis_criteria JSON
operator_selection VARCHAR(255)
```

### Step 2: Configure API Access

Create environment variables in `.env`:
```bash
# NocoDB API Configuration
NOCODB_API_URL=http://nocodb:8080/api/v1
NOCODB_API_TOKEN=your_api_token_here
NOCODB_PROJECT_ID=your_project_id
NOCODB_BASE_ID=your_base_id

# LLM Configuration (for analysis phases)
OPENAI_API_KEY=your_openai_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Phase 1: Strategic Triage

### Implementation: `adapters/phase1_strategic_triage.py`

```python
import os
import sys
import json
import httpx
from datetime import datetime
from typing import List, Dict, Any

class StrategicTriageAgent:
    """
    Phase 1: Compares external research topics against HAiOS canon
    to identify high-priority areas for investigation.
    """
    
    def __init__(self):
        self.nocodb_url = os.getenv('NOCODB_API_URL')
        self.nocodb_token = os.getenv('NOCODB_API_TOKEN')
        self.llm_client = self._init_llm_client()
        
    def _init_llm_client(self):
        # Initialize your preferred LLM client
        # Could be OpenAI, Anthropic, or local model
        pass
        
    def load_haios_canon(self) -> Dict[str, Any]:
        """Load current ADRs and open questions from the canon."""
        canon = {
            'adrs': [],
            'open_questions': [],
            'strategic_priorities': []
        }
        
        # In production, this would query NocoDB or read from files
        # For now, we'll use a structured representation
        return canon
        
    def analyze_research_landscape(self, 
                                 corpus_source: str,
                                 categories: List[str]) -> Dict[str, Any]:
        """
        Analyze research corpus against HAiOS needs.
        
        Args:
            corpus_source: e.g., "arxiv"
            categories: e.g., ["cs.AI", "cs.DC", "cs.SE"]
            
        Returns:
            Research priorities ranked by relevance
        """
        canon = self.load_haios_canon()
        
        # Fetch recent papers from each category
        recent_papers = self._fetch_recent_papers(corpus_source, categories)
        
        # Prepare analysis prompt
        prompt = self._build_analysis_prompt(canon, recent_papers)
        
        # Get LLM analysis
        analysis = self._analyze_with_llm(prompt)
        
        # Structure the output
        priorities = self._structure_priorities(analysis)
        
        return priorities
        
    def _fetch_recent_papers(self, source: str, categories: List[str]) -> List[Dict]:
        """Fetch recent paper metadata from source."""
        papers = []
        
        if source == "arxiv":
            for category in categories:
                url = f"http://export.arxiv.org/api/query"
                params = {
                    "search_query": f"cat:{category}",
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                    "max_results": 20
                }
                
                response = httpx.get(url, params=params)
                # Parse and extract paper metadata
                # ... (implementation details)
                
        return papers
        
    def _build_analysis_prompt(self, canon: Dict, papers: List[Dict]) -> str:
        """Build prompt for strategic analysis."""
        prompt = f"""
You are the Strategic Triage component of the Rhiza research mining system for HAiOS.

Your task is to analyze the current research landscape and identify topics 
most relevant to HAiOS's architectural needs.

CURRENT HAIOS CONTEXT:
- Open ADR Questions: {json.dumps(canon['open_questions'], indent=2)}
- Strategic Priorities: {json.dumps(canon['strategic_priorities'], indent=2)}

RECENT RESEARCH PAPERS:
{json.dumps(papers, indent=2)}

ANALYSIS REQUIRED:
1. Identify research topics/themes that directly address open ADR questions
2. Spot emerging patterns that could impact HAiOS architecture
3. Rank topics by relevance (1-10 scale)
4. Provide rationale for each ranking

Output as JSON:
{{
    "priorities": [
        {{
            "topic": "topic name",
            "relevance_score": 8,
            "open_questions": ["ADR question it addresses"],
            "impacted_adrs": ["ADR-OS-XXX"],
            "rationale": "explanation"
        }}
    ]
}}
"""
        return prompt
        
    def save_priorities_report(self, priorities: Dict[str, Any]) -> str:
        """Save priorities to database and return report path."""
        report_id = f"priorities_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save to NocoDB
        # ... (implementation)
        
        # Also save as markdown for human review
        report_path = f"reports/Research_Priorities_{report_id}.md"
        # ... (implementation)
        
        return report_path

# CLI Interface
if __name__ == "__main__":
    agent = StrategicTriageAgent()
    
    # Default to AI/Distributed Systems/Software Engineering
    categories = ["cs.AI", "cs.DC", "cs.SE"]
    
    priorities = agent.analyze_research_landscape("arxiv", categories)
    report_path = agent.save_priorities_report(priorities)
    
    print(json.dumps({
        "status": "success",
        "report_path": report_path,
        "top_priorities": priorities["priorities"][:3]
    }))
```

## Phase 2: Tactical Ingestion

### Enhancement: `adapters/phase2_tactical_ingestion.py`

```python
import os
import sys
import json
from typing import List, Dict, Tuple
from datetime import datetime

class TacticalIngestionAgent:
    """
    Phase 2: Deep dive into specific topic, categorizing papers
    into relevance tiers.
    """
    
    def __init__(self):
        self.nocodb_url = os.getenv('NOCODB_API_URL')
        self.nocodb_token = os.getenv('NOCODB_API_TOKEN')
        self.llm_client = self._init_llm_client()
        
    def ingest_topic(self, topic: str, paper_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze papers for a specific topic and categorize by relevance.
        
        Args:
            topic: Selected high-priority topic from Phase 1
            paper_ids: List of paper IDs to analyze
            
        Returns:
            Triage report with papers sorted into tiers
        """
        # Fetch full paper data
        papers = self._fetch_papers_data(paper_ids)
        
        # Load relevance criteria
        criteria = self._load_relevance_criteria(topic)
        
        # Analyze each paper
        tier_1, tier_2, tier_3 = [], [], []
        
        for paper in papers:
            tier, analysis = self._analyze_paper_relevance(paper, criteria)
            
            paper_summary = {
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "relevance_analysis": analysis
            }
            
            if tier == 1:
                tier_1.append(paper_summary)
            elif tier == 2:
                tier_2.append(paper_summary)
            else:
                tier_3.append(paper_summary)
                
        # Generate triage report
        report = self._generate_triage_report(topic, tier_1, tier_2, tier_3)
        
        return report
        
    def _analyze_paper_relevance(self, 
                               paper: Dict, 
                               criteria: Dict) -> Tuple[int, str]:
        """
        Analyze a single paper against relevance criteria.
        
        Returns:
            (tier_number, analysis_explanation)
        """
        prompt = f"""
Analyze this paper's relevance to HAiOS architecture:

PAPER:
Title: {paper['title']}
Abstract: {paper['abstract']}
Categories: {paper.get('categories', [])}

RELEVANCE CRITERIA:
{json.dumps(criteria, indent=2)}

TIER DEFINITIONS:
- Tier 1: Directly solves current HAiOS problems or answers open ADR questions
- Tier 2: Provides strategic insights for future evolution
- Tier 3: Low relevance, tangential connection

Respond with:
{{
    "tier": 1|2|3,
    "analysis": "explanation of relevance",
    "specific_applications": ["concrete ways this could be used"],
    "impacted_components": ["HAiOS components affected"]
}}
"""
        
        response = self.llm_client.complete(prompt)
        result = json.loads(response)
        
        return result["tier"], result["analysis"]
        
    def _generate_triage_report(self, 
                              topic: str,
                              tier_1: List[Dict],
                              tier_2: List[Dict],
                              tier_3: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive triage report."""
        report = {
            "report_id": f"triage_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "topic": topic,
            "analysis_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_papers": len(tier_1) + len(tier_2) + len(tier_3),
                "tier_1_count": len(tier_1),
                "tier_2_count": len(tier_2),
                "tier_3_count": len(tier_3)
            },
            "tier_1_papers": tier_1,
            "tier_2_papers": tier_2,
            "tier_3_papers": tier_3,
            "recommendations": self._generate_recommendations(tier_1, tier_2)
        }
        
        # Save to database
        self._save_triage_report(report)
        
        # Generate markdown report
        self._generate_markdown_report(report)
        
        return report
```

## Phase 3: Crystal Seed Extraction

### Implementation: `adapters/phase3_crystal_seed.py`

```python
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any

class CrystalSeedExtractor:
    """
    Phase 3: Deep analysis of Tier 1 papers to extract
    actionable "crystal seeds" for HAiOS evolution.
    """
    
    def __init__(self):
        self.nocodb_url = os.getenv('NOCODB_API_URL')
        self.nocodb_token = os.getenv('NOCODB_API_TOKEN')
        self.llm_client = self._init_llm_client()
        
    def extract_crystal_seed(self, paper_id: str) -> Dict[str, Any]:
        """
        Perform deep analysis of a paper to extract crystal seeds.
        
        Args:
            paper_id: ID of Tier 1 paper to analyze
            
        Returns:
            Crystal Seed Proposal with actionable insights
        """
        # Fetch full paper content
        paper = self._fetch_full_paper(paper_id)
        
        # Load HAiOS architectural context
        context = self._load_architectural_context()
        
        # Multi-stage extraction process
        concepts = self._extract_key_concepts(paper)
        patterns = self._identify_patterns(paper, concepts)
        applications = self._map_to_haios(patterns, context)
        
        # Generate crystal seed proposal
        proposal = self._generate_proposal(paper, concepts, patterns, applications)
        
        # Save extraction report
        self._save_extraction_report(proposal)
        
        return proposal
        
    def _extract_key_concepts(self, paper: Dict) -> List[Dict[str, Any]]:
        """Extract key concepts from paper using LLM analysis."""
        prompt = f"""
Analyze this research paper and extract KEY CONCEPTS relevant to distributed systems architecture:

PAPER CONTENT:
{paper['full_text'][:10000]}  # Truncated for context window

EXTRACTION TARGETS:
1. Novel algorithms or protocols
2. Architectural patterns
3. System design principles
4. Performance optimization techniques
5. Security/trust mechanisms

For each concept, provide:
- Name and type (ALGORITHM/PROTOCOL/ARCHITECTURE/PATTERN/PRINCIPLE)
- Clear description
- Direct quote demonstrating the concept
- Potential applications

Output as JSON array of concepts.
"""
        
        response = self.llm_client.complete(prompt)
        concepts = json.loads(response)
        
        # Validate and enrich concepts
        for concept in concepts:
            concept['concept_id'] = hashlib.sha256(
                f"{paper['paper_id']}_{concept['name']}".encode()
            ).hexdigest()[:16]
            concept['source_paper_id'] = paper['paper_id']
            
        return concepts
        
    def _map_to_haios(self, 
                     patterns: List[Dict], 
                     context: Dict) -> List[Dict[str, Any]]:
        """Map extracted patterns to specific HAiOS applications."""
        applications = []
        
        for pattern in patterns:
            prompt = f"""
Given this research pattern, identify SPECIFIC applications to HAiOS:

PATTERN:
{json.dumps(pattern, indent=2)}

HAIOS CONTEXT:
- Core Principles: {context['principles']}
- Current Challenges: {context['open_questions']}
- Architecture Components: {context['components']}

Identify:
1. Which HAiOS components could use this pattern
2. Which ADRs would be impacted
3. Concrete implementation suggestions
4. Expected benefits and risks

Be specific and actionable.
"""
            
            response = self.llm_client.complete(prompt)
            application = json.loads(response)
            application['pattern_id'] = pattern['id']
            
            applications.append(application)
            
        return applications
        
    def _generate_proposal(self,
                         paper: Dict,
                         concepts: List[Dict],
                         patterns: List[Dict],
                         applications: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive Crystal Seed Proposal."""
        proposal = {
            "proposal_id": f"crystal_seed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "source_paper": {
                "paper_id": paper['paper_id'],
                "title": paper['title'],
                "authors": paper['authors'],
                "url": paper['source_url']
            },
            "extraction_metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "extraction_method": "phase3_deep_analysis",
                "llm_model": self.llm_client.model_name
            },
            "core_insights": {
                "summary": self._synthesize_summary(concepts, patterns),
                "key_concepts": concepts,
                "patterns": patterns,
                "haios_applications": applications
            },
            "architectural_impact": {
                "answered_questions": self._identify_answered_questions(applications),
                "revealed_questions": self._identify_new_questions(applications),
                "impacted_adrs": self._collect_impacted_adrs(applications),
                "proposed_changes": self._generate_change_proposals(applications)
            },
            "implementation_priority": self._assess_priority(applications),
            "risk_assessment": self._assess_risks(applications)
        }
        
        return proposal
        
    def _generate_change_proposals(self, 
                                 applications: List[Dict]) -> List[Dict[str, Any]]:
        """Generate specific ADR updates or new components."""
        proposals = []
        
        for app in applications:
            if app.get('requires_adr_update'):
                proposals.append({
                    "type": "ADR_UPDATE",
                    "target": app['impacted_adrs'],
                    "changes": app['suggested_changes'],
                    "rationale": app['rationale']
                })
                
            if app.get('new_component_needed'):
                proposals.append({
                    "type": "NEW_COMPONENT",
                    "name": app['component_name'],
                    "purpose": app['component_purpose'],
                    "integration_points": app['integration_points']
                })
                
        return proposals

# Crystal Seed Proposal Template Generator
def generate_proposal_markdown(proposal: Dict[str, Any]) -> str:
    """Generate human-readable Crystal Seed Proposal."""
    template = f"""
# Crystal Seed Proposal: {proposal['proposal_id']}

## Source Paper
- **Title**: {proposal['source_paper']['title']}
- **Authors**: {', '.join(proposal['source_paper']['authors'])}
- **URL**: {proposal['source_paper']['url']}

## Executive Summary
{proposal['core_insights']['summary']}

## Key Concepts Extracted

{chr(10).join([f"### {c['name']} ({c['concept_type']})\n{c['description']}\n\n**Relevance Quote**: \"{c['relevance_quote']}\"\n" for c in proposal['core_insights']['key_concepts']])}

## HAiOS Applications

{chr(10).join([f"### Application {i+1}: {app['component']}\n{app['description']}\n\n**Expected Benefit**: {app['benefit']}\n" for i, app in enumerate(proposal['core_insights']['haios_applications'])])}

## Architectural Impact

### Answered Questions
{chr(10).join([f"- {q}" for q in proposal['architectural_impact']['answered_questions']])}

### New Questions Revealed
{chr(10).join([f"- {q}" for q in proposal['architectural_impact']['revealed_questions']])}

### Impacted ADRs
{chr(10).join([f"- {adr}" for adr in proposal['architectural_impact']['impacted_adrs']])}

## Proposed Actions

{chr(10).join([f"### {p['type']}\n{p.get('changes', p.get('purpose', ''))}\n\n**Rationale**: {p['rationale']}\n" for p in proposal['architectural_impact']['proposed_changes']])}

## Implementation Priority: {proposal['implementation_priority']}

## Risk Assessment
{proposal['risk_assessment']}

---
Generated: {proposal['extraction_metadata']['extraction_timestamp']}
"""
    return template
```

## n8n Workflow Implementation

### Workflow 1: Main Orchestration Flow

```json
{
  "name": "Rhiza_Main_Orchestration",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "rhiza/trigger",
        "responseMode": "responseNode",
        "options": {}
      },
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "// Determine which phase to execute\nconst phase = $input.item.json.phase;\nconst data = $input.item.json.data;\n\nswitch(phase) {\n  case 'strategic_triage':\n    return {\n      json: {\n        action: 'run_phase1',\n        categories: data.categories || ['cs.AI', 'cs.DC', 'cs.SE']\n      }\n    };\n  \n  case 'tactical_ingestion':\n    return {\n      json: {\n        action: 'run_phase2',\n        topic: data.topic,\n        paper_ids: data.paper_ids\n      }\n    };\n    \n  case 'crystal_seed':\n    return {\n      json: {\n        action: 'run_phase3',\n        paper_id: data.paper_id\n      }\n    };\n    \n  default:\n    throw new Error('Unknown phase: ' + phase);\n}"
      },
      "name": "Route by Phase",
      "type": "n8n-nodes-base.code",
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "leftValue": "={{ $json.action }}",
              "rightValue": "run_phase1",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            }
          ],
          "combinator": "and"
        },
        "options": {}
      },
      "name": "IF Phase 1",
      "type": "n8n-nodes-base.if",
      "position": [650, 200]
    },
    {
      "parameters": {
        "command": "cd /data/agents/rhiza_agent && python adapters/phase1_strategic_triage.py",
        "cwd": "/data"
      },
      "name": "Execute Phase 1",
      "type": "n8n-nodes-base.executeCommand",
      "position": [850, 100]
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [[{"node": "Route by Phase", "type": "main", "index": 0}]]
    },
    "Route by Phase": {
      "main": [[{"node": "IF Phase 1", "type": "main", "index": 0}]]
    },
    "IF Phase 1": {
      "main": [
        [{"node": "Execute Phase 1", "type": "main", "index": 0}],
        [{"node": "IF Phase 2", "type": "main", "index": 0}]
      ]
    }
  }
}
```

### Workflow 2: Ingestion Pipeline (from stage1.md)

```json
{
  "name": "Rhiza_Ingestion_Pipeline",
  "nodes": [
    {
      "parameters": {
        "content": "## Paper Ingestion Request\n\nPaper ID: {{ $json.paper_id }}\nSource: {{ $json.source_name }}",
        "height": 150,
        "width": 200
      },
      "name": "Note",
      "type": "n8n-nodes-base.stickyNote",
      "position": [250, 100]
    },
    {
      "parameters": {
        "operation": "list",
        "resource": "record",
        "projectId": "={{ $env.NOCODB_PROJECT_ID }}",
        "tableId": "raw_research_artifacts",
        "limit": 1,
        "filterType": "parameter",
        "filters": {
          "conditions": [
            {
              "field": "paper_id",
              "condition": "eq",
              "value": "={{ $json.paper_id }}"
            }
          ]
        }
      },
      "name": "Check Exists",
      "type": "n8n-nodes-base.nocodb",
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "loose"
          },
          "conditions": [
            {
              "leftValue": "={{ $json.list ? $json.list.length : 0 }}",
              "rightValue": 0,
              "operator": {
                "type": "number",
                "operation": "equals"
              }
            }
          ],
          "combinator": "and"
        },
        "options": {}
      },
      "name": "IF New",
      "type": "n8n-nodes-base.if",
      "position": [650, 300]
    },
    {
      "parameters": {
        "language": "python",
        "pythonCode": "import subprocess\nimport json\n\n# Execute the extraction adapter\npaper_id = items[0].json['paper_id']\n\nresult = subprocess.run(\n    ['python', '/data/agents/rhiza_agent/adapters/extract_arxiv.py', paper_id],\n    capture_output=True,\n    text=True\n)\n\nif result.returncode != 0:\n    raise Exception(f\"Extraction failed: {result.stderr}\")\n\n# Parse the output\nextracted_data = json.loads(result.stdout)\n\nreturn [{'json': extracted_data}]"
      },
      "name": "Extract Data",
      "type": "n8n-nodes-base.code",
      "position": [850, 200]
    },
    {
      "parameters": {
        "mode": "runOnceForEachItem",
        "jsCode": "// Structure to canonical schema\nconst input = $input.item.json;\nconst crypto = require('crypto');\n\n// Generate artifact_id\nconst artifact_id = 'rra_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);\n\n// Calculate integrity hash\nconst content = JSON.stringify({\n  title: input.metadata.title,\n  authors: input.metadata.authors,\n  abstract: input.metadata.abstract,\n  full_text: input.raw_text_from_pdf\n});\nconst integrity_hash = crypto.createHash('sha256').update(content).digest('hex');\n\n// Build canonical structure\nreturn {\n  json: {\n    artifact_id: artifact_id,\n    paper_id: input.paper_id,\n    schema_version: '1.0',\n    source_name: 'arXiv',\n    source_url: input.source_abs_url,\n    source_pdf_url: input.source_pdf_url,\n    title: input.metadata.title,\n    authors: input.metadata.authors,\n    abstract: input.metadata.abstract,\n    categories: [], // TODO: Extract from paper\n    full_text: input.raw_text_from_pdf,\n    extracted_sections: {}, // TODO: Parse sections\n    integrity_hash: integrity_hash,\n    trace_id: $execution.id,\n    _locked_payload: true\n  }\n};"
      },
      "name": "Structure Data",
      "type": "n8n-nodes-base.code",
      "position": [1050, 200]
    },
    {
      "parameters": {
        "operation": "create",
        "resource": "record",
        "projectId": "={{ $env.NOCODB_PROJECT_ID }}",
        "tableId": "raw_research_artifacts",
        "fieldsUi": {
          "fieldValues": []
        },
        "options": {}
      },
      "name": "Save to DB",
      "type": "n8n-nodes-base.nocodb",
      "position": [1250, 200]
    }
  ]
}
```

## Integration & Testing

### Test Scripts

Create `test/test_rhiza_integration.py`:

```python
import httpx
import json
import time
from typing import Dict, Any

class RhizaIntegrationTest:
    def __init__(self, n8n_url: str = "http://localhost:5678"):
        self.n8n_url = n8n_url
        self.webhook_url = f"{n8n_url}/webhook/rhiza/trigger"
        
    def test_phase1_strategic_triage(self):
        """Test Phase 1: Strategic Triage"""
        print("Testing Phase 1: Strategic Triage...")
        
        payload = {
            "phase": "strategic_triage",
            "data": {
                "categories": ["cs.AI", "cs.DC"]
            }
        }
        
        response = httpx.post(self.webhook_url, json=payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "report_path" in result
        assert "top_priorities" in result
        
        print(f"✓ Phase 1 completed. Report: {result['report_path']}")
        return result
        
    def test_phase2_tactical_ingestion(self, topic: str):
        """Test Phase 2: Tactical Ingestion"""
        print(f"Testing Phase 2: Tactical Ingestion for topic '{topic}'...")
        
        # First, get some paper IDs
        paper_ids = self._get_sample_paper_ids(topic)
        
        payload = {
            "phase": "tactical_ingestion",
            "data": {
                "topic": topic,
                "paper_ids": paper_ids[:10]  # Test with 10 papers
            }
        }
        
        response = httpx.post(self.webhook_url, json=payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "tier_1_papers" in result
        
        print(f"✓ Phase 2 completed. Tier 1 papers: {len(result['tier_1_papers'])}")
        return result
        
    def test_phase3_crystal_seed(self, paper_id: str):
        """Test Phase 3: Crystal Seed Extraction"""
        print(f"Testing Phase 3: Crystal Seed Extraction for paper {paper_id}...")
        
        payload = {
            "phase": "crystal_seed",
            "data": {
                "paper_id": paper_id
            }
        }
        
        response = httpx.post(self.webhook_url, json=payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "proposal_id" in result
        assert "core_insights" in result
        
        print(f"✓ Phase 3 completed. Proposal: {result['proposal_id']}")
        return result
        
    def run_full_pipeline_test(self):
        """Run complete Rhiza pipeline test"""
        print("="*50)
        print("RHIZA INTEGRATION TEST")
        print("="*50)
        
        # Phase 1
        phase1_result = self.test_phase1_strategic_triage()
        time.sleep(2)
        
        # Phase 2 - use top priority topic
        if phase1_result["top_priorities"]:
            topic = phase1_result["top_priorities"][0]["topic"]
            phase2_result = self.test_phase2_tactical_ingestion(topic)
            time.sleep(2)
            
            # Phase 3 - use first Tier 1 paper
            if phase2_result["tier_1_papers"]:
                paper_id = phase2_result["tier_1_papers"][0]["paper_id"]
                phase3_result = self.test_phase3_crystal_seed(paper_id)
                
                print("\n" + "="*50)
                print("ALL TESTS PASSED ✓")
                print("="*50)
            else:
                print("No Tier 1 papers found for Phase 3 test")
        else:
            print("No priorities found for Phase 2 test")

if __name__ == "__main__":
    tester = RhizaIntegrationTest()
    tester.run_full_pipeline_test()
```

## Deployment Checklist

### Prerequisites
- [ ] Docker services running (n8n, NocoDB, Langflow)
- [ ] NocoDB tables created with correct schema
- [ ] Environment variables configured in `.env`
- [ ] Python dependencies installed in `agents/rhiza_agent`

### Implementation Steps

1. **Security Foundation**
   - [ ] Deploy deterministic router (`deterministic_router.py`)
   - [ ] Implement builder/validator pattern (`builder_validator_pattern.py`)
   - [ ] Configure security sandboxes (`security_sandbox_config.yaml`)
   - [ ] Set up evidence artifact schemas
   - [ ] Test separation of duties

2. **Database Setup**
   - [ ] Create all tables in NocoDB
   - [ ] Configure API tokens with minimal permissions
   - [ ] Set up row-level security
   - [ ] Test database connectivity with auth

3. **Phase 1 Implementation (Strategic Triage)**
   - [ ] Deploy `phase1_strategic_triage.py` with deterministic routing
   - [ ] Replace LLM routing with rule-based system
   - [ ] Implement evidence generation for decisions
   - [ ] Test with sample categories
   - [ ] Verify signed report generation

4. **Phase 2 Implementation (Tactical Ingestion)**
   - [ ] Enhance ingestion adapters with security controls
   - [ ] Add input sanitization layer
   - [ ] Implement relevance analysis with audit trail
   - [ ] Generate cryptographically signed triage reports
   - [ ] Test tier categorization with validation

5. **Phase 3 Implementation (Crystal Seed Extraction)**
   - [ ] Deploy `phase3_crystal_seed.py` in sandbox
   - [ ] Configure concept extraction with evidence chain
   - [ ] Implement separate validator for proposals
   - [ ] Test extraction with signature verification
   - [ ] Verify immutable proposal generation

6. **n8n Workflow Setup**
   - [ ] Import main orchestration workflow
   - [ ] Configure deterministic routing nodes
   - [ ] Set up builder/validator separation in workflows
   - [ ] Configure webhook endpoints with auth
   - [ ] Test phase routing with security controls

7. **Security Testing**
   - [ ] Test sandbox isolation between agents
   - [ ] Verify builder cannot validate own work
   - [ ] Test evidence chain integrity
   - [ ] Attempt prompt injection attacks
   - [ ] Verify resource limit enforcement

8. **Integration Testing**
   - [ ] Run individual phase tests with validation
   - [ ] Execute full pipeline with security monitoring
   - [ ] Verify cryptographic signatures
   - [ ] Check evidence chain completeness
   - [ ] Test failure scenarios and recovery

9. **Monitoring & Operations**
   - [ ] Deploy structured logging with trace_id
   - [ ] Configure security alerting rules
   - [ ] Create dashboards for anomaly detection
   - [ ] Set up audit log retention
   - [ ] Document security runbooks

### Success Criteria
- Strategic Triage generates ranked research priorities with evidence
- Tactical Ingestion correctly categorizes papers with audit trail
- Crystal Seed Extraction produces cryptographically signed proposals
- All artifacts pass independent validation
- Builder/Validator separation enforced throughout
- No LLM-based routing decisions
- All data persists with integrity verification
- Security sandboxes prevent unauthorized access
- n8n workflows execute with deterministic routing
- Integration tests pass with security checks
- Zero security violations in monitoring

## Next Steps

1. **Implement Rhiza-Lead Orchestrator**: Create the high-level agent that coordinates the three phases
2. **Add Scheduling**: Implement periodic polling for new research
3. **Build UI Dashboard**: Create interface for reviewing reports and proposals
4. **Integrate with HAiOS Core**: Connect crystal seeds to ADR update process
5. **Scale Testing**: Test with larger paper volumes
6. **Add More Sources**: Extend beyond arXiv to other research databases

This blueprint provides a complete implementation path from the current basic adapters to a fully functional Rhiza research mining system.