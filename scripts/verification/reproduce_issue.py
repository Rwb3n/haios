import langextract as lx
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyBCEHH_XBnNjfmywbuenGyUvvJrzqF6Wgw")

def test_extraction(content, description):
    print(f"\n--- Testing: {description} ---")
    try:
        # Dummy example
        examples = [
            lx.data.ExampleData(
                text="User: Hello",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="User:",
                        attributes={"entity_type": "User"}
                    )
                ]
            )
        ]

        lx.extract(
            text_or_documents=content,
            prompt_description="Extract entities",
            examples=examples,
            model_id="gemini-2.5-flash",
            api_key=API_KEY
        )
        print("Success: Extraction proceeded (or failed at API level)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 1. Malformed JSON
    # We use a string that definitely looks like JSON but is invalid
    malformed_json = '{"key": "unterminated string'
    test_extraction(malformed_json, "Malformed JSON string")

    # 2. Prepended Text
    prepended_text = 'File: test.txt\n\n{"key": "unterminated string'
    test_extraction(prepended_text, "Prepended text string")
