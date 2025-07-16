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
    Architect1Node, 
    Architect2Node, 
    ConsensusCheckNode,
    DialogueSummaryNode,
    SummarizerNode
)


def create_2a_flow():
    """
    Create the 2A dialogue flow with clean PocketFlow implementation.
    
    Flow structure matches original working pattern:
    - Check consensus (skip first round)
    - Run Architect-1 (reads file, appends response)
    - Run Architect-2 (reads file, appends response, checks consensus)
    - Loop or end based on consensus
    """
    
    # Create node instances
    consensus_check = ConsensusCheckNode()
    summarizer = SummarizerNode()
    architect1 = Architect1Node()
    architect2 = Architect2Node()
    summary = DialogueSummaryNode()
    
    # Define the flow graph according to v1.1 specification
    # Start with consensus check
    consensus_check - "continue" >> summarizer
    consensus_check - "consensus" >> summary
    
    # Summarizer creates dialogue context before Architect-1
    summarizer - "default" >> architect1
    
    # Architect-1 flows to Architect-2 on success
    architect1 - "default" >> architect2
    architect1 - "error" >> summary  # End on error
    
    # Architect-2 determines next action based on consensus
    architect2 - "continue" >> consensus_check  # Loop back for next round
    architect2 - "consensus" >> summary         # End on consensus
    architect2 - "error" >> summary            # End on error
    
    # Summary node ends the flow
    summary - "default" >> None  # Flow ends naturally
    
    # Create the flow starting with consensus check
    return AsyncFlow(start=consensus_check)


def create_single_round_flow():
    """Create a single round flow for testing."""
    architect1 = Architect1Node()
    architect2 = Architect2Node()
    summary = DialogueSummaryNode()
    
    # Simple linear flow with error handling
    architect1 - "default" >> architect2
    architect1 - "error" >> summary
    
    architect2 - "default" >> summary
    architect2 - "continue" >> summary
    architect2 - "consensus" >> summary
    architect2 - "error" >> summary
    
    summary - "default" >> None
    
    return AsyncFlow(start=architect1)


def create_custom_flow(a1_prompt: str = "A1/A1_PROMPT_FILE_BASED.txt",
                      a2_prompt: str = "A2/A2_PROMPT_FILE_BASED.txt"):
    """Create a customized 2A flow with specific prompt files."""
    
    # Create nodes with custom parameters
    consensus_check = ConsensusCheckNode()
    summarizer = SummarizerNode()
    architect1 = Architect1Node(prompt_file=a1_prompt)
    architect2 = Architect2Node(prompt_file=a2_prompt)
    summary = DialogueSummaryNode()
    
    # Same graph structure as create_2a_flow with summarizer
    consensus_check - "continue" >> summarizer
    consensus_check - "consensus" >> summary
    
    summarizer - "default" >> architect1
    
    architect1 - "default" >> architect2
    architect1 - "error" >> summary
    
    architect2 - "continue" >> consensus_check
    architect2 - "consensus" >> summary
    architect2 - "error" >> summary
    
    summary - "default" >> None
    
    return AsyncFlow(start=consensus_check)