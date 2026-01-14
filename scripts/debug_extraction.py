import sys
import os
import logging

# Add project root to path
sys.path.append(os.getcwd())

from haios_etl.extraction import ExtractionManager
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def debug_extraction():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found.")
        return

    manager = ExtractionManager(api_key=api_key)
    
    file_path = r"d:\PROJECTS\haios\HAIOS-RAW\docs\source\Cody_Reports\Epoch_2\Cody_Report_1005.md"
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"Extracting from {file_path}...")
    try:
        result = manager.extract_from_file(file_path, content)
        
        print("\n--- Entities ---")
        for entity in result.entities:
            print(f"[{entity.type}] {entity.value}")
            
        print("\n--- Concepts ---")
        for concept in result.concepts:
            print(f"[{concept.type}] {concept.content}")
            
        # Check for AntiPattern
        ap_count = sum(1 for e in result.entities if e.type == "AntiPattern")
        print(f"\nAntiPatterns found: {ap_count}")
        
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    debug_extraction()
