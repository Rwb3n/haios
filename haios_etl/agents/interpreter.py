# generated: 2025-12-01
# System Auto: last updated on: 2025-12-01 14:44:48
"""
Interpreter Agent - The "Front Desk" of HAIOS

Translates operator intent (natural language) into system directives (structured).
Implements DD-012 (LLM translation), DD-013 (confidence), DD-014 (no-context behavior).

Reference: docs/plans/PLAN-AGENT-ECOSYSTEM-001.md
           docs/handoff/2025-12-01-VALIDATION-interpreter-ingester-implementation.md
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import logging
import re
import os

logger = logging.getLogger(__name__)


@dataclass
class InterpreterConfig:
    """Configuration for Interpreter agent (DD-020)."""
    timeout_seconds: int = 30
    use_llm: bool = True
    fallback_to_rules: bool = True
    model_id: str = "gemini-2.5-flash-lite"


@dataclass
class InterpretationResult:
    """Result of translating operator intent to system directive (DD-013)."""
    directive: Dict[str, Any]       # Structured system directive
    confidence: float               # 0.0-1.0 (DD-013: no threshold, caller decides)
    grounded: bool                  # True if relevant context was found (DD-014)
    context_used: List[str]         # Memory items used for grounding


class Interpreter:
    """
    Interpreter Agent - Translates operator intent to system directives.

    Design Decisions:
        DD-012: LLM-based translation with rule-based fallback
        DD-013: No confidence threshold; return score, let caller decide
        DD-014: Proceed when no context, flag as grounded=false
    """

    AGENT_ID = "interpreter-v1"

    # Rule-based patterns for common operations (DD-012 fallback)
    RULE_PATTERNS = [
        (r'\b(search|find|look for|query)\b', 'search'),
        (r'\b(ingest|store|save|add)\b', 'ingest'),
        (r'\b(list|show|display|get all)\b', 'list'),
        (r'\b(delete|remove|clear)\b', 'delete'),
        (r'\b(update|modify|change)\b', 'update'),
        (r'\b(classify|categorize)\b', 'classify'),
        (r'\b(extract|parse)\b', 'extract'),
    ]

    # Content type patterns for ingestion hints
    TYPE_PATTERNS = [
        (r'\b(episteme|knowledge|fact|truth)\b', 'episteme'),
        (r'\b(techne|how-?to|procedure|step|guide)\b', 'techne'),
        (r'\b(doxa|opinion|belief|think|feel)\b', 'doxa'),
    ]

    def __init__(
        self,
        config: Optional[InterpreterConfig] = None,
        db_manager=None,
        api_key: Optional[str] = None
    ):
        self.config = config or InterpreterConfig()
        self.db_manager = db_manager
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

    def translate(self, intent: str) -> InterpretationResult:
        """
        Translate operator intent to system directive.

        Args:
            intent: Natural language operator intent

        Returns:
            InterpretationResult with directive, confidence, grounding status
        """
        # Handle empty intent
        if not intent or not intent.strip():
            return InterpretationResult(
                directive={"action": "unknown", "note": "empty intent"},
                confidence=0.1,
                grounded=False,
                context_used=[]
            )

        # Step 1: Search memory for context
        context = self._search_memory(intent)
        grounded = len(context) > 0

        # Step 2: Translate (LLM or rule-based)
        directive = None
        confidence = 0.5

        if self.config.use_llm:
            try:
                directive = self._translate_with_llm(intent, context)
                if directive:
                    confidence = self._calculate_confidence(directive, context)
            except Exception as e:
                logger.warning(f"LLM translation failed: {e}")
                if not self.config.fallback_to_rules:
                    raise

        # Fallback to rule-based if LLM failed or disabled
        if directive is None and self.config.fallback_to_rules:
            directive = self._translate_with_rules(intent)
            confidence = self._calculate_confidence(directive, context, is_rule_based=True)

        # Ensure we always have a directive
        if directive is None:
            directive = {"action": "unknown", "raw_intent": intent}
            confidence = 0.2

        return InterpretationResult(
            directive=directive,
            confidence=confidence,
            grounded=grounded,
            context_used=context
        )

    def _search_memory(self, intent: str) -> List[str]:
        """
        Search memory for relevant context.

        Args:
            intent: The operator intent to search context for

        Returns:
            List of relevant context strings from memory
        """
        if self.db_manager is None:
            return []

        try:
            # Use memory search functionality if available
            from ..retrieval import ReasoningAwareRetrieval
            from ..extraction import ExtractionManager

            extraction_manager = ExtractionManager(api_key=self.api_key or "dummy")
            retrieval = ReasoningAwareRetrieval(self.db_manager, extraction_manager)

            result = retrieval.search_with_experience(intent)

            # Extract relevant context strings
            context = []
            if isinstance(result, dict):
                if 'concepts' in result:
                    for concept in result.get('concepts', [])[:5]:
                        if isinstance(concept, dict):
                            context.append(f"{concept.get('type', '')}: {concept.get('content', '')}")
                        else:
                            context.append(str(concept))
                if 'entities' in result:
                    for entity in result.get('entities', [])[:5]:
                        if isinstance(entity, dict):
                            context.append(f"{entity.get('type', '')}: {entity.get('value', '')}")
                        else:
                            context.append(str(entity))

            return context

        except Exception as e:
            logger.warning(f"Memory search failed: {e}")
            return []

    def _translate_with_llm(self, intent: str, context: List[str]) -> Optional[Dict[str, Any]]:
        """
        Translate intent using LLM (DD-012 primary method).

        Args:
            intent: The operator intent
            context: Memory context for grounding

        Returns:
            Structured directive dict or None if failed
        """
        try:
            import google.generativeai as genai

            if not self.api_key:
                logger.warning("No API key available for LLM translation")
                return None

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.config.model_id)

            # Build prompt with context
            context_str = "\n".join(context) if context else "No relevant context found."

            prompt = f"""You are a HAIOS system interpreter. Translate the operator's intent into a structured directive.

CONTEXT FROM MEMORY:
{context_str}

OPERATOR INTENT:
{intent}

Respond with a JSON object containing:
- action: The primary action (search, ingest, list, delete, update, classify, extract, unknown)
- target: What the action applies to (optional)
- parameters: Additional parameters (optional)
- type: Content type for ingestion (episteme, techne, doxa) if applicable

Example response:
{{"action": "ingest", "target": "document.md", "type": "episteme"}}

JSON response:"""

            response = model.generate_content(prompt)

            # Parse JSON from response
            import json
            response_text = response.text.strip()

            # Try to extract JSON from response
            if response_text.startswith('{'):
                return json.loads(response_text)

            # Try to find JSON in response
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                return json.loads(json_match.group())

            return None

        except Exception as e:
            logger.error(f"LLM translation error: {e}")
            return None

    def _translate_with_rules(self, intent: str) -> Dict[str, Any]:
        """
        Translate intent using rule-based patterns (DD-012 fallback).

        Args:
            intent: The operator intent

        Returns:
            Structured directive dict
        """
        intent_lower = intent.lower()

        # Detect action
        action = "unknown"
        for pattern, action_name in self.RULE_PATTERNS:
            if re.search(pattern, intent_lower, re.IGNORECASE):
                action = action_name
                break

        # Build directive
        directive = {"action": action, "raw_intent": intent}

        # Extract target (quoted strings or last noun phrase)
        quoted = re.findall(r'"([^"]+)"', intent)
        if quoted:
            directive["target"] = quoted[0]

        # Detect content type for ingestion
        if action == "ingest":
            for pattern, type_name in self.TYPE_PATTERNS:
                if re.search(pattern, intent_lower, re.IGNORECASE):
                    directive["type"] = type_name
                    break

        return directive

    def _calculate_confidence(
        self,
        directive: Dict[str, Any],
        context: List[str],
        is_rule_based: bool = False
    ) -> float:
        """
        Calculate confidence score for the interpretation (DD-013).

        Args:
            directive: The generated directive
            context: Memory context used
            is_rule_based: Whether rule-based (lower base confidence)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence
        if is_rule_based:
            confidence = 0.5
        else:
            confidence = 0.7

        # Boost for grounded interpretation
        if context:
            confidence += 0.15

        # Boost for known action
        if directive.get("action") != "unknown":
            confidence += 0.1

        # Penalty for unclear or ambiguous
        if directive.get("action") == "unclear" or directive.get("note") == "ambiguous input":
            confidence -= 0.3

        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, confidence))
