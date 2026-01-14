"""
Preprocessor for Gemini API session dumps.

Gemini session dumps are JSON files containing conversation history with metadata.
This preprocessor extracts only the conversational text fields, discarding metadata.
"""

import re
import json
import logging
from .base import Preprocessor


class GeminiDumpPreprocessor(Preprocessor):
    """Preprocessor that extracts text from Gemini API session dump JSON files."""
    
    def can_handle(self, content: str) -> bool:
        """
        Detect Gemini session dumps by looking for characteristic markers.
        
        Args:
            content: Raw file content
            
        Returns:
            True if content appears to be a Gemini session dump
        """
        # Check if this looks like a JSON object (starts with {)
        if not content.strip().startswith('{'):
            return False
            
        # Look for Gemini session dump markers
        return '"runSettings"' in content or '"chunkedPrompt"' in content
    
    def preprocess(self, content: str) -> str:
        """
        Extract text fields from Gemini session dump JSON.
        
        Uses regex to extract values from "text", "content", and "adr" keys.
        Handles malformed JSON with literal newlines using re.DOTALL flag.
        
        Args:
            content: Raw Gemini session dump JSON
            
        Returns:
            Extracted text concatenated with newlines, or empty string if no text found
        """
        try:
            # Extract values for "text", "content", or "adr" keys
            # Pattern matches: "(text|content|adr)": "..." (handling escaped quotes and literal newlines)
            # Added re.DOTALL to handle literal newlines in malformed JSON
            pattern = r'"(?:text|content|adr)":\s*"((?:[^"\\]|\\.)*)"'
            matches = re.finditer(pattern, content, flags=re.DOTALL)
            
            cleaned_lines = []
            for match in matches:
                raw_str = match.group(1)
                try:
                    # Unescape the JSON string safely
                    decoded_str = json.loads(f'"{raw_str}"')
                    cleaned_lines.append(decoded_str)
                except Exception:
                    # Fallback to raw string if decoding fails
                    cleaned_lines.append(raw_str)
            
            if cleaned_lines:
                logging.info(f"Gemini dump preprocessor: extracted {len(cleaned_lines)} text blocks")
                return "\n\n".join(cleaned_lines)
            
            # If no text found, return empty string
            logging.warning("Gemini dump detected but no text fields found")
            return ""

        except Exception as e:
            logging.warning(f"Gemini dump preprocessor failed: {e}")
            # Return original content as fallback
            return content
