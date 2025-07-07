#!/usr/bin/env python3
"""
Phase 3: Crystal Seed Extraction - Claude-as-a-Service Version

Extracts actionable insights from Tier 1 papers using Claude MCP server.
The server's automatic HAiOS context loading enables deep integration analysis.
"""

import os
import json
import httpx
import hashlib
from datetime import datetime, UTC
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from .mcp_client import MCPClient, MockMCPClient
except ImportError:
    from mcp_client import MCPClient, MockMCPClient


class CrystalSeedExtractor:
    """
    Phase 3: Deep analysis of Tier 1 papers to extract actionable insights.
    Uses Claude-as-a-Service for HAiOS-aware concept extraction.
    """
    
    def __init__(self, use_mock: bool = False):
        self.agent_id = "crystal_seed_extractor_v3"
        self.use_mock = use_mock or os.getenv("USE_MOCK_LLM", "true").lower() == "true"
        
        # Initialize MCP client
        if self.use_mock:
            self.mcp_client = MockMCPClient({
                "extract": {
                    "content": json.dumps({
                        "concepts": [
                            {
                                "name": "Byzantine Fault Tolerant Consensus",
                                "type": "PROTOCOL",
                                "description": "Consensus mechanism resistant to malicious agents",
                                "relevance_to_haios": "Critical for trust engine's distributed validation",
                                "integration_points": ["Plan Validation Gateway", "Agent Registry"]
                            },
                            {
                                "name": "Cryptographic Evidence Chains",
                                "type": "PATTERN",
                                "description": "Immutable proof sequences using hash chains",
                                "relevance_to_haios": "Implements Core Pillar #1 - Evidence-Based Development",
                                "integration_points": ["Artifact Storage", "Audit System"]
                            },
                            {
                                "name": "Deterministic State Machine Replication",
                                "type": "ARCHITECTURE",
                                "description": "Ensures consistent state across distributed agents",
                                "relevance_to_haios": "Supports Certainty Ratchet mechanism",
                                "integration_points": ["Agent Orchestration", "State Management"]
                            }
                        ],
                        "proposed_actions": [
                            {
                                "action": "Implement BFT consensus for Plan Validation Gateway",
                                "priority": "HIGH",
                                "effort": "2-3 sprints",
                                "dependencies": ["Agent communication protocol", "State persistence"]
                            },
                            {
                                "action": "Add cryptographic signatures to all agent artifacts",
                                "priority": "HIGH",
                                "effort": "1 sprint",
                                "dependencies": ["PKI infrastructure"]
                            },
                            {
                                "action": "Create deterministic replay mechanism for validation",
                                "priority": "MEDIUM",
                                "effort": "3-4 sprints",
                                "dependencies": ["Event sourcing", "State snapshots"]
                            }
                        ],
                        "risk_assessment": {
                            "technical_risks": ["Performance overhead of BFT", "Key management complexity"],
                            "mitigation_strategies": ["Implement caching layer", "Use hardware security modules"]
                        }
                    })
                }
            })
        else:
            self.mcp_client = MCPClient()
        
        # NocoDB configuration
        self.nocodb_url = os.getenv('NOCODB_API_URL', 'http://localhost:8081/api/v1')
        self.nocodb_token = os.getenv('NOCODB_API_TOKEN')
    
    def extract_crystal_seed(self, paper_id: str, paper_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extract actionable insights from a research paper.
        
        The Claude MCP server automatically includes HAiOS context,
        enabling deep integration analysis.
        """
        print(f"=== Phase 3: Crystal Seed Extraction (v3) ===")
        print(f"Paper ID: {paper_id}")
        print(f"Using {'mock' if self.use_mock else 'real'} MCP client")
        
        # Generate evidence for this extraction
        evidence = self._generate_evidence({
            'action': 'extract_crystal_seed',
            'paper_id': paper_id,
            'timestamp': datetime.now(UTC).isoformat()
        })
        
        # Fetch paper if not provided
        if paper_data is None:
            paper_data = self._fetch_paper(paper_id)
            if not paper_data:
                return self._error_response(paper_id, "Failed to fetch paper", evidence)
        
        # Extract concepts using Claude MCP
        concepts = self._extract_concepts_with_mcp(paper_data)
        
        if "error" in concepts:
            return self._error_response(paper_id, concepts["error"], evidence)
        
        # Create crystal seed proposal
        proposal = {
            "proposal_id": f"crystal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "paper_id": paper_id,
            "paper_title": paper_data.get('title', 'Unknown'),
            "generation_counter": int(datetime.now(UTC).timestamp()),
            "created_at": datetime.now(UTC).isoformat(),
            "evidence_chain": [evidence],
            "extraction_results": concepts,
            "metadata": {
                "extractor_version": "v3",
                "mcp_enabled": True,
                "categories": paper_data.get('categories', [])
            }
        }
        
        # Validate proposal structure
        is_valid, issues = self._validate_proposal(proposal)
        proposal['validation'] = {
            'is_valid': is_valid,
            'issues': issues
        }
        
        # Save proposal
        self._save_proposal(proposal)
        
        # Print summary
        if isinstance(concepts, dict) and "concepts" in concepts:
            print(f"Extracted {len(concepts.get('concepts', []))} concepts")
            print(f"Proposed {len(concepts.get('proposed_actions', []))} actions")
        
        return proposal
    
    def _extract_concepts_with_mcp(self, paper_data: Dict) -> Dict:
        """Extract concepts using Claude MCP server."""
        # Prepare paper summary
        paper_summary = {
            "title": paper_data.get('title', ''),
            "abstract": paper_data.get('abstract', ''),
            "categories": paper_data.get('categories', [])
        }
        
        prompt = f"""
Analyze this research paper and extract actionable concepts for HAiOS integration.

Paper:
{json.dumps(paper_summary, indent=2)}

Extract:
1. **Key Concepts**: Identify 3-5 core concepts with:
   - Name and type (PROTOCOL, PATTERN, ARCHITECTURE, ALGORITHM)
   - Description
   - Direct relevance to HAiOS Trust Engine
   - Specific integration points in HAiOS architecture

2. **Proposed Actions**: For each concept, suggest:
   - Concrete implementation action
   - Priority (HIGH, MEDIUM, LOW)
   - Estimated effort
   - Dependencies on existing HAiOS components

3. **Risk Assessment**:
   - Technical risks of adoption
   - Mitigation strategies

Focus on concepts that directly support:
- Evidence-based development
- Distributed agent coordination
- Trust verification mechanisms
- Deterministic validation

Remember that HAiOS uses:
- n8n for workflow orchestration
- NocoDB for state management
- Agent separation patterns
- Cryptographic evidence chains
"""
        
        response = self.mcp_client.query(prompt, max_tokens=3000)
        
        if "error" in response:
            return {"error": response["error"]}
        
        try:
            if isinstance(response.get("content"), str):
                return json.loads(response["content"])
            else:
                return response.get("content", {})
        except json.JSONDecodeError:
            return {"error": "Failed to parse MCP response", "raw": str(response)}
    
    def _fetch_paper(self, paper_id: str) -> Optional[Dict]:
        """Fetch paper metadata from arXiv."""
        try:
            # Clean paper ID (remove version if present)
            clean_id = paper_id.split('v')[0]
            
            url = f"https://export.arxiv.org/api/query"
            params = {"id_list": clean_id}
            
            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            
            # Parse XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entry = root.find('atom:entry', ns)
            
            if entry is None:
                print(f"Paper {paper_id} not found")
                return None
            
            paper = {
                'id': paper_id,
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
                ]
            }
            
            return paper
            
        except Exception as e:
            print(f"Failed to fetch paper {paper_id}: {e}")
            return None
    
    def _generate_evidence(self, action_data: Dict) -> str:
        """Generate cryptographic evidence for this action."""
        evidence_data = {
            'agent_id': self.agent_id,
            'action': action_data,
            'timestamp': datetime.now(UTC).isoformat()
        }
        
        # Create hash
        evidence_str = json.dumps(evidence_data, sort_keys=True)
        evidence_hash = hashlib.sha256(evidence_str.encode()).hexdigest()
        
        return f"sha256:{evidence_hash[:16]}"
    
    def _validate_proposal(self, proposal: Dict) -> tuple[bool, List[str]]:
        """Validate crystal seed proposal structure."""
        issues = []
        
        # Check required fields
        required_fields = ['proposal_id', 'paper_id', 'extraction_results', 'evidence_chain']
        for field in required_fields:
            if field not in proposal:
                issues.append(f"Missing required field: {field}")
        
        # Validate extraction results
        if 'extraction_results' in proposal:
            results = proposal['extraction_results']
            if isinstance(results, dict):
                if 'error' not in results and 'concepts' not in results:
                    issues.append("Extraction results missing concepts")
        
        return len(issues) == 0, issues
    
    def _save_proposal(self, proposal: Dict):
        """Save crystal seed proposal."""
        # Ensure reports directory exists
        report_dir = Path("reports") / "phase3_crystal_seeds"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_file = report_dir / f"{proposal['proposal_id']}.json"
        with open(json_file, 'w') as f:
            json.dump(proposal, f, indent=2)
        print(f"Proposal saved to: {json_file}")
        
        # Save markdown summary
        md_file = report_dir / f"{proposal['proposal_id']}.md"
        self._save_markdown_proposal(proposal, md_file)
    
    def _save_markdown_proposal(self, proposal: Dict, filepath: Path):
        """Save human-readable markdown proposal."""
        with open(filepath, 'w') as f:
            f.write(f"# Crystal Seed Proposal\n\n")
            f.write(f"**Paper**: {proposal.get('paper_title', 'Unknown')}\n")
            f.write(f"**Paper ID**: {proposal['paper_id']}\n")
            f.write(f"**Generated**: {proposal['created_at']}\n\n")
            
            results = proposal.get('extraction_results', {})
            
            if isinstance(results, dict) and 'concepts' in results:
                concepts = results['concepts']
                f.write(f"## Extracted Concepts ({len(concepts)})\n\n")
                
                for i, concept in enumerate(concepts, 1):
                    f.write(f"### {i}. {concept.get('name', 'Unknown')}\n")
                    f.write(f"**Type**: {concept.get('type', 'Unknown')}\n")
                    f.write(f"**Description**: {concept.get('description', '')}\n")
                    f.write(f"**HAiOS Relevance**: {concept.get('relevance_to_haios', '')}\n")
                    f.write(f"**Integration Points**: {', '.join(concept.get('integration_points', []))}\n\n")
                
                if 'proposed_actions' in results:
                    actions = results['proposed_actions']
                    f.write(f"## Proposed Actions ({len(actions)})\n\n")
                    
                    for action in actions:
                        f.write(f"- **{action.get('action', '')}**\n")
                        f.write(f"  - Priority: {action.get('priority', 'Unknown')}\n")
                        f.write(f"  - Effort: {action.get('effort', 'Unknown')}\n")
                        f.write(f"  - Dependencies: {', '.join(action.get('dependencies', []))}\n\n")
    
    def _error_response(self, paper_id: str, error: str, evidence: str) -> Dict:
        """Create error response."""
        return {
            "proposal_id": f"crystal_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "paper_id": paper_id,
            "created_at": datetime.now(UTC).isoformat(),
            "evidence_chain": [evidence],
            "error": error,
            "validation": {
                "is_valid": False,
                "issues": [error]
            }
        }


def main():
    """Test the extractor independently."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--paper-id', default='2412.16224v1',
                       help='arXiv paper ID to analyze')
    parser.add_argument('--mock', action='store_true',
                       help='Use mock MCP client')
    args = parser.parse_args()
    
    extractor = CrystalSeedExtractor(use_mock=args.mock)
    proposal = extractor.extract_crystal_seed(args.paper_id)
    
    print(f"\nProposal ID: {proposal['proposal_id']}")
    print(f"Valid: {proposal['validation']['is_valid']}")
    print(f"Check reports/phase3_crystal_seeds/ directory for full proposal")


if __name__ == "__main__":
    main()