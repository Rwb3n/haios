"""
Architect1Node - DEPRECATED Compatibility Wrapper

This node is deprecated as of v1.3 due to AP-007: In-Node Orchestration anti-pattern.

MIGRATION: Use ReadPromptNode + UpdateDialogueNode chain instead for atomic execution.

This wrapper exists only for backwards compatibility and will be removed in v2.0.
"""

import warnings
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PocketFlow'))

from pocketflow import AsyncNode


class Architect1Node(AsyncNode):
    """DEPRECATED: Use ReadPromptNode + UpdateDialogueNode chain instead."""
    
    def __init__(self, prompt_file: str = "A1/A1_PROMPT_FILE_BASED.txt"):
        super().__init__(max_retries=2, wait=1.0)
        self.prompt_file = prompt_file
        
        # Issue deprecation warning
        warnings.warn(
            "Architect1Node is deprecated due to AP-007 anti-pattern. "
            "Use ReadPromptNode + UpdateDialogueNode chain for atomic execution.",
            DeprecationWarning,
            stacklevel=2
        )
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Deprecated preparation method."""
        return {"error": "DEPRECATED: Use atomic node chain instead"}
    
    async def exec_async(self, context: Dict[str, Any]) -> str:
        """Deprecated execution method."""
        return "ERROR: Architect1Node is deprecated. Use ReadPromptNode + UpdateDialogueNode chain."
    
    async def exec_fallback_async(self, prep_res: Dict[str, Any], exc: Exception) -> str:
        """Deprecated fallback method."""
        return "ERROR: Architect1Node is deprecated."
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Deprecated post method."""
        return "error"