"""
Architect1Node - Primary architect responsible for analysis and proposals.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode
from .shared_components import run_agent_step


class Architect1Node(AsyncNode):
    """Architect-1 complete workflow node."""
    
    def __init__(self, prompt_file: str = "A1/A1_PROMPT_FILE_BASED.txt"):
        super().__init__(max_retries=2, wait=1.0)
        self.prompt_file = prompt_file
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for Architect-1 execution."""
        # Read both dialogue.json and summary.md for full context
        session_dir = shared.get("session_dir")
        summary_content = "No previous dialogue to summarize."
        
        if session_dir:
            summary_path = Path(session_dir) / "summary.md"
            if summary_path.exists():
                try:
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        summary_content = f.read()
                except Exception as e:
                    print(f"  [WARNING] Failed to read summary file: {e}")
        
        return {
            "round_num": shared["round_num"],
            "dialogue_path": shared["dialogue_path"],
            "dialogue_summary": summary_content
        }
    
    async def exec_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Architect-1 workflow using Claude SDK directly."""
        print(f"\n--- Architect-1 (Round {context['round_num']}) ---")
        
        # Step 1: Read prompt file with read-only access (principle of least privilege)
        print(f"Step 1: Reading prompt file...")
        base_dir = Path.cwd()
        prompt_file = str(base_dir / self.prompt_file)
        
        from .shared_components import run_read_only_step
        response, tools = await run_read_only_step(f"Read {prompt_file}", prompt_file)
        if tools == 0:
            return {"success": False, "error": "Failed to read prompt file"}
        
        print(f"  [OK] Architect-1 read prompt file ({len(response)} chars)")
        
        # Step 2: Update dialogue
        print(f"Step 2: Reading dialogue and appending response...")
        
        # Read current dialogue count
        dialogue_path = context["dialogue_path"]
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        before_count = len(data["dialogue"])
        
        # Update dialogue using working Read/Edit pattern (revert to working approach)
        base_dir = Path.cwd()
        dialogue_abs = str(base_dir / dialogue_path)
        timestamp = datetime.now().isoformat()
        
        # Simple file operation instruction
        base_dir = Path.cwd()
        dialogue_abs = str(base_dir / dialogue_path)
        
        # Orchestrator pre-fills skeleton entry, agent only fills content
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from utils import extract_speaker_role
        speaker_role = extract_speaker_role(self.prompt_file)
        
        # Pre-create skeleton entry in dialogue
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        skeleton_entry = {
            "round": context['round_num'],
            "role": speaker_role,
            "timestamp": timestamp,
            "content": ""
        }
        data["dialogue"].append(skeleton_entry)
        
        with open(dialogue_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        instruction = f"""Read {dialogue_abs} then use Edit to fill in the content field of the last entry in the dialogue array with your response."""
        
        # Standard Read + Edit pattern
        response, tools_used = await run_agent_step(instruction, ["Read", "Edit"])
        print(f"  [DEBUG] Architect-1 used {tools_used} tools")
        
        if tools_used < 2:
            return {"success": False, "error": "Failed to update dialogue - insufficient tool usage"}
        
        # Verify dialogue was updated
        await asyncio.sleep(1)
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        after_count = len(data["dialogue"])
        
        if after_count <= before_count:
            return {"success": False, "error": "Dialogue not updated"}
        
        print(f"  [OK] Architect-1 updated dialogue ({before_count} -> {after_count} entries)")
        return {"success": True}
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> Dict[str, Any]:
        """Graceful fallback if Architect-1 workflow fails."""
        print(f"  [FALLBACK] Architect-1 workflow failed: {exc}")
        return {"success": False, "error": str(exc)}
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Return success status."""
        return "default" if exec_res.get("success", False) else "error"