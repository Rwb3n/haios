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
from .shared_components import run_agent_step, run_read_only_step, AgentStepResult, AGENT_CONFIGS


class SummarizerNode(AsyncNode):
    """Node that creates a summary of the dialogue history for agent context."""
    
    def __init__(self):
        super().__init__(max_retries=2, wait=1.0)
        self.scribe_prompt = "Scribe/Scribe_PROMPT.txt"
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for summarization and read scribe prompt."""
        round_num = shared["round_num"]
        
        # Skip summary for first round
        if round_num <= 1:
            return {
                "skip_summary": True,
                "dialogue_path": shared["dialogue_path"],
                "round_num": round_num,
                "session_dir": shared.get("session_dir", "output_2A/session_default")
            }
        
        # Read scribe prompt file with read-only access (principle of least privilege)
        base_dir = Path.cwd()
        scribe_prompt_path = str(base_dir / self.scribe_prompt)
        
        prompt_result: AgentStepResult = await run_read_only_step(f"Read {scribe_prompt_path}", scribe_prompt_path)
        if prompt_result.error or prompt_result.tool_count == 0:
            print(f"  [ERROR] Failed to read Scribe prompt from {scribe_prompt_path}: {prompt_result.error}")
            return {
                "error": f"Failed to read Scribe prompt: {prompt_result.error}",
                "dialogue_path": shared["dialogue_path"],
                "round_num": round_num,
                "session_dir": shared.get("session_dir", "output_2A/session_default")
            }
        
        # Prepare file paths
        session_dir = shared.get("session_dir", "output_2A/session_default")
        summary_file_path = f"{session_dir}/summary.md"
        
        base_dir = Path.cwd()
        summary_abs = str(base_dir / summary_file_path)
        dialogue_abs = str(base_dir / shared["dialogue_path"])
        
        return {
            "skip_summary": False,
            "dialogue_path": shared["dialogue_path"],
            "round_num": round_num,
            "session_dir": session_dir,
            "summary_file_path": summary_file_path,
            "summary_abs": summary_abs,
            "dialogue_abs": dialogue_abs,
            "prompt_content": prompt_result.response_text
        }
    
    async def exec_async(self, context: Dict[str, Any]) -> str:
        """Generate dialogue summary using Scribe persona with restricted tools."""
        # Check if summary should be skipped
        if context.get("skip_summary", False):
            return "No previous dialogue to summarize."
        
        # Check for prep errors
        if context.get("error"):
            return f"Error: {context['error']}"
        
        print(f"Step 3: Generating dialogue summary (Round {context['round_num']})...")
        
        # Simple file operation instruction (identical pattern to Architects)
        summary_instruction = f"""Read {context['dialogue_abs']} then read {context['summary_abs']} then use Edit ONCE to replace the entire summary file with an updated version containing key information from the dialogue."""
        
        # Validation log for file access
        print(f"  [VALIDATION] Summary file access validated: {context['summary_abs']}")
        print(f"  [VALIDATION] Dialogue file access validated: {context['dialogue_abs']}")
        
        # Standard Read + Edit pattern (identical to Architects)
        result: AgentStepResult = await run_agent_step(summary_instruction, ["Read", "Edit"])
        print(f"  [DEBUG] Scribe used {result.tool_count} tools: {result.tools_used}")
        
        if result.error:
            return f"Error: {result.error}"
        
        # Validation log for tool usage
        if result.tool_count < 3:
            print(f"  [VALIDATION] Tool usage validation failed: Scribe must use Read (dialogue), Read (summary), and Edit tools (used {result.tool_count} tools)")
            return f"Error: Scribe must use Read (dialogue), Read (summary), and Edit tools (used {result.tool_count} tools)"
        else:
            print(f"  [VALIDATION] Tool usage validated: Scribe used {result.tool_count} tools correctly")
        
        # Log cost information if available
        if result.cost_usd:
            print(f"  [COST] Scribe operation cost: ${result.cost_usd:.4f}")
        
        # Validation log for operation completion
        print(f"  [VALIDATION] Summary generation completed successfully ({len(result.response_text)} chars)")
        
        return result.response_text
    
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