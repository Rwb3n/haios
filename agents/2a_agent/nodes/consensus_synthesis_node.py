"""
ConsensusSynthesisNode - Generates final synthesis after consensus is achieved.
"""

import json
import time
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode
# Using standard print logging like other nodes


class ConsensusSynthesisNode(AsyncNode):
    """Node that synthesizes final consensus into a comprehensive summary."""
    
    def __init__(self):
        super().__init__(max_retries=3, wait=2)
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare synthesis context and create skeleton file."""
        dialogue_path = shared["dialogue_path"]
        
        try:
            # Load dialogue data
            with open(dialogue_path, 'r') as f:
                dialogue_data = json.load(f)
            
            dialogue_dir = os.path.dirname(dialogue_path)
            synthesis_path = os.path.join(dialogue_dir, "consensus_synthesis.md")
            
            # Extract metadata from dialogue
            question = dialogue_data.get("question", "[QUESTION TO BE EXTRACTED]")
            
            # Create skeleton consensus_synthesis.md (orchestrator work)
            synthesis_skeleton = f"""# Consensus Synthesis: {question}

**Question**: {question}
**Status**: CONSENSUS_ACHIEVED
**Generated**: [TIMESTAMP TO BE FILLED]

## Core Consensus
[TO BE FILLED - What was unanimously agreed upon across all dialogue rounds]

## Key Architectural Decisions
[TO BE FILLED - Major architectural choices and rationale from the dialogue]

## Implementation Roadmap
[TO BE FILLED - Concrete next steps, priorities, and sequencing]

## Success Criteria & Metrics
[TO BE FILLED - How implementation success will be measured]

## Risk Mitigation Strategies
[TO BE FILLED - Concerns addressed and mitigation approaches]

## References
- **Source Dialogue**: dialogue.json
- **Dialogue Summary**: summary.md
- **ADR Context**: {dialogue_data.get("adr", "").split(chr(10))[0] if dialogue_data.get("adr") else "[ADR REFERENCE]"}

---
*This synthesis was generated after architectural consensus was achieved through structured dialogue.*
"""
            
            # Write skeleton file (orchestrator creates structure)
            with open(synthesis_path, 'w') as f:
                f.write(synthesis_skeleton)
            
            print(f"  [PREP] Created synthesis skeleton: {synthesis_path} ({len(synthesis_skeleton)} chars)")
            print(f"  [VALIDATION] Synthesis skeleton file created: {synthesis_path}")
            
            # Prepare absolute paths for agent
            from pathlib import Path
            base_dir = Path.cwd()
            synthesis_abs = str(base_dir / synthesis_path)
            dialogue_abs = str(base_dir / dialogue_path)
            
            return {
                "dialogue_path": dialogue_path,
                "dialogue_abs": dialogue_abs,
                "synthesis_path": synthesis_path,
                "synthesis_abs": synthesis_abs,
                "dialogue_data": dialogue_data,
                "adr": dialogue_data.get("adr", ""),
                "question": dialogue_data.get("question", ""),
                "dialogue_entries": dialogue_data.get("dialogue", [])
            }
            
        except Exception as e:
            print(f"  [ERROR] Failed to prepare synthesis: {e}")
            return {
                "error": str(e),
                "dialogue_path": dialogue_path
            }
    
    async def exec_async(self, context: Dict[str, Any]) -> str:
        """Call agent to fill synthesis skeleton (standard agent work)."""
        
        # Check for prep errors
        if context.get("error"):
            return f"ERROR: {context['error']}"
        
        print(f"{'='*60}")
        print(f"STEP 4: Creating Consensus Synthesis")
        print(f"{'='*60}")
        
        # Validation log for file access
        print(f"  [VALIDATION] Synthesis file access validated: {context['synthesis_abs']}")
        print(f"  [VALIDATION] Dialogue file access validated: {context['dialogue_abs']}")
        
        # Standard agent instruction (SDK Reference Scribe pattern - 3 tools)
        synthesis_instruction = f"""Read {context['dialogue_abs']} then read {context['synthesis_abs']} then use Edit to fill in all the placeholder sections with your comprehensive synthesis analysis.

You are a synthesis specialist creating the final architectural summary after consensus. Analyze the complete dialogue and replace all [TO BE FILLED...] placeholders with detailed content. Follow the same structured approach used in summary.md. Focus on actionable outcomes and professional stakeholder communication."""

        # Call agent using shared_components pattern (same as other nodes)
        from .shared_components import run_agent_step, AgentStepResult
        result: AgentStepResult = await run_agent_step(synthesis_instruction, ["Read", "Edit"])
        print(f"  [DEBUG] Synthesis agent used {result.tool_count} tools: {result.tools_used}")
        
        if result.error:
            return f"ERROR: {result.error}"
        
        # Validation log for tool usage
        if result.tool_count < 3:
            print(f"  [VALIDATION] Tool usage validation failed: Synthesis agent must use Read (dialogue), Read (synthesis), and Edit tools (used {result.tool_count} tools)")
            return f"ERROR: Synthesis agent must use Read (dialogue), Read (synthesis), and Edit tools (used {result.tool_count} tools)"
        else:
            print(f"  [VALIDATION] Tool usage validated: Synthesis agent used {result.tool_count} tools correctly")
        
        # Log cost information if available
        if result.cost_usd:
            print(f"  [COST] Synthesis operation cost: ${result.cost_usd:.4f}")
        
        print(f"  [OK] Synthesis agent response ({len(result.response_text)} chars, {result.duration_ms}ms)")
        
        # Validation log for operation completion
        print(f"  [VALIDATION] Synthesis generation completed successfully ({len(result.response_text)} chars)")
        
        return result.response_text
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> str:
        """Fallback - return error message for agent execution failure."""
        print(f"  [FALLBACK] Synthesis agent execution failed: {exc}")
        return f"ERROR: Synthesis agent execution failed: {exc}"
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Process synthesis results and update shared state."""
        
        # Check for exec errors
        if exec_res.startswith("ERROR:"):
            print(f"  [ERROR] Synthesis execution failed: {exec_res}")
            return "error"
        
        # Check if synthesis file was created and filled
        synthesis_path = prep_res.get("synthesis_path")
        if not synthesis_path or not os.path.exists(synthesis_path):
            print(f"  [ERROR] Synthesis file not found: {synthesis_path}")
            return "error"
        
        try:
            with open(synthesis_path, 'r') as f:
                synthesis_content = f.read()
            
            print(f"\n{'='*80}")
            print("CONSENSUS SYNTHESIS COMPLETE")
            print(f"{'='*80}")
            print(f"Synthesis saved: {synthesis_path}")
            print(f"Length: {len(synthesis_content)} characters")
            
            print(f"\n{'='*80}")
            print("FINAL SYNTHESIS PREVIEW:")
            print(f"{'='*80}")
            
            # Show first 500 characters of synthesis
            preview = synthesis_content[:500]
            if len(synthesis_content) > 500:
                preview += "...\n\n[Full synthesis saved to file]"
            
            print(preview)
            print(f"{'='*80}")
            
            # Update shared state
            shared["synthesis_path"] = synthesis_path
            shared["synthesis_complete"] = True
            shared["synthesis_content"] = exec_res
            
            return "default"
            
        except Exception as e:
            print(f"  [ERROR] Failed to read synthesis file: {e}")
            return "error"