import json
import tiktoken
import time

# Mock HAIOS Data (Concepts)
concepts = [
    {
        "id": i,
        "type": "Directive",
        "content": f"System must ensure idempotency for operation {i}",
        "source_adr": f"ADR-{i:03d}",
        "confidence": 0.95,
        "tags": ["reliability", "backend", "critical"]
    }
    for i in range(1, 51)  # 50 items
]

# 1. JSON Serialization
start = time.time()
json_str = json.dumps({"concepts": concepts}, indent=2)
json_time = time.time() - start

# 2. TOON Serialization (Manual Implementation for Benchmark)
def to_toon(data):
    lines = []
    # Header
    count = len(data)
    # Tabular array header: concepts[N]{id,type,content,source_adr,confidence,tags}
    # Note: tags is a list, so it breaks pure tabular if we don't handle it.
    # TOON spec says tabular is for primitives only.
    # So we must use "Mixed Array" or "Expanded List" for tags?
    # Or we can flatten tags to a string "tag1|tag2"?
    # Let's assume we flatten tags for maximum efficiency, or use TOON's inline array syntax if supported in table?
    # Spec 9.3: "All values across these keys are primitives". So list is NOT allowed in tabular.
    # We will flatten tags to a string for this benchmark to simulate optimized storage.
    
    lines.append(f"concepts[{count}]{{id,type,content,source_adr,confidence,tags}}:")
    
    for item in data:
        tags_str = "|".join(item["tags"])
        # Simple CSV escaping (just quote if comma exists)
        # For benchmark, we assume no commas in content for simplicity
        row = f"{item['id']},{item['type']},{item['content']},{item['source_adr']},{item['confidence']},{tags_str}"
        lines.append(f"  {row}")
        
    return "\n".join(lines)

start = time.time()
toon_str = to_toon(concepts)
toon_time = time.time() - start

# 3. Token Counting
enc = tiktoken.get_encoding("cl100k_base")
json_tokens = len(enc.encode(json_str))
toon_tokens = len(enc.encode(toon_str))

# 4. Report
print(f"JSON Tokens: {json_tokens}")
print(f"TOON Tokens: {toon_tokens}")
savings = (json_tokens - toon_tokens) / json_tokens * 100
print(f"Savings: {savings:.2f}%")
print(f"JSON Size (chars): {len(json_str)}")
print(f"TOON Size (chars): {len(toon_str)}")
