#!/usr/bin/env python3
"""Test using exact same pattern as working example."""

import anyio
from claude_code_sdk import (
    AssistantMessage,
    ClaudeCodeOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

async def test_exact_pattern():
    """Test exact pattern from working example."""
    print("=== Testing Exact Working Pattern ===")
    
    options = ClaudeCodeOptions(
        allowed_tools=["Read"],
        system_prompt="You are a helpful file assistant.",
    )
    
    prompt = "Read D:\\PROJECTS\\haios\\agents\\2a_agent\\A1\\A1_PROMPT_FILE_BASED.txt"
    print(f"Prompt: {prompt}")
    
    message_count = 0
    tool_count = 0
    response_text = ""
    
    async for message in query(prompt=prompt, options=options):
        message_count += 1
        print(f"[DEBUG] Received message #{message_count}: {type(message).__name__}")
        
        if isinstance(message, AssistantMessage):
            print(f"[DEBUG] AssistantMessage with {len(message.content)} blocks")
            for i, block in enumerate(message.content):
                print(f"[DEBUG] Block {i}: {type(block).__name__}")
                if isinstance(block, TextBlock):
                    response_text += block.text
                    print(f"Claude response: {len(block.text)} chars")
                elif isinstance(block, ToolUseBlock):
                    tool_count += 1
                    print(f"Tool used: {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"[DEBUG] ResultMessage: cost=${message.total_cost_usd if message.total_cost_usd else 0}")
    
    print(f"[DEBUG] Query complete. Total messages: {message_count}")
    print(f"[DEBUG] Total tools used: {tool_count}")
    print(f"[DEBUG] Response length: {len(response_text)}")
    
    return message_count > 0 and (tool_count > 0 or len(response_text) > 0)

if __name__ == "__main__":
    success = anyio.run(test_exact_pattern)
    print(f"Success: {success}")