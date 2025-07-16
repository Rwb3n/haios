"""
Shared components used by multiple nodes in the 2A orchestrator.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from claude_code_sdk import (
    query, 
    ClaudeCodeOptions, 
    AssistantMessage, 
    TextBlock, 
    ToolUseBlock,
    ResultMessage
)


async def run_agent_step(prompt: str, tools: list[str]) -> tuple[str, int]:
    """
    Run a single agent step and return (response_text, tool_count).
    
    EXACT COPY from original working 2a_orchestrator_working.py
    This is a utility function, not a node method.
    """
    options = ClaudeCodeOptions(allowed_tools=tools)
    
    response_text = ""
    tool_count = 0
    
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text
                elif isinstance(block, ToolUseBlock):
                    tool_count += 1
                    print(f"  [Tool] {block.name}: {block.input.get('file_path', 'N/A')}")
    
    return response_text, tool_count