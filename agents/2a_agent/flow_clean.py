"""
2A Orchestrator Flow - Clean PocketFlow Implementation

Simplified flow that preserves the exact file-based dialogue pattern.
Each agent reads from and appends to the same dialogue file.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'PocketFlow'))

from pocketflow import AsyncFlow
from nodes import (
    ConsensusCheckNode,
    ConsensusSynthesisNode,
    SummarizerNode,
    ReadPromptNode,
    UpdateDialogueNode
)

# Legacy imports for deprecated test flows
from nodes.__legacy.architect1_node import Architect1Node
from nodes.__legacy.architect2_node import Architect2Node


def create_2a_flow():
    """
    Create the 2A dialogue flow with ATOMIC execution nodes (v1.3).
    
    New atomic flow structure (EXEC_PLAN_REFACTOR_ATOMIC_EXECUTION):
    - ConsensusCheck → Summarizer
    - ReadPrompt_A1 → UpdateDialogue_A1
    - ReadPrompt_A2 → UpdateDialogue_A2  
    - Loop based on consensus
    
    Each node performs exactly one atomic operation.
    """
    
    # Create atomic node instances
    consensus_check = ConsensusCheckNode()
    summarizer = SummarizerNode()
    
    # Atomic nodes for Architect-1 workflow
    read_prompt_a1 = ReadPromptNode("A1/A1_PROMPT_FILE_BASED.txt")
    update_dialogue_a1 = UpdateDialogueNode("Architect-1")
    
    # Atomic nodes for Architect-2 workflow  
    read_prompt_a2 = ReadPromptNode("A2/A2_PROMPT_FILE_BASED.txt")
    update_dialogue_a2 = UpdateDialogueNode("Architect-2")
    
    synthesis = ConsensusSynthesisNode()
    
    # Define the atomic flow graph
    # Start with consensus check
    consensus_check - "continue" >> summarizer
    consensus_check - "consensus" >> synthesis
    
    # Summarizer → Architect-1 atomic chain
    summarizer - "default" >> read_prompt_a1
    
    # Architect-1 atomic chain: ReadPrompt → UpdateDialogue
    read_prompt_a1 - "default" >> update_dialogue_a1
    read_prompt_a1 - "error" >> synthesis
    
    # Architect-1 → Architect-2 atomic chain
    update_dialogue_a1 - "continue" >> read_prompt_a2
    update_dialogue_a1 - "error" >> synthesis
    
    # Architect-2 atomic chain: ReadPrompt → UpdateDialogue
    read_prompt_a2 - "default" >> update_dialogue_a2
    read_prompt_a2 - "error" >> synthesis
    
    # Architect-2 determines next action based on consensus  
    update_dialogue_a2 - "continue" >> consensus_check  # Loop back for next round
    update_dialogue_a2 - "consensus" >> synthesis       # End on consensus with synthesis
    update_dialogue_a2 - "error" >> synthesis          # End on error
    
    # IMPORTANT: Also handle consensus detection from Architect-1
    update_dialogue_a1 - "consensus" >> synthesis       # End on consensus from A1
    
    # Synthesis node ends the flow
    synthesis - "default" >> None  # Flow ends naturally
    
    # Create the flow starting with consensus check
    return AsyncFlow(start=consensus_check)


def create_single_round_flow():
    """Create a single round flow for testing."""
    architect1 = Architect1Node()
    architect2 = Architect2Node()
    synthesis = ConsensusSynthesisNode()
    
    # Simple linear flow with error handling
    architect1 - "default" >> architect2
    architect1 - "error" >> synthesis
    
    architect2 - "default" >> synthesis
    architect2 - "continue" >> synthesis
    architect2 - "consensus" >> synthesis
    architect2 - "error" >> synthesis
    
    synthesis - "default" >> None
    
    return AsyncFlow(start=architect1)


def create_custom_flow(a1_prompt: str = "A1/A1_PROMPT_FILE_BASED.txt",
                      a2_prompt: str = "A2/A2_PROMPT_FILE_BASED.txt"):
    """Create a customized 2A flow with atomic nodes and specific prompt files."""
    
    # Create atomic nodes with custom parameters
    consensus_check = ConsensusCheckNode()
    summarizer = SummarizerNode()
    
    # Atomic nodes with custom prompts
    read_prompt_a1 = ReadPromptNode(a1_prompt)
    update_dialogue_a1 = UpdateDialogueNode("Architect-1")
    
    read_prompt_a2 = ReadPromptNode(a2_prompt)
    update_dialogue_a2 = UpdateDialogueNode("Architect-2")
    
    synthesis = ConsensusSynthesisNode()
    
    # Same atomic graph structure as create_2a_flow
    consensus_check - "continue" >> summarizer
    consensus_check - "consensus" >> synthesis
    
    summarizer - "default" >> read_prompt_a1
    
    read_prompt_a1 - "default" >> update_dialogue_a1
    read_prompt_a1 - "error" >> synthesis
    
    update_dialogue_a1 - "continue" >> read_prompt_a2
    update_dialogue_a1 - "error" >> synthesis
    
    read_prompt_a2 - "default" >> update_dialogue_a2
    read_prompt_a2 - "error" >> synthesis
    
    update_dialogue_a2 - "continue" >> consensus_check
    update_dialogue_a2 - "consensus" >> synthesis
    update_dialogue_a2 - "error" >> synthesis
    
    synthesis - "default" >> None
    
    return AsyncFlow(start=consensus_check)