---
template: observations
work_id: WORK-108
captured_session: '325'
generated: '2026-02-08'
last_updated: '2026-02-08T23:51:18'
---
# Observations: WORK-108

## What surprised you?

The scope was broader than documented. WORK.md listed 5 source files but the actual codebase had 11 files with references to `text-embedding-004`. More critically, the model swap was **not** a simple find-and-replace: `gemini-embedding-001` defaults to 3072-dimensional vectors while `text-embedding-004` produced 768-dim. Without discovering this and adding `output_dimensionality=768`, the fix would have silently broken all similarity search — queries would execute without error but return no meaningful results because 3072-dim query vectors can't match 768-dim stored vectors in sqlite-vec. This is the kind of "fix that creates a worse bug" pattern.

## What's missing?

The embedding model name is hardcoded in 11 locations across the codebase. There's no single constant or config entry for it. If Google retires `gemini-embedding-001` in the future, we'll face the same multi-file hunt. A `EMBEDDING_MODEL` constant in a shared config (or `haios.yaml`) with a companion `EMBEDDING_DIMENSIONS` would prevent this. However, the `output_dimensionality` coupling means a config-only swap is dangerous — changing model without verifying dimension compatibility could silently break search. Any future migration needs a compatibility verification step.

## What should we remember?

When migrating embedding models: **always verify output dimensionality**. The API will happily generate embeddings with a different dimension count, and vector similarity search will execute without errors — it just returns garbage or empty results. The `output_dimensionality` parameter on `genai.embed_content()` is the safety valve. Also: the MCP server runs the code in-process, so file changes require a server restart to take effect — two restarts were needed during this fix (one for model name, one for dimensionality).

## What drift did you notice?

`haios_etl/synthesis.py:499` stores the model name as metadata but was not listed in WORK.md's `source_files`. The WORK.md scope underestimated the actual blast radius by ~50%. The `scripts/generate_embeddings.py` docstring at line 64 references "text-embedding-004 has a token limit; ~25k chars is safe" — this token limit claim may or may not apply to `gemini-embedding-001` and should be verified if that script is used again.
