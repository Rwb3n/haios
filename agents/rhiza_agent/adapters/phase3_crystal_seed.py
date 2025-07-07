#!/usr/bin/env python3
"""
Phase 3: Crystal Seed Extraction
Extracts actionable insights from Tier 1 papers.
This is where deep LLM analysis happens.
"""

import os
import sys
import json
import httpx
import hashlib
from datetime import datetime, UTC
from typing import Dict, List, Any, Optional
from pathlib import Path

class CrystalSeedExtractor:
    """
    Phase 3: Deep analysis of Tier 1 papers to extract actionable insights.
    This is where we use LLM for concept extraction and HAiOS mapping.
    """
    
    def __init__(self):
        self.agent_id = "crystal_seed_extractor_v1"
        self.nocodb_url = os.getenv('NOCODB_API_URL', 'http://localhost:8081/api/v1')
        self.nocodb_token = os.getenv('NOCODB_API_TOKEN')
        self.llm_client = self._init_llm_client()
        
    def _init_llm_client(self):
        """Initialize LLM client based on available API keys."""
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if anthropic_key:
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=anthropic_key)
            except ImportError:
                print("Warning: anthropic package not installed")
        elif openai_key:
            try:
                import openai
                openai.api_key = openai_key
                return openai
            except ImportError:
                print("Warning: openai package not installed")
        
        # Default to mock client
        print("Using mock LLM client (no API keys found)")
        return MockLLMClient()
        
    def extract_crystal_seed(self, paper_id: str, paper_data: Dict = None) -> Dict[str, Any]:
        """
        Extract actionable insights from a Tier 1 paper.
        
        Args:
            paper_id: arXiv paper ID
            paper_data: Optional pre-loaded paper data
            
        Returns:
            Crystal Seed Proposal with concepts and applications
        """
        print(f"=== Phase 3: Crystal Seed Extraction ===")
        print(f"Paper ID: {paper_id}")
        
        # Fetch paper if not provided
        if paper_data is None:
            paper_data = self._fetch_paper(paper_id)
            if not paper_data:
                raise ValueError(f"Could not fetch paper {paper_id}")
                
        print(f"Title: {paper_data.get('title', 'Unknown')}")
        
        # Extract concepts using LLM
        concepts = self._extract_concepts(paper_data)
        print(f"Extracted {len(concepts)} concepts")
        
        # Map concepts to HAiOS applications
        applications = self._identify_applications(concepts, paper_data)
        print(f"Identified {len(applications)} potential applications")
        
        # Generate proposal
        proposal = self._generate_proposal(paper_data, concepts, applications)
        
        return proposal
        
    def _fetch_paper(self, paper_id: str) -> Optional[Dict]:
        """Fetch paper metadata and content from arXiv."""
        try:
            # Fetch metadata
            url = "https://export.arxiv.org/api/query"
            params = {"id_list": paper_id}
            
            response = httpx.get(url, params=params, timeout=30)
            if response.status_code == 200:
                papers = self._parse_arxiv_response(response.text)
                if papers:
                    paper = papers[0]
                    # Note: In production, would fetch full PDF and extract text
                    # For MVP, we work with title and abstract only
                    return paper
        except Exception as e:
            print(f"Error fetching paper: {e}")
            
        return None
        
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """Parse arXiv API XML response."""
        papers = []
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_content)
        
        # Define namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            paper = {
                'id': entry.find('atom:id', ns).text.split('/')[-1],
                'title': entry.find('atom:title', ns).text.strip(),
                'abstract': entry.find('atom:summary', ns).text.strip(),
                'authors': [
                    author.find('atom:name', ns).text 
                    for author in entry.findall('atom:author', ns)
                ],
                'published': entry.find('atom:published', ns).text,
                'categories': [
                    cat.attrib['term'] 
                    for cat in entry.findall('atom:category', ns)
                ],
                'pdf_url': entry.find('atom:id', ns).text.replace('/abs/', '/pdf/') + '.pdf'
            }
            papers.append(paper)
            
        return papers
        
    def _extract_concepts(self, paper: Dict) -> List[Dict[str, Any]]:
        """Extract key concepts from paper using LLM."""
        prompt = f"""Analyze this research paper and extract KEY CONCEPTS relevant to distributed systems and AI governance.

PAPER:
Title: {paper['title']}
Abstract: {paper['abstract']}

Focus on concepts related to:
1. Trust verification and evidence chains
2. Distributed coordination and consensus
3. Security and validation mechanisms
4. Agent orchestration patterns
5. Deterministic controls

For each concept, provide:
- Name (short, descriptive)
- Type: ALGORITHM, PROTOCOL, ARCHITECTURE, PATTERN, or PRINCIPLE
- Description (2-3 sentences)
- Relevance quote from the abstract
- HAiOS applicability (how it could be used)

Output as JSON:
{{
    "concepts": [
        {{
            "name": "concept name",
            "concept_type": "PATTERN",
            "description": "what it does",
            "relevance_quote": "exact quote showing the concept",
            "haios_applicability": "how HAiOS could use this",
            "confidence_score": 0.8
        }}
    ]
}}"""
        
        try:
            if hasattr(self.llm_client, 'messages'):  # Anthropic
                response = self.llm_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            elif hasattr(self.llm_client, 'ChatCompletion'):  # OpenAI
                response = self.llm_client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.choices[0].message.content
            else:  # Mock
                content = self.llm_client.complete(prompt)
                
            result = json.loads(content)
            concepts = result.get("concepts", [])
            
            # Add concept IDs
            for i, concept in enumerate(concepts):
                concept['concept_id'] = hashlib.sha256(
                    f"{paper['id']}_{concept['name']}_{i}".encode()
                ).hexdigest()[:16]
                
            return concepts
            
        except Exception as e:
            print(f"Error extracting concepts: {e}")
            return self._fallback_concept_extraction(paper)
            
    def _fallback_concept_extraction(self, paper: Dict) -> List[Dict]:
        """Simple fallback concept extraction without LLM."""
        # Extract based on keywords in abstract
        abstract_lower = paper['abstract'].lower()
        concepts = []
        
        concept_patterns = {
            "consensus": ("Distributed Consensus Mechanism", "PROTOCOL"),
            "verification": ("Verification Framework", "PATTERN"),
            "orchestration": ("Agent Orchestration Pattern", "ARCHITECTURE"),
            "trust": ("Trust Establishment Protocol", "PROTOCOL"),
            "validation": ("Validation Pipeline", "PATTERN")
        }
        
        for keyword, (name, ctype) in concept_patterns.items():
            if keyword in abstract_lower:
                concepts.append({
                    "concept_id": hashlib.sha256(f"{paper['id']}_{name}".encode()).hexdigest()[:16],
                    "name": name,
                    "concept_type": ctype,
                    "description": f"Concept related to {keyword} found in paper",
                    "relevance_quote": "See abstract",
                    "haios_applicability": f"Could enhance HAiOS {keyword} capabilities",
                    "confidence_score": 0.5
                })
                
        return concepts
        
    def _identify_applications(self, concepts: List[Dict], paper: Dict) -> List[Dict[str, Any]]:
        """Map extracted concepts to specific HAiOS applications."""
        if not concepts:
            return []
            
        # For MVP, use simple mapping based on concept types
        applications = []
        
        for concept in concepts:
            app = {
                "application_id": hashlib.sha256(
                    f"app_{concept['concept_id']}".encode()
                ).hexdigest()[:16],
                "concept_id": concept['concept_id'],
                "component": self._map_to_component(concept),
                "description": f"Apply {concept['name']} to improve {self._map_to_component(concept)}",
                "implementation_notes": concept['haios_applicability'],
                "priority": "medium",
                "complexity": "moderate"
            }
            applications.append(app)
            
        return applications
        
    def _map_to_component(self, concept: Dict) -> str:
        """Map concept to HAiOS component."""
        type_mapping = {
            "ALGORITHM": "Validation Engine",
            "PROTOCOL": "Agent Communication Layer",
            "ARCHITECTURE": "System Architecture",
            "PATTERN": "Workflow Patterns",
            "PRINCIPLE": "Governance Framework"
        }
        return type_mapping.get(concept['concept_type'], "Core System")
        
    def _generate_proposal(self, 
                         paper: Dict,
                         concepts: List[Dict],
                         applications: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive Crystal Seed Proposal."""
        proposal_id = f"crystal_seed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate artifact hash for raw research
        artifact_content = json.dumps({
            "title": paper['title'],
            "authors": paper['authors'],
            "abstract": paper['abstract']
        }, sort_keys=True)
        integrity_hash = hashlib.sha256(artifact_content.encode()).hexdigest()
        
        # First, save raw research artifact
        artifact_id = self._save_raw_artifact(paper, integrity_hash)
        
        proposal = {
            "report_id": proposal_id,
            "source_artifact_id": artifact_id,
            "extraction_timestamp": datetime.now(UTC).isoformat(),
            "extraction_method": "llm_analysis_v1",
            "llm_model": getattr(self.llm_client, 'model_name', 'unknown'),
            "source_paper": {
                "paper_id": paper['id'],
                "title": paper['title'],
                "authors": paper['authors'],
                "url": f"https://arxiv.org/abs/{paper['id']}",
                "pdf_url": paper.get('pdf_url', '')
            },
            "concepts": concepts,
            "primary_category": paper['categories'][0] if paper.get('categories') else 'unknown',
            "keywords": self._extract_keywords(paper, concepts),
            "relevance_tier": 1,  # Only Tier 1 papers reach Phase 3
            "impacted_adrs": self._identify_impacted_adrs(concepts, applications),
            "proposed_actions": self._generate_actions(applications),
            "trace_id": f"rhiza_{proposal_id}",
            "status": "pending_review"
        }
        
        return proposal
        
    def _save_raw_artifact(self, paper: Dict, integrity_hash: str) -> str:
        """Save raw research artifact to database."""
        artifact_id = f"rra_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{paper['id']}"
        
        if self.nocodb_token:
            try:
                headers = {
                    'xc-token': self.nocodb_token,
                    'Content-Type': 'application/json'
                }
                
                data = {
                    "artifact_id": artifact_id,
                    "paper_id": paper['id'],
                    "source_name": "arxiv",
                    "source_url": f"https://arxiv.org/abs/{paper['id']}",
                    "source_pdf_url": paper.get('pdf_url', ''),
                    "title": paper['title'],
                    "authors": json.dumps(paper['authors']),
                    "abstract": paper['abstract'],
                    "categories": json.dumps(paper.get('categories', [])),
                    "full_text": None,  # Would be populated if we had PDF extraction
                    "extracted_sections": json.dumps({}),
                    "integrity_hash": integrity_hash,
                    "trace_id": f"rhiza_{artifact_id}",
                    "_locked_payload": True
                }
                
                response = httpx.post(
                    f"{self.nocodb_url}/db/data/v1/rhiza/raw_research_artifacts",
                    headers=headers,
                    json=data,
                    timeout=10
                )
                response.raise_for_status()
                print(f"Saved raw artifact: {artifact_id}")
            except Exception as e:
                print(f"Warning: Failed to save artifact: {e}")
                
        return artifact_id
        
    def _extract_keywords(self, paper: Dict, concepts: List[Dict]) -> List[str]:
        """Extract keywords from paper and concepts."""
        keywords = set()
        
        # From concepts
        for concept in concepts:
            keywords.add(concept['name'].lower())
            
        # From categories
        keywords.update(paper.get('categories', []))
        
        return list(keywords)[:10]  # Limit to 10
        
    def _identify_impacted_adrs(self, concepts: List[Dict], applications: List[Dict]) -> List[str]:
        """Identify which ADRs might be impacted."""
        # For MVP, use simple mapping
        adrs = set()
        
        for concept in concepts:
            if "trust" in concept['name'].lower():
                adrs.add("ADR-OS-021")  # Trust architecture
            if "consensus" in concept['name'].lower():
                adrs.add("ADR-OS-023")  # Distributed systems
            if "validation" in concept['name'].lower():
                adrs.add("ADR-OS-035")  # Validation framework
                
        return list(adrs)
        
    def _generate_actions(self, applications: List[Dict]) -> List[Dict]:
        """Generate proposed actions based on applications."""
        actions = []
        
        for app in applications[:3]:  # Top 3 applications
            actions.append({
                "action_type": "EVALUATE_INTEGRATION",
                "target_component": app['component'],
                "description": app['description'],
                "priority": app['priority']
            })
            
        return actions
        
    def save_crystal_seed(self, proposal: Dict[str, Any]) -> str:
        """Save crystal seed proposal to database and file."""
        # Save to NocoDB if configured
        if self.nocodb_token:
            try:
                self._save_to_nocodb(proposal)
                print("Saved to NocoDB")
            except Exception as e:
                print(f"Warning: Failed to save to NocoDB: {e}")
                
        # Save as files
        report_dir = Path(__file__).parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)
        
        # JSON version
        json_path = report_dir / f"{proposal['report_id']}.json"
        with open(json_path, 'w') as f:
            json.dump(proposal, f, indent=2)
            
        # Markdown version
        self._save_markdown_report(proposal, report_dir)
        
        print(f"Crystal Seed saved to: {json_path}")
        return str(json_path)
        
    def _save_to_nocodb(self, proposal: Dict[str, Any]):
        """Save crystal seed to concept_extraction_reports table."""
        headers = {
            'xc-token': self.nocodb_token,
            'Content-Type': 'application/json'
        }
        
        data = {
            "report_id": proposal["report_id"],
            "source_artifact_id": proposal["source_artifact_id"],
            "extraction_timestamp": proposal["extraction_timestamp"],
            "extraction_method": proposal["extraction_method"],
            "llm_model": proposal["llm_model"],
            "concepts": json.dumps(proposal["concepts"]),
            "primary_category": proposal["primary_category"],
            "keywords": json.dumps(proposal["keywords"]),
            "relevance_tier": proposal["relevance_tier"],
            "impacted_adrs": json.dumps(proposal["impacted_adrs"]),
            "proposed_actions": json.dumps(proposal["proposed_actions"]),
            "trace_id": proposal["trace_id"],
            "status": proposal["status"]
        }
        
        response = httpx.post(
            f"{self.nocodb_url}/db/data/v1/rhiza/concept_extraction_reports",
            headers=headers,
            json=data,
            timeout=10
        )
        response.raise_for_status()
        
    def _save_markdown_report(self, proposal: Dict, report_dir: Path):
        """Generate human-readable crystal seed proposal."""
        md_path = report_dir / f"{proposal['report_id']}.md"
        
        content = f"""# Crystal Seed Proposal

**Report ID**: {proposal['report_id']}  
**Generated**: {proposal['extraction_timestamp']}  
**Status**: {proposal['status']}

## Source Paper

- **Title**: {proposal['source_paper']['title']}
- **Authors**: {', '.join(proposal['source_paper']['authors'])}
- **URL**: {proposal['source_paper']['url']}
- **Paper ID**: {proposal['source_paper']['paper_id']}

## Extracted Concepts ({len(proposal['concepts'])})

"""
        for i, concept in enumerate(proposal['concepts'], 1):
            content += f"""### {i}. {concept['name']} ({concept['concept_type']})

**Description**: {concept['description']}

**Relevance Quote**: "{concept['relevance_quote']}"

**HAiOS Applicability**: {concept['haios_applicability']}

**Confidence**: {concept['confidence_score']}

---

"""

        content += f"""## Proposed Actions

"""
        for i, action in enumerate(proposal['proposed_actions'], 1):
            content += f"""{i}. **{action['action_type']}**
   - Target: {action['target_component']}
   - Description: {action['description']}
   - Priority: {action['priority']}

"""

        content += f"""## Impact Analysis

**Impacted ADRs**: {', '.join(proposal['impacted_adrs']) if proposal['impacted_adrs'] else 'None identified'}

**Keywords**: {', '.join(proposal['keywords'])}

## Next Steps

1. Review extracted concepts for accuracy
2. Validate proposed actions with architecture team
3. Create detailed implementation plan for high-priority items
4. Update relevant ADRs if needed
"""
        
        with open(md_path, 'w') as f:
            f.write(content)


class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self):
        self.model_name = "mock-llm"
        
    def complete(self, prompt: str) -> str:
        """Return mock concept extraction."""
        return json.dumps({
            "concepts": [
                {
                    "name": "Byzantine Fault Tolerant Consensus",
                    "concept_type": "PROTOCOL",
                    "description": "A consensus mechanism that can tolerate malicious actors in distributed systems",
                    "relevance_quote": "ensures agreement even with Byzantine failures",
                    "haios_applicability": "Could strengthen agent coordination against malicious agents",
                    "confidence_score": 0.9
                },
                {
                    "name": "Cryptographic Evidence Chains",
                    "concept_type": "PATTERN",
                    "description": "Immutable chains of cryptographically linked evidence for audit trails",
                    "relevance_quote": "tamper-evident logging with cryptographic guarantees",
                    "haios_applicability": "Perfect for HAiOS evidence chain implementation",
                    "confidence_score": 0.95
                },
                {
                    "name": "Deterministic State Machine Replication",
                    "concept_type": "ARCHITECTURE",
                    "description": "Ensures identical state across distributed nodes through deterministic execution",
                    "relevance_quote": "deterministic execution ensures consistency",
                    "haios_applicability": "Could improve agent state synchronization",
                    "confidence_score": 0.85
                }
            ]
        })


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Crystal Seed Extractor - Deep analysis of Tier 1 papers"
    )
    parser.add_argument(
        "--paper-id",
        type=str,
        required=True,
        help="arXiv paper ID to analyze"
    )
    parser.add_argument(
        "--paper-data",
        type=str,
        help="JSON file with paper data (optional)"
    )
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = CrystalSeedExtractor()
    
    # Load paper data if provided
    paper_data = None
    if args.paper_data:
        with open(args.paper_data, 'r') as f:
            paper_data = json.load(f)
    
    # Extract crystal seed
    try:
        proposal = extractor.extract_crystal_seed(args.paper_id, paper_data)
        output_path = extractor.save_crystal_seed(proposal)
        
        # Show summary
        print("\n=== Crystal Seed Extracted ===")
        print(f"Concepts Found: {len(proposal['concepts'])}")
        if proposal['concepts']:
            print("\nKey Concepts:")
            for concept in proposal['concepts'][:3]:
                print(f"- {concept['name']} ({concept['concept_type']})")
                print(f"  Confidence: {concept['confidence_score']}")
                
        print(f"\nProposed Actions: {len(proposal['proposed_actions'])}")
        print(f"Impacted ADRs: {', '.join(proposal['impacted_adrs'])}")
        
        print(f"\nFull proposal saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)