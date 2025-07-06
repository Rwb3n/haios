#!/usr/bin/env python3
"""
Test script for Phase 1: Strategic Triage Agent
Run this to verify the implementation works correctly.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from adapters.phase1_strategic_triage import (
    StrategicTriageAgent, 
    StrategicTriageValidator
)

def test_strategic_triage():
    """Test the strategic triage agent."""
    print("="*50)
    print("TESTING PHASE 1: STRATEGIC TRIAGE")
    print("="*50)
    
    # Create agent
    agent = StrategicTriageAgent()
    
    # Test with a small set of categories
    categories = ["cs.AI", "cs.DC"]
    
    print(f"\n1. Analyzing research landscape for categories: {categories}")
    
    try:
        # Run analysis
        priorities = agent.analyze_research_landscape("arxiv", categories)
        
        print(f"\n2. Analysis complete. Found {len(priorities['priorities'])} priorities")
        
        # Save report
        report_path = agent.save_priorities_report(priorities)
        print(f"\n3. Report saved to: {report_path}")
        
        # Print top priorities
        print("\n4. Top Research Priorities:")
        for i, priority in enumerate(priorities['priorities'][:3], 1):
            print(f"\n   Priority {i}:")
            print(f"   - Topic: {priority.get('topic', 'N/A')}")
            print(f"   - Relevance: {priority.get('relevance_score', 'N/A')}/10")
            print(f"   - Rationale: {priority.get('rationale', 'N/A')[:100]}...")
        
        # Validate the report
        print("\n5. Validating report...")
        validator = StrategicTriageValidator(agent_id="strategic_triage_validator")
        validation_result = validator.validate(priorities)
        
        print(f"\n   Validation Result:")
        print(f"   - Valid: {validation_result['valid']}")
        print(f"   - Issues: {validation_result['issues']}")
        print(f"   - Warnings: {validation_result['warnings']}")
        
        if validation_result['valid']:
            print("\n✅ TEST PASSED: Strategic Triage working correctly!")
        else:
            print("\n❌ TEST FAILED: Validation issues found")
            
        return priorities
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_deterministic_routing():
    """Test that routing is deterministic."""
    print("\n" + "="*50)
    print("TESTING DETERMINISTIC ROUTING")
    print("="*50)
    
    agent = StrategicTriageAgent()
    
    # Create test papers
    test_papers = [
        {
            'id': '2401.00001',
            'title': 'Trust Verification in Multi-Agent Systems',
            'abstract': 'We present a formal verification approach for trust...'
        },
        {
            'id': '2401.00002', 
            'title': 'Deep Learning for Image Recognition',
            'abstract': 'A new CNN architecture for image classification...'
        },
        {
            'id': '2401.00003',
            'title': 'Distributed Consensus with Byzantine Fault Tolerance',
            'abstract': 'Novel protocol for achieving consensus with malicious agents...'
        }
    ]
    
    # Test categorization
    canon = agent.load_haios_canon()
    categorized = agent._categorize_papers_deterministically(test_papers, canon)
    
    print("\nCategorization Results:")
    print(f"- High Relevance: {len(categorized['high_relevance'])} papers")
    print(f"- Medium Relevance: {len(categorized['medium_relevance'])} papers") 
    print(f"- Low Relevance: {len(categorized['low_relevance'])} papers")
    
    # Verify deterministic behavior
    categorized2 = agent._categorize_papers_deterministically(test_papers, canon)
    
    if categorized == categorized2:
        print("\n✅ Routing is deterministic (same results on multiple runs)")
    else:
        print("\n❌ Routing is NOT deterministic!")

if __name__ == "__main__":
    # Test strategic triage
    priorities = test_strategic_triage()
    
    # Test deterministic routing
    test_deterministic_routing()
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETE")
    print("="*50)