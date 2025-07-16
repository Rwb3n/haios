"""
Shared components used by multiple nodes in the 2A orchestrator.
"""

import sys
import os
import time
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
    Run a single agent step with principle of least privilege.
    
    Args:
        prompt: The prompt to send to the agent
        tools: Whitelist of allowed tools (principle of least privilege)
    
    Returns:
        tuple: (response_text, tool_count)
    """
    start_time = time.time()
    # Principle of least privilege: explicitly allow only requested tools
    # Block all dangerous tools by default
    dangerous_tools = ["Bash", "Write", "WebFetch", "WebSearch", "Task"]
    
    # Adjust system prompt based on tool availability
    if not tools:
        system_prompt = "You are in text-only mode. Provide your response without using any tools."
    else:
        system_prompt = f"You have been granted minimal tool access: {tools}. Use only these tools for your specific task."
    
    options = ClaudeCodeOptions(
        allowed_tools=tools,
        disallowed_tools=dangerous_tools,
        system_prompt=system_prompt
    )
    
    response_text = ""
    tool_count = 0
    
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text
                elif isinstance(block, ToolUseBlock):
                    tool_count += 1
                    # Validate tool is in allowed list
                    if block.name not in tools:
                        print(f"  [VIOLATION] Agent used disallowed tool: {block.name}")
                    else:
                        file_path = block.input.get('file_path', 'N/A')
                        
                        # Enhanced logging with operation details
                        if block.name == "Read":
                            # For Read operations, we'll get the content length from the response later
                            print(f"  [Tool] {block.name}: {file_path}")
                        elif block.name == "Edit":
                            old_string = block.input.get('old_string', '')
                            new_string = block.input.get('new_string', '')
                            print(f"  [Tool] {block.name}: {file_path} (old: {len(old_string)} chars, new: {len(new_string)} chars)")
                        elif block.name == "Write":
                            content = block.input.get('content', '')
                            print(f"  [Tool] {block.name}: {file_path} ({len(content)} chars)")
                        else:
                            print(f"  [Tool] {block.name}: {file_path}")
    
    # Log final response character count and duration for observability
    duration_ms = int((time.time() - start_time) * 1000)
    if response_text:
        print(f"  [OK] Agent response ({len(response_text)} chars, {duration_ms}ms)")
    
    return response_text, tool_count


async def run_read_only_step(prompt: str, file_path: str = None) -> tuple[str, int]:
    """
    Run a read-only agent step - most restrictive privilege level.
    
    Args:
        prompt: The prompt to send to the agent
        file_path: Optional specific file path for Read tool
    
    Returns:
        tuple: (response_text, tool_count)
    """
    start_time = time.time()
    # Ultra-restrictive: only Read tool allowed
    options = ClaudeCodeOptions(
        allowed_tools=["Read"],
        disallowed_tools=["Edit", "Write", "Bash", "LS", "Glob", "Grep", "Task", "WebFetch", "WebSearch"],
        system_prompt="You are in read-only mode. You may only read the specific file requested. No other operations are permitted."
    )
    
    response_text = ""
    tool_count = 0
    
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text
                elif isinstance(block, ToolUseBlock):
                    tool_count += 1
                    # Validate read-only operation
                    if block.name != "Read":
                        print(f"  [VIOLATION] Read-only agent used: {block.name}")
                    elif file_path and block.input.get('file_path') != file_path:
                        print(f"  [VIOLATION] Read access to unauthorized file: {block.input.get('file_path')}")
                    else:
                        file_path_accessed = block.input.get('file_path', 'N/A')
                        print(f"  [Tool] {block.name}: {file_path_accessed}")
    
    # Log final response character count and duration for observability
    duration_ms = int((time.time() - start_time) * 1000)
    if response_text:
        print(f"  [OK] Read operation ({len(response_text)} chars, {duration_ms}ms)")
    
    return response_text, tool_count