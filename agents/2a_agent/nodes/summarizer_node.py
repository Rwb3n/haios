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
        """Prepare context for summarization."""
        return {
            "dialogue_path": shared["dialogue_path"],
            "round_num": shared["round_num"],
            "session_dir": shared.get("session_dir", "output_2A/session_default")
        }
    
    async def exec_async(self, context: Dict[str, Any]) -> str:
        """Generate dialogue summary using Scribe persona with restricted tools."""
        round_num = context["round_num"]
        
        # Skip summary for first round
        if round_num <= 1:
            return "No previous dialogue to summarize."
        
        print(f"\n--- Generating Dialogue Summary (Round {round_num}) ---")
        
        # Read scribe prompt file with read-only access (principle of least privilege)
        base_dir = Path.cwd()
        scribe_prompt_path = str(base_dir / self.scribe_prompt)
        
        from .shared_components import run_read_only_step
        prompt_response, prompt_tools = await run_read_only_step(f"Read {scribe_prompt_path}", scribe_prompt_path)
        if prompt_tools == 0:
            print(f"  [ERROR] Failed to read Scribe prompt from {scribe_prompt_path}")
            return "Error: Failed to read Scribe prompt"
        
        print(f"  [OK] Scribe read prompt file ({len(prompt_response)} chars)")
        
        # Get session directory from context
        session_dir = context.get("session_dir", "output_2A/session_default")
        summary_file_path = f"{session_dir}/summary.md"
        
        # Simple file operation instruction (identical pattern to Architects)
        base_dir = Path.cwd()
        summary_abs = str(base_dir / summary_file_path)
        dialogue_abs = str(base_dir / context["dialogue_path"])
        
        summary_instruction = f"""Read {dialogue_abs} then read {summary_abs} then use Edit ONCE to replace the entire summary file with an updated version containing key information from the dialogue."""
        
        # Standard Read + Edit pattern (identical to Architects)
        response, tools_used = await run_agent_step(summary_instruction, ["Read", "Edit"])
        print(f"  [DEBUG] Scribe used {tools_used} tools")
        
        if tools_used < 3:
            return f"Error: Scribe must use Read (dialogue), Read (summary), and Edit tools (used {tools_used} tools)"
        
        print(f"  [OK] Generated dialogue summary ({len(response)} chars)")
        return response
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> str:
        """Graceful fallback if summary generation fails."""
        print(f"  [FALLBACK] Summary generation failed: {exc}")
        return "Summary generation failed. Proceeding without dialogue context."
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Store summary in shared state (file already written by Scribe)."""
        # Store in shared state for backwards compatibility
        shared["dialogue_summary"] = exec_res
        
        # Note: File is already written by Scribe agent using Write tool
        # No need to write again here - just update shared state
        
        print(f"  [OK] Dialogue summary stored in shared state")
        print(f"\n{'='*60}")
        print("DIALOGUE SUMMARY CONTENT:")
        print(f"{'='*60}")
        print(exec_res)
        print(f"{'='*60}")
        print("END DIALOGUE SUMMARY")
        print(f"{'='*60}\n")
        return "default"