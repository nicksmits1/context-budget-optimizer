---
title: "Database Migration Plan — pgvector 0.7"
department: "engineering"
doc_type: "technical"
created: "2025-09-15"
sensitivity: "internal"
---

# Database Migration Plan — pgvector 0.7 Upgrade

## Background

We're upgrading from pgvector 0.5 to 0.7 to take advantage of HNSW index support, which should reduce vector search latency by 40-60% for our largest tenants. Currently our p95 vector search time is 180ms for tenants with >1M embeddings; target is <80ms.

## Migration Strategy

We'll use a blue-green migration approach to avoid downtime:

1. **Phase 1 — Parallel Write (Week 1-2):** Deploy a new PostgreSQL instance with pgvector 0.7. Modify the Context Engine to dual-write embeddings to both old and new databases. Backfill historical embeddings in batches of 10K.

2. **Phase 2 — Shadow Read (Week 3):** Route 10% of read traffic to the new database in shadow mode (results compared but not returned to users). Monitor for correctness and performance.

3. **Phase 3 — Cutover (Week 4):** Switch read traffic to the new database. Keep the old database in read-only mode for 1 week as a rollback safety net.

4. **Phase 4 — Cleanup (Week 5):** Decommission the old database instance. Remove dual-write code paths.

## HNSW Index Configuration

```sql
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);
```

Query-time `ef_search` parameter will start at 100 and be tuned based on recall benchmarks. Higher `ef_search` = better recall but slower queries.

## Risk Mitigation

- Embedding dimensions must match exactly (384 for our current model). Verify before backfill.
- HNSW indexes consume more memory than IVFFlat (~2x). We'll need to upgrade the database instance from db.r6g.xlarge to db.r6g.2xlarge ($1,200/month increase).
- Backfill will generate significant I/O. Schedule during off-peak hours (2-6am PT).

## Rollback Plan

If issues are detected during Phase 3, revert the read path to the old database within minutes via a feature flag. The old database remains fully operational until Phase 4 is complete.

## Timeline

- Start: October 1, 2025
- Target completion: November 1, 2025
- Owner: Platform team (lead: Alex Rivera)
