"""
Phase 1: Strategic Triage Agent - Claude-as-a-Service Version

This version uses the Claude MCP server instead of direct API calls.
The server automatically includes HAiOS context from CLAUDE.md.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, UTC
from pathlib import Path
import json
import httpx
import os
import hashlib

try:
    from .mcp_client import MCPClient, MockMCPClient
except ImportError:
    # For standalone execution
    from mcp_client import MCPClient, MockMCPClient


class StrategicTriageAgent:
    """
    Phase 1: Identifies high-priority research themes.
    Uses Claude-as-a-Service for LLM analysis.
    """
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock or os.getenv("USE_MOCK_LLM", "true").lower() == "true"
        self.trace_id = f"phase1-{int(datetime.now(UTC).timestamp())}"
        
        if self.use_mock:
            # Mock responses for testing
            self.mcp_client = MockMCPClient({
                "research": {
                    "content": json.dumps({
                        "themes": [
                            {
                                "name": "Distributed Trust Verification in Multi-Agent Systems",
                                "relevance_score": 9,
                                "description": "Critical for HAiOS trust engine architecture",
                                "key_papers": ["2412.16224v1", "2412.19367v1"],
                                "open_questions": [
                                    "How to ensure byzantine fault tolerance?",
                                    "What are optimal consensus mechanisms?"
                                ]
                            },
                            {
                                "name": "Deterministic Security Controls for AI Systems",
                                "relevance_score": 8,
                                "description": "Aligns with HAiOS deterministic kernel",
                                "key_papers": ["2412.18279v1"],
                                "open_questions": [
                                    "How to implement provable security boundaries?",
                                    "What formal verification methods apply?"
                                ]
                            },
                            {
                                "name": "Evidence-Based Validation Frameworks",
                                "relevance_score": 7,
                                "description": "Supports HAiOS evidence chain requirements",
                                "key_papers": ["2412.18832v1"],
                                "open_questions": [
                                    "How to automate evidence collection?",
                                    "What constitutes sufficient evidence?"
                                ]
                            }
                        ]
                    })
                }
            })
        else:
            self.mcp_client = MCPClient()
    
    def log_error(self, message: str):
        """Log error message."""
        print(f"ERROR [{self.trace_id}]: {message}")
    
    def log_warning(self, message: str):
        """Log warning message."""
        print(f"WARNING [{self.trace_id}]: {message}")
    
    def generate_evidence(self, data: Dict) -> str:
        """Generate evidence hash."""
        evidence_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(evidence_str.encode()).hexdigest()[:16]
    
    def analyze_research_landscape(self, 
                                 corpus_source: str,
                                 categories: List[str]) -> Dict[str, Any]:
        """
        Analyze research corpus using Claude-as-a-Service.
        
        The MCP server automatically includes HAiOS context,
        so we don't need to manually load CLAUDE.md or ADRs.
        """
        print(f"=== Phase 1: Strategic Triage (v3) ===")
        print(f"Corpus: {corpus_source}")
        print(f"Categories: {categories}")
        print(f"Using {'mock' if self.use_mock else 'real'} MCP client")
        
        # Generate evidence
        evidence = self.generate_evidence({
            'action': 'analyze_research_landscape',
            'corpus_source': corpus_source,
            'categories': categories,
            'timestamp': datetime.now(UTC).isoformat(),
            'mcp_version': 'v3'
        })
        
        # Fetch recent papers
        recent_papers = self._fetch_recent_papers(corpus_source, categories)
        
        if not recent_papers:
            self.log_warning("No papers found from arXiv")
            return self._empty_result(evidence, corpus_source, categories)
        
        print(f"Fetched {len(recent_papers)} papers")
        
        # Prepare paper summaries for analysis
        paper_summaries = self._prepare_paper_summaries(recent_papers)
        
        # Simple prompt - context is handled by the server
        prompt = f"""
Analyze these {len(recent_papers)} research papers and identify the top 3-5 themes 
most relevant to the HAiOS architecture and goals.

Research Papers:
{json.dumps(paper_summaries, indent=2)}

For each theme, provide:
1. Theme name and description
2. Relevance score (1-10) to HAiOS
3. Key papers that support this theme
4. Open questions that could be addressed

Focus on themes related to:
- Trust engines and verification
- Distributed systems and consensus
- Evidence-based validation
- Deterministic security controls
- Agent orchestration patterns
"""
        
        # Query Claude server
        response = self.mcp_client.query(prompt)
        
        if "error" in response:
            self.log_error(f"MCP query failed: {response['error']}")
            return self._fallback_analysis(recent_papers, evidence)
        
        # Parse and structure the response
        try:
            if isinstance(response.get("content"), str):
                analysis = json.loads(response["content"])
            else:
                analysis = response.get("content", {})
        except json.JSONDecodeError:
            self.log_error("Failed to parse MCP response as JSON")
            return self._fallback_analysis(recent_papers, evidence)
        
        # Structure the final output
        return self._structure_priorities(analysis, evidence, recent_papers)
    
    def _fetch_recent_papers(self, corpus_source: str, categories: List[str]) -> List[Dict]:
        """Fetch recent papers from arXiv."""
        if corpus_source != "arxiv":
            self.log_warning(f"Unsupported corpus source: {corpus_source}")
            return []
        
        papers = []
        for category in categories:
            try:
                # Use HTTPS for arXiv API
                url = f"https://export.arxiv.org/api/query"
                params = {
                    "search_query": f"cat:{category}",
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                    "max_results": 10
                }
                
                response = httpx.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                
                parsed_papers = self._parse_arxiv_response(response.text)
                papers.extend(parsed_papers)
            except Exception as e:
                self.log_error(f"Failed to fetch papers for {category}: {e}")
        
        return papers
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """Parse arXiv API XML response."""
        papers = []
        
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            self.log_error(f"Failed to parse arXiv XML: {e}")
            return papers
        
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Check for API errors
        error_elem = root.find('atom:error', ns)
        if error_elem is not None:
            self.log_error(f"arXiv API error: {error_elem.text}")
            return papers
        
        for entry in root.findall('atom:entry', ns):
            try:
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
                    ]
                }
                papers.append(paper)
            except Exception as e:
                self.log_error(f"Failed to parse paper entry: {e}")
        
        return papers
    
    def _prepare_paper_summaries(self, papers: List[Dict]) -> List[Dict]:
        """Prepare concise paper summaries for LLM analysis."""
        summaries = []
        for paper in papers[:20]:  # Limit to 20 most recent
            summaries.append({
                "id": paper['id'],
                "title": paper['title'],
                "abstract": paper['abstract'][:500] + "..." if len(paper['abstract']) > 500 else paper['abstract'],
                "categories": paper['categories']
            })
        return summaries
    
    def _structure_priorities(self, 
                            analysis: Dict, 
                            evidence: str,
                            papers: List[Dict]) -> Dict[str, Any]:
        """Structure the analysis into the expected output format."""
        themes = analysis.get("themes", [])
        
        # Sort themes by relevance score
        themes.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Build priority list
        priorities = []
        for i, theme in enumerate(themes[:5]):  # Top 5 themes
            priority = {
                "priority_id": f"PRI_{datetime.now().strftime('%Y%m%d')}_{i+1}",
                "theme": theme.get("name", "Unknown Theme"),
                "description": theme.get("description", ""),
                "relevance_score": theme.get("relevance_score", 0),
                "key_papers": theme.get("key_papers", []),
                "open_questions": theme.get("open_questions", []),
                "evidence_chain": [evidence]
            }
            priorities.append(priority)
        
        return {
            "priorities": priorities,
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "corpus_source": "arxiv",
                "categories": ["cs.AI", "cs.DC"],
                "papers_analyzed": len(papers),
                "mcp_version": "v3",
                "evidence": evidence
            }
        }
    
    def _fallback_analysis(self, papers: List[Dict], evidence: str) -> Dict[str, Any]:
        """Fallback analysis when MCP server is unavailable."""
        # Simple keyword-based fallback
        themes = {
            "distributed": {"count": 0, "papers": []},
            "trust": {"count": 0, "papers": []},
            "verification": {"count": 0, "papers": []},
            "consensus": {"count": 0, "papers": []},
            "security": {"count": 0, "papers": []}
        }
        
        for paper in papers:
            text = (paper.get('title', '') + ' ' + paper.get('abstract', '')).lower()
            for keyword, data in themes.items():
                if keyword in text:
                    data["count"] += 1
                    data["papers"].append(paper['id'])
        
        # Sort by count and create priorities
        sorted_themes = sorted(themes.items(), key=lambda x: x[1]["count"], reverse=True)
        
        priorities = []
        for i, (keyword, data) in enumerate(sorted_themes[:3]):
            if data["count"] > 0:
                priorities.append({
                    "priority_id": f"PRI_FALLBACK_{i+1}",
                    "theme": f"{keyword.title()}-based Systems",
                    "description": f"Papers mentioning {keyword} (fallback analysis)",
                    "relevance_score": min(data["count"], 10),
                    "key_papers": data["papers"][:3],
                    "evidence_chain": [evidence]
                })
        
        return {
            "priorities": priorities,
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "corpus_source": "arxiv",
                "papers_analyzed": len(papers),
                "fallback_mode": True,
                "evidence": evidence
            }
        }
    
    def _empty_result(self, evidence: str, corpus_source: str, categories: List[str]) -> Dict:
        """Return empty result when no papers found."""
        return {
            "priorities": [],
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "corpus_source": corpus_source,
                "categories": categories,
                "papers_analyzed": 0,
                "error": "No papers found",
                "evidence": evidence
            }
        }


def main():
    """Test the agent independently."""
    agent = StrategicTriageAgent(use_mock=True)
    
    # Test with sample categories
    result = agent.analyze_research_landscape(
        corpus_source="arxiv",
        categories=["cs.AI", "cs.DC"]
    )
    
    # Save result
    report_dir = Path(__file__).parent.parent / "reports" / "phase1_priorities"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = report_dir / f"priorities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print(f"Found {len(result['priorities'])} priority themes")
    
    for priority in result['priorities']:
        print(f"\n- {priority['theme']} (Score: {priority['relevance_score']})")


if __name__ == "__main__":
    main()