"""
2A Orchestrator Node Classes - Atomic Node Pattern

This module provides a clean API for accessing individual node classes
while maintaining the modular structure of one class per file.

v1.3: Added atomic execution nodes implementing EXEC_PLAN_REFACTOR_ATOMIC_EXECUTION
"""

from .consensus_check_node import ConsensusCheckNode
from .consensus_synthesis_node import ConsensusSynthesisNode
from .summarizer_node import SummarizerNode
from .shared_components import run_agent_step

# v1.3 Atomic execution nodes (active)
from .read_prompt_node import ReadPromptNode
from .update_dialogue_node import UpdateDialogueNode

# Legacy nodes (deprecated) - import from __legacy/ if needed
# from .__legacy.architect1_node import Architect1Node
# from .__legacy.architect2_node import Architect2Node  
# from .__legacy.dialogue_summary_node import DialogueSummaryNode

__all__ = [
    'ConsensusCheckNode',
    'ConsensusSynthesisNode',
    'SummarizerNode',
    'run_agent_step',
    # v1.3 Atomic nodes (active)
    'ReadPromptNode',
    'UpdateDialogueNode'
]