
import logging
import sys
import os

sys.path.append(os.getcwd())

from haios_etl.synthesis import SynthesisManager

logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_investigation():
    print("Initializing SynthesisManager...")
    manager = SynthesisManager("haios_memory.db")
    
    # 1. Clean Garbage
    conn = manager.db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM reasoning_traces WHERE query LIKE 'simulation_query%'")
    deleted = c.rowcount
    conn.commit()
    print(f"Deleted {deleted} garbage traces.")
    
    # 2. Run Cross-Pollination Check
    print("\nCalling find_cross_type_overlaps() with new logging...")
    results = manager.find_cross_type_overlaps(limit=50)
    
    print(f"\nFound {len(results)} overlaps.")
    for i, (cid, tid, score) in enumerate(results[:5]):
        print(f"[{i+1}] Concept {cid} <-> Trace {tid} (Score: {score:.4f})")

if __name__ == "__main__":
    run_investigation()


if __name__ == "__main__":
    run_investigation()
