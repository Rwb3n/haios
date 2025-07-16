"""
Test the basic structure of the clean PocketFlow implementation
without requiring Claude SDK to be fully functional.
"""

import json
import asyncio
from pathlib import Path
from nodes import ConsensusCheckNode
from nodes.__legacy.architect1_node import Architect1Node  
from nodes.__legacy.architect2_node import Architect2Node
from nodes.__legacy.dialogue_summary_node import DialogueSummaryNode
from flow_clean import create_2a_flow, create_single_round_flow


async def test_node_structure():
    """Test that nodes are properly structured."""
    print("=== Testing Node Structure ===")
    
    # Test node creation
    consensus_check = ConsensusCheckNode()
    architect1 = Architect1Node()
    architect2 = Architect2Node()
    summary = DialogueSummaryNode()
    
    print("[OK] All nodes created successfully")
    
    # Test shared store structure
    shared = {
        "round_num": 1,
        "dialogue_path": "output_2A/dialogue_working.json",
        "max_rounds": 3
    }
    
    # Test prep methods (should not fail)
    try:
        prep_result = await consensus_check.prep_async(shared)
        print("[OK] ConsensusCheckNode.prep_async() works")
        
        prep_result = await architect1.prep_async(shared)
        print("[OK] Architect1Node.prep_async() works")
        
        prep_result = await architect2.prep_async(shared)
        print("[OK] Architect2Node.prep_async() works")
        
        prep_result = await summary.prep_async(shared)
        print("[OK] DialogueSummaryNode.prep_async() works")
        
    except Exception as e:
        print(f"[ERROR] Prep method failed: {e}")
        return False
    
    return True


async def test_flow_structure():
    """Test that flows are properly structured."""
    print("\n=== Testing Flow Structure ===")
    
    try:
        # Test flow creation
        main_flow = create_2a_flow()
        print("✓ Main 2A flow created successfully")
        
        single_flow = create_single_round_flow()
        print("✓ Single round flow created successfully")
        
        # Test flow has start node
        assert main_flow.start_node is not None
        assert single_flow.start_node is not None
        print("✓ Flows have start nodes")
        
        # Test flow connections exist
        start_node = main_flow.start_node
        assert hasattr(start_node, 'successors')
        assert len(start_node.successors) > 0
        print("✓ Flow connections exist")
        
    except Exception as e:
        print(f"✗ Flow structure test failed: {e}")
        return False
    
    return True


def test_file_structure():
    """Test that required files exist."""
    print("\n=== Testing File Structure ===")
    
    required_files = [
        "A1/A1_PROMPT_FILE_BASED.txt",
        "A2/A2_PROMPT_FILE_BASED.txt",
        "input_2A/initial_question.txt"
    ]
    
    required_dirs = [
        "A1",
        "A2", 
        "input_2A",
        "output_2A"
    ]
    
    # Check directories
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ Directory {dir_name} exists")
        else:
            print(f"✗ Directory {dir_name} missing")
            return False
    
    # Check files
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✓ File {file_name} exists")
        else:
            print(f"✗ File {file_name} missing")
            return False
    
    return True


def test_dialogue_file_structure():
    """Test dialogue file structure."""
    print("\n=== Testing Dialogue File Structure ===")
    
    dialogue_path = "output_2A/dialogue_working.json"
    
    if not Path(dialogue_path).exists():
        print(f"✗ Dialogue file {dialogue_path} doesn't exist")
        return False
    
    try:
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        required_keys = ['metadata', 'adr', 'question', 'dialogue']
        for key in required_keys:
            if key in data:
                print(f"✓ Dialogue has {key} field")
            else:
                print(f"✗ Dialogue missing {key} field")
                return False
        
        if isinstance(data['dialogue'], list):
            print("✓ Dialogue field is a list")
        else:
            print("✗ Dialogue field is not a list")
            return False
        
        print(f"✓ Dialogue file structure is valid")
        print(f"  - Question: {data['question'][:50]}...")
        print(f"  - Dialogue entries: {len(data['dialogue'])}")
        
    except Exception as e:
        print(f"✗ Failed to read dialogue file: {e}")
        return False
    
    return True


async def main():
    """Run all tests."""
    print("=== 2A Orchestrator Structure Tests ===\n")
    
    tests = [
        test_file_structure,
        test_dialogue_file_structure,
        test_node_structure,
        test_flow_structure,
    ]
    
    results = []
    for test in tests:
        if asyncio.iscoroutinefunction(test):
            result = await test()
        else:
            result = test()
        results.append(result)
    
    print(f"\n=== Test Results ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All structure tests passed!")
        print("The clean PocketFlow implementation is properly structured.")
        return True
    else:
        print("✗ Some tests failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)