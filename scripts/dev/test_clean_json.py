# generated: 2025-11-23
# System Auto: last updated on: 2025-11-23 20:35:06
import re
import json

# Read one of the failing files
with open('HAIOS-RAW/docs/source/Cody_Reports/RAW/adr.json', 'r', encoding='utf-8') as f:
    content = f.read()

print("="*80)
print("FILE LENGTH:", len(content))
print("="*80)

# Check markers
has_chunked = '"chunkedPrompt"' in content
has_settings = '"runSettings"' in content
print(f"Has chunkedPrompt: {has_chunked}")
print(f"Has runSettings: {has_settings}")
print("="*80)

# Try the regex pattern
pattern = r'"(?:text|content|adr)":\s*"((?:[^"\\]|\\.)*)"'
matches = list(re.finditer(pattern, content, flags=re.DOTALL))
print(f"Regex matches found: {len(matches)}")
print("="*80)

# If no matches, return empty and see what happens
if len(matches) == 0:
    print("NO MATCHES - Would return empty string")
    cleaned_content = ""
else:
    print("MATCHES FOUND:")
    for i, match in enumerate(matches[:5]):
        print(f"  Match {i+1}: {match.group(1)[:100]}...")

    cleaned_lines = []
    for match in matches:
        raw_str = match.group(1)
        try:
            decoded_str = json.loads(f'"{raw_str}"')
            cleaned_lines.append(decoded_str)
        except Exception as e:
            print(f"  JSON decode error: {e}")
            cleaned_lines.append(raw_str)

    cleaned_content = "\n\n".join(cleaned_lines)
    print(f"Cleaned content length: {len(cleaned_content)}")

print("="*80)
# Prepend file path
final_content = f"File: adr.json\n\n{cleaned_content}"
print(f"Final content length: {len(final_content)}")
print("Final content preview:")
print(final_content[:500])
print("="*80)

# Try to validate as JSON (this is what's failing)
try:
    json.loads(final_content)
    print("SUCCESS: Content is valid JSON")
except json.JSONDecodeError as e:
    print(f"FAIL: JSON decode error: {e}")
