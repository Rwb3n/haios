import sys
import os
import sqlite3
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from haios_etl.database import DatabaseManager

def investigate_concepts():
    db_path = "haios_memory.db"
    db = DatabaseManager(db_path)
    conn = db.get_connection()
    
    print("--- Concept Types Distribution ---")
    query = """
        SELECT type, COUNT(*) as count 
        FROM concepts 
        GROUP BY type 
        ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_markdown(index=False))
    
    print("\n--- Top 10 Concepts by Occurrence ---")
    query = """
        SELECT c.type, c.content, COUNT(co.id) as occurrences
        FROM concepts c
        JOIN concept_occurrences co ON c.id = co.concept_id
        GROUP BY c.id
        ORDER BY occurrences DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_markdown(index=False))

    print("\n--- Entity Types Distribution ---")
    query = """
        SELECT type, COUNT(*) as count 
        FROM entities 
        GROUP BY type 
        ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    investigate_concepts()
