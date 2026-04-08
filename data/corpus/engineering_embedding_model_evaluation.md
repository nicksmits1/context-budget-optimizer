---
title: "Embedding Model Evaluation Results"
department: "engineering"
doc_type: "technical"
created: "2025-08-30"
sensitivity: "internal"
---

# Embedding Model Evaluation Results

## Objective

Evaluate candidate embedding models to replace our current `all-MiniLM-L6-v2` (384-dim) model. Goals: improve retrieval recall@10 by at least 10% while keeping latency under 50ms per document chunk.

## Models Tested

| Model | Dimensions | Size | Recall@10 | Latency (p50) | Latency (p99) |
|-------|-----------|------|-----------|---------------|---------------|
| all-MiniLM-L6-v2 (current) | 384 | 80MB | 72.3% | 8ms | 22ms |
| bge-base-en-v1.5 | 768 | 220MB | 81.7% | 15ms | 38ms |
| bge-large-en-v1.5 | 1024 | 650MB | 84.2% | 32ms | 78ms |
| e5-large-v2 | 1024 | 670MB | 83.8% | 34ms | 82ms |
| gte-base-en-v1.5 | 768 | 220MB | 80.1% | 14ms | 35ms |
| nomic-embed-text-v1.5 | 768 | 274MB | 82.4% | 16ms | 40ms |

## Evaluation Dataset

We used a benchmark of 500 query-document pairs sampled from real customer queries (anonymized). Queries span all departments and document types in our corpus.

## Recommendation

**bge-base-en-v1.5** is the recommended upgrade path. It offers a 13% improvement in recall@10 over our current model with only a modest latency increase (8ms → 15ms p50). The larger models (bge-large, e5-large) provide diminishing returns for 2x the latency.

## Migration Considerations

- All existing embeddings will need to be re-generated (estimated 48 hours for full corpus)
- Vector dimension change from 384 → 768 doubles storage requirements (currently 120GB → ~240GB)
- The pgvector HNSW index needs to be rebuilt after re-embedding
- Recommend coordinating with the pgvector 0.7 migration to avoid doing this twice

## Next Steps

1. Get approval from David (CTO) on the model choice
2. Coordinate timeline with pgvector migration (Alex Rivera)
3. Run A/B test in production with 5% traffic before full cutover
4. Update the Context Budget API to account for the new embedding quality in its optimization
