"""
ConsensusCheckNode - Checks for consensus before starting a new round.
"""

import json
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode
from .shared_components import init_round_tracking, log_round_summary


class ConsensusCheckNode(AsyncNode):
    """Node that checks for consensus before starting a new round."""
    
    def __init__(self):
        super().__init__(max_retries=1, wait=0)
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for consensus check."""
        return {
            "dialogue_path": shared["dialogue_path"],
            "round_num": shared.get("round_num", 1)
        }
    
    async def exec_async(self, context: Dict[str, Any]) -> str:
        """Check if consensus was reached in previous round."""
        round_num = context["round_num"]
        
        # Skip check for first round
        if round_num <= 1:
            return "continue"
        
        # Read dialogue file to check for consensus
        with open(context["dialogue_path"], 'r') as f:
            data = json.load(f)
        
        dialogue_entries = data.get("dialogue", [])
        
        if not dialogue_entries:
            return "continue"
        
        last_entry = dialogue_entries[-1]
        content = last_entry.get("content", "")
        consensus_field = last_entry.get("consensus", False)
        
        # Primary: Check boolean consensus field
        if consensus_field:
            return "consensus"
        
        # Fallback: Pattern matching
        if "**No Further Dissent**" in content:
            return "consensus"
        return "continue"
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> str:
        """Graceful fallback if consensus check fails."""
        print(f"  [FALLBACK] Consensus check failed: {exc}")
        return "continue"  # Assume no consensus on error
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Return consensus status."""
        if exec_res == "consensus":
            print(f"\n{'='*80}")
            print("CONSENSUS DETECTED")
            print(f"{'='*80}")
            print("Consensus was reached in previous round - proceeding to synthesis")
            print(f"{'='*80}\n")
            return "consensus"
        
        # Starting new round - initialize round tracking
        round_num = prep_res.get("round_num", 1)
        
        # Phase 2: Initialize new round metrics
        round_metrics = init_round_tracking(round_num)
        shared["current_round_metrics"] = round_metrics
        
        print(f"\n{'='*80}")
        print(f"ROUND {round_num} START")
        print(f"{'='*80}")
        print("No consensus detected - continuing dialogue...")
        print(f"{'='*80}\n")
        
        return "continue"