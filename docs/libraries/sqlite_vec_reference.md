# generated: 2025-11-26
# System Auto: last updated on: 2025-11-26 20:16:28
# SQLite-Vec Library Reference

**Library:** sqlite-vec by Alex Garcia
**Context7 ID:** `/asg017/sqlite-vec`
**Version:** v0.1.x
**Source Reputation:** High
**Code Examples:** 122

**Description:** An extremely small and fast vector search SQLite extension written in pure C, supporting float, int8, and binary vectors with metadata storage, runnable anywhere SQLite runs.

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Concepts](#core-concepts)
3. [Basic Usage](#basic-usage)
4. [Python Integration](#python-integration)
5. [API Reference](#api-reference)
6. [vec0 Virtual Tables](#vec0-virtual-tables)
7. [Distance Functions](#distance-functions)
8. [Best Practices](#best-practices)
9. [HAIOS Integration](#haios-integration)

---

## Installation & Setup

### Python Installation (Recommended)

```bash
pip install sqlite-vec
```

### Verify Installation

```bash
python -c 'import sqlite_vec; print("sqlite-vec installed successfully")'
```

### Check SQLite Version

```bash
python -c 'import sqlite3; print(sqlite3.sqlite_version)'
```

**Note:** sqlite-vec requires SQLite 3.41.0 or later for optimal performance.

### Alternative Installation Methods

**For sqlite-utils:**
```bash
sqlite-utils install sqlite-utils-sqlite-vec
```

**For Datasette:**
```bash
datasette install datasette-sqlite-vec
```

**Pre-compiled Extension (Linux/macOS):**
```sh
curl -L 'https://github.com/asg017/sqlite-vec/releases/latest/download/install.sh' | sh
```

---

## Core Concepts

### Vector Types

sqlite-vec supports multiple vector formats:

| Type | Declaration | Use Case |
|------|-------------|----------|
| `float[N]` | `float[768]` | Standard embeddings (32-bit float) |
| `int8[N]` | `int8[768]` | Quantized vectors (8-bit integer) |
| `bit[N]` | `bit[768]` | Binary vectors (1-bit per dimension) |

### Storage Approaches

1. **vec0 Virtual Table**: Optimized KNN search with `MATCH` operator
2. **Regular Table with BLOB**: Manual distance calculation with scalar functions

### Distance Metrics

| Metric | Function | vec0 Declaration |
|--------|----------|------------------|
| L2 (Euclidean) | `vec_distance_L2()` | Default |
| Cosine | `vec_distance_cosine()` | `distance_metric=cosine` |

---

## Basic Usage

### Loading the Extension (Python)

```python
import sqlite3
import sqlite_vec

db = sqlite3.connect(":memory:")
db.enable_load_extension(True)
sqlite_vec.load(db)
db.enable_load_extension(False)

# Verify
vec_version, = db.execute("select vec_version()").fetchone()
print(f"vec_version={vec_version}")
```

### Creating a Vector Table

```sql
-- Create vec0 virtual table for KNN search
create virtual table vec_documents using vec0(
  document_id integer primary key,
  contents_embedding float[768]
);
```

### Inserting Vectors

```sql
-- Insert as JSON string
insert into vec_documents(rowid, contents_embedding)
values (1, '[-0.200, 0.250, 0.341, -0.211, 0.645, 0.935, -0.316, -0.924]');

-- Insert multiple
insert into vec_documents(rowid, contents_embedding)
  values
    (1, '[-0.200, 0.250, 0.341, ...]'),
    (2, '[0.443, -0.501, 0.355, ...]'),
    (3, '[0.716, -0.927, 0.134, ...]');
```

### KNN Search

```sql
-- Find 10 nearest neighbors
select
  rowid,
  distance
from vec_documents
where contents_embedding match '[0.890, 0.544, 0.825, ...]'
  and k = 10
order by distance;
```

---

## Python Integration

### Serializing Vectors

```python
from sqlite_vec import serialize_float32

# Convert Python list to sqlite-vec BLOB format
embedding = [0.1, 0.2, 0.3, 0.4]
blob = serialize_float32(embedding)

# Use in query
result = db.execute('select vec_length(?)', [blob])
print(result.fetchone()[0])  # 4
```

### Complete Python Example

```python
import sqlite3
import sqlite_vec
from sqlite_vec import serialize_float32

# Setup
db = sqlite3.connect(":memory:")
db.enable_load_extension(True)
sqlite_vec.load(db)
db.enable_load_extension(False)

# Create table
db.execute("""
    create virtual table vec_items using vec0(
        item_embedding float[4]
    )
""")

# Insert data
items = [
    (1, [0.1, 0.2, 0.3, 0.4]),
    (2, [0.5, 0.6, 0.7, 0.8]),
    (3, [0.9, 0.1, 0.2, 0.3]),
]

for rowid, embedding in items:
    db.execute(
        "insert into vec_items(rowid, item_embedding) values (?, ?)",
        [rowid, serialize_float32(embedding)]
    )

# Search
query = [0.15, 0.25, 0.35, 0.45]
results = db.execute("""
    select rowid, distance
    from vec_items
    where item_embedding match ?
      and k = 2
""", [serialize_float32(query)]).fetchall()

for rowid, distance in results:
    print(f"Row {rowid}: distance={distance:.4f}")
```

### Using struct for Manual Serialization

```python
import struct

def serialize_vector(vector):
    """Serialize float list to bytes for sqlite-vec."""
    return struct.pack(f'{len(vector)}f', *vector)

# Use with raw sqlite3
embedding = [0.1, 0.2, 0.3, 0.4]
blob = serialize_vector(embedding)
```

---

## API Reference

### Scalar Functions

| Function | Description | Example |
|----------|-------------|---------|
| `vec_version()` | Returns sqlite-vec version | `select vec_version()` |
| `vec_length(v)` | Number of elements in vector | `select vec_length('[1,2,3]')` → 3 |
| `vec_f32(v)` | Convert to float32 vector | `select vec_f32('[1.0, 2.0]')` |
| `vec_int8(v)` | Convert to int8 vector | `select vec_int8(X'AABBCCDD')` |
| `vec_bit(v)` | Convert to bit vector | `select vec_bit(X'F0')` |
| `vec_to_json(v)` | Convert vector to JSON | `select vec_to_json(embedding)` |
| `vec_distance_L2(a, b)` | Euclidean distance | See below |
| `vec_distance_cosine(a, b)` | Cosine distance | See below |
| `vec_quantize_binary(v)` | Binary quantization | `select vec_quantize_binary(v)` |

### Distance Functions

```sql
-- L2 (Euclidean) distance
select vec_distance_L2(
    '[1.0, 2.0, 3.0]',
    '[1.1, 2.1, 3.1]'
);

-- Cosine distance
select vec_distance_cosine(
    '[1.0, 2.0, 3.0]',
    '[1.1, 2.1, 3.1]'
);
```

### Table Functions

```sql
-- Iterate through vector elements
select rowid, value from vec_each('[1,2,3,4]');
/*
┌───────┬───────┐
│ rowid │ value │
├───────┼───────┤
│ 0     │ 1     │
│ 1     │ 2     │
│ 2     │ 3     │
│ 3     │ 4     │
└───────┴───────┘
*/
```

---

## vec0 Virtual Tables

### Basic vec0 Table

```sql
create virtual table vec_embeddings using vec0(
  embedding float[768]
);
```

### vec0 with Primary Key

```sql
create virtual table vec_documents using vec0(
  document_id integer primary key,
  contents_embedding float[768]
);
```

### vec0 with Metadata Columns

Metadata columns can be used in WHERE clauses for filtering:

```sql
create virtual table vec_movies using vec0(
  movie_id integer primary key,
  synopsis_embedding float[1024],
  genre text,
  num_reviews int,
  mean_rating float,
  contains_violence boolean
);

-- Query with filters
select *
from vec_movies
where synopsis_embedding match '[...]'
  and k = 5
  and genre = 'scifi'
  and num_reviews between 100 and 500
  and mean_rating > 3.5;
```

### vec0 with Auxiliary Columns

Auxiliary columns (prefixed with `+`) store data but aren't indexed:

```sql
create virtual table vec_chunks using vec0(
  contents_embedding float[1024],
  +contents text,
  +metadata blob
);

-- Select auxiliary columns
select rowid, contents, distance
from vec_chunks
where contents_embedding match :query
  and k = 10;
```

### vec0 with Partition Key

```sql
create virtual table vec_chunks using vec0(
  user_id integer partition key,
  contents_embedding float[768]
);
```

### vec0 with Cosine Distance

```sql
create virtual table vec_documents using vec0(
  document_id integer primary key,
  contents_embedding float[768] distance_metric=cosine
);
```

---

## Distance Functions

### Manual KNN with Scalar Functions

For regular tables (not vec0), use scalar distance functions:

```sql
-- Create regular table
create table documents(
  id integer primary key,
  contents text,
  contents_embedding blob
);

-- Insert with vec_f32
insert into documents values
  (1, 'document one', vec_f32('[1.1, 1.1, 1.1, 1.1]')),
  (2, 'document two', vec_f32('[2.2, 2.2, 2.2, 2.2]'));

-- Manual KNN query
select
  id,
  contents,
  vec_distance_L2(contents_embedding, vec_f32('[2.0, 2.0, 2.0, 2.0]')) as distance
from documents
order by distance
limit 10;
```

### vec0 KNN with MATCH

```sql
-- vec0 uses MATCH operator (optimized)
select rowid, distance
from vec_documents
where contents_embedding match '[query vector...]'
  and k = 10
order by distance;
```

---

## Best Practices

### 1. Choose the Right Storage

```sql
-- For KNN search: use vec0 (optimized)
create virtual table vec_search using vec0(
  embedding float[768]
);

-- For flexibility with joins: use regular table
create table embeddings(
  id integer primary key,
  artifact_id integer references artifacts(id),
  vector blob,
  model text
);
```

### 2. Use Appropriate Dimensions

```sql
-- Match your embedding model's output
-- text-embedding-004: 768 dimensions
create virtual table vec_memories using vec0(
  memory_embedding float[768]
);
```

### 3. Batch Inserts

```python
# Insert in batches for better performance
with db:
    db.executemany(
        "insert into vec_items(rowid, embedding) values (?, ?)",
        [(i, serialize_float32(vec)) for i, vec in enumerate(vectors)]
    )
```

### 4. Use Binary Quantization for Large Datasets

```sql
-- Binary quantization reduces storage 32x
create virtual table vec_movies using vec0(
  synopsis_embedding bit[768]
);

-- Insert quantized vectors
insert into vec_movies(rowid, synopsis_embedding)
values (1, vec_quantize_binary('[0.1, -0.2, 0.3, ...]'));
```

### 5. Re-ranking Strategy

For high accuracy with large datasets:

```sql
-- Two-stage: coarse binary search + fine float re-ranking
create virtual table vec_movies using vec0(
  synopsis_embedding float[768],
  synopsis_embedding_coarse bit[768]
);
```

---

## HAIOS Integration

### Current Implementation

The HAIOS database uses a regular embeddings table with manual distance calculation:

```python
# haios_etl/database.py
def search_memories(self, query_vector, space_id=None, filters=None, limit=10):
    """
    Search memories using vector similarity.
    Requires sqlite-vec extension to be loaded.
    """
    conn = self.get_connection()

    # Load sqlite-vec extension
    try:
        conn.enable_load_extension(True)
        conn.load_extension("vec0")
    except Exception:
        pass  # Graceful fallback

    # Serialize query vector
    import struct
    query_bytes = struct.pack(f'{len(query_vector)}f', *query_vector)

    # Vector search
    sql = """
        SELECT
            a.id,
            a.file_path,
            vec_distance_cosine(e.vector, ?) as distance
        FROM embeddings e
        JOIN artifacts a ON e.artifact_id = a.id
        ORDER BY distance ASC
        LIMIT ?
    """

    cursor.execute(sql, [query_bytes, limit])
    return [{'id': r[0], 'file_path': r[1], 'score': 1 - r[2]} for r in cursor.fetchall()]
```

### Recommended Upgrade Path

To enable full vector search in HAIOS:

**Step 1: Install sqlite-vec**
```bash
pip install sqlite-vec
```

**Step 2: Update database.py**
```python
import sqlite_vec
from sqlite_vec import serialize_float32

class DatabaseManager:
    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA foreign_keys = ON")

            # Load sqlite-vec
            self.conn.enable_load_extension(True)
            sqlite_vec.load(self.conn)
            self.conn.enable_load_extension(False)

        return self.conn

    def search_memories(self, query_vector, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()

        query_blob = serialize_float32(query_vector)

        cursor.execute("""
            SELECT a.id, a.file_path, vec_distance_cosine(e.vector, ?) as distance
            FROM embeddings e
            JOIN artifacts a ON e.artifact_id = a.id
            ORDER BY distance ASC
            LIMIT ?
        """, [query_blob, limit])

        return [{'id': r[0], 'file_path': r[1], 'score': 1 - r[2]}
                for r in cursor.fetchall()]
```

**Step 3: Optional - Migrate to vec0 for Better Performance**
```sql
-- Create vec0 table for optimized KNN
create virtual table vec_memories using vec0(
    artifact_id integer primary key,
    embedding float[768] distance_metric=cosine
);

-- Migrate existing embeddings
insert into vec_memories(artifact_id, embedding)
select artifact_id, vector from embeddings;
```

### Windows Considerations

On Windows, the sqlite-vec Python package includes pre-built binaries. If you encounter issues:

1. **Verify Python architecture matches:**
   ```bash
   python -c "import struct; print(struct.calcsize('P') * 8)"
   ```
   Should return `64` for 64-bit Python.

2. **Check for conflicting SQLite versions:**
   ```bash
   python -c "import sqlite3; print(sqlite3.sqlite_version)"
   ```
   Requires SQLite 3.41.0+.

3. **Manual extension loading (fallback):**
   ```python
   import sqlite3
   db = sqlite3.connect(":memory:")
   db.enable_load_extension(True)
   db.load_extension("path/to/vec0.dll")
   ```

---

## References

- **Official Repository:** https://github.com/asg017/sqlite-vec
- **Documentation:** https://alexgarcia.xyz/sqlite-vec/
- **Context7 Library ID:** `/asg017/sqlite-vec`
- **PyPI:** https://pypi.org/project/sqlite-vec/
- **Documentation Retrieved:** 2025-11-26

---

**END OF REFERENCE**
