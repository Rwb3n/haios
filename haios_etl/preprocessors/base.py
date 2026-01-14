"""
Base interface for file format preprocessors.

Preprocessors transform non-standard file formats (e.g., JSON dumps, proprietary formats)
into plain text before extraction. This allows the extraction pipeline to remain format-agnostic.
"""

from abc import ABC, abstractmethod


class Preprocessor(ABC):
    """Abstract base class for file format preprocessors."""
    
    @abstractmethod
    def can_handle(self, content: str) -> bool:
        """
        Determine if this preprocessor can handle the given content.
        
        Args:
            content: Raw file content as string
            
        Returns:
            True if this preprocessor should process this content, False otherwise
        """
        pass
    
    @abstractmethod
    def preprocess(self, content: str) -> str:
        """
        Transform the content into plain text suitable for extraction.
        
        Args:
            content: Raw file content as string
            
        Returns:
            Transformed content as plain text
        """
        pass
