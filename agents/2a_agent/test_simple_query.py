#!/usr/bin/env python3
"""Test the exact same pattern as the working example."""

import anyio
from claude_code_sdk import (
    AssistantMessage,
    ClaudeCodeOptions,
    ResultMessage,
    TextBlock,
    query,
)

async def test_read_prompt():
    """Test reading a prompt file using the same pattern as working example."""
    print("=== Testing Read Prompt (Working Example Pattern) ===")
    
    # Use same options pattern as working example
    options = ClaudeCodeOptions(
        allowed_tools=["Read"],
        system_prompt="You are a helpful file assistant.",
    )
    
    prompt = "Read D:\\PROJECTS\\haios\\agents\\2a_agent\\A1\\A1_PROMPT_FILE_BASED.txt"
    print(f"Prompt: {prompt}")
    
    message_count = 0
    async for message in query(prompt=prompt, options=options):
        message_count += 1
        print(f"[DEBUG] Received message #{message_count}: {type(message).__name__}")
        
        if isinstance(message, AssistantMessage):
            print(f"[DEBUG] AssistantMessage with {len(message.content)} blocks")
            for i, block in enumerate(message.content):
                print(f"[DEBUG] Block {i}: {type(block).__name__}")
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text[:100]}...")  # First 100 chars
        elif isinstance(message, ResultMessage):
            print(f"[DEBUG] ResultMessage: cost=${message.total_cost_usd if message.total_cost_usd else 0}")
    
    print(f"[DEBUG] Query complete. Total messages: {message_count}")
    return message_count > 0

if __name__ == "__main__":
    success = anyio.run(test_read_prompt)
    print(f"Success: {success}")