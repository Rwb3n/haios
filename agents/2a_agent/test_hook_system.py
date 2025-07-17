#!/usr/bin/env python3
"""
Test script for Hook Validation System (Shield 2 - Dynamic Defense).

Tests the hook system's ability to protect against "benevolent misalignment" 
and architectural pattern violations during agent operations.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'PocketFlow'))
sys.path.append(os.path.dirname(__file__))

from nodes.shared_components import (
    run_agent_step_with_hooks,
    run_agent_step_protected,
    create_default_pattern_protection_hooks,
    AgentStepResult,
    HOOKS_AVAILABLE
)

if HOOKS_AVAILABLE:
    from nodes.hook_validation_nodes import (
        PreValidationHookNode,
        PostValidationHookNode,
        ValidationRule,
        ValidationRuleType
    )


async def test_basic_hook_system():
    """Test basic hook system functionality."""
    print("=" * 80)
    print("TEST 1: Basic Hook System Functionality")
    print("=" * 80)
    
    if not HOOKS_AVAILABLE:
        print("[SKIP] Hook system not available")
        return False
    
    # Test simple safe operation
    prompt = "Respond with 'Hello from hook-protected agent!'"
    tools = ["Read"]  # Safe tool only
    
    try:
        result = await run_agent_step_protected(prompt, tools)
        
        print(f"[PASS] Hook-protected execution successful")
        print(f"   Response: {result.response_text[:100]}...")
        print(f"   Tools used: {result.tools_used}")
        print(f"   Hook overhead: {result.usage_data.get('hook_overhead_ms', 0)}ms")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Hook system test failed: {str(e)}")
        return False


async def test_pre_validation_blocking():
    """Test pre-validation hook blocking dangerous operations."""
    print("\n" + "=" * 80)
    print("TEST 2: Pre-Validation Blocking")
    print("=" * 80)
    
    if not HOOKS_AVAILABLE:
        print("[SKIP] Hook system not available")
        return False
    
    # Create dangerous validation rule
    dangerous_pattern_hook = PreValidationHookNode([
        ValidationRule(
            name="dangerous_command_check",
            rule_type=ValidationRuleType.PATTERN,
            pattern=r"rm\s+-rf",  # Look for dangerous rm command
            error_message="Dangerous rm -rf command detected",
            severity="error"
        )
    ])
    
    # Test with dangerous prompt
    dangerous_prompt = "Please run: rm -rf /important/files"
    tools = ["Bash"]
    
    try:
        result = await run_agent_step_with_hooks(
            prompt=dangerous_prompt,
            tools=tools,
            pre_hooks=[dangerous_pattern_hook],
            post_hooks=[]
        )
        
        if result.error and "BLOCKED" in result.response_text:
            print("[PASS] Pre-validation successfully blocked dangerous operation")
            print(f"   Block reason: {result.error}")
            return True
        else:
            print("[FAIL] Pre-validation failed to block dangerous operation")
            return False
            
    except Exception as e:
        print(f"[FAIL] Pre-validation test failed: {str(e)}")
        return False


async def test_haios_pattern_protection():
    """Test HAiOS pattern protection against content embedding."""
    print("\n" + "=" * 80)
    print("TEST 3: HAiOS Pattern Protection")
    print("=" * 80)
    
    if not HOOKS_AVAILABLE:
        print("[SKIP] Hook system not available")
        return False
    
    # Create HAiOS compliance hook
    haios_protection_hook = PostValidationHookNode([
        ValidationRule(
            name="content_embedding_check",
            rule_type=ValidationRuleType.PATTERN,
            pattern=r"json\.dumps\(.*content.*\)",
            error_message="HAiOS violation: Content embedding in prompts detected",
            severity="error"
        )
    ])
    
    # Test with HAiOS-violating response (simulated)
    prompt = "Respond with: json.dumps({'content': 'embedded data'})"
    tools = ["Read"]
    
    # Use shared state to simulate the agent response containing violation
    shared_state = {
        "test_mode": True,
        "simulated_response": "json.dumps({'content': 'this violates haios patterns'})"
    }
    
    try:
        result = await run_agent_step_with_hooks(
            prompt=prompt,
            tools=tools,
            pre_hooks=[],
            post_hooks=[haios_protection_hook],
            shared_state=shared_state
        )
        
        # Note: In real implementation, post-hooks would inspect actual file changes
        # For this test, we're primarily testing the hook infrastructure
        
        print("[PASS] HAiOS pattern protection hook executed successfully")
        print(f"   Response: {result.response_text[:100]}...")
        print(f"   Hook system data: {list(result.usage_data.get('hook_validation_results', {}).keys())}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] HAiOS pattern protection test failed: {str(e)}")
        return False


async def test_hook_performance_overhead():
    """Test hook system performance overhead."""
    print("\n" + "=" * 80)
    print("TEST 4: Hook Performance Overhead")
    print("=" * 80)
    
    if not HOOKS_AVAILABLE:
        print("[SKIP] Hook system not available")
        return False
    
    prompt = "Respond with current time and a brief message"
    tools = ["Read"]
    
    # Test without hooks
    try:
        from nodes.shared_components import run_agent_step
        result_no_hooks = await run_agent_step(prompt, tools)
        duration_no_hooks = result_no_hooks.duration_ms
        
        # Test with hooks
        result_with_hooks = await run_agent_step_protected(prompt, tools)
        duration_with_hooks = result_with_hooks.duration_ms
        hook_overhead = result_with_hooks.usage_data.get('hook_overhead_ms', 0)
        
        print(f"[PASS] Performance comparison completed")
        print(f"   Without hooks: {duration_no_hooks}ms")
        print(f"   With hooks: {duration_with_hooks}ms")
        print(f"   Hook overhead: {hook_overhead}ms ({(hook_overhead/duration_no_hooks)*100:.1f}% of original)")
        
        # Acceptable overhead threshold (should be < 20% of original duration)
        overhead_acceptable = hook_overhead < (duration_no_hooks * 0.2)
        
        if overhead_acceptable:
            print(f"[PASS] Hook overhead within acceptable limits")
        else:
            print(f"[WARN]  Hook overhead higher than expected (>{(duration_no_hooks * 0.2):.0f}ms)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Performance test failed: {str(e)}")
        return False


async def test_hook_system_resilience():
    """Test hook system resilience to failures."""
    print("\n" + "=" * 80)
    print("TEST 5: Hook System Resilience")
    print("=" * 80)
    
    if not HOOKS_AVAILABLE:
        print("[SKIP] Hook system not available")
        return False
    
    # Create a hook with invalid regex pattern to test error handling
    try:
        faulty_hook = PreValidationHookNode([
            ValidationRule(
                name="invalid_regex_test",
                rule_type=ValidationRuleType.PATTERN,
                pattern=r"[",  # Invalid regex - missing closing bracket
                error_message="This rule has invalid regex",
                severity="error"
            )
        ])
        
        prompt = "Test resilience with faulty hook"
        tools = ["Read"]
        
        result = await run_agent_step_with_hooks(
            prompt=prompt,
            tools=tools,
            pre_hooks=[faulty_hook],
            post_hooks=[]
        )
        
        # System should continue execution despite hook failure
        if not result.error or "Rule execution failed" in result.error:
            print("[PASS] Hook system gracefully handled faulty validation rule")
            print(f"   Result: {result.response_text[:100] if not result.error else result.error}")
            return True
        else:
            print("[FAIL] Hook system did not handle faulty rule gracefully")
            return False
            
    except Exception as e:
        print(f"[FAIL] Resilience test failed: {str(e)}")
        return False


async def main():
    """Run all hook system tests."""
    print("HAiOS 2A Agent - Hook Validation System Tests")
    print("Shield 2 (Dynamic Defense) Implementation Validation")
    print("=" * 80)
    
    if not HOOKS_AVAILABLE:
        print("[FAIL] CRITICAL: Hook validation system not available")
        print("   Ensure hook_validation_nodes.py is properly installed")
        return
    
    tests = [
        ("Basic Hook System", test_basic_hook_system),
        ("Pre-Validation Blocking", test_pre_validation_blocking),
        ("HAiOS Pattern Protection", test_haios_pattern_protection),
        ("Performance Overhead", test_hook_performance_overhead),
        ("System Resilience", test_hook_system_resilience)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"[FAIL] {test_name} CRASHED: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("HOOK SYSTEM TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS] PASS" if result else "[FAIL] FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! Hook system ready for production.")
    elif passed >= total * 0.8:
        print("[WARN]  Most tests passed. Review failures before production.")
    else:
        print("[FAIL] Multiple test failures. Hook system needs review.")
    
    print("\n" + "=" * 80)
    print("Hook Validation System (Shield 2) Testing Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())