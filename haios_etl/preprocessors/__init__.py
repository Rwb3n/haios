"""
File format preprocessors for the HAiOS ETL pipeline.

Preprocessors transform non-standard file formats into plain text before extraction.
"""

from .base import Preprocessor
from .gemini_dump import GeminiDumpPreprocessor

# Registry of available preprocessors
_PREPROCESSORS = [
    GeminiDumpPreprocessor()
]


def get_preprocessors():
    """
    Get the list of available preprocessors.
    
    Returns:
        List of Preprocessor instances
    """
    return _PREPROCESSORS


__all__ = ['Preprocessor', 'GeminiDumpPreprocessor', 'get_preprocessors']
