"""
ConsensusCheckNode - Checks for consensus before starting a new round.
"""

import json
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode


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
        
        if not data["dialogue"]:
            return "continue"
        
        last_entry = data["dialogue"][-1]
        content = last_entry.get("content", "")
        
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
            print("\n[CONSENSUS REACHED!]")
            print("Architect-2 indicated no further dissent in previous round")
            return "consensus"
        
        return "continue"