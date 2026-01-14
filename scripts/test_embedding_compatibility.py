
import os
import sys
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

# Load env for API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API Key")
    sys.exit(1)

genai.configure(api_key=api_key)

def get_embedding(text, task_type):
    return genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type=task_type
    )['embedding']

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

query_text = "How do I fix SQLite database locked error?"
concept_text = "Decision: Enabled WAL mode in SQLite to prevent locking issues."

print(f"Query: {query_text}")
print(f"Concept: {concept_text}")
print("-" * 40)

# Scenario A: Current State (Both are Queries)
vec_q = get_embedding(query_text, "retrieval_query")
vec_c_query = get_embedding(concept_text, "retrieval_query")
sim_qq = cosine_similarity(vec_q, vec_c_query)
print(f"Similarity (Query vs Query): {sim_qq:.4f}")

# Scenario B: Proposed State (Concept is Document)
vec_c_doc = get_embedding(concept_text, "retrieval_document")
sim_qd = cosine_similarity(vec_q, vec_c_doc)
print(f"Similarity (Query vs Document): {sim_qd:.4f}")

# Scenario C: Trace vs Trace (Query vs Query - Control)
vec_q2 = get_embedding("SQLite database is locked, help", "retrieval_query")
sim_qq_control = cosine_similarity(vec_q, vec_q2)
print(f"Similarity (Query vs Similar Query): {sim_qq_control:.4f}")
