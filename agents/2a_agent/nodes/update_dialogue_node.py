"""
UpdateDialogueNode - Atomic node for updating dialogue with agent response.

Single responsibility: Get agent response and update dialogue file.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode
from .shared_components import run_agent_step, AgentStepResult, AGENT_CONFIGS


class UpdateDialogueNode(AsyncNode):
    """Atomic node that only handles agent response and dialogue update."""
    
    def __init__(self, persona_name: str):
        super().__init__(max_retries=2, wait=1.0)
        self.persona_name = persona_name
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for dialogue update."""
        return {
            "dialogue_path": shared["dialogue_path"],
            "round_num": shared["round_num"],
            "persona_name": self.persona_name,
            "prompt_content": shared.get("prompt_content", ""),
            "prompt_error": shared.get("prompt_error", None)
        }
    
    async def exec_async(self, context: Dict[str, Any]) -> str:
        """ATOMIC: Get agent response only. No file operations."""
        if context["prompt_error"]:
            return f"ERROR: Cannot proceed without prompt: {context['prompt_error']}"
        
        if not context["prompt_content"]:
            return "ERROR: No prompt content available"
        
        print(f"{'='*60}")
        print(f"STEP 2: Getting {context['persona_name']} Response")
        print(f"{'='*60}")
        
        # Auto-extract speaker role from prompt content (HAiOS pattern)
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from utils import extract_speaker_role
        
        # For prompt content, we need to extract from the first line
        first_line = context["prompt_content"].split('\n')[0].strip()
        if first_line.startswith('<') and first_line.endswith('>'):
            content = first_line[1:-1]
            if 'Prompt:' in content:
                speaker_role = content.split('Prompt:')[0].strip()
            else:
                speaker_role = self.persona_name
        else:
            speaker_role = self.persona_name
        
        # Pre-create skeleton entry (HAiOS pattern)
        dialogue_path = context["dialogue_path"]
        timestamp = datetime.now().isoformat()
        
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        skeleton_entry = {
            "round": context['round_num'],
            "role": speaker_role,
            "timestamp": timestamp,
            "content": "",
            "consensus": False
        }
        data["dialogue"].append(skeleton_entry)
        
        with open(dialogue_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Validation log for skeleton creation
        print(f"  [VALIDATION] Dialogue skeleton entry created for {speaker_role} (round {context['round_num']})")
        
        # ATOMIC operation: Get agent response only
        base_dir = Path.cwd()
        dialogue_abs = str(base_dir / dialogue_path)
        
        instruction = f"""Read {dialogue_abs} then use Edit to fill in the content field of the last entry in the dialogue array with your response.

IMPORTANT: If you believe consensus has been reached, also set the "consensus" field to true in your entry. Only set consensus=true if you are certain the architectural question has been fully resolved and no further discussion is needed."""
        
        # Single atomic operation: get agent response
        result: AgentStepResult = await run_agent_step(instruction, ["Read", "Edit"])
        print(f"  [DEBUG] {context['persona_name']} used {result.tool_count} tools: {result.tools_used}")
        
        if result.error:
            return f"ERROR: {result.error}"
        
        # Validation log for tool usage
        if result.tool_count < 2:
            print(f"  [VALIDATION] Tool usage validation failed: {context['persona_name']} must use both Read and Edit tools")
            return f"ERROR: {context['persona_name']} must use both Read and Edit tools"
        else:
            print(f"  [VALIDATION] Tool usage validated: {context['persona_name']} used {result.tool_count} tools correctly")
        
        # Log cost information if available
        if result.cost_usd:
            print(f"  [COST] {context['persona_name']} operation cost: ${result.cost_usd:.4f}")
        
        # Validation log for operation completion
        print(f"  [VALIDATION] {context['persona_name']} dialogue update completed successfully")
        
        return result.response_text
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> str:
        """Graceful fallback if dialogue update fails."""
        print(f"  [FALLBACK] {prep_res['persona_name']} workflow failed: {exc}")
        return f"ERROR: {prep_res['persona_name']} failed: {exc}"
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Update shared state and determine next action."""
        if exec_res.startswith("ERROR:"):
            shared["last_error"] = exec_res
            return "error"
        
        # Read dialogue file to get updated entry count and check consensus
        dialogue_path = prep_res["dialogue_path"]
        
        try:
            with open(dialogue_path, 'r') as f:
                data = json.load(f)
            
            dialogue_entries = data.get("dialogue", [])
            entry_count = len(dialogue_entries)
            
            print(f"  [OK] {prep_res['persona_name']} updated dialogue ({entry_count} entries)")
            
            # Check for consensus from either architect
            last_entry = dialogue_entries[-1] if dialogue_entries else {}
            
            # Primary: Check boolean consensus field (structured approach)
            consensus_boolean = last_entry.get("consensus", False)
            
            if consensus_boolean:
                print(f"  [CONSENSUS] Detected consensus signal (boolean field) from {prep_res['persona_name']}")
                shared["consensus_reached"] = True
                return "consensus"
            
            # Fallback: Pattern matching for backwards compatibility
            content = last_entry.get("content", "")
            consensus_patterns = [
                "**No Further Dissent**",
                "UNANIMOUS APPROVAL", 
                "DIALOGUE COMPLETE",
                "Complete Agreement",
                "Consensus Declaration",
                "APPROVED FOR IMPLEMENTATION",
                "ready for immediate implementation",
                "production-ready"
            ]
            
            content_upper = content.upper()
            consensus_found = any(pattern.upper() in content_upper for pattern in consensus_patterns)
            
            if consensus_found:
                print(f"  [CONSENSUS] Detected consensus signal (pattern fallback) from {prep_res['persona_name']}")
                shared["consensus_reached"] = True
                return "consensus"
            
            # Only increment round after Architect-2 responses (complete round finished)
            if prep_res['persona_name'] == "Architect-2":
                completed_round = shared.get("round_num", 1)
                shared["round_num"] = completed_round + 1
                
                print(f"\n{'='*80}")
                print(f"ROUND {completed_round} COMPLETED")
                print(f"{'='*80}")
                print(f"Starting Round {shared['round_num']} - Continuing Dialogue...")
                print(f"{'='*80}\n")
            
            shared["last_error"] = None
            return "continue"
            
        except Exception as e:
            shared["last_error"] = f"Failed to read dialogue after update: {e}"
            return "error"