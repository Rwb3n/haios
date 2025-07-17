#!/usr/bin/env python3
"""
Test script to verify consensus synthesis flow routing works correctly.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'PocketFlow'))
sys.path.append(os.path.dirname(__file__))

from flow_clean import create_2a_flow


async def test_consensus_synthesis():
    """Test that consensus synthesis is created when consensus is reached."""
    
    print("Testing Consensus Synthesis Flow Routing")
    print("=" * 50)
    
    # Create a test session directory
    test_session = "output_2A/test_consensus_synthesis"
    os.makedirs(test_session, exist_ok=True)
    
    # Create test dialogue with consensus already reached
    test_dialogue = {
        "metadata": {
            "created": "2025-07-17T13:30:00.000000",
            "status": "active",
            "max_rounds": 2
        },
        "adr": "Test ADR content",
        "question": "Test question for consensus synthesis",
        "dialogue": [
            {
                "round": 1,
                "role": "Architect-1",
                "timestamp": "2025-07-17T13:30:01.000000",
                "content": "I propose solution A.",
                "consensus": False
            },
            {
                "round": 1,
                "role": "Architect-2",
                "timestamp": "2025-07-17T13:30:02.000000",
                "content": "I agree with solution A and believe we have reached consensus.",
                "consensus": True
            }
        ]
    }
    
    # Write test dialogue file
    dialogue_path = f"{test_session}/dialogue.json"
    with open(dialogue_path, 'w') as f:
        json.dump(test_dialogue, f, indent=2)
    
    # Write test summary file
    summary_path = f"{test_session}/summary.md"
    with open(summary_path, 'w') as f:
        f.write("# Test Summary\nThis is a test summary file.\n")
    
    # Create shared state for flow execution
    shared_state = {
        "dialogue_path": dialogue_path,
        "round_num": 2,  # Start at round 2 to trigger consensus check
        "session_dir": test_session,
        "consensus_reached": False
    }
    
    try:
        # Create and run flow
        flow = create_2a_flow()
        
        print("Starting flow execution...")
        result = await flow.run_async(shared_state)
        
        print(f"Flow completed with result: {result}")
        
        # Check if consensus synthesis was created
        synthesis_path = f"{test_session}/consensus_synthesis.md"
        if os.path.exists(synthesis_path):
            print("[PASS] Consensus synthesis file created successfully")
            
            # Read and display synthesis content
            with open(synthesis_path, 'r') as f:
                content = f.read()
            
            print(f"Synthesis file size: {len(content)} characters")
            print("First 200 characters:")
            print(content[:200] + "..." if len(content) > 200 else content)
            
            return True
        else:
            print("[FAIL] Consensus synthesis file was not created")
            print(f"Expected file: {synthesis_path}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Flow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_consensus_synthesis())
    
    if success:
        print("\n[SUCCESS] Consensus synthesis flow test passed")
    else:
        print("\n[FAIL] Consensus synthesis flow test failed")