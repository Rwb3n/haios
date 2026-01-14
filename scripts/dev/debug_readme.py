import os
import logging
from dotenv import load_dotenv
from haios_etl.extraction import ExtractionManager

# Configure logging
logging.basicConfig(level=logging.INFO)

def debug_readme():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("No API Key")
        return

    manager = ExtractionManager(api_key)
    
    file_path = r"HAIOS-RAW\templates\README.md"
    
    # Read content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read file: {e}")
        return

    print(f"Extracting from {file_path} ({len(content)} chars)...")
    
    try:
        result = manager.extract_from_file(file_path, content)
        print("Success!")
        print(f"Entities: {len(result.entities)}")
        print(f"Concepts: {len(result.concepts)}")
    except Exception as e:
        print(f"\nExtraction Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_readme()
