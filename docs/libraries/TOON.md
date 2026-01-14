# generated: 2025-12-04
# System Auto: last updated on: 2025-12-04 23:21:46
# TOON - Token-Oriented Object Notation
## Library Reference for HAIOS

> **Source:** Context7 `/xaviviro/python-toon` (Benchmark: 98.6)
> **Spec:** `/toon-format/toon` (Benchmark: 79.6)
> **Extracted:** 2025-12-04

---

## Overview

TOON (Token-Oriented Object Notation) is a compact, human-readable serialization format designed for LLM contexts. It reduces token usage by 30-60% compared to JSON while maintaining human readability.

### Key Benefits for HAIOS
- **57% token reduction** (per TOON investigation report)
- **Tabular format** for uniform arrays - fields declared once, not per row
- **Built-in validation** via explicit `[N]` count and `{fields}` notation
- **Truncation detection** - array length mismatches caught on decode

---

## Installation

```bash
pip install python-toon
```

---

## Core API

### encode(value, options=None)

Converts Python value to TOON format.

```python
from toon import encode

# Simple object
data = {"id": 123, "name": "Ada"}
print(encode(data))
# Output:
# id: 123
# name: Ada

# Uniform array (tabular format - major token savings)
data = {
    "users": [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35}
    ]
}
print(encode(data))
# Output:
# users[3,]{id,name,age}:
#   1,Alice,30
#   2,Bob,25
#   3,Charlie,35
```

### decode(input_str, options=None)

Converts TOON string back to Python values.

```python
from toon import decode

toon_str = """items[2,]{sku,qty,price}:
  A1,2,9.99
  B2,1,14.5"""

data = decode(toon_str)
# Result:
# {
#     "items": [
#         {"sku": "A1", "qty": 2, "price": 9.99},
#         {"sku": "B2", "qty": 1, "price": 14.5}
#     ]
# }
```

---

## Encoding Options

```python
from toon import encode

data = {"items": [{"a": 1}, {"a": 2}]}

toon_str = encode(data, {
    "indent": 2,           # Spaces per indentation level (default: 2)
    "delimiter": ",",      # Array delimiter: "," | "\t" | "|" (default: ",")
    "lengthMarker": "#"    # Optional marker prefix: "#" | False (default: False)
})
```

## Decoding Options

```python
from toon import decode, DecodeOptions

options = DecodeOptions(
    indent=2,    # Expected spaces per indentation level (default: 2)
    strict=True  # Enable strict validation (default: True)
)

data = decode(toon_str, options)
```

---

## Format Examples

### Objects
```python
{"name": "Alice", "age": 30}
```
```toon
name: Alice
age: 30
```

### Primitive Arrays
```python
[1, 2, 3, 4, 5]
```
```toon
[5]: 1,2,3,4,5
```

### Tabular Arrays (Major Token Savings)
```python
[
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]
```
```toon
[2,]{id,name}:
  1,Alice
  2,Bob
```

### Mixed Arrays
```python
[{"name": "Alice"}, 42, "hello"]
```
```toon
[3]:
  - name: Alice
  - 42
  - hello
```

### Nested Objects
```toon
user:
  name: Alice
  age: 30
  address:
    city: Boston
    zip: 02101
```

---

## LLM Integration Pattern

```python
from toon import encode, decode

# Prepare structured data for LLM
conversation_data = {
    "messages": [
        {"role": "user", "content": "What is the weather?", "timestamp": 1234567890},
        {"role": "assistant", "content": "It's sunny today.", "timestamp": 1234567895},
    ],
    "metadata": {
        "session_id": "abc123",
        "model": "gpt-4"
    }
}

# Encode to TOON (saves tokens)
toon_payload = encode(conversation_data)

# Construct LLM prompt
prompt = f"""
Respond using TOON format.
Use `key: value` syntax and `[N,]{{fields}}:` for uniform arrays.

Context:
```toon
{toon_payload}
```

Generate a summary with fields: total_messages, user_questions
"""

# Parse LLM response
llm_response = """summary:
  total_messages: 2
  user_questions: 1"""

parsed = decode(llm_response)
# {'summary': {'total_messages': 2, 'user_questions': 1}}
```

---

## Type Normalization

TOON automatically converts Python types to JSON-compatible values:

```python
from toon import encode
from datetime import datetime, date
from decimal import Decimal

# Date/datetime -> ISO 8601 strings
data = {"date": date(2025, 1, 15)}
# Output: date: "2025-01-15"

# Decimal -> float
data = {"price": Decimal("19.99")}
# Output: price: 19.99

# Special values -> null
data = {"infinity": float('inf'), "nan": float('nan')}
# Output:
# infinity: null
# nan: null
```

---

## Error Handling

```python
from toon import decode, ToonDecodeError

# Array length mismatch in strict mode
mismatched_toon = """items[5,]{id}:
  1
  2"""  # Declares 5 items but only has 2

try:
    data = decode(mismatched_toon, strict=True)
except ToonDecodeError as e:
    print(f"Validation error: {e}")
```

---

## CLI Usage

```bash
# Convert JSON to TOON
toon data.json -o data.toon

# Convert TOON to JSON
toon data.toon -o output.json

# Force encode
toon data.json --encode
```

---

## HAIOS Integration Notes

### Recommended Use Cases
1. **Memory retrieval responses** - Encode concept lists in TOON before injecting into prompts
2. **Agent communication** - Reduce token overhead in inter-agent messages
3. **Reasoning traces** - Compact representation of strategy lists

### Token Savings Estimation
Per investigation report (`docs/reports/2025-12-04-REPORT-toon-investigation.md`):
- Average savings: 57% for tabular data
- Best for: Uniform arrays of objects (concepts, entities, traces)
- Less benefit for: Deeply nested single objects

### Implementation Priority
**HIGH** - Quick win, minimal integration effort, significant token reduction

---

## References

- GitHub: https://github.com/toon-format/toon-python
- Spec: https://github.com/toon-format/toon
- PyPI: https://pypi.org/project/python-toon/

---

**END OF LIBRARY REFERENCE**
