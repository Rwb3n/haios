#!/usr/bin/env python3
"""
Phase 2: Tactical Ingestion Agent
Categorizes papers into relevance tiers using simple keyword matching.
No LLM required for MVP - just deterministic rules.
"""

import os
import sys
import json
import httpx
from datetime import datetime, UTC
from typing import List, Dict, Any, Tuple
from pathlib import Path

class TacticalIngestionAgent:
    """
    Phase 2: Categorizes papers into tiers using simple rules.
    No LLM needed for MVP - just keyword matching.
    """
    
    def __init__(self):
        self.agent_id = "tactical_ingestion_v1"
        self.nocodb_url = os.getenv('NOCODB_API_URL', 'http://localhost:8081/api/v1')
        self.nocodb_token = os.getenv('NOCODB_API_TOKEN')
        
        # Define keyword sets for each tier
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
            "neural network training", "dataset", "benchmark",
            "image recognition", "natural language generation",
            "reinforcement learning", "gan", "transformer model"
        ]
        
    def triage_papers(self, topic: str, papers: List[Dict] = None) -> Dict[str, Any]:
        """
        Categorize papers into tiers based on relevance to topic.
        
        Args:
            topic: Research topic/theme to focus on
            papers: List of paper dictionaries (if None, fetches from topic)
            
        Returns:
            Triage report with papers sorted into three tiers
        """
        print(f"=== Phase 2: Tactical Ingestion ===")
        print(f"Topic: {topic}")
        
        # If no papers provided, fetch based on topic
        if papers is None:
            papers = self._fetch_papers_for_topic(topic)
        
        # Check if we have any papers to analyze
        if not papers:
            print("WARNING: No papers found to analyze")
            return {
                "report_id": f"triage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "topic": topic,
                "generation_counter": int(datetime.now().timestamp()),
                "created_at": datetime.now(UTC).isoformat(),
                "total_papers_analyzed": 0,
                "tier_1_papers": [],
                "tier_2_papers": [],
                "tier_3_papers": [],
                "error": "No papers found to analyze"
            }
            
        print(f"Analyzing {len(papers)} papers...")
        
        # Categorize each paper
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
        
        # Create triage report
        report = {
            "report_id": f"triage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "topic": topic,
            "generation_counter": int(datetime.now().timestamp()),
            "created_at": datetime.now(UTC).isoformat(),
            "total_papers_analyzed": len(papers),
            "tier_1_papers": tier_1,
            "tier_2_papers": tier_2,
            "tier_3_papers": tier_3,
            "analysis_criteria": {
                "tier_1_keywords": self.tier1_keywords[:10],  # Sample
                "tier_2_keywords": self.tier2_keywords[:10],  # Sample
                "method": "keyword_matching"
            }
        }
        
        print(f"Tier 1 (High Priority): {len(tier_1)} papers")
        print(f"Tier 2 (Medium Priority): {len(tier_2)} papers")
        print(f"Tier 3 (Low Priority): {len(tier_3)} papers")
        
        return report
        
    def _calculate_relevance(self, paper: Dict, topic: str) -> Tuple[int, float, List[str]]:
        """
        Calculate relevance tier and score for a paper.
        
        Returns:
            (tier, score, keywords_found)
        """
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        full_text = f"{title} {abstract}"
        
        # Check for exclusion keywords first
        for keyword in self.exclusion_keywords:
            if keyword in full_text:
                return (3, 0.1, [keyword])  # Tier 3
                
        # Count keyword matches
        tier1_matches = []
        tier2_matches = []
        
        for keyword in self.tier1_keywords:
            if keyword in full_text:
                tier1_matches.append(keyword)
                
        for keyword in self.tier2_keywords:
            if keyword in full_text:
                tier2_matches.append(keyword)
        
        # Calculate score and determine tier
        tier1_score = len(tier1_matches) * 0.3  # Higher weight for tier 1
        tier2_score = len(tier2_matches) * 0.1
        total_score = min(tier1_score + tier2_score, 1.0)
        
        # Topic relevance boost
        if topic.lower() in full_text:
            total_score = min(total_score + 0.2, 1.0)
            
        # Determine tier
        if tier1_matches and total_score >= 0.3:
            return (1, total_score, tier1_matches[:5])  # Tier 1
        elif tier2_matches or total_score >= 0.2:
            return (2, total_score, tier2_matches[:5])  # Tier 2
        else:
            return (3, total_score, [])  # Tier 3
            
    def _fetch_papers_for_topic(self, topic: str) -> List[Dict]:
        """
        Fetch papers related to a topic from arXiv.
        Simple implementation - searches for topic in all fields.
        """
        papers = []
        
        try:
            # Simple search query
            url = "https://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{topic}",
                "sortBy": "relevance",
                "max_results": 20
            }
            
            response = httpx.get(url, params=params, timeout=30)
            if response.status_code == 200:
                papers = self._parse_arxiv_response(response.text)
        except Exception as e:
            print(f"Warning: Failed to fetch papers: {e}")
            
        return papers
        
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
                'categories': [
                    cat.attrib['term'] 
                    for cat in entry.findall('atom:category', ns)
                ]
            }
            papers.append(paper)
            
        return papers
        
    def save_triage_report(self, report: Dict[str, Any]) -> str:
        """Save triage report to database and file."""
        # Save to NocoDB if configured
        if self.nocodb_token:
            try:
                self._save_to_nocodb(report)
                print("Saved to NocoDB")
            except Exception as e:
                print(f"Warning: Failed to save to NocoDB: {e}")
                
        # Save as JSON
        report_dir = Path(__file__).parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)
        
        json_path = report_dir / f"{report['report_id']}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Also save human-readable version
        self._save_markdown_report(report, report_dir)
        
        print(f"Report saved to: {json_path}")
        return str(json_path)
        
    def _save_to_nocodb(self, report: Dict[str, Any]):
        """Save triage report to NocoDB."""
        headers = {
            'xc-token': self.nocodb_token,
            'Content-Type': 'application/json'
        }
        
        data = {
            "report_id": report["report_id"],
            "topic": report["topic"],
            "generation_counter": report["generation_counter"],
            "tier_1_papers": json.dumps(report["tier_1_papers"]),
            "tier_2_papers": json.dumps(report["tier_2_papers"]),
            "tier_3_papers": json.dumps(report["tier_3_papers"]),
            "total_papers_analyzed": report["total_papers_analyzed"],
            "analysis_criteria": json.dumps(report["analysis_criteria"])
        }
        
        response = httpx.post(
            f"{self.nocodb_url}/db/data/v1/rhiza/triage_reports",
            headers=headers,
            json=data,
            timeout=10
        )
        response.raise_for_status()
        
    def _save_markdown_report(self, report: Dict, report_dir: Path):
        """Generate human-readable markdown report."""
        md_path = report_dir / f"{report['report_id']}.md"
        
        content = f"""# Triage Report: {report['topic']}

**Report ID**: {report['report_id']}  
**Generated**: {report['created_at']}  
**Total Papers Analyzed**: {report['total_papers_analyzed']}

## Summary

- **Tier 1 (High Priority)**: {len(report['tier_1_papers'])} papers
- **Tier 2 (Medium Priority)**: {len(report['tier_2_papers'])} papers  
- **Tier 3 (Low Priority)**: {len(report['tier_3_papers'])} papers

## Tier 1: High Priority Papers

These papers directly address HAiOS concerns and should be analyzed in Phase 3.

"""
        for i, paper in enumerate(report['tier_1_papers'], 1):
            content += f"""### {i}. {paper['title']}
- **Paper ID**: {paper['paper_id']}
- **Relevance Score**: {paper['relevance_score']:.2f}
- **Keywords Found**: {', '.join(paper['keywords_found'])}

"""

        content += """## Tier 2: Medium Priority Papers

These papers contain relevant architectural patterns and concepts.

"""
        for i, paper in enumerate(report['tier_2_papers'][:5], 1):  # Show top 5
            content += f"""### {i}. {paper['title']}
- **Paper ID**: {paper['paper_id']}
- **Relevance Score**: {paper['relevance_score']:.2f}

"""

        content += f"""## Analysis Method

- **Method**: Keyword-based deterministic matching
- **Tier 1 Keywords**: {', '.join(report['analysis_criteria']['tier_1_keywords'][:5])}...
- **Tier 2 Keywords**: {', '.join(report['analysis_criteria']['tier_2_keywords'][:5])}...
"""
        
        with open(md_path, 'w') as f:
            f.write(content)


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Tactical Ingestion Agent - Categorizes papers into tiers"
    )
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Research topic to analyze"
    )
    parser.add_argument(
        "--papers-file",
        type=str,
        help="JSON file with papers (from Phase 1 output)"
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=20,
        help="Maximum papers to analyze"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = TacticalIngestionAgent()
    
    # Load papers if provided
    papers = None
    if args.papers_file:
        with open(args.papers_file, 'r') as f:
            data = json.load(f)
            # Extract papers from Phase 1 report if available
            # This is a simplified approach - in production would be more robust
            papers = []
            
    # Run triage
    report = agent.triage_papers(args.topic, papers)
    output_path = agent.save_triage_report(report)
    
    # Show results
    print("\n=== Triage Complete ===")
    if report['tier_1_papers']:
        print("\nTop Tier 1 Papers:")
        for paper in report['tier_1_papers'][:3]:
            print(f"- {paper['title'][:80]}...")
            print(f"  Score: {paper['relevance_score']:.2f}, Keywords: {', '.join(paper['keywords_found'][:3])}")
    
    print(f"\nNext Step: Run Phase 3 on Tier 1 papers")
    if report['tier_1_papers']:
        print(f"Example: python phase3_crystal_seed.py --paper-id {report['tier_1_papers'][0]['paper_id']}")