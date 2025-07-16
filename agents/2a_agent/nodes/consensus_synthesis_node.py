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
        """Prepare synthesis context."""
        dialogue_path = shared["dialogue_path"]
        
        # Load dialogue data
        with open(dialogue_path, 'r') as f:
            dialogue_data = json.load(f)
        
        return {
            "dialogue_path": dialogue_path,
            "dialogue_data": dialogue_data,
            "adr": dialogue_data.get("adr", ""),
            "question": dialogue_data.get("question", ""),
            "dialogue_entries": dialogue_data.get("dialogue", [])
        }
    
    async def exec_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create skeleton synthesis file and prompt (HAiOS skeleton pattern)."""
        
        dialogue_dir = os.path.dirname(context["dialogue_path"])
        
        # No prompt file needed - direct instruction like other nodes (SDK Reference compliant)

        # Create skeleton consensus_synthesis.md (follows summary.md pattern from main_clean.py)
        synthesis_path = os.path.join(dialogue_dir, "consensus_synthesis.md")
        
        # Extract metadata from dialogue (same pattern as SummarizerNode)
        dialogue_data = context.get("dialogue_data", {})
        question = dialogue_data.get("question", "[QUESTION TO BE EXTRACTED]")
        
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
- **ADR Context**: {dialogue_data.get("adr", "").split("\\n")[0] if dialogue_data.get("adr") else "[ADR REFERENCE]"}

---
*This synthesis was generated after architectural consensus was achieved through structured dialogue.*
"""
        
        # Write skeleton file (orchestrator creates structure - SDK Reference pattern)
        with open(synthesis_path, 'w') as f:
            f.write(synthesis_skeleton)
        
        print(f"  [Tool] Write: consensus_synthesis.md ({len(synthesis_skeleton)} chars) - skeleton created")
        
        return {
            "synthesis_path": synthesis_path,
            "dialogue_path": context["dialogue_path"]
        }
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> Dict[str, Any]:
        """Fallback - create basic synthesis skeleton if dialogue reading fails."""
        print(f"  [FALLBACK] Failed to read dialogue for synthesis: {exc}")
        
        # Create basic fallback synthesis skeleton
        dialogue_dir = os.path.dirname(prep_res.get("dialogue_path", ""))
        synthesis_path = os.path.join(dialogue_dir, "consensus_synthesis.md")
        
        fallback_skeleton = """# Consensus Synthesis: [FALLBACK]

**Question**: [Unable to extract from dialogue]
**Status**: CONSENSUS_ACHIEVED
**Generated**: [TIMESTAMP TO BE FILLED]

## Core Consensus
[TO BE FILLED - Basic consensus summary from available dialogue data]

## Key Architectural Decisions
[TO BE FILLED - Note: Fallback mode - manual review recommended]

## Implementation Roadmap
[TO BE FILLED - Basic next steps if available]

## Success Criteria & Metrics
[TO BE FILLED - Manual review required]

## Risk Mitigation Strategies
[TO BE FILLED - Recommend manual analysis]

---
*This is a fallback synthesis generated due to dialogue reading limitations. Manual review recommended.*
"""
        
        try:
            with open(synthesis_path, 'w') as f:
                f.write(fallback_skeleton)
            
            return {
                "synthesis_path": synthesis_path,
                "dialogue_path": prep_res.get("dialogue_path", ""),
                "fallback": True
            }
        except Exception as e:
            print(f"  [ERROR] Failed to create fallback synthesis: {e}")
            return {"error": str(e)}
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Call agent to perform synthesis using file-based operations."""
        
        if "error" in exec_res:
            print(f"  [ERROR] Synthesis preparation failed: {exec_res['error']}")
            return "error"
        
        try:
            # Use standard agent calling pattern (SDK Reference Scribe pattern - 3 tools)
            synthesis_instruction = """Read dialogue.json then read consensus_synthesis.md then use Edit to fill in all the placeholder sections with your comprehensive synthesis analysis.

You are a synthesis specialist creating the final architectural summary after consensus. Analyze the complete dialogue and replace all [TO BE FILLED...] placeholders with detailed content. Follow the same structured approach used in summary.md. Focus on actionable outcomes and professional stakeholder communication."""

            start_time = time.time()
            
            # Call agent using shared_components pattern (same as other nodes)
            from .shared_components import run_agent_step
            response, tools_used = await run_agent_step(synthesis_instruction, ["Read", "Edit"])
            print(f"  [DEBUG] Synthesis agent used {tools_used} tools")
            
            # Validate agent used required tools (SDK Reference Scribe pattern: Read dialogue + Read synthesis + Edit synthesis)
            if tools_used < 3:
                print(f"  [ERROR] Synthesis agent must use Read (dialogue), Read (synthesis), and Edit tools (used {tools_used} tools)")
                return "error"
            
            duration_ms = int((time.time() - start_time) * 1000)
            print(f"  [OK] Synthesis agent response ({len(response)} chars, {duration_ms}ms)")
            
            # Check if synthesis skeleton was filled
            synthesis_path = exec_res["synthesis_path"]
            
            if os.path.exists(synthesis_path):
                with open(synthesis_path, 'r') as f:
                    synthesis_content = f.read()
                
                print(f"\n{'='*80}")
                print("🎯 CONSENSUS SYNTHESIS COMPLETE")
                print(f"{'='*80}")
                print(f"📝 Synthesis saved: {synthesis_path}")
                print(f"📊 Length: {len(synthesis_content)} characters")
                print(f"⏱️  Generation time: {duration_ms}ms")
                
                if exec_res.get("fallback"):
                    print("⚠️  Generated using fallback method")
                
                print(f"\n{'='*80}")
                print("FINAL SYNTHESIS PREVIEW:")
                print(f"{'='*80}")
                
                # Show first 500 characters of synthesis
                preview = synthesis_content[:500]
                if len(synthesis_content) > 500:
                    preview += "...\n\n[Full synthesis saved to file]"
                
                print(preview)
                print(f"{'='*80}")
                
                shared["synthesis_path"] = synthesis_path
                shared["synthesis_complete"] = True
                
                return "default"
            else:
                print(f"  [ERROR] Agent failed to create synthesis file")
                return "error"
                
        except Exception as e:
            print(f"  [ERROR] Synthesis agent call failed: {e}")
            return "error"