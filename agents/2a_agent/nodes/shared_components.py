"""
Shared components used by multiple nodes in the 2A orchestrator.

Enhanced with Hook Validation System for Shield 2 (Dynamic Defense).
"""

import sys
import os
import time
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
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

# Hook validation system imports (Shield 2)
try:
    from .hook_validation_nodes import (
        BaseHookNode, 
        PreValidationHookNode, 
        PostValidationHookNode,
        ValidationRule,
        ValidationResult,
        ValidationRuleType,
        POCKETFLOW_PATTERN_RULES,
        HAIOS_COMPLIANCE_RULES
    )
    HOOKS_AVAILABLE = True
except ImportError:
    HOOKS_AVAILABLE = False
    print("  [WARNING] Hook validation system not available")


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
class StepMetrics:
    """Minimal step metrics for tracking (Phase 1)."""
    
    step_name: str
    node_name: str
    start_time: float
    end_time: Optional[float] = None
    
    # Performance tracking
    duration_ms: int = 0
    cost_usd: float = 0.0
    chars_generated: int = 0
    
    # Tool usage
    tools_used: List[str] = field(default_factory=list)
    tool_count: int = 0
    
    # Status
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class RoundMetrics:
    """Round-level metrics aggregation (Phase 2)."""
    
    round_number: int
    start_time: float
    end_time: Optional[float] = None
    
    # Tool usage aggregation
    tools_used: Dict[str, int] = field(default_factory=dict)  # {"Read": 3, "Edit": 2}
    total_tools: int = 0
    
    # Performance aggregation
    total_duration_ms: int = 0
    total_cost_usd: float = 0.0
    total_chars_generated: int = 0
    
    # Step-level breakdown
    step_metrics: List[StepMetrics] = field(default_factory=list)
    
    # Round outcome
    consensus_reached: bool = False
    consensus_architect: Optional[str] = None
    
    # Status tracking
    successful_steps: int = 0
    failed_steps: int = 0


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
    
    # Calculate final duration
    duration_ms = int((time.time() - start_time) * 1000)
    
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


# ============================================================================
# HOOK-AWARE AGENT EXECUTION (SHIELD 2 - DYNAMIC DEFENSE)
# ============================================================================

async def run_agent_step_with_hooks(
    prompt: str, 
    tools: List[str], 
    pre_hooks: Optional[List[BaseHookNode]] = None,
    post_hooks: Optional[List[BaseHookNode]] = None,
    shared_state: Optional[Dict[str, Any]] = None
) -> AgentStepResult:
    """
    Run agent step with hook validation system for Shield 2 (Dynamic Defense).
    
    Provides defense-in-depth protection against "benevolent misalignment" 
    through pre- and post-execution validation hooks.
    
    Args:
        prompt: The prompt to send to the agent
        tools: Whitelist of allowed tools
        pre_hooks: Optional list of pre-execution validation hooks
        post_hooks: Optional list of post-execution validation hooks  
        shared_state: Optional shared state for hook context
        
    Returns:
        AgentStepResult: Enhanced with hook validation results
    """
    if not HOOKS_AVAILABLE:
        print("  [HOOK_WARNING] Hook system not available, falling back to standard execution")
        return await run_agent_step(prompt, tools)
    
    shared_state = shared_state or {}
    start_time = time.time()
    
    # Store input context for hooks
    shared_state.update({
        "input_prompt": prompt,
        "allowed_tools": tools,
        "hook_execution_start": start_time
    })
    
    # ========================================================================
    # PHASE 1: PRE-EXECUTION VALIDATION (Shield 2 Input Validation)
    # ========================================================================
    
    if pre_hooks:
        print(f"  [HOOK_SYSTEM] Running {len(pre_hooks)} pre-execution validation hooks...")
        
        for hook in pre_hooks:
            try:
                # Execute hook validation
                hook_context = await hook.prep_async(shared_state)
                validation_result: ValidationResult = await hook.exec_async(hook_context)
                
                # Process hook results
                if validation_result.has_errors:
                    error_msg = f"Pre-validation failed: {', '.join(validation_result.rule_violations)}"
                    print(f"  [HOOK_BLOCK] {error_msg}")
                    
                    # Return early with validation failure
                    return AgentStepResult(
                        response_text=f"BLOCKED: {error_msg}",
                        tool_count=0,
                        tools_used=[],
                        duration_ms=int((time.time() - start_time) * 1000),
                        error=error_msg
                    )
                
                if validation_result.has_warnings:
                    for warning in validation_result.warnings:
                        print(f"  [HOOK_WARNING] {warning}")
                
                # Store hook results
                shared_state[f"pre_hook_{hook.node_name}_result"] = validation_result
                
            except Exception as e:
                error_msg = f"Pre-hook execution failed: {hook.node_name} - {str(e)}"
                print(f"  [HOOK_ERROR] {error_msg}")
                
                # Fail-safe: Continue execution but log error
                shared_state[f"pre_hook_{hook.node_name}_error"] = str(e)
    
    # ========================================================================
    # PHASE 2: AGENT EXECUTION (Standard Agent Operations)
    # ========================================================================
    
    print(f"  [HOOK_SYSTEM] Pre-validation passed, executing agent with {len(tools)} tools...")
    agent_result = await run_agent_step(prompt, tools)
    
    # Store agent results for post-hooks
    shared_state.update({
        "last_agent_response": agent_result.response_text,
        "last_tools_used": agent_result.tools_used,
        "last_operation_duration": agent_result.duration_ms,
        "last_agent_error": agent_result.error
    })
    
    # ========================================================================
    # PHASE 3: POST-EXECUTION VALIDATION (Shield 2 Output Validation)
    # ========================================================================
    
    if post_hooks and not agent_result.error:
        print(f"  [HOOK_SYSTEM] Running {len(post_hooks)} post-execution validation hooks...")
        
        for hook in post_hooks:
            try:
                # Execute post-validation hook
                hook_context = await hook.prep_async(shared_state)
                validation_result: ValidationResult = await hook.exec_async(hook_context)
                
                # Process post-validation results
                if validation_result.has_errors:
                    error_msg = f"Post-validation failed: {', '.join(validation_result.rule_violations)}"
                    print(f"  [HOOK_ROLLBACK] {error_msg}")
                    
                    # Attempt rollback if supported
                    if hasattr(hook, 'trigger_rollback'):
                        rollback_success = await hook.trigger_rollback(error_msg)
                        if rollback_success:
                            print(f"  [HOOK_ROLLBACK] Operation successfully rolled back")
                        else:
                            print(f"  [HOOK_ROLLBACK] Rollback failed - manual intervention required")
                    
                    # Return with rollback information
                    agent_result.error = f"Post-validation failure (rollback {'successful' if rollback_success else 'failed'}): {error_msg}"
                    break
                
                if validation_result.has_warnings:
                    for warning in validation_result.warnings:
                        print(f"  [HOOK_WARNING] {warning}")
                
                # Store post-hook results
                shared_state[f"post_hook_{hook.node_name}_result"] = validation_result
                
            except Exception as e:
                error_msg = f"Post-hook execution failed: {hook.node_name} - {str(e)}"
                print(f"  [HOOK_ERROR] {error_msg}")
                shared_state[f"post_hook_{hook.node_name}_error"] = str(e)
    
    # ========================================================================
    # PHASE 4: FINAL RESULT PROCESSING
    # ========================================================================
    
    total_duration = int((time.time() - start_time) * 1000)
    hook_overhead = total_duration - agent_result.duration_ms
    
    print(f"  [HOOK_SYSTEM] Hook-aware execution completed (total: {total_duration}ms, overhead: {hook_overhead}ms)")
    
    # Enhanced result with hook information
    if agent_result.usage_data is None:
        agent_result.usage_data = {}
    
    agent_result.usage_data.update({
        "hook_system_enabled": True,
        "hook_overhead_ms": hook_overhead,
        "pre_hooks_executed": len(pre_hooks) if pre_hooks else 0,
        "post_hooks_executed": len(post_hooks) if post_hooks else 0,
        "hook_validation_results": {
            key: value for key, value in shared_state.items() 
            if key.endswith("_result") or key.endswith("_error")
        }
    })
    
    return agent_result


def create_default_pattern_protection_hooks() -> Tuple[List[BaseHookNode], List[BaseHookNode]]:
    """
    Create default pre- and post-hooks for architectural pattern protection.
    
    Returns:
        Tuple of (pre_hooks, post_hooks) with standard validation rules
    """
    if not HOOKS_AVAILABLE:
        return [], []
    
    # Pre-execution hooks for input validation
    pre_hooks = [
        PreValidationHookNode([
            ValidationRule(
                name="basic_safety_check",
                rule_type=ValidationRuleType.PATTERN,
                pattern=r".*",  # Basic pattern - allows all for testing
                error_message="Basic safety validation passed",
                severity="info"
            ),
            ValidationRule(
                name="prompt_safety_check", 
                rule_type=ValidationRuleType.PATTERN,
                pattern=r"^(?!.*rm\s+-rf).*$",
                error_message="Potentially dangerous command detected in prompt",
                severity="error"
            )
        ])
    ]
    
    # Post-execution hooks for output validation and pattern protection
    post_hooks = [
        PostValidationHookNode([
            ValidationRule(
                name="content_quality_check",
                rule_type=ValidationRuleType.PATTERN,
                pattern=r".{50,}",  # At least 50 characters
                error_message="Agent response too short, may indicate failure",
                severity="warning"
            ),
            ValidationRule(
                name="haios_pattern_protection",
                rule_type=ValidationRuleType.PATTERN,
                pattern=r"(?!.*json\.dumps\(.*content.*\))",
                error_message="HAiOS violation: Content embedding detected",
                severity="error"
            )
        ])
    ]
    
    return pre_hooks, post_hooks


# Backward compatibility function with optional hooks
async def run_agent_step_protected(prompt: str, tools: List[str]) -> AgentStepResult:
    """
    Run agent step with default pattern protection hooks.
    
    Provides automatic Shield 2 protection for standard agent operations.
    """
    pre_hooks, post_hooks = create_default_pattern_protection_hooks()
    
    return await run_agent_step_with_hooks(
        prompt=prompt,
        tools=tools,
        pre_hooks=pre_hooks,
        post_hooks=post_hooks
    )


# ============================================================================
# PHASE 1: MINIMAL STEP METRICS TRACKING
# ============================================================================

def start_step_tracking(step_name: str, node_name: str) -> StepMetrics:
    """Start minimal step tracking (Phase 1)."""
    return StepMetrics(
        step_name=step_name,
        node_name=node_name,
        start_time=time.time()
    )


def finalize_step_tracking(step_metrics: StepMetrics, result: AgentStepResult) -> StepMetrics:
    """Finalize step tracking with agent results (Phase 1)."""
    step_metrics.end_time = time.time()
    step_metrics.duration_ms = result.duration_ms
    step_metrics.cost_usd = result.cost_usd or 0.0
    step_metrics.chars_generated = len(result.response_text) if result.response_text else 0
    step_metrics.tools_used = result.tools_used.copy()
    step_metrics.tool_count = result.tool_count
    step_metrics.success = not bool(result.error)
    step_metrics.error_message = result.error
    
    return step_metrics


def log_step_summary(step_metrics: StepMetrics) -> None:
    """Log minimal step summary (Phase 1)."""
    duration_s = step_metrics.duration_ms / 1000.0
    status = "SUCCESS" if step_metrics.success else "FAILED"
    tools_str = ", ".join(step_metrics.tools_used) if step_metrics.tools_used else "0 tools"
    
    print(f"  [METRICS] {step_metrics.step_name}: {status} | {duration_s:.1f}s | {tools_str} | ${step_metrics.cost_usd:.4f} | {step_metrics.chars_generated} chars")


# ============================================================================
# PHASE 2: ROUND-LEVEL AGGREGATION AND TRACKING
# ============================================================================

def init_round_tracking(round_number: int) -> RoundMetrics:
    """Initialize round tracking (Phase 2)."""
    return RoundMetrics(
        round_number=round_number,
        start_time=time.time()
    )


def add_step_to_round(round_metrics: RoundMetrics, step_metrics: StepMetrics) -> None:
    """Add completed step to round metrics (Phase 2)."""
    # Add step to round
    round_metrics.step_metrics.append(step_metrics)
    
    # Aggregate tool usage
    for tool in step_metrics.tools_used:
        round_metrics.tools_used[tool] = round_metrics.tools_used.get(tool, 0) + 1
    
    # Aggregate performance
    round_metrics.total_tools += step_metrics.tool_count
    round_metrics.total_duration_ms += step_metrics.duration_ms
    round_metrics.total_cost_usd += step_metrics.cost_usd
    round_metrics.total_chars_generated += step_metrics.chars_generated
    
    # Update status counters
    if step_metrics.success:
        round_metrics.successful_steps += 1
    else:
        round_metrics.failed_steps += 1


def finalize_round_tracking(round_metrics: RoundMetrics, consensus_reached: bool = False, consensus_architect: str = None) -> RoundMetrics:
    """Finalize round tracking (Phase 2)."""
    round_metrics.end_time = time.time()
    round_metrics.consensus_reached = consensus_reached
    round_metrics.consensus_architect = consensus_architect
    return round_metrics


def format_tool_summary(tools_used: Dict[str, int]) -> str:
    """Format tool usage summary as '3x Read, 2x Edit' (Phase 2)."""
    if not tools_used:
        return "0 tools"
    
    tool_strings = [f"{count}x {tool}" for tool, count in sorted(tools_used.items())]
    return ", ".join(tool_strings)


def log_round_summary(round_metrics: RoundMetrics) -> None:
    """Log comprehensive round summary (Phase 2)."""
    duration_s = round_metrics.total_duration_ms / 1000.0
    tools_summary = format_tool_summary(round_metrics.tools_used)
    
    status = "CONSENSUS" if round_metrics.consensus_reached else "CONTINUE"
    if round_metrics.consensus_reached and round_metrics.consensus_architect:
        status += f" ({round_metrics.consensus_architect})"
    
    print(f"")
    print(f"{'='*80}")
    print(f"ROUND {round_metrics.round_number} SUMMARY")
    print(f"{'='*80}")
    print(f"Steps: {len(round_metrics.step_metrics)} ({round_metrics.successful_steps} success, {round_metrics.failed_steps} failed)")
    print(f"Duration: {duration_s:.1f}s | Cost: ${round_metrics.total_cost_usd:.4f} | Tools: {tools_summary}")
    print(f"Characters: {round_metrics.total_chars_generated:,} | Status: {status}")
    print(f"{'='*80}")
    print(f"")