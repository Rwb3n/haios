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
from .shared_components import (
    run_read_only_step, AgentStepResult,
    start_step_tracking, finalize_step_tracking, log_step_summary,
    add_step_to_round
)


class ReadPromptNode(AsyncNode):
    """Atomic node that only reads a prompt file and stores content."""
    
    def __init__(self, prompt_file: str, step_number: int = 1, architect_name: str = ""):
        super().__init__(max_retries=2, wait=1.0)
        self.prompt_file = prompt_file
        self.step_number = step_number
        self.architect_name = architect_name
    
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
        
        print(f"{'='*60}")
        step_desc = f"Reading {self.architect_name} Prompt File" if self.architect_name else "Reading Prompt File"
        print(f"STEP {self.step_number}: {step_desc}")
        print(f"{'='*60}")
        
        # Phase 1: Start step tracking
        step_metrics = start_step_tracking(step_desc, "ReadPromptNode")
        
        # Single atomic operation: read prompt file with absolute path
        result: AgentStepResult = await run_read_only_step(
            f"Read {context['prompt_file']}", 
            context['prompt_file']
        )
        
        # Phase 1: Finalize tracking but don't log yet
        step_metrics = finalize_step_tracking(step_metrics, result)
        
        # Store step metrics for post_async to use in round tracking
        context["step_metrics"] = step_metrics
        
        if result.error:
            return f"ERROR: {result.error}"
        
        # Validation log for file access
        print(f"  [VALIDATION] Prompt file read access validated: {context['prompt_file']}")
        
        # Phase 1: Log summary as final line
        log_step_summary(step_metrics)
        
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
            # Phase 2: Add step to current round metrics (if available)
            step_metrics = prep_res.get("step_metrics")
            current_round_metrics = shared.get("current_round_metrics")
            if step_metrics and current_round_metrics:
                add_step_to_round(current_round_metrics, step_metrics)
            
            shared["prompt_content"] = exec_res
            shared["prompt_error"] = None
            return "default"