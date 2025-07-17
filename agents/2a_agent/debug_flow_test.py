#!/usr/bin/env python3
"""
Debug flow test to isolate the routing issue.
"""

import asyncio
import sys
import os

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'PocketFlow'))
sys.path.append(os.path.dirname(__file__))

from pocketflow import AsyncFlow
from nodes import (
    ConsensusCheckNode,
    SummarizerNode,
    ReadPromptNode,
    UpdateDialogueNode
)

async def test_simple_flow():
    """Test a simple 2-node flow to isolate the issue."""
    print("=== DEBUGGING FLOW ROUTING ===")
    
    # Create simple 2-node flow
    read_prompt = ReadPromptNode("A1/A1_PROMPT_FILE_BASED.txt")
    update_dialogue = UpdateDialogueNode("Architect-1")
    
    # Simple connection
    read_prompt - "default" >> update_dialogue
    read_prompt - "error" >> None  # End on error
    
    update_dialogue - "continue" >> None
    update_dialogue - "consensus" >> None
    update_dialogue - "error" >> None
    
    # Create minimal shared state
    shared = {
        "round_num": 1,
        "dialogue_path": "output_2A/test_debug/dialogue.json",
        "session_dir": "output_2A/test_debug"
    }
    
    # Ensure test directory exists
    os.makedirs("output_2A/test_debug", exist_ok=True)
    
    # Create minimal dialogue file
    import json
    dialogue_data = {
        "dialogue": [],
        "metadata": {"test": True}
    }
    with open(shared["dialogue_path"], 'w') as f:
        json.dump(dialogue_data, f)
    
    # Create flow and test
    flow = AsyncFlow(start=read_prompt)
    
    print("Starting flow test...")
    print("Expected: ReadPromptNode -> UpdateDialogueNode")
    
    try:
        result = await flow.run_async(shared)
        print(f"Flow completed with result: {result}")
        print(f"Final shared state keys: {list(shared.keys())}")
        if "prompt_content" in shared:
            print(f"Prompt content length: {len(shared['prompt_content'])}")
        else:
            print("No prompt_content in shared state!")
    except Exception as e:
        print(f"Flow failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_flow())