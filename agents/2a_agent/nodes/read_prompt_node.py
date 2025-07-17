"""
ReadPromptNode - Atomic node for reading prompt files.

Single responsibility: Read a prompt file and store content in shared state.
"""

from pathlib import Path
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode
from .shared_components import run_read_only_step, AgentStepResult


class ReadPromptNode(AsyncNode):
    """Atomic node that only reads a prompt file and stores content."""
    
    def __init__(self, prompt_file: str):
        super().__init__(max_retries=2, wait=1.0)
        self.prompt_file = prompt_file
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare absolute prompt file path for reading."""
        # Convert to absolute path to avoid Claude Code SDK path issues
        base_dir = Path.cwd()
        prompt_abs = str(base_dir / self.prompt_file)
        
        return {
            "prompt_file": prompt_abs,
            "prompt_exists": Path(prompt_abs).exists()
        }
    
    async def exec_async(self, context: Dict[str, Any]) -> str:
        """ATOMIC: Read prompt file only. No other operations."""
        if not context["prompt_exists"]:
            return f"ERROR: Prompt file not found: {context['prompt_file']}"
        
        print(f"Step 1: Reading prompt file...")
        
        # Single atomic operation: read prompt file with absolute path
        result: AgentStepResult = await run_read_only_step(
            f"Read {context['prompt_file']}", 
            context['prompt_file']
        )
        
        if result.error:
            return f"ERROR: {result.error}"
        
        # Validation log for file access
        print(f"  [VALIDATION] Prompt file read access validated: {context['prompt_file']}")
        
        return result.response_text
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> str:
        """Graceful fallback if prompt reading fails."""
        print(f"  [FALLBACK] Failed to read prompt {prep_res['prompt_file']}: {exc}")
        return f"ERROR: Could not read prompt file: {exc}"
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Store prompt content in shared state for next node."""
        if exec_res.startswith("ERROR:"):
            shared["prompt_content"] = ""
            shared["prompt_error"] = exec_res
            return "error"
        else:
            shared["prompt_content"] = exec_res
            shared["prompt_error"] = None
            return "default"