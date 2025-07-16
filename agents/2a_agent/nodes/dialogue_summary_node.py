"""
DialogueSummaryNode - Displays the final dialogue summary.
"""

import json
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode


class DialogueSummaryNode(AsyncNode):
    """Node that displays the final dialogue summary."""
    
    def __init__(self):
        super().__init__(max_retries=1, wait=0)
    
    async def prep_async(self, shared: Dict[str, Any]) -> str:
        """Prepare dialogue path for reading."""
        return shared["dialogue_path"]
    
    async def exec_async(self, dialogue_path: str) -> Dict[str, Any]:
        """Load and analyze final dialogue."""
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        return {
            "dialogue": data["dialogue"],
            "total_entries": len(data["dialogue"])
        }
    
    async def exec_fallback_async(self, prep_res: str, exc: Exception) -> Dict[str, Any]:
        """Graceful fallback if dialogue reading fails."""
        print(f"  [FALLBACK] Failed to read dialogue for summary: {exc}")
        return {"dialogue": [], "total_entries": 0}
    
    async def post_async(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> str:
        """Display dialogue summary."""
        print(f"\n{'='*60}")
        print("DIALOGUE COMPLETE")
        print(f"Total entries: {exec_res['total_entries']}")
        
        if exec_res["dialogue"]:
            for i, entry in enumerate(exec_res["dialogue"]):
                print(f"\nEntry {i+1}: {entry['role']} (Round {entry['round']})")
                print(f"  Preview: {entry['content'][:100]}...")
        
        return "default"