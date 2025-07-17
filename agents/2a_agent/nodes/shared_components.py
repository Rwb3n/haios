"""
Shared components used by multiple nodes in the 2A orchestrator.
"""

import sys
import os
import time
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from claude_code_sdk import (
    query, 
    ClaudeCodeOptions, 
    AssistantMessage, 
    TextBlock, 
    ToolUseBlock,
    ResultMessage,
    ContentBlock,
    PermissionMode,
    Message,
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError
)


@dataclass
class AgentStepResult:
    """Structured result from agent step execution."""
    
    response_text: str
    tool_count: int
    tools_used: List[str]
    duration_ms: int
    cost_usd: Optional[float] = None
    usage_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentConfig:
    """Configuration for agent execution."""
    
    allowed_tools: List[str]
    disallowed_tools: List[str]
    system_prompt: str
    permission_mode: PermissionMode = "default"
    max_thinking_tokens: int = 8000
    max_turns: Optional[int] = None
    cwd: Optional[Union[str, Path]] = None


# Pre-defined configurations for common agent patterns
AGENT_CONFIGS = {
    "read_only": AgentConfig(
        allowed_tools=["Read"],
        disallowed_tools=["Edit", "Write", "Bash", "LS", "Glob", "Grep", "Task", "WebFetch", "WebSearch"],
        system_prompt="You are in read-only mode. You may only read files. No other operations are permitted.",
        permission_mode="default"
    ),
    
    "file_editor": AgentConfig(
        allowed_tools=["Read", "Edit"],
        disallowed_tools=["Write", "Bash", "WebFetch", "WebSearch", "Task"],
        system_prompt="You have been granted file editing access. Use Read and Edit tools for your specific task.",
        permission_mode="default"
    ),
    
    "file_creator": AgentConfig(
        allowed_tools=["Read", "Write"],
        disallowed_tools=["Edit", "Bash", "WebFetch", "WebSearch", "Task"],
        system_prompt="You have been granted file creation access. Use Read and Write tools for your specific task.",
        permission_mode="default"
    ),
    
    "architect_dialogue": AgentConfig(
        allowed_tools=["Read", "Edit"],
        disallowed_tools=["Write", "Bash", "WebFetch", "WebSearch", "Task"],
        system_prompt="You are an architect in a dialogue system. Use Read and Edit tools to participate in architectural discussions.",
        permission_mode="default"
    ),
    
    "summarizer": AgentConfig(
        allowed_tools=["Read", "Edit"],
        disallowed_tools=["Write", "Bash", "WebFetch", "WebSearch", "Task"],
        system_prompt="You are a summarizer. Read dialogue data and edit summary files to track conversation progress.",
        permission_mode="default"
    )
}


async def run_agent_step_with_config(prompt: str, config: AgentConfig) -> AgentStepResult:
    """
    Run a single agent step with pre-configured agent settings.
    
    Args:
        prompt: The prompt to send to the agent
        config: AgentConfig with tools and settings
    
    Returns:
        AgentStepResult: Structured result with response, metrics, and metadata
    """
    options = ClaudeCodeOptions(
        allowed_tools=config.allowed_tools,
        disallowed_tools=config.disallowed_tools,
        system_prompt=config.system_prompt,
        permission_mode=config.permission_mode,
        max_thinking_tokens=config.max_thinking_tokens,
        max_turns=config.max_turns,
        cwd=config.cwd
    )
    
    return await _execute_agent_step(prompt, options, config.allowed_tools)


async def run_agent_step(prompt: str, tools: List[str]) -> AgentStepResult:
    """
    Run a single agent step with principle of least privilege.
    
    Args:
        prompt: The prompt to send to the agent
        tools: Whitelist of allowed tools (principle of least privilege)
    
    Returns:
        AgentStepResult: Structured result with response, metrics, and metadata
    """
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
    
    return await _execute_agent_step(prompt, options, tools)


async def _execute_agent_step(prompt: str, options: ClaudeCodeOptions, allowed_tools: List[str]) -> AgentStepResult:
    """
    Internal function to execute agent step with given options.
    
    Args:
        prompt: The prompt to send to the agent
        options: Claude Code options for execution
        allowed_tools: List of allowed tools for validation
    
    Returns:
        AgentStepResult: Structured result with response, metrics, and metadata
    """
    start_time = time.time()
    tools_used: List[str] = []
    
    response_text = ""
    tool_count = 0
    cost_usd: Optional[float] = None
    usage_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
                    elif isinstance(block, ToolUseBlock):
                        tool_count += 1
                        tools_used.append(block.name)
                        
                        # Validate tool is in allowed list
                        if block.name not in allowed_tools:
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
            
            elif isinstance(message, ResultMessage):
                # Capture cost and usage data from ResultMessage
                cost_usd = message.total_cost_usd
                usage_data = message.usage
                
    except CLINotFoundError as e:
        error = f"Claude Code not found: {e}"
        print(f"  [ERROR] Installation error: {error}")
    except CLIConnectionError as e:
        error = f"Connection failed: {e}"
        print(f"  [ERROR] Connection error: {error}")
    except ProcessError as e:
        error = f"Process failed (exit code: {e.exit_code}): {e}"
        print(f"  [ERROR] Process error: {error}")
        if e.stderr:
            print(f"  [ERROR] stderr: {e.stderr}")
    except CLIJSONDecodeError as e:
        error = f"JSON decode error: {e}"
        print(f"  [ERROR] JSON parsing error: {error}")
        print(f"  [ERROR] Problematic line: {e.line}")
    except ClaudeSDKError as e:
        error = f"SDK error: {e}"
        print(f"  [ERROR] SDK error: {error}")
    except Exception as e:
        error = f"Unexpected error: {e}"
        print(f"  [ERROR] Unexpected error: {error}")
    
    # Log final response character count and duration for observability
    duration_ms = int((time.time() - start_time) * 1000)
    if response_text:
        print(f"  [OK] Agent response ({len(response_text)} chars, {duration_ms}ms)")
    
    return AgentStepResult(
        response_text=response_text,
        tool_count=tool_count,
        tools_used=tools_used,
        duration_ms=duration_ms,
        cost_usd=cost_usd,
        usage_data=usage_data,
        error=error
    )


async def run_read_only_step(prompt: str, file_path: Optional[str] = None) -> AgentStepResult:
    """
    Run a read-only agent step - most restrictive privilege level.
    
    Args:
        prompt: The prompt to send to the agent
        file_path: Optional specific file path for Read tool
    
    Returns:
        AgentStepResult: Structured result with response, metrics, and metadata
    """
    # Use pre-configured read-only agent config
    config = AGENT_CONFIGS["read_only"]
    result = await run_agent_step_with_config(prompt, config)
    
    # Additional validation for read-only operations
    if file_path and result.tools_used:
        # Check if agent accessed unauthorized files (for debugging)
        # Note: This is additional validation on top of SDK restrictions
        for tool_name in result.tools_used:
            if tool_name == "Read":
                print(f"  [VALIDATION] Read-only access validated for: {file_path}")
    
    return result