#!/usr/bin/env python3
"""
Phase 1: Strategic Triage Agent
Compares external research topics against HAiOS canon to identify high-priority areas.
Implements deterministic routing and evidence-based decision making.
"""

import os
import sys
import json
import httpx
import hashlib
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from deterministic_router import DeterministicResearchRouter as DeterministicRouter
from builder_validator_pattern import ResearchBuilderAgent as BuilderAgent, ResearchValidatorAgent as ValidatorAgent

class StrategicTriageAgent(BuilderAgent):
    """
    Phase 1: Strategic analysis of research landscape against HAiOS needs.
    This is a BUILDER agent - it creates analysis but cannot validate its own work.
    """
    
    def __init__(self):
        super().__init__(agent_id="strategic_triage_builder")
        self.nocodb_url = os.getenv('NOCODB_API_URL', 'http://localhost:8081/api/v1')
        self.nocodb_token = os.getenv('NOCODB_API_TOKEN')
        self.llm_client = self._init_llm_client()
        self.router = DeterministicRouter()
        
    def _init_llm_client(self):
        """Initialize LLM client based on available API keys."""
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if anthropic_key:
            from anthropic import Anthropic
            return Anthropic(api_key=anthropic_key)
        elif openai_key:
            import openai
            openai.api_key = openai_key
            return openai
        else:
            # For testing without LLM - returns mock responses
            return MockLLMClient()
            
    def load_haios_canon(self) -> Dict[str, Any]:
        """Load current ADRs and open questions from the canon."""
        canon = {
            'adrs': [],
            'open_questions': [],
            'strategic_priorities': []
        }
        
        # Load ADRs from docs directory
        adr_path = Path(__file__).parent.parent.parent.parent / "docs" / "ADR"
        if adr_path.exists():
            canon['adrs'] = self._load_adrs(adr_path)
            
        # Extract open questions from ADRs
        canon['open_questions'] = self._extract_open_questions(canon['adrs'])
        
        # Define strategic priorities based on HAIOS architecture
        canon['strategic_priorities'] = [
            "Distributed agent coordination and governance",
            "Trust verification and evidence chains",
            "Deterministic security controls",
            "AI safety and alignment mechanisms",
            "Semantic validation of AI outputs"
        ]
        
        return canon
        
    def _load_adrs(self, adr_path: Path) -> List[Dict[str, Any]]:
        """Load and parse ADR files."""
        adrs = []
        for adr_file in adr_path.glob("ADR-OS-*.md"):
            try:
                content = adr_file.read_text()
                adr = {
                    'id': adr_file.stem,
                    'title': self._extract_title(content),
                    'status': self._extract_status(content),
                    'open_questions': self._extract_questions_from_adr(content)
                }
                adrs.append(adr)
            except Exception as e:
                self.log_error(f"Failed to load ADR {adr_file}: {e}")
        return adrs
        
    def _extract_open_questions(self, adrs: List[Dict]) -> List[str]:
        """Extract all open questions from ADRs."""
        questions = []
        for adr in adrs:
            questions.extend(adr.get('open_questions', []))
        return questions
        
    def analyze_research_landscape(self, 
                                 corpus_source: str,
                                 categories: List[str]) -> Dict[str, Any]:
        """
        Analyze research corpus against HAiOS needs using deterministic routing.
        """
        # Generate evidence for this analysis
        evidence = self.generate_evidence({
            'action': 'analyze_research_landscape',
            'corpus_source': corpus_source,
            'categories': categories,
            'timestamp': datetime.now(UTC).isoformat()
        })
        
        # Load canon for analysis
        canon = self.load_haios_canon()
        
        # Fetch recent papers from each category
        recent_papers = self._fetch_recent_papers(corpus_source, categories)
        
        # Check if we got any papers
        if not recent_papers:
            self.log_warning("No papers found from arXiv. Returning empty analysis.")
            return {
                'priorities': [],
                'metadata': {
                    'evidence': evidence,
                    'timestamp': datetime.now(UTC).isoformat(),
                    'corpus_source': corpus_source,
                    'categories': categories,
                    'papers_analyzed': 0,
                    'error': 'No papers found from arXiv'
                }
            }
        
        # Use deterministic routing to categorize papers by relevance
        categorized_papers = self._categorize_papers_deterministically(
            recent_papers, canon
        )
        
        # Analyze with LLM for deeper insights (but not for routing decisions)
        if self.llm_client:
            analysis = self._analyze_with_llm(canon, categorized_papers)
        else:
            analysis = self._analyze_without_llm(categorized_papers)
            
        # Structure the output with evidence chain
        priorities = self._structure_priorities(analysis, evidence)
        
        return priorities
        
    def _categorize_papers_deterministically(self, 
                                           papers: List[Dict],
                                           canon: Dict) -> Dict[str, List[Dict]]:
        """
        Use deterministic rules to categorize papers by relevance.
        No LLM routing decisions allowed.
        """
        categories = {
            'high_relevance': [],
            'medium_relevance': [],
            'low_relevance': []
        }
        
        # Define keyword mappings for each priority level
        high_keywords = [
            "trust", "verification", "evidence", "deterministic",
            "agent coordination", "distributed consensus", "byzantine",
            "formal verification", "security proof", "audit trail"
        ]
        
        medium_keywords = [
            "distributed systems", "multi-agent", "orchestration",
            "workflow", "pipeline", "validation", "testing",
            "architecture", "microservices", "event-driven"
        ]
        
        for paper in papers:
            title_lower = paper.get('title', '').lower()
            abstract_lower = paper.get('abstract', '').lower()
            full_text = f"{title_lower} {abstract_lower}"
            
            # High relevance: directly addresses HAIOS concerns
            if any(keyword in full_text for keyword in high_keywords):
                categories['high_relevance'].append(paper)
            # Medium relevance: related architectural patterns
            elif any(keyword in full_text for keyword in medium_keywords):
                categories['medium_relevance'].append(paper)
            # Low relevance: everything else
            else:
                categories['low_relevance'].append(paper)
                
        return categories
        
    def _fetch_recent_papers(self, source: str, categories: List[str]) -> List[Dict]:
        """Fetch recent paper metadata from source."""
        papers = []
        
        if source == "arxiv":
            for category in categories:
                try:
                    url = "http://export.arxiv.org/api/query"
                    params = {
                        "search_query": f"cat:{category}",
                        "sortBy": "submittedDate",
                        "sortOrder": "descending",
                        "max_results": 20
                    }
                    
                    response = httpx.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        # Parse arXiv XML response
                        parsed_papers = self._parse_arxiv_response(response.text)
                        papers.extend(parsed_papers)
                except Exception as e:
                    self.log_error(f"Failed to fetch papers for {category}: {e}")
                    
        return papers
        
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict]:
        """Parse arXiv API XML response."""
        papers = []
        
        # Simple XML parsing (in production, use proper XML parser)
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            self.log_error(f"Failed to parse arXiv XML response: {e}")
            return papers
        
        # Define namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Check if response contains error message
        error_elem = root.find('atom:error', ns)
        if error_elem is not None:
            self.log_error(f"arXiv API error: {error_elem.text}")
            return papers
        
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
        
    def _analyze_with_llm(self, canon: Dict, categorized_papers: Dict) -> Dict:
        """Use LLM for deeper analysis (not for routing decisions)."""
        prompt = self._build_analysis_prompt(canon, categorized_papers)
        
        try:
            if hasattr(self.llm_client, 'messages'):  # Anthropic
                response = self.llm_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            else:  # OpenAI or mock
                response = self.llm_client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.choices[0].message.content
                
            return json.loads(content)
        except Exception as e:
            self.log_error(f"LLM analysis failed: {e}")
            return self._analyze_without_llm(categorized_papers)
            
    def _analyze_without_llm(self, categorized_papers: Dict) -> Dict:
        """Fallback analysis without LLM."""
        priorities = []
        
        # Convert high relevance papers to priorities
        for paper in categorized_papers['high_relevance'][:5]:
            priorities.append({
                "topic": paper['title'][:100],
                "relevance_score": 8,
                "paper_ids": [paper['id']],
                "rationale": "High keyword match with HAIOS priorities"
            })
            
        return {"priorities": priorities}
        
    def _build_analysis_prompt(self, canon: Dict, papers: Dict) -> str:
        """Build prompt for strategic analysis."""
        return f"""
You are the Strategic Triage component of the Rhiza research mining system for HAiOS.

Your task is to analyze papers that have ALREADY been categorized by relevance
and provide deeper insights about their potential impact on HAiOS.

CURRENT HAIOS CONTEXT:
- Open ADR Questions: {json.dumps(canon['open_questions'][:5], indent=2)}
- Strategic Priorities: {json.dumps(canon['strategic_priorities'], indent=2)}

PRE-CATEGORIZED PAPERS:
High Relevance Papers: {len(papers['high_relevance'])}
Medium Relevance Papers: {len(papers['medium_relevance'])}
Low Relevance Papers: {len(papers['low_relevance'])}

Top High Relevance Papers:
{json.dumps([{
    'title': p['title'],
    'abstract': p['abstract'][:200] + '...'
} for p in papers['high_relevance'][:5]], indent=2)}

ANALYSIS REQUIRED:
1. For each high-relevance paper, explain HOW it could address HAiOS needs
2. Identify which open ADR questions might be answered
3. Suggest specific architectural components that could benefit
4. DO NOT re-categorize papers - work with the existing categorization

Output as JSON:
{{
    "priorities": [
        {{
            "topic": "specific research topic/theme",
            "relevance_score": 8,
            "open_questions": ["specific ADR questions addressed"],
            "impacted_adrs": ["ADR-OS-XXX"],
            "paper_ids": ["paper IDs exploring this topic"],
            "rationale": "detailed explanation of relevance",
            "specific_applications": ["concrete HAiOS applications"]
        }}
    ]
}}
"""
        
    def _structure_priorities(self, analysis: Dict, evidence: Dict) -> Dict[str, Any]:
        """Structure the final output with evidence chain."""
        generation_counter = self._get_next_generation_counter()
        
        report = {
            "report_id": f"priorities_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generation_counter": generation_counter,
            "analysis_timestamp": datetime.now(UTC).isoformat(),
            "evidence_chain": [evidence],
            "priorities": analysis.get("priorities", []),
            "corpus_source": "arxiv",
            "analysis_window": "last_30_days",
            "deterministic_routing": True,
            "validation_required": True
        }
        
        # Calculate integrity hash
        report["integrity_hash"] = self.calculate_hash(report)
        
        return report
        
    def _get_next_generation_counter(self) -> int:
        """Get the next generation counter from database."""
        # In production, query NocoDB for max generation_counter
        # For now, return timestamp-based counter
        return int(datetime.now().timestamp())
        
    def save_priorities_report(self, priorities: Dict[str, Any]) -> str:
        """Save priorities to database and return report path."""
        report_id = priorities["report_id"]
        
        # Save to NocoDB
        if self.nocodb_token:
            self._save_to_nocodb(priorities)
            
        # Also save as markdown for human review
        report_path = f"reports/Research_Priorities_{report_id}.md"
        self._generate_markdown_report(priorities, report_path)
        
        return report_path
        
    def _save_to_nocodb(self, priorities: Dict[str, Any]):
        """Save priorities to NocoDB database."""
        headers = {
            'xc-token': self.nocodb_token,
            'Content-Type': 'application/json'
        }
        
        data = {
            "priority_id": priorities["report_id"],
            "generation_counter": priorities["generation_counter"],
            "topics": priorities["priorities"],
            "corpus_source": priorities["corpus_source"],
            "analysis_window": priorities["analysis_window"]
        }
        
        try:
            response = httpx.post(
                f"{self.nocodb_url}/db/data/v1/rhiza_research/research_priorities",
                headers=headers,
                json=data
            )
            if response.status_code != 200:
                self.log_error(f"Failed to save to NocoDB: {response.text}")
        except Exception as e:
            self.log_error(f"NocoDB save failed: {e}")
            
    def _generate_markdown_report(self, priorities: Dict, report_path: str):
        """Generate human-readable markdown report."""
        report_dir = Path(__file__).parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)
        
        content = f"""# Research Priorities Report

**Report ID**: {priorities['report_id']}  
**Generated**: {priorities['analysis_timestamp']}  
**Generation Counter**: {priorities['generation_counter']}  
**Integrity Hash**: {priorities['integrity_hash']}

## Analysis Summary

- **Corpus Source**: {priorities['corpus_source']}
- **Analysis Window**: {priorities['analysis_window']}
- **Deterministic Routing**: {priorities['deterministic_routing']}
- **Total Priorities Identified**: {len(priorities['priorities'])}

## Top Research Priorities

"""
        
        for i, priority in enumerate(priorities['priorities'], 1):
            content += f"""
### {i}. {priority['topic']}

**Relevance Score**: {priority['relevance_score']}/10  
**Paper IDs**: {', '.join(priority.get('paper_ids', []))}

**Rationale**: {priority['rationale']}

**Open Questions Addressed**:
{chr(10).join(['- ' + q for q in priority.get('open_questions', [])])}

**Impacted ADRs**:
{chr(10).join(['- ' + adr for adr in priority.get('impacted_adrs', [])])}

**Specific Applications**:
{chr(10).join(['- ' + app for app in priority.get('specific_applications', [])])}

---
"""
        
        content += f"""
## Evidence Chain

```json
{json.dumps(priorities['evidence_chain'], indent=2)}
```

## Validation Required

This report requires validation by a separate validator agent before use.
"""
        
        with open(report_dir / report_path.split('/')[-1], 'w') as f:
            f.write(content)


class StrategicTriageValidator(ValidatorAgent):
    """Validator for Strategic Triage reports."""
    
    def validate(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a strategic triage report."""
        validation_result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = [
            "report_id", "generation_counter", "priorities",
            "integrity_hash", "evidence_chain"
        ]
        
        for field in required_fields:
            if field not in artifact:
                validation_result["valid"] = False
                validation_result["issues"].append(f"Missing required field: {field}")
                
        # Verify integrity hash
        if "integrity_hash" in artifact:
            computed_hash = self.calculate_hash({
                k: v for k, v in artifact.items() 
                if k != "integrity_hash"
            })
            if computed_hash != artifact["integrity_hash"]:
                validation_result["valid"] = False
                validation_result["issues"].append("Integrity hash mismatch")
                
        # Validate priorities structure
        if "priorities" in artifact:
            for i, priority in enumerate(artifact["priorities"]):
                if "relevance_score" not in priority:
                    validation_result["warnings"].append(
                        f"Priority {i} missing relevance_score"
                    )
                elif not (1 <= priority["relevance_score"] <= 10):
                    validation_result["issues"].append(
                        f"Priority {i} has invalid relevance_score"
                    )
                    
        return validation_result


class MockLLMClient:
    """Mock LLM client for testing without API keys."""
    
    def __init__(self):
        self.model_name = "mock-llm"
        
    class ChatCompletion:
        @staticmethod
        def create(**kwargs):
            # Return mock analysis
            return type('obj', (object,), {
                'choices': [type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': json.dumps({
                            "priorities": [
                                {
                                    "topic": "Distributed Trust Verification in Multi-Agent Systems",
                                    "relevance_score": 9,
                                    "open_questions": ["How to ensure trust in distributed agent decisions?"],
                                    "impacted_adrs": ["ADR-OS-021", "ADR-OS-035"],
                                    "rationale": "Directly addresses HAiOS trust engine requirements",
                                    "specific_applications": ["Agent output validation", "Evidence chain verification"]
                                }
                            ]
                        })
                    })()
                })]
            })()


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Strategic Triage Agent")
    parser.add_argument("--categories", nargs="+", 
                       default=["cs.AI", "cs.DC", "cs.SE"],
                       help="arXiv categories to analyze")
    parser.add_argument("--validate", type=str,
                       help="Path to report JSON to validate")
    
    args = parser.parse_args()
    
    if args.validate:
        # Run validator
        validator = StrategicTriageValidator(agent_id="strategic_triage_validator")
        with open(args.validate, 'r') as f:
            report = json.load(f)
        result = validator.validate(report)
        print(json.dumps(result, indent=2))
    else:
        # Run builder
        agent = StrategicTriageAgent()
        
        print("Running Strategic Triage Analysis...")
        print(f"Categories: {args.categories}")
        
        priorities = agent.analyze_research_landscape("arxiv", args.categories)
        report_path = agent.save_priorities_report(priorities)
        
        print(json.dumps({
            "status": "success",
            "report_path": report_path,
            "report_id": priorities["report_id"],
            "top_priorities": priorities["priorities"][:3],
            "validation_required": True
        }, indent=2))