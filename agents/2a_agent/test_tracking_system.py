#!/usr/bin/env python3
"""
Test the new round and session tracking system.
"""

import asyncio
import sys
import os

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'PocketFlow'))
sys.path.append(os.path.dirname(__file__))

from nodes.shared_components import (
    init_session_tracking, init_round_tracking, start_step_tracking,
    finalize_step_tracking, update_round_metrics, finalize_round_metrics,
    generate_round_summary, generate_session_summary, AgentStepResult
)


def test_tracking_infrastructure():
    """Test the basic tracking infrastructure."""
    print("Testing Round & Session Tracking Infrastructure")
    print("=" * 60)
    
    # Initialize session
    session_metrics = init_session_tracking("test_session_123")
    print(f"[PASS] Session initialized: {session_metrics.session_id}")
    
    # Initialize round
    round_metrics = init_round_tracking(1)
    print(f"[PASS] Round initialized: Round {round_metrics.round_number}")
    
    # Start step tracking
    step_metrics = start_step_tracking("Test Agent Response", "TestNode")
    print(f"[PASS] Step tracking started: {step_metrics.step_name}")
    
    # Simulate agent result
    agent_result = AgentStepResult(
        response_text="This is a test response with some content.",
        tool_count=2,
        tools_used=["Read", "Edit"],
        duration_ms=1500,
        cost_usd=0.0123,
        usage_data={"test": "data"},
        error=None
    )
    
    # Finalize step
    step_metrics = finalize_step_tracking(step_metrics, agent_result)
    print(f"[PASS] Step finalized: {step_metrics.tool_count} tools, {step_metrics.duration_ms}ms")
    
    # Update round with step
    update_round_metrics(round_metrics, step_metrics)
    print(f"[PASS] Round updated: {round_metrics.total_tools} total tools")
    
    # Finalize round
    round_metrics = finalize_round_metrics(round_metrics)
    print(f"[PASS] Round finalized")
    
    # Add round to session
    session_metrics.add_round(round_metrics)
    print(f"[PASS] Round added to session: {session_metrics.total_rounds} rounds")
    
    # Generate summaries
    round_summary = generate_round_summary(round_metrics)
    print("\n" + round_summary)
    
    session_summary = generate_session_summary(session_metrics)
    print("\n" + session_summary)
    
    print("\n[SUCCESS] All tracking infrastructure tests passed!")
    return True


if __name__ == "__main__":
    success = test_tracking_infrastructure()
    
    if success:
        print("\n[COMPLETE] Tracking system ready for integration")
    else:
        print("\n[FAIL] Tracking system needs fixes")