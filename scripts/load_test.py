import time
import random
import concurrent.futures
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from haios_etl.database import DatabaseManager
from haios_etl.retrieval import ReasoningAwareRetrieval
from haios_etl.extraction import ExtractionManager

# Mock ExtractionManager to avoid API calls
class MockExtractionManager(ExtractionManager):
    def __init__(self):
        pass
    
    def embed_content(self, text):
        # Return random 768-dim vector (simulating text-embedding-004)
        return [random.random() for _ in range(768)]

def run_query(db_path, query_id):
    # Create fresh instances per thread/request to avoid SQLite threading issues
    db = DatabaseManager(db_path)
    extractor = MockExtractionManager()
    service = ReasoningAwareRetrieval(db, extractor)
    
    start = time.time()
    try:
        # We use a simple query
        service.search_with_experience(f"simulation_query_{query_id}")
        duration = time.time() - start
        return duration, "success"
    except Exception as e:
        duration = time.time() - start
        return duration, f"error: {e}"

def load_test(concurrency=10, total_requests=100):
    db_path = "haios_memory.db"
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return
    
    print(f"Starting load test: {total_requests} requests, concurrency {concurrency}")
    
    times = []
    errors = 0
    
    start_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(run_query, db_path, i) for i in range(total_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            duration, status = future.result()
            times.append(duration)
            if status != "success":
                errors += 1
                # Only print first few errors to avoid spam
                if errors <= 5:
                    print(f"Error: {status}")

    total_time = time.time() - start_total
    
    if not times:
        print("No requests completed.")
        return

    avg_latency = sum(times) / len(times)
    p95_latency = sorted(times)[int(len(times) * 0.95)]
    throughput = total_requests / total_time
    
    print(f"\nResults:")
    print(f"Total Requests: {total_requests}")
    print(f"Concurrency: {concurrency}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Throughput: {throughput:.2f} req/s")
    print(f"Avg Latency: {avg_latency*1000:.2f}ms")
    print(f"P95 Latency: {p95_latency*1000:.2f}ms")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    load_test()
