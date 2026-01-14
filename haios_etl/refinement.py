# generated: 2025-11-27
# System Auto: last updated on: 2025-12-14 20:23:12
import logging
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from .database import DatabaseManager

# Optional LLM import (may not be available in all environments)
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

@dataclass
class RefinementResult:
    knowledge_type: str
    confidence: float
    concepts: List[str]
    reasoning: str

class RefinementManager:
    def __init__(self, db_path: str, api_key: Optional[str] = None):
        self.db = DatabaseManager(db_path)
        self.api_key = api_key

    def scan_raw_memories(self, limit: int = 10) -> List[Dict]:
        """
        Find concepts that have not been refined yet.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Select concepts that do NOT have a 'refinement_status' metadata entry
        # We'll refine concepts rather than artifacts
        sql = """
            SELECT c.id, c.type, c.content
            FROM concepts c
            LEFT JOIN memory_metadata m ON c.id = m.memory_id AND m.key = 'refinement_status'
            WHERE m.value IS NULL OR m.value = 'raw'
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
        rows = cursor.fetchall()
        
        return [{'id': r[0], 'type': r[1], 'content': r[2]} for r in rows]

    def _classify_with_llm(self, content: str) -> Optional[str]:
        """
        Classify content using LLM (Greek Triad taxonomy).

        Returns:
            Classification string ('episteme', 'techne', 'doxa') or None if LLM fails.
        """
        if not self.api_key or not GENAI_AVAILABLE:
            return None

        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-2.5-flash-lite")

            prompt = f"""Classify this content using Greek Triad taxonomy.

DEFINITIONS:
- episteme: Factual knowledge, definitions, architecture specs, verified truths
- techne: How-to guides, procedures, implementation steps, practical skills
- doxa: Opinions, recommendations, beliefs, proposals, critiques

CONTENT:
{content[:2000]}

Respond with ONLY one word: episteme, techne, or doxa"""

            response = model.generate_content(prompt)
            result = response.text.strip().lower()

            if result in ("episteme", "techne", "doxa"):
                return result
            return None

        except Exception as e:
            logging.warning(f"LLM classification failed: {e}")
            return None

    def refine_memory(self, memory_id: int, content: str) -> RefinementResult:
        """
        Analyze memory content using LLM with heuristic fallback.

        Classification order:
        1. Try LLM classification (if api_key available)
        2. Fall back to heuristic if LLM fails or unavailable
        """
        # Try LLM first
        llm_result = self._classify_with_llm(content)

        if llm_result:
            return RefinementResult(
                knowledge_type=llm_result,
                confidence=0.9,
                concepts=[],
                reasoning=f"LLM classification: {llm_result}"
            )

        # Fallback to heuristic
        if "Directive" in content or "must" in content.lower():
            return RefinementResult(
                knowledge_type="doxa",
                confidence=0.6,
                concepts=[],
                reasoning="Heuristic: directive language detected."
            )
        elif "Concept" in content:
            return RefinementResult(
                knowledge_type="episteme",
                confidence=0.7,
                concepts=[],
                reasoning="Heuristic: concept label detected."
            )
        else:
            return RefinementResult(
                knowledge_type="doxa",
                confidence=0.5,
                concepts=[],
                reasoning="Heuristic: default classification."
            )

    def save_refinement(self, memory_id: int, result: RefinementResult):
        """
        Save refinement results: metadata and links.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 1. Save Metadata
        self._set_metadata(cursor, memory_id, "knowledge_type", result.knowledge_type)
        self._set_metadata(cursor, memory_id, "refinement_status", "processed")
        self._set_metadata(cursor, memory_id, "refinement_confidence", str(result.confidence))
        
        # 2. Process Concepts (Deduplicate & Link)
        for concept_text in result.concepts:
            episteme_id = self._get_or_create_episteme(concept_text)
            self._link_memories(cursor, memory_id, episteme_id, "derived_from")
            
        conn.commit()

    def _set_metadata(self, cursor, memory_id, key, value):
        cursor.execute("""
            INSERT INTO memory_metadata (memory_id, key, value)
            VALUES (?, ?, ?)
        """, (memory_id, key, value))

    def _get_or_create_episteme(self, content: str) -> int:
        """
        Find existing Episteme node or create new one.

        Design Decision DD-001: Uses concepts table (not artifacts) because:
        - concepts table has content column (artifacts does not)
        - Consistent with existing data model
        - Preserves existing metadata row references
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # 1. Simple exact match check (TODO: Vector Search per P8-G3)
        # Look for concepts with type=episteme in metadata and same content
        sql = """
            SELECT c.id
            FROM concepts c
            JOIN memory_metadata m ON c.id = m.memory_id
            WHERE m.key = 'knowledge_type' AND m.value = 'episteme'
            AND c.content = ?
        """
        cursor.execute(sql, (content,))
        row = cursor.fetchone()

        if row:
            return row[0]

        # 2. Create New Episteme in concepts table
        cursor.execute(
            "INSERT INTO concepts (type, content, source_adr) VALUES (?, ?, ?)",
            ("Episteme", content, "virtual:episteme")
        )
        new_id = cursor.lastrowid

        self._set_metadata(cursor, new_id, "knowledge_type", "episteme")
        conn.commit()
        return new_id

    def _link_memories(self, cursor, source_id, target_id, rel_type):
        cursor.execute("""
            INSERT INTO memory_relationships (source_id, target_id, relationship_type)
            VALUES (?, ?, ?)
        """, (source_id, target_id, rel_type))
