#!/usr/bin/env python3
"""Test agent execution directly without the flow."""

import asyncio
import sys
import os

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'PocketFlow'))
sys.path.append(os.path.dirname(__file__))

from nodes.shared_components import run_read_only_step, AgentStepResult

async def test_direct_agent():
    """Test agent execution directly."""
    print("=== TESTING DIRECT AGENT EXECUTION ===")
    
    prompt = "Read D:\\PROJECTS\\haios\\agents\\2a_agent\\A1\\A1_PROMPT_FILE_BASED.txt"
    file_path = "D:\\PROJECTS\\haios\\agents\\2a_agent\\A1\\A1_PROMPT_FILE_BASED.txt"
    
    print(f"Prompt: {prompt}")
    print(f"File: {file_path}")
    print()
    
    try:
        result: AgentStepResult = await run_read_only_step(prompt, file_path)
        
        print("=== RESULTS ===")
        print(f"Response text length: {len(result.response_text)}")
        print(f"Tool count: {result.tool_count}")
        print(f"Tools used: {result.tools_used}")
        print(f"Duration: {result.duration_ms}ms")
        print(f"Cost: ${result.cost_usd}")
        print(f"Error: {result.error}")
        
        if result.response_text:
            print(f"Response preview: {result.response_text[:200]}...")
        
        return len(result.response_text) > 0 and result.tool_count > 0
        
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_agent())
    print(f"\nSuccess: {success}")