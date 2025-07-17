#!/usr/bin/env python3
"""
Create missing consensus synthesis for session_20250717_132404
"""

import asyncio
import sys
import os

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'PocketFlow'))
sys.path.append(os.path.dirname(__file__))

from nodes.consensus_synthesis_node import ConsensusSynthesisNode


async def create_missing_synthesis():
    """Create the missing consensus synthesis for the completed dialogue."""
    
    synthesis_node = ConsensusSynthesisNode()
    shared_state = {
        'dialogue_path': 'output_2A/session_20250717_132404/dialogue.json',
        'session_dir': 'output_2A/session_20250717_132404'
    }
    
    print("Creating missing consensus synthesis for session_20250717_132404...")
    
    try:
        context = await synthesis_node.prep_async(shared_state)
        result = await synthesis_node.exec_async(context) 
        final_result = await synthesis_node.post_async(shared_state, context, result)
        
        print(f"Synthesis creation completed with result: {final_result}")
        
        # Check if file was created
        synthesis_path = "output_2A/session_20250717_132404/consensus_synthesis.md"
        if os.path.exists(synthesis_path):
            with open(synthesis_path, 'r') as f:
                content = f.read()
            print(f"Synthesis file created successfully ({len(content)} characters)")
        else:
            print("Synthesis file was not created")
            
    except Exception as e:
        print(f"Error creating synthesis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(create_missing_synthesis())