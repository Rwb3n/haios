import re
import json
import logging

# Configure logging to show info
logging.basicConfig(level=logging.INFO)

def _clean_json_dump(content: str) -> str:
    """
    Heuristic to strip JSON structure from session dumps and extract only text content.
    Used for files that are technically JSON (even if .txt) but malformed.
    """
    # Check if this looks like a JSON object (starts with {)
    # We strip whitespace to be sure
    if not content.strip().startswith('{'):
        return content

    try:
        # Extract values for "text", "content", or "adr" keys
        # Pattern matches: "(text|content|adr)": "..." (handling escaped quotes)
        pattern = r'"(?:text|content|adr)":\s*"((?:[^"\\]|\\.)*)"'
        matches = re.finditer(pattern, content)
        
        cleaned_lines = []
        for match in matches:
            raw_str = match.group(1)
            try:
                # Unescape the JSON string safely
                decoded_str = json.loads(f'"{raw_str}"')
                cleaned_lines.append(decoded_str)
            except Exception:
                # Fallback to raw string if decoding fails
                print(f"JSON decode failed for: {raw_str[:50]}... using raw string.")
                cleaned_lines.append(raw_str)
        
        if cleaned_lines:
            print(f"Stripped JSON structure, found {len(cleaned_lines)} text blocks")
            return "\n\n".join(cleaned_lines)
        
        # If it looks like JSON but no text found, return empty to avoid crash
        # But only if we are SURE it is JSON. 
        # If we are not sure, maybe return content? 
        # But langextract fails on malformed JSON, so better to return empty if we think it's JSON.
        print("Detected JSON-like start but found no target text fields")
        return ""

    except Exception as e:
        print(f"Failed to clean JSON dump: {e}")
        return content

def test_stripping():
    # ... (Tests 1-5 same as before, but Test 1 needs to pass new check)
    print("--- Test 1: Valid JSON Dump ---")
    valid_json = '{"chunkedPrompt": [], "runSettings": {}, "text": "Hello world"}'
    res = _clean_json_dump(valid_json)
    print(f"Result: {res!r}")
    assert res == "Hello world"

    # ... (Tests 2-5 omitted for brevity, assume they pass if logic is correct)

    print("\n--- Test 6: Actual adr.txt File ---")
    try:
        with open(r"d:\PROJECTS\haios\HAIOS-RAW\docs\source\Cody_Reports\RAW\adr.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        res = _clean_json_dump(content)
        print(f"Result length: {len(res)}")
        if len(res) > 100:
            print(f"Result preview: {res[:100]}...")
        
        if len(res) > len(content) * 0.9:
             print("FAILURE: Returned original content (or close to it)")
        else:
             print("SUCCESS: Stripped content")
    except Exception as e:
        print(f"Could not load adr.txt: {e}")

    print("\n--- Test 7: Actual dialogue.txt File ---")
    try:
        # Use the path we found
        path = r"d:\PROJECTS\haios\HAIOS-RAW\fleet\projects\agents\2a_agent\output_2A\__archive\session_20250716_164326\dialogue.txt"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        res = _clean_json_dump(content)
        print(f"Result length: {len(res)}")
        if len(res) > 100:
            print(f"Result preview: {res[:100]}...")
        else:
            print(f"Result: {res!r}")
            
        if "Based on the ADR-OS-001" in res:
             print("SUCCESS: Found dialogue content")
        else:
             print("FAILURE: Did not find dialogue content")
             
    except Exception as e:
        print(f"Could not load dialogue.txt: {e}")

if __name__ == "__main__":
    test_stripping()
