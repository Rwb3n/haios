#!/usr/bin/env python3
"""
Phase 2: Tactical Ingestion Agent - Claude-as-a-Service Version

This version uses the Claude MCP server for enhanced paper analysis
while maintaining deterministic tier categorization.
"""

import os
import json
import httpx
from datetime import datetime, UTC
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

try:
    from .mcp_client import MCPClient, MockMCPClient
except ImportError:
    from mcp_client import MCPClient, MockMCPClient


class TacticalIngestionAgent:
    """
    Phase 2: Categorizes papers into relevance tiers.
    Uses keyword matching for deterministic categorization,
    Claude MCP for enhanced analysis and insights.
    """
    
    def __init__(self, use_mock: bool = False):
        self.agent_id = "tactical_ingestion_v3"
        self.use_mock = use_mock or os.getenv("USE_MOCK_LLM", "true").lower() == "true"
        
        # Initialize MCP client
        if self.use_mock:
            self.mcp_client = MockMCPClient({
                "categorize": {
                    "content": json.dumps({
                        "tier_analysis": {
                            "tier_1_insights": "Papers show direct relevance to trust verification",
                            "tier_2_insights": "General distributed systems patterns applicable",
                            "tier_3_insights": "Limited relevance, mostly theoretical"
                        },
                        "recommendations": [
                            "Focus on Tier 1 papers for immediate integration",
                            "Monitor Tier 2 for architectural patterns"
                        ]
                    })
                }
            })
        else:
            self.mcp_client = MCPClient()
        
        # NocoDB configuration
        self.nocodb_url = os.getenv('NOCODB_API_URL', 'http://localhost:8081/api/v1')
        self.nocodb_token = os.getenv('NOCODB_API_TOKEN')
        
        # Define keyword sets for deterministic categorization
        self.tier1_keywords = [
            # Direct HAiOS concerns
            "trust verification", "evidence chain", "deterministic routing",
            "agent governance", "distributed consensus", "byzantine fault",
            "formal verification", "audit trail", "cryptographic proof",
            "multi-agent coordination", "agent orchestration",
            # Security & validation
            "security proof", "tamper evident", "integrity verification",
            "validation framework", "attestation", "non-repudiation"
        ]
        
        self.tier2_keywords = [
            # Related architectural patterns
            "distributed system", "microservice", "event-driven",
            "workflow orchestration", "pipeline architecture", 
            "message queue", "pub-sub", "event sourcing",
            # General AI/ML governance
            "ai safety", "alignment", "robustness", "interpretability",
            "model validation", "testing framework", "monitoring"
        ]
        
        # Exclusion keywords (push to tier 3)
        self.exclusion_keywords = [
            "game theory", "economics", "biology", "chemistry",
            "social media", "recommendation", "advertising"
        ]
    
    def categorize_papers(self, 
                         topic: str,
                         papers: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Main entry point: Categorize papers into tiers.
        
        Uses deterministic keyword matching for categorization,
        then enhances with Claude MCP insights.
        """
        print(f"=== Phase 2: Tactical Ingestion (v3) ===")
        print(f"Topic: {topic}")
        print(f"Using {'mock' if self.use_mock else 'real'} MCP client")
        
        # If no papers provided, fetch based on topic
        if papers is None:
            papers = self._fetch_papers_for_topic(topic)
        
        # Check if we have any papers to analyze
        if not papers:
            print("WARNING: No papers found to analyze")
            return self._empty_result(topic)
            
        print(f"Analyzing {len(papers)} papers...")
        
        # Categorize each paper using deterministic rules
        tier_1, tier_2, tier_3 = [], [], []
        
        for paper in papers:
            tier, score, keywords_found = self._calculate_relevance(paper, topic)
            
            paper_summary = {
                "paper_id": paper.get('id', 'unknown'),
                "title": paper.get('title', ''),
                "relevance_score": score,
                "keywords_found": keywords_found,
                "categories": paper.get('categories', [])
            }
            
            if tier == 1:
                tier_1.append(paper_summary)
            elif tier == 2:
                tier_2.append(paper_summary)
            else:
                tier_3.append(paper_summary)
        
        # Sort each tier by relevance score
        tier_1.sort(key=lambda x: x['relevance_score'], reverse=True)
        tier_2.sort(key=lambda x: x['relevance_score'], reverse=True)
        tier_3.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Get enhanced analysis from Claude MCP
        analysis = self._get_mcp_analysis(topic, tier_1, tier_2, tier_3)
        
        # Create triage report
        report = {
            "report_id": f"triage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "topic": topic,
            "generation_counter": int(datetime.now(UTC).timestamp()),
            "created_at": datetime.now(UTC).isoformat(),
            "total_papers_analyzed": len(papers),
            "tier_1_papers": tier_1,
            "tier_2_papers": tier_2,
            "tier_3_papers": tier_3,
            "analysis_criteria": {
                "tier_1_keywords": self.tier1_keywords[:10],  # Sample
                "tier_2_keywords": self.tier2_keywords[:10],  # Sample
                "method": "keyword_matching_with_mcp_enhancement"
            },
            "mcp_analysis": analysis
        }
        
        print(f"Tier 1 (High Priority): {len(tier_1)} papers")
        print(f"Tier 2 (Medium Priority): {len(tier_2)} papers")
        print(f"Tier 3 (Low Priority): {len(tier_3)} papers")
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _calculate_relevance(self, paper: Dict, topic: str) -> Tuple[int, float, List[str]]:
        """
        Calculate relevance tier using deterministic keyword matching.
        Returns: (tier, score, keywords_found)
        """
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        full_text = f"{title} {abstract}"
        
        # Check for exclusions first
        for keyword in self.exclusion_keywords:
            if keyword in full_text:
                return 3, 0.0, [keyword]  # Tier 3
        
        # Count keyword matches
        tier1_matches = []
        tier2_matches = []
        
        for keyword in self.tier1_keywords:
            if keyword in full_text:
                tier1_matches.append(keyword)
        
        for keyword in self.tier2_keywords:
            if keyword in full_text:
                tier2_matches.append(keyword)
        
        # Scoring logic
        tier1_score = len(tier1_matches) * 0.3  # Higher weight for tier 1
        tier2_score = len(tier2_matches) * 0.1  # Lower weight for tier 2
        total_score = tier1_score + tier2_score
        
        # Determine tier
        if tier1_matches:
            return 1, min(total_score, 1.0), tier1_matches[:5]  # Cap at 1.0
        elif tier2_matches:
            return 2, min(total_score, 0.5), tier2_matches[:5]  # Cap at 0.5
        else:
            return 3, 0.0, []
    
    def _get_mcp_analysis(self, topic: str, 
                         tier_1: List[Dict], 
                         tier_2: List[Dict], 
                         tier_3: List[Dict]) -> Dict:
        """Get enhanced analysis from Claude MCP server."""
        prompt = f"""
Analyze the paper categorization results for topic: "{topic}"

Tier 1 (High Priority): {len(tier_1)} papers
Top 3 Tier 1 papers:
{json.dumps(tier_1[:3], indent=2)}

Tier 2 (Medium Priority): {len(tier_2)} papers
Tier 3 (Low Priority): {len(tier_3)} papers

Provide:
1. Key insights about the Tier 1 papers
2. Patterns observed across tiers
3. Recommendations for which papers to process in Phase 3
4. Any missing research areas related to the topic

Focus on practical insights for HAiOS architecture integration.
"""
        
        response = self.mcp_client.query(prompt)
        
        if "error" in response:
            print(f"MCP analysis failed: {response['error']}")
            return {"status": "failed", "error": response['error']}
        
        try:
            if isinstance(response.get("content"), str):
                analysis = json.loads(response["content"])
            else:
                analysis = response.get("content", {})
            return analysis
        except:
            return {"status": "failed", "raw_response": str(response)}
    
    def _fetch_papers_for_topic(self, topic: str) -> List[Dict]:
        """Fetch papers related to the topic from arXiv."""
        # Convert topic to search query
        search_query = topic.replace(" ", "+")
        
        try:
            url = "https://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{search_query}",
                "sortBy": "relevance",
                "max_results": 20
            }
            
            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            papers = []
            
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
                        'categories': [
                            cat.attrib['term'] 
                            for cat in entry.findall('atom:category', ns)
                        ]
                    }
                    papers.append(paper)
                except Exception as e:
                    print(f"Failed to parse paper: {e}")
            
            return papers
            
        except Exception as e:
            print(f"Failed to fetch papers: {e}")
            return []
    
    def _save_report(self, report: Dict):
        """Save triage report to file."""
        # Ensure reports directory exists
        report_dir = Path("reports") / "phase2_triage"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_file = report_dir / f"{report['report_id']}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {json_file}")
        
        # Save markdown summary
        md_file = report_dir / f"{report['report_id']}.md"
        self._save_markdown_report(report, md_file)
    
    def _save_markdown_report(self, report: Dict, filepath: Path):
        """Save human-readable markdown report."""
        with open(filepath, 'w') as f:
            f.write(f"# Tactical Ingestion Report\n\n")
            f.write(f"**Topic**: {report['topic']}\n")
            f.write(f"**Date**: {report['created_at']}\n")
            f.write(f"**Total Papers**: {report['total_papers_analyzed']}\n\n")
            
            f.write(f"## Tier Distribution\n\n")
            f.write(f"- **Tier 1 (High Priority)**: {len(report['tier_1_papers'])} papers\n")
            f.write(f"- **Tier 2 (Medium Priority)**: {len(report['tier_2_papers'])} papers\n")
            f.write(f"- **Tier 3 (Low Priority)**: {len(report['tier_3_papers'])} papers\n\n")
            
            if report['tier_1_papers']:
                f.write(f"## Top Tier 1 Papers\n\n")
                for paper in report['tier_1_papers'][:5]:
                    f.write(f"### {paper['paper_id']}\n")
                    f.write(f"**Title**: {paper['title']}\n")
                    f.write(f"**Score**: {paper['relevance_score']:.2f}\n")
                    f.write(f"**Keywords**: {', '.join(paper['keywords_found'])}\n\n")
            
            if "mcp_analysis" in report and report["mcp_analysis"].get("status") != "failed":
                f.write(f"## Enhanced Analysis\n\n")
                f.write(f"{json.dumps(report['mcp_analysis'], indent=2)}\n")
    
    def _empty_result(self, topic: str) -> Dict:
        """Return empty result when no papers found."""
        return {
            "report_id": f"triage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "topic": topic,
            "generation_counter": int(datetime.now(UTC).timestamp()),
            "created_at": datetime.now(UTC).isoformat(),
            "total_papers_analyzed": 0,
            "tier_1_papers": [],
            "tier_2_papers": [],
            "tier_3_papers": [],
            "error": "No papers found to analyze"
        }


def main():
    """Test the agent independently."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', default="Distributed Trust Verification", 
                       help='Topic to search for')
    parser.add_argument('--mock', action='store_true', 
                       help='Use mock MCP client')
    args = parser.parse_args()
    
    agent = TacticalIngestionAgent(use_mock=args.mock)
    report = agent.categorize_papers(args.topic)
    
    print(f"\nReport ID: {report['report_id']}")
    print(f"Check reports/phase2_triage/ directory for full results")


if __name__ == "__main__":
    main()