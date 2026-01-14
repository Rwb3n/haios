# generated: 2025-11-24
# System Auto: last updated on: 2025-12-04 22:57:22
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import os
import time
import logging

import langextract as lx
import textwrap
from .preprocessors import get_preprocessors

@dataclass
class Entity:
    type: str
    value: str

@dataclass
class Concept:
    type: str
    content: str
    source_adr: Optional[str] = None

@dataclass
class ExtractionResult:
    entities: List[Entity]
    concepts: List[Concept]

class ExtractionError(Exception):
    """Custom exception for extraction failures."""
    pass

class ErrorType(Enum):
    """Classification of extraction errors."""
    RETRYABLE = "retryable"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"

@dataclass
class ExtractionConfig:
    """Configuration for extraction with error handling."""
    max_retries: int = 3
    backoff_base: float = 2.0
    max_workers: int = 5  # Reduced to avoid rate limits (Gemini free tier: 15 RPM)
    max_char_buffer: int = 10000
    timeout: int = 120  # seconds

class ExtractionManager:
    def __init__(
        self,
        api_key: str,
        # Using gemini-2.5-flash-lite because it offers UNLIMITED daily quota
        # Standard gemini-2.5-flash has a 1,500 request/day limit
        model_id: str = "gemini-2.5-flash-lite",
        config: Optional[ExtractionConfig] = None
    ):
        self.api_key = api_key
        self.model_id = model_id
        self.config = config or ExtractionConfig()
        self.prompt = self._build_prompt()
        self.examples = self._build_examples()
        self.preprocessors = get_preprocessors()

    def _build_prompt(self) -> str:
        """Build extraction prompt from schema definition."""
        return textwrap.dedent("""
            Extract entities and concepts from HAIOS agent conversation logs.

            ENTITIES to extract:
            - User: Speaker role for human operator (User:, human:, operator:)
            - Agent: Speaker role for AI (Cody:, Gemini:, Claude:, agent:)
            - ADR: Architecture Decision Records (ADR-OS-XXX)
            - Filepath: File references (paths ending in .py, .md, .json, etc.)
            - AntiPattern: Anti-pattern references (AP-XXX)

            CONCEPTS to extract (use FIRST matching type - priority order):

            1. Decision: FORMAL CHOICES announced with explicit decision language
               - Markers: "decided", "decision:", "will adopt", "choosing", "selected"
               - NOT status updates like "I'm now doing X" without choice context

            2. Critique: EVALUATIVE statements identifying problems or assessments
               - Markers: "wrong", "flaw", "issue", "problem", "risk", "concern", "should not"
               - Includes negative feedback AND analytical quality assessments

            3. Proposal: SUGGESTIONS or RECOMMENDATIONS for future action
               - Markers: "propose", "suggest", "recommend", "could", "might", "consider"
               - NOT statements with imperative mood (those are Directives)

            4. Directive: COMMANDS or INSTRUCTIONS requiring action
               - Markers: Imperative verbs ("implement", "create", "ensure"), "must", "shall"
               - NOT descriptions of how something works (skip those entirely)
               - NOT present progressive status updates ("I'm doing X", "I'm implementing X")

            DO NOT EXTRACT any of these (skip entirely):
            - Process descriptions explaining how something works
            - Status updates using present progressive ("I'm doing X", "We're migrating X")
            - Pure factual descriptions without action or evaluation
            - Statements starting with "currently" describing ongoing work

            Only extract actionable concepts (commands, evaluations, suggestions, decisions).

            Use exact text for extractions. Extract in order of appearance.
            Provide attributes for context when available.
        """)

    def _build_examples(self) -> List[lx.data.ExampleData]:
        """Build few-shot examples from schema."""
        return [
            # Example 1: Entity extraction
            lx.data.ExampleData(
                text="User: Please implement ADR-OS-023 in the database.py file.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="User:",
                        attributes={"entity_type": "User"}
                    ),
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="ADR-OS-023",
                        attributes={"entity_type": "ADR"}
                    ),
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="database.py",
                        attributes={"entity_type": "Filepath"}
                    ),
                ]
            ),

            # Example 2: Concept extraction
            lx.data.ExampleData(
                text="Agent: I propose we implement a Decoupled Adapter Pattern to solve this issue.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="Agent:",
                        attributes={"entity_type": "Agent"}
                    ),
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="I propose we implement a Decoupled Adapter Pattern",
                        attributes={"concept_type": "Proposal"}
                    ),
                ]
            ),

            # Example 3: Critique
            lx.data.ExampleData(
                text="User: No, that's wrong. The flaw is that the logic lives in the n8n database.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="User:",
                        attributes={"entity_type": "User"}
                    ),
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="No, that's wrong",
                        attributes={"concept_type": "Critique"}
                    ),
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="The flaw is that the logic lives in the n8n database",
                        attributes={"concept_type": "Critique"}
                    ),
                ]
            ),

            # Example 4: Decision
            lx.data.ExampleData(
                text="Decision: ADOPT AND CANONIZE THIS POLICY per ADR-OS-015.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="Decision: ADOPT AND CANONIZE THIS POLICY",
                        attributes={"concept_type": "Decision"}
                    ),
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="ADR-OS-015",
                        attributes={"entity_type": "ADR"}
                    ),
                ]
            ),

            # Example 5: AntiPattern
            lx.data.ExampleData(
                text="This violates AP-042 (Tight Coupling). We should refactor.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="AP-042",
                        attributes={"entity_type": "AntiPattern"}
                    ),
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="This violates AP-042 (Tight Coupling)",
                        attributes={"concept_type": "Critique"}
                    ),
                ]
            ),

            # Example 6: Proposal (suggestive language) - NOT Directive
            lx.data.ExampleData(
                text="Agent: We could implement caching here to improve performance.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="Agent:",
                        attributes={"entity_type": "Agent"}
                    ),
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="We could implement caching here to improve performance",
                        attributes={"concept_type": "Proposal"}  # "could" = suggestive
                    ),
                ]
            ),

            # Example 7: Decision with explicit choice language
            lx.data.ExampleData(
                text="After reviewing the options, we've decided to use PostgreSQL for the database.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="we've decided to use PostgreSQL for the database",
                        attributes={"concept_type": "Decision"}  # Explicit "decided"
                    ),
                ]
            ),

        ]

    def _classify_error(self, exception: Exception) -> ErrorType:
        """Classify error as retryable or permanent using heuristics."""
        error_msg = str(exception).lower()

        # Retryable errors (transient)
        retryable_patterns = [
            "rate limit", "quota", "429", "503", "timeout",
            "temporarily unavailable", "connection reset"
        ]

        # Permanent errors (bad request, auth, etc.)
        permanent_patterns = [
            "invalid api key", "authentication failed",
            "400", "401", "403", "404",
            "invalid model", "provider not found"
        ]

        if any(pattern in error_msg for pattern in retryable_patterns):
            return ErrorType.RETRYABLE

        if any(pattern in error_msg for pattern in permanent_patterns):
            return ErrorType.PERMANENT

        return ErrorType.UNKNOWN

    def _apply_preprocessors(self, content: str) -> str:
        """
        Apply registered preprocessors to transform non-standard formats.
        
        Loops through all preprocessors and applies the first one that can handle the content.
        
        Args:
            content: Raw file content
            
        Returns:
            Preprocessed content (or original if no preprocessor matched)
        """
        for preprocessor in self.preprocessors:
            if preprocessor.can_handle(content):
                logging.info(f"Applying preprocessor: {preprocessor.__class__.__name__}")
                return preprocessor.preprocess(content)
        
        # No preprocessor matched, return original content
        return content

    def extract_from_file(self, file_path: str, content: str) -> ExtractionResult:
        """Extract entities and concepts from file content using LLM with retry logic."""
        
        # Apply preprocessors to handle non-standard formats (e.g., JSON dumps)
        content = self._apply_preprocessors(content)
        
        # Prepend file path to provide context to the LLM
        content = f"File: {file_path}\n\n{content}"
        
        for attempt in range(self.config.max_retries):
            try:
                # Call langextract with proper parameters
                result = lx.extract(
                    text_or_documents=content,
                    prompt_description=self.prompt,
                    examples=self.examples,
                    model_id=self.model_id,
                    api_key=self.api_key,

                    # Optional: Quality settings
                    temperature=0.2,              # High precision
                    use_schema_constraints=True,  # Enforce structure
                    fence_output=True,            # Clean JSON output
                )

                # Parse langextract result into our format
                entities = []
                concepts = []

                for extraction in result.extractions:
                    # Defensive check for None attributes
                    attributes = extraction.attributes or {}

                    if extraction.extraction_class == "entity":
                        entity_type = attributes.get("entity_type", "Unknown")
                        entities.append(Entity(
                            type=entity_type,
                            value=extraction.extraction_text
                        ))

                    elif extraction.extraction_class == "concept":
                        concept_type = attributes.get("concept_type", "Unknown")
                        concepts.append(Concept(
                            type=concept_type,
                            content=extraction.extraction_text,
                            source_adr=None  # Could extract from context
                        ))

                return ExtractionResult(entities=entities, concepts=concepts)

            except Exception as e:
                error_type = self._classify_error(e)

                # Fail immediately on permanent errors
                if error_type == ErrorType.PERMANENT:
                    logging.error(f"Permanent error for {file_path}: {e}")
                    raise ExtractionError(f"Extraction failed for {file_path}: {str(e)}") from e

                # Retry on retryable/unknown errors
                if error_type in (ErrorType.RETRYABLE, ErrorType.UNKNOWN) and attempt < self.config.max_retries - 1:
                    sleep_time = self.config.backoff_base ** attempt
                    logging.warning(
                        f"Retryable error for {file_path} "
                        f"(attempt {attempt + 1}/{self.config.max_retries}): {e}. "
                        f"Retrying in {sleep_time}s..."
                    )
                    time.sleep(sleep_time)
                else:
                    # Final attempt or unknown error
                    logging.error(f"Extraction failed for {file_path} after {attempt + 1} attempts: {e}")
                    raise ExtractionError(f"Extraction failed for {file_path}: {str(e)}") from e


    def embed_content(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using the configured model.
        """
        try:
            # Use langextract's underlying model provider (Gemini)
            # Since langextract wraps it, we might need to access the provider directly
            # or use google.generativeai directly since we have the API key.
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)

            # Use a dedicated embedding model
            embedding_model = "models/text-embedding-004"

            result = genai.embed_content(
                model=embedding_model,
                content=text,
                task_type="retrieval_query"
            )

            return result['embedding']

        except Exception as e:
            logging.error(f"Embedding generation failed: {e}")
            raise ExtractionError(f"Embedding generation failed: {str(e)}") from e

    def extract_strategy(
        self,
        query: str,
        approach: str,
        outcome: str,
        results_summary: str = "",
        error_details: str = ""
    ) -> dict:
        """
        Extract transferable strategy from execution outcome.

        Per ReasoningBank paper: stores WHAT WAS LEARNED, not what happened.
        - For success: extracts generalizable strategies
        - For failure: articulates preventive lessons

        Args:
            query: The original search query
            approach: The approach/strategy used
            outcome: 'success' or 'failure'
            results_summary: Summary of results (for success cases)
            error_details: Error information (for failure cases)

        Returns:
            dict with {title, description, content} per ReasoningBank paper format
        """
        import json
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_id)

        if outcome == 'success':
            prompt = f"""Analyze this successful memory search execution and extract a transferable reasoning strategy.

Query: {query}
Approach Used: {approach}
Results Summary: {results_summary if results_summary else "Found relevant results"}

Your task: Extract a HIGH-LEVEL STRATEGY that could help with similar future tasks.
Do NOT just describe what happened. Instead, extract WHAT WE LEARNED that is transferable.

Output ONLY valid JSON (no markdown):
{{"title": "brief strategy name (3-5 words)", "description": "one-line summary of when to use this", "content": "detailed transferable strategy (2-3 sentences)"}}"""
        else:
            prompt = f"""Analyze this failed memory search execution and extract a preventive lesson.

Query: {query}
Approach Used: {approach}
Error/Failure Details: {error_details if error_details else "No results found"}

Your task: Extract a PREVENTIVE LESSON to avoid this failure in future.
Do NOT just describe what went wrong. Instead, extract WHAT TO AVOID and WHY.

Output ONLY valid JSON (no markdown):
{{"title": "brief lesson name (3-5 words)", "description": "one-line summary of what to avoid", "content": "detailed preventive lesson (2-3 sentences)"}}"""

        try:
            response = model.generate_content(prompt)
            # Clean up response - remove markdown code blocks if present
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]  # Remove first line
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

            return json.loads(text)
        except json.JSONDecodeError as e:
            logging.warning(f"Strategy extraction JSON parse failed: {e}")
            # Fallback to structured default
            return {
                'title': f'{outcome.capitalize()} Trace',
                'description': approach,
                'content': f'Outcome: {outcome}. Query: {query[:100]}'
            }
        except Exception as e:
            logging.warning(f"Strategy extraction failed: {e}")
            return {
                'title': f'{outcome.capitalize()} Trace',
                'description': approach,
                'content': f'Outcome: {outcome}. Query: {query[:100]}'
            }

