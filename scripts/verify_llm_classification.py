from haios_etl.refinement import RefinementManager
import os
import sys
# Add project root to path
sys.path.append(os.getcwd())

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key present: {bool(api_key)}")

# Create a dummy db for the manager (it needs a path, but we won't write to it for this test if we mock the db or just use a temp one, 
# but RefinementManager inits DatabaseManager which connects. Let's use a temp file.)
import tempfile
fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    # Initialize DB schema
    import sqlite3
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE concepts (id INTEGER PRIMARY KEY, type TEXT, content TEXT, source_adr TEXT);
        CREATE TABLE memory_metadata (memory_id INTEGER, key TEXT, value TEXT);
        CREATE TABLE memory_relationships (source_id INTEGER, target_id INTEGER, relationship_type TEXT);
    """)
    conn.close()

    rm = RefinementManager(path, api_key)
    
    # Test content
    content = "The system architecture defines three layers: Presentation, Logic, and Data."
    print(f"\nTesting content: '{content}'")
    result = rm.refine_memory(1, content)
    print(f"Result Type: {result.knowledge_type}")
    print(f"Confidence: {result.confidence}")
    print(f"Reasoning: {result.reasoning}")

    # Test fallback
    content_directive = "You must follow the protocol."
    print(f"\nTesting content: '{content_directive}'")
    result_d = rm.refine_memory(1, content_directive)
    print(f"Result Type: {result_d.knowledge_type}")
    print(f"Confidence: {result_d.confidence}")
    print(f"Reasoning: {result_d.reasoning}")

finally:
    if os.path.exists(path):
        os.unlink(path)
