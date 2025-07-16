"""
Architect2Node - Secondary architect responsible for critique and validation.
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


class Architect2Node(AsyncNode):
    """Architect-2 complete workflow node with consensus detection."""
    
    def __init__(self, prompt_file: str = "A2/A2_PROMPT_FILE_BASED.txt"):
        super().__init__(max_retries=2, wait=1.0)
        self.prompt_file = prompt_file
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for Architect-2 execution."""
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
        """Execute Architect-2 workflow using Claude SDK directly."""
        print(f"\n--- Architect-2 (Round {context['round_num']}) ---")
        
        # Step 1: Read prompt file with read-only access (principle of least privilege)
        print(f"Step 1: Reading prompt file...")
        base_dir = Path.cwd()
        prompt_file = str(base_dir / self.prompt_file)
        
        from .shared_components import run_read_only_step
        response, tools = await run_read_only_step(f"Read {prompt_file}", prompt_file)
        if tools == 0:
            return {"success": False, "error": "Failed to read prompt file"}
        
        print(f"  [OK] Architect-2 read prompt file ({len(response)} chars)")
        
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
        
        # Simple file operation instruction  
        instruction = f"""Read {dialogue_abs} then use Edit to fill in the content field of the last entry in the dialogue array with your critique."""
        
        # Standard Read + Edit pattern
        response, tools_used = await run_agent_step(instruction, ["Read", "Edit"])
        print(f"  [DEBUG] Architect-2 used {tools_used} tools")
        
        if tools_used < 2:
            return {"success": False, "error": "Failed to update dialogue - insufficient tool usage"}
        
        # Verify dialogue was updated
        await asyncio.sleep(1)
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        after_count = len(data["dialogue"])
        
        if after_count <= before_count:
            return {"success": False, "error": "Dialogue not updated"}
        
        print(f"  [OK] Architect-2 updated dialogue ({before_count} -> {after_count} entries)")
        return {"success": True, "dialogue_data": data}
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> Dict[str, Any]:
        """Graceful fallback if Architect-2 workflow fails."""
        print(f"  [FALLBACK] Architect-2 workflow failed: {exc}")
        return {"success": False, "error": str(exc)}
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Check for consensus and return appropriate action."""
        if not exec_res.get("success", False):
            return "error"
        
        # Check for consensus in the dialogue data
        dialogue_data = exec_res.get("dialogue_data", {})
        if dialogue_data.get("dialogue") and "**No Further Dissent**" in dialogue_data["dialogue"][-1].get("content", ""):
            print("\n[CONSENSUS REACHED!]")
            print("Architect-2 indicated no further dissent")
            return "consensus"
        
        # Increment round number for next round
        shared["round_num"] += 1
        
        # Check if we've reached max rounds (skip check if max_rounds = -1 for infinite)
        if shared["max_rounds"] != -1 and shared["round_num"] > shared["max_rounds"]:
            print(f"\n[MAX ROUNDS REACHED] ({shared['max_rounds']} rounds completed)")
            return "consensus"  # End the dialogue
        
        return "continue"