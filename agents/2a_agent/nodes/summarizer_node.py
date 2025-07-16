"""
SummarizerNode - Creates a summary of the dialogue history for agent context.
"""

import json
from pathlib import Path
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode
from .shared_components import run_agent_step


class SummarizerNode(AsyncNode):
    """Node that creates a summary of the dialogue history for agent context."""
    
    def __init__(self):
        super().__init__(max_retries=2, wait=1.0)
        self.scribe_prompt = "Scribe/Scribe_PROMPT.txt"
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare dialogue history for summarization."""
        dialogue_path = shared["dialogue_path"]
        
        # Read current dialogue file
        try:
            with open(dialogue_path, 'r') as f:
                data = json.load(f)
            
            dialogue_history = data.get("dialogue", [])
            return {
                "dialogue_history": dialogue_history,
                "round_num": shared["round_num"],
                "total_entries": len(dialogue_history)
            }
        except Exception as e:
            print(f"  [ERROR] Failed to read dialogue for summary: {e}")
            return {"dialogue_history": [], "round_num": 1, "total_entries": 0}
    
    async def exec_async(self, context: Dict[str, Any]) -> str:
        """Generate dialogue summary using Scribe persona."""
        dialogue_history = context["dialogue_history"]
        round_num = context["round_num"]
        
        # Skip summary for first round or empty dialogues
        if round_num <= 1 or len(dialogue_history) == 0:
            return "No previous dialogue to summarize."
        
        print(f"\n--- Generating Dialogue Summary (Round {round_num}) ---")
        
        # Read scribe prompt
        base_dir = Path.cwd()
        scribe_prompt_path = str(base_dir / self.scribe_prompt)
        
        response, tools = await run_agent_step(f"Read {scribe_prompt_path}", ["Read"])
        if tools == 0:
            return "Error: Failed to read Scribe prompt"
        
        # Create summary request
        dialogue_json = json.dumps(dialogue_history, indent=2)
        summary_instruction = f"""Read the following dialogue history and create a concise summary following your instructions:

{dialogue_json}

Please provide a bullet-point summary of the key arguments, decisions, and open questions."""
        
        summary_response, summary_tools = await run_agent_step(summary_instruction, ["Read"])
        if summary_tools == 0:
            return "Error: Failed to generate dialogue summary"
        
        print(f"  [OK] Generated dialogue summary ({len(summary_response)} chars)")
        return summary_response
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> str:
        """Graceful fallback if summary generation fails."""
        print(f"  [FALLBACK] Summary generation failed: {exc}")
        return "Summary generation failed. Proceeding without dialogue context."
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Store summary in shared state."""
        shared["dialogue_summary"] = exec_res
        print(f"  [OK] Dialogue summary stored in shared state")
        print(f"\n{'='*60}")
        print("DIALOGUE SUMMARY CONTENT:")
        print(f"{'='*60}")
        print(exec_res)
        print(f"{'='*60}")
        print("END DIALOGUE SUMMARY")
        print(f"{'='*60}\n")
        return "default"