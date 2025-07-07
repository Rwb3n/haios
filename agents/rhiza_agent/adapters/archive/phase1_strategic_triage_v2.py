#!/usr/bin/env python3
"""
Phase 1: Strategic Triage Agent (v2 - Refactored)
Identifies high-priority research themes relevant to HAiOS.
This version focuses ONLY on theme identification, not paper categorization.
"""

import os
import sys
import json
import httpx
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional
from pathlib import Path

class StrategicTriageAgent:
    """
    Phase 1: Strategic analysis of research landscape.
    ONLY identifies high-priority research topics.
    Does NOT categorize papers or perform deep analysis.
    """
    
    def __init__(self):
        self.agent_id = "strategic_triage_v2"
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
        
        # Default to mock client for testing
        print("Using mock LLM client (no API keys found)")
        return MockLLMClient()
            
    def analyze_research_landscape(self, 
                                 corpus_source: str = "arxiv",
                                 categories: List[str] = None) -> Dict[str, Any]:
        """
        Analyze research corpus to identify high-priority themes for HAiOS.
        
        This method ONLY:
        1. Fetches recent papers from arXiv
        2. Asks LLM to identify themes relevant to HAiOS
        3. Returns prioritized research topics
        
        It does NOT categorize individual papers or perform deep analysis.
        """
        if categories is None:
            categories = ["cs.AI", "cs.DC", "cs.SE"]
            
        print(f"Fetching recent papers from {corpus_source}...")
        recent_papers = self._fetch_recent_papers(corpus_source, categories)
        print(f"Found {len(recent_papers)} papers")
        
        print("Identifying high-priority themes...")
        priorities = self._identify_themes(recent_papers)
        
        # Structure the output
        report = {
            "report_id": f"priorities_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generation_counter": int(datetime.now().timestamp()),
            "created_at": datetime.now(UTC).isoformat(),
            "corpus_source": corpus_source,
            "categories_analyzed": categories,
            "total_papers_analyzed": len(recent_papers),
            "topics": priorities,
            "analysis_window": "last_7_days"
        }
        
        return report
        
    def _fetch_recent_papers(self, source: str, categories: List[str]) -> List[Dict]:
        """Fetch recent paper metadata from source."""
        papers = []
        
        if source == "arxiv":
            for category in categories:
                try:
                    url = "https://export.arxiv.org/api/query"
                    params = {
                        "search_query": f"cat:{category}",
                        "sortBy": "submittedDate",
                        "sortOrder": "descending",
                        "max_results": 10  # Reduced for MVP
                    }
                    
                    response = httpx.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        parsed_papers = self._parse_arxiv_response(response.text)
                        papers.extend(parsed_papers)
                except Exception as e:
                    print(f"Warning: Failed to fetch papers for {category}: {e}")
                    
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
                'published': entry.find('atom:published', ns).text,
                'categories': [
                    cat.attrib['term'] 
                    for cat in entry.findall('atom:category', ns)
                ]
            }
            papers.append(paper)
            
        return papers
        
    def _identify_themes(self, papers: List[Dict]) -> List[Dict[str, Any]]:
        """
        Use LLM to identify high-priority research themes.
        This is the ONLY job of Phase 1 - theme identification.
        """
        if not papers:
            return []
            
        prompt = self._build_analysis_prompt(papers)
        
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
                
            # Parse JSON response
            result = json.loads(content)
            return result.get("themes", [])
            
        except Exception as e:
            print(f"Warning: LLM analysis failed: {e}")
            # Fallback to simple keyword-based themes
            return self._fallback_theme_extraction(papers)
            
    def _build_analysis_prompt(self, papers: List[Dict]) -> str:
        """
        Build a SIMPLE prompt focused on theme identification.
        No complex analysis, no paper categorization.
        """
        # Prepare paper summaries (just titles for simplicity)
        paper_titles = [p['title'] for p in papers[:20]]  # Limit to 20 papers
        
        return f"""You are analyzing recent research papers to identify themes relevant to HAiOS.

HAiOS is a trust engine that orchestrates AI agents, focusing on:
- Trust verification and evidence chains
- Distributed agent coordination
- Deterministic security controls
- AI output validation
- Architectural governance

Recent paper titles:
{json.dumps(paper_titles, indent=2)}

Task: Identify 3-5 research themes from these papers that are most relevant to HAiOS.

For each theme, provide:
- A clear theme name
- Relevance score (1-10)
- Brief rationale for HAiOS relevance
- List of paper indices that relate to this theme

Output as JSON:
{{
    "themes": [
        {{
            "topic": "theme name",
            "relevance_score": 8,
            "rationale": "why this matters to HAiOS",
            "paper_indices": [0, 3, 7],
            "open_questions": ["what questions this might answer"],
            "impacted_adrs": ["ADR-OS-XXX"]
        }}
    ]
}}"""
        
    def _fallback_theme_extraction(self, papers: List[Dict]) -> List[Dict]:
        """Simple fallback theme extraction without LLM."""
        # Define theme keywords
        theme_keywords = {
            "Trust and Verification Systems": ["trust", "verification", "evidence", "proof", "audit"],
            "Multi-Agent Coordination": ["multi-agent", "coordination", "distributed", "consensus"],
            "AI Safety and Validation": ["safety", "validation", "alignment", "robustness"],
            "Distributed System Architecture": ["architecture", "microservice", "orchestration", "pipeline"]
        }
        
        theme_scores = {theme: 0 for theme in theme_keywords}
        theme_papers = {theme: [] for theme in theme_keywords}
        
        # Score each theme based on keyword matches
        for i, paper in enumerate(papers):
            text = f"{paper['title']} {paper['abstract']}".lower()
            for theme, keywords in theme_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        theme_scores[theme] += 1
                        if i not in theme_papers[theme]:
                            theme_papers[theme].append(i)
                        
        # Convert to output format
        themes = []
        for theme, score in theme_scores.items():
            if score > 0:
                themes.append({
                    "topic": theme,
                    "relevance_score": min(10, score * 2),  # Simple scoring
                    "rationale": f"Found {score} papers with relevant keywords",
                    "paper_indices": theme_papers[theme][:5],  # Limit to 5 papers
                    "open_questions": [],
                    "impacted_adrs": []
                })
                
        # Sort by relevance score
        themes.sort(key=lambda x: x['relevance_score'], reverse=True)
        return themes[:5]  # Return top 5 themes
        
    def save_priorities_report(self, report: Dict[str, Any]) -> str:
        """Save priorities to database and return report path."""
        # Save to NocoDB if configured
        if self.nocodb_token:
            try:
                self._save_to_nocodb(report)
                print("Saved to NocoDB")
            except Exception as e:
                print(f"Warning: Failed to save to NocoDB: {e}")
                
        # Save as JSON for later processing
        report_dir = Path(__file__).parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)
        
        json_path = report_dir / f"{report['report_id']}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"Report saved to: {json_path}")
        return str(json_path)
        
    def _save_to_nocodb(self, report: Dict[str, Any]):
        """Save priorities to NocoDB database."""
        headers = {
            'xc-token': self.nocodb_token,
            'Content-Type': 'application/json'
        }
        
        data = {
            "priority_id": report["report_id"],
            "generation_counter": report["generation_counter"],
            "topics": json.dumps(report["topics"]),  # JSON column
            "corpus_source": report["corpus_source"],
            "analysis_window": report["analysis_window"]
        }
        
        response = httpx.post(
            f"{self.nocodb_url}/db/data/v1/rhiza/research_priorities",
            headers=headers,
            json=data,
            timeout=10
        )
        response.raise_for_status()


class MockLLMClient:
    """Mock LLM client for testing without API keys."""
    
    def complete(self, prompt: str) -> str:
        """Return mock theme analysis."""
        return json.dumps({
            "themes": [
                {
                    "topic": "Distributed Trust Verification in Multi-Agent Systems",
                    "relevance_score": 9,
                    "rationale": "Directly addresses HAiOS trust engine requirements",
                    "paper_indices": [0, 2, 5],
                    "open_questions": ["How to ensure trust in distributed agent decisions?"],
                    "impacted_adrs": ["ADR-OS-021", "ADR-OS-035"]
                },
                {
                    "topic": "Deterministic Security Controls for AI Systems",
                    "relevance_score": 8,
                    "rationale": "Aligns with HAiOS security architecture needs",
                    "paper_indices": [1, 3, 7],
                    "open_questions": ["How to implement deterministic routing without LLM decisions?"],
                    "impacted_adrs": ["ADR-OS-024"]
                },
                {
                    "topic": "Evidence-Based Validation Frameworks",
                    "relevance_score": 7,
                    "rationale": "Supports HAiOS evidence chain requirements",
                    "paper_indices": [4, 6, 8],
                    "open_questions": ["How to create tamper-proof evidence chains?"],
                    "impacted_adrs": ["ADR-OS-023"]
                }
            ]
        })


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Strategic Triage Agent v2 - Identifies research themes"
    )
    parser.add_argument(
        "--categories", 
        nargs="+", 
        default=["cs.AI", "cs.DC", "cs.SE"],
        help="arXiv categories to analyze"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: auto-generated)"
    )
    
    args = parser.parse_args()
    
    # Run analysis
    agent = StrategicTriageAgent()
    
    print("=== Phase 1: Strategic Triage v2 ===")
    print(f"Analyzing categories: {args.categories}")
    
    report = agent.analyze_research_landscape("arxiv", args.categories)
    output_path = agent.save_priorities_report(report)
    
    # Print summary
    print("\n=== Analysis Complete ===")
    print(f"Report ID: {report['report_id']}")
    print(f"Papers Analyzed: {report['total_papers_analyzed']}")
    print(f"Themes Identified: {len(report['topics'])}")
    
    if report['topics']:
        print("\nTop Themes:")
        for i, theme in enumerate(report['topics'][:3], 1):
            print(f"{i}. {theme['topic']} (Score: {theme['relevance_score']}/10)")
    
    print(f"\nFull report saved to: {output_path}")