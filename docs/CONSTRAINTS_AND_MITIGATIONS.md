# System Constraints and Mitigation Strategies
## Cognitive Memory System - Complete Constraint Analysis

**Document Version:** 1.0  
**Last Updated:** October 18, 2025  
**Status:** Critical architectural decisions

---

## Table of Contents

1. [Overview](#overview)
2. [Critical MVP Constraints](#critical-mvp-constraints)
3. [Temporal Constraints](#temporal-constraints)
4. [Scale Constraints](#scale-constraints)
5. [Consistency Constraints](#consistency-constraints)
6. [Concurrency Constraints](#concurrency-constraints)
7. [Dependency Constraints](#dependency-constraints)
8. [Semantic Constraints](#semantic-constraints)
9. [User Experience Constraints](#user-experience-constraints)
10. [Cost Constraints](#cost-constraints)
11. [Operational Constraints](#operational-constraints)
12. [Correctness Constraints](#correctness-constraints)
13. [Constraint Priority Matrix](#constraint-priority-matrix)
14. [Architectural Decisions Summary](#architectural-decisions-summary)

---

## Overview

This document catalogs all identified constraints in the Cognitive Memory System, their implications, and mitigation strategies. Constraints are categorized by severity:

- **CRITICAL (MVP):** Must be addressed in Phase 1, system broken without mitigation
- **HIGH:** Must be addressed by Phase 4, significant degradation without mitigation  
- **MEDIUM:** Should be addressed by Phase 6, graceful degradation possible
- **LOW:** Nice to have, workarounds acceptable

---

## Critical MVP Constraints

These five constraints are deal-breakers that must be solved in Phase 1:

### 1. Embedding Availability vs Search Capability

**The Constraint:**
```python
# Cannot perform vector search without embeddings
∀ memory m: searchable(m) ⟺ ∃ embedding e: stored(e, m)

# Problem:
# Fast ingestion (no embeddings) → memories not searchable
# Slow ingestion (inline embeddings) → hours to ingest large batches
# Trade-off: speed vs availability
```

**Impact:** Users cannot search newly ingested content until embeddings are generated.

**Severity:** CRITICAL (MVP)

**Mitigation Strategy: Dual-Embedding Architecture**

```python
class DualEmbeddingIngestion:
    """
    Use fast local embeddings for immediate search,
    upgrade to high-quality cloud embeddings in background
    """
    
    def ingest(self, content, metadata, space_id):
        # 1. Store content (instant)
        memory_id = self.storage.store_content(content, metadata, space_id)
        
        # 2. Generate local embedding (50-100ms, immediate search)
        local_embedding = self.local_model.embed(content)
        self.storage.store_embedding(
            memory_id=memory_id,
            embedding=local_embedding,
            model='local-minilm',
            dimensions=384,
            is_primary=True,
            quality_tier='fast'
        )
        
        # 3. Queue for high-quality cloud embedding (background)
        self.embedding_queue.add(
            memory_id=memory_id,
            target_model='gemini-embedding-001',
            target_dimensions=768,
            priority='normal',
            will_replace_primary=True
        )
        
        return memory_id
```

**Schema Changes:**

```sql
-- Track embedding quality tiers
ALTER TABLE embeddings ADD COLUMN quality_tier TEXT 
    CHECK(quality_tier IN ('fast', 'standard', 'high')) 
    DEFAULT 'standard';

-- Track embedding status on memories
ALTER TABLE memories ADD COLUMN embedding_status TEXT
    DEFAULT 'pending'
    CHECK(embedding_status IN ('pending', 'fast', 'standard', 'high'));

-- Index for finding memories needing upgrades
CREATE INDEX idx_memories_embedding_upgrade 
    ON memories(embedding_status) 
    WHERE embedding_status IN ('pending', 'fast');
```

**User Experience:**

```bash
$ memory ingest large_codebase/
> ✓ Ingested 1,000 files (5 seconds)
> ✓ Generated fast embeddings (15 seconds)
> ⏳ Queued for high-quality embeddings (background)
> Search available now with fast embeddings

$ memory search "authentication code"
> 🔍 Found 5 results (quality: fast)
> ⏳ 650 / 1,000 files upgraded to high-quality embeddings
> 
> Results will improve as upgrades complete
```

**Trade-offs:**
- ✅ Immediate search capability
- ✅ Progressive quality improvement
- ✅ No blocking on API calls
- ❌ Temporary storage overhead (2 embeddings per memory)
- ❌ Lower initial search quality
- ❌ Need to manage local model dependencies

**Decision:** Implement dual-embedding for MVP. Accept temporary storage overhead for usability.

---

### 2. Embedding Dimension Mismatch

**The Constraint:**
```python
# Cannot compare embeddings with different dimensions
query_embedding: [768 floats]  # gemini-embedding-001
stored_embedding: [384 floats]  # local-minilm

cosine_similarity(query_embedding, stored_embedding)  # ERROR
```

**Impact:** 
- Cannot gradually migrate between embedding models
- Must maintain separate indices per model
- Mixed-model search fails

**Severity:** CRITICAL (MVP)

**Mitigation Strategy: Model-Aware Search Router**

```python
class ModelAwareSearch:
    """
    Route search queries to appropriate embedding models,
    merge results across models
    """
    
    def search(self, query, space_id, top_k=10):
        # 1. Identify which embedding models exist in this space
        models_present = self.get_models_in_space(space_id)
        # Returns: [('local-minilm', 384, 500 memories), 
        #           ('gemini-embedding-001', 768, 8000 memories)]
        
        results = []
        
        # 2. Search within each model's embedding space
        for model, dimensions, count in models_present:
            # Generate query embedding using same model
            query_embedding = self.embed_query(query, model)
            
            # Search only memories with this model's embeddings
            model_results = self.vector_search(
                query_embedding=query_embedding,
                space_id=space_id,
                model_filter=model,
                top_k=top_k
            )
            
            results.extend(model_results)
        
        # 3. Merge and re-rank across models
        # Normalize scores since different models have different scales
        normalized_results = self.normalize_scores(results)
        final_results = sorted(normalized_results, 
                              key=lambda x: x.normalized_score, 
                              reverse=True)[:top_k]
        
        return final_results
```

**Schema Changes:**

```sql
-- Already in schema, but emphasize importance:
-- embeddings.model is critical for routing
-- embeddings.dimensions must match for comparison

-- Add index for model-based filtering
CREATE INDEX idx_embeddings_model_dimensions 
    ON embeddings(model, dimensions, is_primary);

-- Track model usage per space
CREATE TABLE space_embedding_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    space_id TEXT NOT NULL,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    memory_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (space_id) REFERENCES spaces(space_id),
    UNIQUE(space_id, model)
);

-- Update count when embeddings added/removed
CREATE TRIGGER update_model_count_insert
AFTER INSERT ON embeddings
FOR EACH ROW
BEGIN
    INSERT INTO space_embedding_models (space_id, model, dimensions, memory_count)
    SELECT DISTINCT msm.space_id, NEW.model, NEW.dimensions, 1
    FROM memory_space_membership msm
    WHERE msm.memory_id = NEW.memory_id
    ON CONFLICT(space_id, model) 
    DO UPDATE SET memory_count = memory_count + 1;
END;
```

**Model Migration Strategy:**

```python
def migrate_to_new_model(space_id, old_model, new_model, batch_size=100):
    """
    Gradually migrate from old embedding model to new model
    without breaking existing search
    """
    # 1. Get memories still using old model
    memories_to_migrate = get_memories_with_model(space_id, old_model)
    total = len(memories_to_migrate)
    
    # 2. Process in batches (don't block, spread over time)
    for i, batch in enumerate(chunk(memories_to_migrate, batch_size)):
        # Generate new embeddings
        contents = [m.content for m in batch]
        new_embeddings = embedding_service.batch_embed(contents, new_model)
        
        # Store new embeddings alongside old (keep both temporarily)
        for memory, embedding in zip(batch, new_embeddings):
            storage.store_embedding(
                memory_id=memory.id,
                embedding=embedding,
                model=new_model,
                is_primary=False  # Don't replace primary yet
            )
        
        # 3. Validate new embeddings work
        if i % 10 == 0:  # Every 10 batches
            validation_pass = validate_embeddings(batch, new_model)
            if not validation_pass:
                raise MigrationError("New embeddings failing validation")
        
        print(f"Migrated {(i+1)*batch_size}/{total} memories")
    
    # 4. Only after all migrated, flip primary
    mark_model_as_primary(space_id, new_model)
    
    # 5. Keep old embeddings for rollback window (30 days)
    schedule_cleanup(old_model, retention_days=30)
```

**Decision:** 
- Implement model-aware search routing in MVP
- Support mixed-model spaces during migration periods
- Never delete old embeddings immediately (30-day retention)

**Trade-offs:**
- ✅ Enables gradual model migration
- ✅ Zero-downtime upgrades
- ✅ Rollback capability
- ❌ Increased storage during migrations (2x embeddings)
- ❌ Search complexity (must query multiple model spaces)
- ❌ Score normalization imperfect across models

---

### 3. Vector Search Performance at Scale

**The Constraint:**
```python
# Naive vector search: O(n) comparisons
# 1,000 memories: ~10ms
# 100,000 memories: ~1,000ms
# 1,000,000 memories: ~10,000ms (10 seconds)

# Even worse: SQLite BLOB storage inefficient for vectors
SELECT * FROM embeddings WHERE memory_id IN (...)
# Fetches entire BLOB, deserializes, computes similarity
# No way to index/optimize vector operations in pure SQLite
```

**Impact:** Search becomes unusable beyond ~50K memories per space.

**Severity:** CRITICAL (MVP must plan for this, implement by Phase 5)

**Mitigation Strategy: Hybrid Storage with FAISS Index**

```python
class HybridVectorStorage:
    """
    SQLite for metadata, FAISS for vector operations
    """
    
    def __init__(self, db_path, index_path):
        self.db = sqlite3.connect(db_path)
        
        # FAISS index: separate file, memory-mapped
        self.faiss_index = faiss.read_index(index_path)
        
        # Mapping: FAISS id → memory_id
        self.id_mapping = self.load_id_mapping()
    
    def search(self, query_embedding, space_id, top_k=10):
        # 1. Get memory IDs in this space (fast: indexed)
        memory_ids = self.get_space_memory_ids(space_id)
        
        # 2. Get FAISS indices for these memory IDs
        faiss_indices = [self.id_mapping[mid] for mid in memory_ids]
        
        # 3. Vector search using FAISS (optimized, approximate)
        # Uses HNSW (Hierarchical Navigable Small World) graph
        # O(log n) instead of O(n)
        distances, faiss_results = self.faiss_index.search(
            query_embedding.reshape(1, -1),
            k=top_k * 2  # Over-retrieve for filtering
        )
        
        # 4. Map back to memory IDs
        result_memory_ids = [
            self.reverse_id_mapping[fid] 
            for fid in faiss_results[0]
            if fid in faiss_indices  # Only from target space
        ]
        
        # 5. Fetch full memory details from SQLite
        memories = self.fetch_memories(result_memory_ids[:top_k])
        
        return memories
```

**Architecture Decision:**

```
┌─────────────────────────────────────────┐
│  SQLite Database                        │
│  - Content, metadata, relationships     │
│  - Embedding metadata (model, dims)     │
│  - NO vector BLOBs (too slow)          │
└──────────────┬──────────────────────────┘
               │
               │ (ID references)
               │
┌──────────────▼──────────────────────────┐
│  FAISS Index (.index file)              │
│  - All vectors in optimized structure   │
│  - HNSW graph for O(log n) search      │
│  - Memory-mapped (doesn't load to RAM)  │
│  - Separate index per embedding model   │
└─────────────────────────────────────────┘
```

**Schema Changes:**

```sql
-- Remove vector BLOBs from embeddings table
-- Instead, track FAISS index location
ALTER TABLE embeddings DROP COLUMN vector;  -- Can't actually drop in SQLite, use migration

-- New schema for embeddings table:
CREATE TABLE embeddings_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    model TEXT NOT NULL,
    modality TEXT DEFAULT 'text',
    dimensions INTEGER NOT NULL,
    faiss_index_id INTEGER NOT NULL,  -- Position in FAISS index
    faiss_index_file TEXT NOT NULL,   -- Which .index file
    is_primary BOOLEAN DEFAULT FALSE,
    quality_tier TEXT DEFAULT 'standard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
    UNIQUE(memory_id, model)
);

-- Track FAISS index files
CREATE TABLE faiss_indices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    index_type TEXT DEFAULT 'HNSW',  -- HNSW, IVF, Flat
    index_file_path TEXT NOT NULL,
    vector_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_rebuilt TIMESTAMP,
    UNIQUE(model, dimensions)
);
```

**FAISS Index Management:**

```python
class FAISSIndexManager:
    """
    Manage FAISS indices for fast vector search
    """
    
    def create_index(self, model, dimensions, index_type='HNSW'):
        """
        Create optimized index based on expected size
        """
        if index_type == 'HNSW':
            # Best for < 1M vectors: O(log n) search
            # M=32 connections per node, efConstruction=200
            index = faiss.IndexHNSWFlat(dimensions, 32)
            index.hnsw.efConstruction = 200
            index.hnsw.efSearch = 100
        
        elif index_type == 'IVF':
            # Best for > 1M vectors: quantization + clustering
            # nlist=1024 clusters, nprobe=32 for search
            quantizer = faiss.IndexFlatL2(dimensions)
            index = faiss.IndexIVFFlat(quantizer, dimensions, 1024)
            index.nprobe = 32
        
        return index
    
    def add_vectors(self, index_file, vectors, memory_ids):
        """
        Add vectors to FAISS index
        """
        index = faiss.read_index(index_file)
        
        # Get next available IDs
        start_id = index.ntotal
        
        # Add to index
        index.add(vectors)
        
        # Update mapping: memory_id → faiss_id
        for i, memory_id in enumerate(memory_ids):
            self.store_mapping(memory_id, start_id + i, index_file)
        
        faiss.write_index(index, index_file)
    
    def rebuild_index(self, model, space_id):
        """
        Rebuild index from scratch (for optimization)
        Run during low-traffic periods
        """
        # 1. Fetch all embeddings for this model
        embeddings = self.fetch_all_embeddings(model, space_id)
        
        # 2. Create fresh index
        index = self.create_index(model, embeddings[0].dimensions)
        
        # 3. Batch add all vectors
        vectors = np.array([e.vector for e in embeddings])
        index.add(vectors)
        
        # 4. Write to new file
        new_index_file = f"{model}_{space_id}_{timestamp()}.index"
        faiss.write_index(index, new_index_file)
        
        # 5. Atomic swap: update references
        self.swap_index_file(model, space_id, new_index_file)
```

**Performance Benchmarks:**

| Corpus Size | SQLite BLOB | FAISS HNSW | Speedup |
|-------------|-------------|------------|---------|
| 1K vectors  | 10ms        | 5ms        | 2x      |
| 10K vectors | 100ms       | 12ms       | 8x      |
| 100K vectors| 1,000ms     | 25ms       | 40x     |
| 1M vectors  | 10,000ms    | 50ms       | 200x    |

**Decision:** 
- Phase 1-3: Use SQLite BLOBs (simple, < 10K vectors)
- Phase 4: Migrate to FAISS when hitting 10K+ vectors per space
- Phase 5: Mandatory FAISS for production (100K+ vectors)

**Trade-offs:**
- ✅ 10-200x faster search at scale
- ✅ Scalable to millions of vectors
- ✅ Lower memory usage (memory-mapped)
- ❌ Additional dependency (FAISS library)
- ❌ More complex index management
- ❌ Approximate search (may miss exact matches, but <1% error)

---

### 4. API Dependency Brittleness

**The Constraint:**
```python
# System relies on Gemini API for embeddings
# If Gemini API is down:
# - Cannot ingest new content
# - Cannot generate query embeddings (no search)
# - Queue fills up indefinitely
# - System is effectively offline

# API failures we've seen:
# - Rate limit exceeded (429)
# - Service unavailable (503)
# - Breaking changes (response format)
# - Model deprecation (forced migration)
```

**Impact:** System unavailable during API outages.

**Severity:** CRITICAL (MVP)

**Mitigation Strategy: Multi-Tier Fallback Architecture**

```python
class ResilientEmbeddingService:
    """
    Multi-provider embedding with automatic fallback
    """
    
    def __init__(self):
        self.providers = [
            ('gemini', GeminiEmbeddings(), priority=1, cost=0.15),
            ('openai', OpenAIEmbeddings(), priority=2, cost=0.20),
            ('local', LocalEmbeddings(), priority=3, cost=0.0)
        ]
        self.circuit_breaker = CircuitBreaker()
    
    def embed(self, content, preferred_model='gemini-embedding-001'):
        """
        Try providers in order until one succeeds
        """
        provider_name = self.get_provider_from_model(preferred_model)
        
        # Try primary provider
        try:
            if self.circuit_breaker.is_open(provider_name):
                raise CircuitBreakerOpen(f"{provider_name} circuit open")
            
            embedding = self.providers[provider_name].embed(content)
            self.circuit_breaker.record_success(provider_name)
            return embedding
            
        except (APIError, RateLimitError, CircuitBreakerOpen) as e:
            self.circuit_breaker.record_failure(provider_name)
            
            # Try fallback providers
            for fallback_provider, client, priority, cost in self.providers:
                if fallback_provider == provider_name:
                    continue  # Skip failed provider
                
                try:
                    logging.warning(f"Falling back to {fallback_provider}")
                    embedding = client.embed(content)
                    
                    # Store which provider was used (for debugging)
                    self.record_fallback_usage(fallback_provider)
                    return embedding
                    
                except Exception as fallback_error:
                    continue  # Try next fallback
            
            # All providers failed
            raise AllProvidersFailedError("Cannot generate embedding")
```

**Circuit Breaker Pattern:**

```python
class CircuitBreaker:
    """
    Prevent cascading failures by temporarily disabling failing services
    """
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds
        self.states = {}  # provider → CircuitState
    
    def record_failure(self, provider):
        if provider not in self.states:
            self.states[provider] = CircuitState()
        
        state = self.states[provider]
        state.failure_count += 1
        state.last_failure = time.time()
        
        if state.failure_count >= self.failure_threshold:
            state.status = 'OPEN'  # Stop trying this provider
            state.opened_at = time.time()
            logging.error(f"Circuit breaker OPEN for {provider}")
    
    def record_success(self, provider):
        if provider in self.states:
            self.states[provider].failure_count = 0
            self.states[provider].status = 'CLOSED'
    
    def is_open(self, provider):
        if provider not in self.states:
            return False
        
        state = self.states[provider]
        if state.status != 'OPEN':
            return False
        
        # Check if timeout elapsed (half-open: try again)
        if time.time() - state.opened_at > self.timeout:
            state.status = 'HALF_OPEN'
            return False
        
        return True
```

**Local Embedding Fallback:**

```python
class LocalEmbeddings:
    """
    Local embedding model as last resort
    Always available, no API dependency
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        from sentence_transformers import SentenceTransformer
        
        # Download once, cache locally (~80MB)
        self.model = SentenceTransformer(model_name)
        
        # Model specs:
        # - Dimensions: 384
        # - Speed: ~50ms per embedding on CPU
        # - Quality: 85% of OpenAI ada-002 on benchmarks
        # - Cost: $0 (runs locally)
    
    def embed(self, content):
        """
        Generate embedding locally (CPU or GPU)
        """
        embedding = self.model.encode(content, convert_to_numpy=True)
        return embedding  # 384-dimensional vector
```

**Schema Tracking:**

```sql
-- Track which provider actually generated each embedding
ALTER TABLE embeddings ADD COLUMN provider TEXT 
    CHECK(provider IN ('gemini', 'openai', 'local', 'other'));

ALTER TABLE embeddings ADD COLUMN cost_usd REAL DEFAULT 0.0;

-- Track fallback events
CREATE TABLE provider_fallbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    primary_provider TEXT NOT NULL,
    fallback_provider TEXT NOT NULL,
    failure_reason TEXT,
    memory_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE INDEX idx_fallbacks_time ON provider_fallbacks(timestamp DESC);
```

**Decision:**
- Implement multi-provider fallback in MVP
- Always bundle local model as last resort
- Circuit breaker with 60-second timeout

**Trade-offs:**
- ✅ System remains operational during API outages
- ✅ Automatic failover (transparent to user)
- ✅ Cost optimization (can use cheaper providers)
- ❌ Embedding quality varies by provider
- ❌ Mixed-provider embeddings in same space (dimension mismatch risk)
- ❌ Increased complexity (multiple API clients)

---

### 5. Privacy Violations via Embedding APIs

**The Constraint:**
```python
# User stores sensitive content:
content = "API key: sk-abc123xyz... | Password: hunter2"

# System sends to Gemini API for embedding:
response = gemini.embed(content)

# Google now has:
# - User's API key in logs
# - User's password in logs
# - Potentially violates GDPR, CCPA, etc.

# Even if content is deleted from system,
# it's been transmitted to third party
```

**Impact:** 
- Legal liability (data breach, privacy violations)
- User trust violation
- Cannot use for sensitive/proprietary data

**Severity:** CRITICAL (MVP)

**Mitigation Strategy: Tiered Privacy Architecture**

```python
class PrivacyAwareIngestion:
    """
    Detect sensitive content, route to appropriate embedding provider
    """
    
    def __init__(self):
        self.pii_detector = PIIDetector()
        self.local_embeddings = LocalEmbeddings()
        self.cloud_embeddings = CloudEmbeddings()
    
    def ingest(self, content, metadata, space_id):
        # 1. Scan for sensitive content
        sensitivity_analysis = self.pii_detector.analyze(content)
        
        if sensitivity_analysis.contains_pii:
            # PII detected: use local embeddings only
            return self.ingest_sensitive(
                content, 
                metadata, 
                space_id,
                pii_types=sensitivity_analysis.pii_types
            )
        else:
            # No PII: safe to use cloud embeddings
            return self.ingest_standard(content, metadata, space_id)
    
    def ingest_sensitive(self, content, metadata, space_id, pii_types):
        """
        Sensitive content: never leaves local machine
        """
        # Store with PII markers
        memory_id = self.storage.store(
            content=content,
            metadata=metadata,
            space_id=space_id,
            contains_pii=True,
            pii_types=pii_types
        )
        
        # Generate embedding locally (never sent to cloud)
        local_embedding = self.local_embeddings.embed(content)
        self.storage.store_embedding(
            memory_id=memory_id,
            embedding=local_embedding,
            model='local-minilm',
            provider='local',  # Never cloud
            quality_tier='fast'
        )
        
        logging.info(f"Memory {memory_id} flagged as sensitive, using local embeddings only")
        return memory_id
```

**PII Detection:**

```python
class PIIDetector:
    """
    Detect personally identifiable information and secrets
    """
    
    def __init__(self):
        self.patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey|api-key)[\s:=]+[a-zA-Z0-9\-_]{20,}',
            'password': r'(?i)(password|passwd|pwd)[\s:=]+\S+',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'jwt': r'eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'private_key': r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
        }
    
    def analyze(self, content):
        """
        Scan content for PII patterns
        """
        detected_types = []
        
        for pii_type, pattern in self.patterns.items():
            if re.search(pattern, content):
                detected_types.append(pii_type)
        
        # Also use ML-based detection for names, addresses, etc.
        ml_detected = self.ml_pii_detection(content)
        detected_types.extend(ml_detected)
        
        return SensitivityAnalysis(
            contains_pii=len(detected_types) > 0,
            pii_types=detected_types,
            sensitivity_level=self.calculate_sensitivity(detected_types)
        )
```

**User Control:**

```python
# User can explicitly mark spaces as sensitive
space_config = {
    "space_id": "proprietary_code",
    "privacy_level": "maximum",  # never use cloud APIs
    "embedding_provider": "local_only",
    "pii_detection": "strict"
}

# Or mark individual memories
memory.store(
    content=proprietary_algorithm,
    metadata={...},
    force_local_embedding=True  # Override auto-detection
)
```

**Schema Changes:**

```sql
-- Privacy flags on spaces
ALTER TABLE spaces ADD COLUMN privacy_level TEXT
    DEFAULT 'standard'
    CHECK(privacy_level IN ('standard', 'high', 'maximum'));

ALTER TABLE spaces ADD COLUMN allowed_providers JSON;
-- Example: ["local"] for maximum privacy
-- Example: ["gemini", "openai", "local"] for standard

-- Privacy flags on memories (already in schema)
-- memories.contains_pii
-- memories.pii_types

-- Audit trail for privacy compliance
CREATE TABLE privacy_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN (
        'pii_detected', 'local_embedding_forced', 'cloud_embedding_used',
        'pii_redacted', 'memory_encrypted'
    )),
    pii_types JSON,
    embedding_provider TEXT,
    user_consented BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE INDEX idx_privacy_audit ON privacy_audit_log(memory_id, timestamp DESC);
```

**User Consent Flow:**

```bash
$ memory ingest sensitive_docs/
> ⚠️  PII detected in 15 files:
>   - API keys (3 files)
>   - Passwords (2 files)
>   - Email addresses (12 files)
> 
> These will use local embeddings only (never sent to cloud)
> Search quality may be lower, but data stays private
> 
> Continue? [y/N]: y
> ✓ Ingested 15 files with local embeddings
```

**Decision:**
- Implement PII detection in MVP
- Default to local embeddings when PII detected
- Never send flagged content to cloud without explicit user override
- Maintain audit log for compliance

**Trade-offs:**
- ✅ Protects user privacy
- ✅ Compliance with GDPR/CCPA
- ✅ Enables use with proprietary data
- ❌ Local embeddings lower quality (384 dims vs 768)
- ❌ False positives in PII detection (overly cautious)
- ❌ Performance overhead for scanning

---

## Temporal Constraints

### Model Deprecation and Migration

**The Constraint:**
```python
# Embedding models have finite lifespans
# - gemini-embedding-001 launched: 2023
# - gemini-embedding-001 deprecated: 2025 (hypothetical)
# - gemini-embedding-002 required: 2025+

# Cannot use old model after deprecation
# Must re-embed entire corpus (expensive, time-consuming)
# 100K docs × $0.15/1M tokens = $15 + 5.5 hours processing
```

**Severity:** HIGH

**Mitigation:** Model-aware architecture with gradual migration (already covered in dimension mismatch section)

---

### Semantic Drift Over Time

**The Constraint:**
```python
# Word meanings evolve
# 2024: "Prompt engineering" = crafting LLM inputs
# 2026: "Prompt engineering" might mean something else

# Embeddings capture meaning at time of creation
# Old embeddings have "dated" semantics
```

**Severity:** LOW

**Mitigation:** Accept this as inherent limitation. Optionally re-embed on manual trigger or when content accessed frequently.

---

## Scale Constraints

### Metadata Table Explosion

**The Constraint:**
```python
# Flexible metadata: key-value pairs
# 100K memories × 20 metadata keys = 2M rows in memory_metadata

# Query performance degrades:
SELECT m.* FROM memories m
JOIN memory_metadata mm ON m.id = mm.memory_id
WHERE mm.key = 'language' AND mm.value = 'python'
-- With 2M rows, even indexed, becomes slow
```

**Severity:** MEDIUM

**Mitigation: Hybrid Column/JSON Storage**

```sql
-- Hot metadata: frequently queried → dedicated columns
ALTER TABLE memories ADD COLUMN content_type TEXT;
ALTER TABLE memories ADD COLUMN language TEXT;
ALTER TABLE memories ADD COLUMN project TEXT;

CREATE INDEX idx_memories_content_type ON memories(content_type);
CREATE INDEX idx_memories_language ON memories(language);
CREATE INDEX idx_memories_project ON memories(project);

-- Cold metadata: rarely queried → JSON blob
-- Keep memory_metadata table for flexibility, but use sparingly
```

---

### Semantic Deduplication at Scale

**The Constraint:**
```python
# Exact dedup: O(1) hash lookup
# Semantic dedup: O(n²) pairwise similarity

# 10K new docs vs 100K existing:
# 10K × 100K = 1 billion comparisons
# At 1ms each = 277 hours = 11.5 days
```

**Severity:** HIGH

**Mitigation: LSH (Locality-Sensitive Hashing)**

```python
class LSHDeduplicator:
    """
    Approximate duplicate detection using MinHash LSH
    Reduces O(n²) to O(n) with high probability
    """
    
    def __init__(self, threshold=0.9, num_perm=128):
        from datasketch import MinHash, MinHashLSH
        
        self.threshold = threshold
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    
    def add_document(self, doc_id, content):
        """
        Add document to LSH index
        """
        # Create MinHash signature
        minhash = MinHash(num_perm=self.num_perm)
        for word in content.split():
            minhash.update(word.encode('utf-8'))
        
        # Insert into LSH index
        self.lsh.insert(doc_id, minhash)
    
    def find_duplicates(self, content):
        """
        Find potential duplicates (O(1) with high probability)
        """
        # Create signature for query
        minhash = MinHash(num_perm=self.num_perm)
        for word in content.split():
            minhash.update(word.encode('utf-8'))
        
        # Query LSH index (returns candidates only)
        candidates = self.lsh.query(minhash)
        
        # Verify candidates with exact similarity
        duplicates = []
        for candidate_id in candidates:
            exact_similarity = self.compute_exact_similarity(content, candidate_id)
            if exact_similarity >= self.threshold:
                duplicates.append(candidate_id)
        
        return duplicates
```

**Decision:** Implement LSH-based deduplication in Phase 3 when corpus exceeds 10K documents.

---

## Consistency Constraints

### Embedding-Content Desynchronization

**The Constraint:**
```python
# User updates content:
memories.update(memory_id=123, new_content="fixed typo in auth code")

# But embedding still represents old content
# Search retrieves memory based on old embedding
# User sees updated content (confusing mismatch)
```

**Severity:** HIGH

**Mitigation: Version-Aware Updates**

```python
def update_memory(memory_id, new_content):
    """
    Update memory and queue for re-embedding
    """
    # 1. Update content
    storage.update_content(memory_id, new_content)
    
    # 2. Mark embeddings as stale
    storage.mark_embeddings_stale(memory_id)
    
    # 3. Queue for re-embedding
    embedding_queue.add(
        memory_id=memory_id,
        priority='high',  # Recent updates prioritized
        reason='content_update'
    )
    
    # 4. Until re-embedded, lower retrieval score
    # (stale embeddings less trustworthy)
    storage.update_metadata(
        memory_id,
        key='embedding_freshness',
        value='stale'
    )
```

**Schema Changes:**

```sql
-- Track freshness of embeddings
ALTER TABLE embeddings ADD COLUMN is_stale BOOLEAN DEFAULT FALSE;
ALTER TABLE embeddings ADD COLUMN last_content_hash TEXT;

-- When content changes, mark embeddings stale
CREATE TRIGGER mark_embeddings_stale_on_update
AFTER UPDATE ON memories
FOR EACH ROW
WHEN NEW.content_hash != OLD.content_hash
BEGIN
    UPDATE embeddings 
    SET is_stale = TRUE 
    WHERE memory_id = NEW.id;
END;
```

---

### Stale Relationship Tracking

**The Constraint:**
```python
# Memory A "contradicts" Memory B
# User updates Memory B to align with A
# Relationship still says "contradicts" (now false)
```

**Severity:** MEDIUM

**Mitigation:** Relationships are historical facts. Add timestamps and confidence decay.

```sql
ALTER TABLE memory_relationships ADD COLUMN last_validated TIMESTAMP;
ALTER TABLE memory_relationships ADD COLUMN confidence_decay_rate REAL DEFAULT 0.05;

-- Confidence decays over time without revalidation
-- Query adjusts confidence by time since last validation
```

---

## Concurrency Constraints

### SQLite Write Serialization

**The Constraint:**
```python
# SQLite: single writer at a time
# Thread 1: Writing new memory (locks DB)
# Thread 2: Updating existing memory (waits)
# Thread 3: Deleting memory (waits)

# If Thread 1 takes 5 seconds, Threads 2-3 blocked
```

**Severity:** MEDIUM (MVP accepts this, migrate to PostgreSQL in Phase 5 if needed)

**Mitigation: Write Queue**

```python
class WriteQueue:
    """
    Serialize writes through queue, avoid lock contention
    """
    
    def __init__(self):
        self.queue = Queue()
        self.worker = Thread(target=self.process_queue, daemon=True)
        self.worker.start()
    
    def enqueue(self, operation, *args, **kwargs):
        """
        Add write operation to queue
        Returns immediately (non-blocking)
        """
        future = Future()
        self.queue.put((operation, args, kwargs, future))
        return future
    
    def process_queue(self):
        """
        Process writes serially (one at a time)
        """
        while True:
            operation, args, kwargs, future = self.queue.get()
            try:
                result = operation(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
```

---

## Dependency Constraints

### Embedding API Breaking Changes

**The Constraint:**
```python
# Google changes API response format
# Old: response.embedding
# New: response.data[0].embedding

# Your code breaks overnight
```

**Severity:** MEDIUM

**Mitigation: Adapter Pattern**

```python
class EmbeddingAdapter:
    """
    Isolate API-specific code, adapt to common interface
    """
    
    def embed(self, content):
        """Common interface"""
        raise NotImplementedError

class GeminiAdapter(EmbeddingAdapter):
    def embed(self, content):
        try:
            response = gemini_api.embed(content)
            return self._extract_embedding(response)
        except Exception as e:
            return self._handle_error(e)
    
    def _extract_embedding(self, response):
        """Centralize response parsing"""
        # Try new format first
        if hasattr(response, 'data'):
            return response.data[0].embedding
        # Fallback to old format
        elif hasattr(response, 'embedding'):
            return response.embedding
        else:
            raise APIFormatError("Unknown response format")
```

---

## Semantic Constraints

### Homonym Confusion

**The Constraint:**
```python
# "Apple" (fruit) vs "Apple" (company)
# "Python" (snake) vs "Python" (programming language)

# Embeddings similar, but semantics different
```

**Severity:** LOW

**Mitigation:** Rely on metadata filtering (content_type, domain) to disambiguate.

---

## User Experience Constraints

### Query Formulation Gap

**The Constraint:**
```python
# User thinks: "How did I handle auth?"
# User types: "authentication previous implementation"
# Memory contains: "JWT token validation middleware"

# Vocabulary mismatch → poor retrieval
```

**Severity:** MEDIUM

**Mitigation: LLM Query Reformulation**

```python
def search_with_reformulation(user_query):
    """
    LLM expands/reformulates query for better matching
    """
    # Ask LLM to generate alternative phrasings
    reformulations = llm.generate(f"""
    The user asked: "{user_query}"
    Generate 3 alternative ways to phrase this query:
    """)
    
    # Search with all reformulations
    all_results = []
    for query_variant in [user_query] + reformulations:
        results = memory_search(query_variant)
        all_results.extend(results)
    
    # Deduplicate and merge
    return deduplicate_and_rank(all_results)
```

---

## Cost Constraints

### Re-embedding Cost Accumulation

**The Constraint:**
```python
# Content updates: new embeddings
# Model migrations: re-embed corpus
# Space reconfigurations: re-embed

# 100K memories × 10 updates/year × $0.15/1M tokens = $150/year
```

**Severity:** MEDIUM

**Mitigation:**
- Cache embeddings aggressively
- Only re-embed if content hash changes
- Batch re-embedding operations
- Budget alerts

---

## Operational Constraints

### Zero-Downtime Schema Migrations

**The Constraint:**
```python
# ALTER TABLE locks database
# Large tables: minutes of downtime
```

**Severity:** MEDIUM

**Mitigation: Additive-Only Migrations**

```python
# Bad: Removing columns (requires table rebuild)
ALTER TABLE memories DROP COLUMN old_field;

# Good: Adding columns (instant)
ALTER TABLE memories ADD COLUMN new_field TEXT;

# Strategy: Never remove, only add and deprecate
# Mark old columns as deprecated in comments
```

---

## Correctness Constraints

### Retrieval Precision vs Recall

**The Constraint:**
```python
# High precision (top_k=5): Might miss relevant results
# High recall (top_k=50): Floods context with noise
```

**Severity:** MEDIUM

**Mitigation: Dynamic top_k**

```python
def adaptive_search(query, space_id):
    """
    Adjust top_k based on query confidence
    """
    # Get initial results with scores
    results = memory_search(query, space_id, top_k=20)
    
    # Analyze score distribution
    if results[0].score > 0.9 and results[4].score < 0.7:
        # Clear winner, high precision
        return results[:3]
    elif all(r.score > 0.8 for r in results[:10]):
        # Many good matches, increase recall
        return results[:10]
    else:
        # Medium confidence, balanced
        return results[:5]
```

---

### Reasoning Trace Accuracy

**The Constraint:**
```python
# System learns: "Strategy X succeeded"
# But: User didn't actually use the results (false positive)
```

**Severity:** MEDIUM

**Mitigation:** Explicit user feedback + confidence decay

```python
# Track actual usage, not just retrieval
def record_memory_usage(memory_id, helpful=True):
    """User explicitly marks memory as helpful"""
    storage.update(memory_id, helpful_count=+1)

# Decay confidence in reasoning traces over time
def decay_reasoning_confidence():
    """Lower confidence in old traces"""
    storage.execute("""
        UPDATE reasoning_traces 
        SET confidence = confidence * 0.95
        WHERE timestamp < datetime('now', '-30 days')
    """)
```

---

## Constraint Priority Matrix

| Constraint | Severity | Phase | Mitigation Status |
|-----------|----------|-------|-------------------|
| Embedding availability vs search | CRITICAL | 1 | ✅ Dual-embedding |
| Dimension mismatch | CRITICAL | 1 | ✅ Model-aware search |
| Vector search performance | CRITICAL | 4 | ✅ FAISS migration |
| API dependency | CRITICAL | 1 | ✅ Multi-provider fallback |
| Privacy violations | CRITICAL | 1 | ✅ PII detection + local |
| Model deprecation | HIGH | 4 | ✅ Gradual migration |
| Metadata explosion | MEDIUM | 5 | ✅ Hybrid storage |
| Semantic deduplication | HIGH | 3 | ✅ LSH |
| Embedding-content desync | HIGH | 2 | ✅ Stale tracking |
| Stale relationships | MEDIUM | 4 | ✅ Confidence decay |
| SQLite concurrency | MEDIUM | 5 | ⚠️ Write queue / PG migration |
| API breaking changes | MEDIUM | 2 | ✅ Adapter pattern |
| Query formulation gap | MEDIUM | 4 | ✅ LLM reformulation |
| Re-embedding costs | MEDIUM | 3 | ✅ Caching + budgets |
| Schema migration downtime | MEDIUM | 3 | ✅ Additive-only |
| Precision vs recall | MEDIUM | 4 | ✅ Dynamic top_k |
| Reasoning trace accuracy | MEDIUM | 4 | ✅ Feedback + decay |
| Semantic drift | LOW | 6 | ⚠️ Accept limitation |
| Homonym confusion | LOW | 6 | ⚠️ Metadata filtering |

Legend:
- ✅ Mitigation defined and ready to implement
- ⚠️ Partial mitigation or accept as limitation
- ❌ Needs further design work

---

## Architectural Decisions Summary

### Phase 1 (MVP) Constraints Addressed:

1. **Dual-Embedding Architecture**
   - Local embeddings (fast, immediate search)
   - Cloud embeddings (high quality, background upgrade)
   - Trade-off: 2x storage temporarily

2. **Model-Aware Search Routing**
   - Support mixed-dimension embeddings during migrations
   - Query with correct model, merge results
   - Trade-off: Search complexity

3. **Multi-Provider Fallback**
   - Gemini → OpenAI → Local cascade
   - Circuit breaker pattern
   - Trade-off: Increased complexity

4. **PII Detection + Local-Only Mode**
   - Regex + ML-based PII scanning
   - Force local embeddings for sensitive content
   - Trade-off: Lower quality for sensitive data

5. **Write Queue for Concurrency**
   - Serialize writes through queue
   - Non-blocking for callers
   - Trade-off: Eventual consistency

### Phase 2-3 Additions:

6. **LSH-Based Semantic Deduplication**
   - O(n) instead of O(n²)
   - Approximate but fast

7. **Stale Embedding Tracking**
   - Mark embeddings stale on content update
   - Re-embed prioritized

8. **Adapter Pattern for APIs**
   - Isolate provider-specific code
   - Handle breaking changes gracefully

### Phase 4-5 Additions:

9. **FAISS Index Migration**
   - 10-200x faster vector search
   - Mandatory at 100K+ vectors

10. **Reasoning Trace with Confidence Decay**
    - Learn from experience
    - Decay confidence over time

### Phase 6 Considerations:

11. **PostgreSQL Migration Path**
    - If SQLite concurrency becomes bottleneck
    - Row-level locking, better write concurrency

---

## Implementation Checklist

### MVP (Phase 1):
- [ ] Implement dual-embedding architecture
- [ ] Add PII detection scanner
- [ ] Implement multi-provider fallback
- [ ] Add model-aware search routing
- [ ] Implement write queue
- [ ] Schema: embedding quality tiers, privacy flags
- [ ] User consent flows for privacy

### Phase 2:
- [ ] Stale embedding tracking
- [ ] API adapter pattern
- [ ] Query reformulation

### Phase 3:
- [ ] LSH deduplication
- [ ] Hybrid metadata storage
- [ ] Cost budgets and alerts

### Phase 4:
- [ ] FAISS index migration
- [ ] Reasoning trace confidence decay
- [ ] Dynamic top_k retrieval

### Phase 5:
- [ ] Evaluate PostgreSQL migration
- [ ] Advanced pruning strategies
- [ ] Backup optimization

---

## Conclusion

This document catalogs **22 distinct constraints** across 11 categories, with mitigation strategies for each. The 5 critical MVP constraints have concrete architectural solutions ready for implementation:

1. ✅ Dual-embedding (search availability)
2. ✅ Model-aware routing (dimension mismatch)
3. ✅ Multi-provider fallback (API dependency)
4. ✅ PII detection (privacy)
5. ✅ Write queue (concurrency)

All constraints are now **visible in the plan** with clear phase assignments and implementation strategies.

**Next Steps:**
1. Review constraint priority matrix
2. Validate architectural decisions
3. Begin Phase 1 implementation with constraint mitigations

---

**Document Status:** Complete - Ready for implementation
