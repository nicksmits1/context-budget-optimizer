---
title: "Incident Post-Mortem: Context Engine Outage Aug 14"
department: "engineering"
doc_type: "postmortem"
created: "2025-08-19"
sensitivity: "internal"
---

# Post-Mortem: Context Engine Outage — August 14, 2025

## Summary

On August 14, 2025 from 14:23 to 15:47 PT (84 minutes), the Context Engine returned errors for approximately 60% of queries. Root cause: a memory leak in the embedding batch processor introduced in a deploy earlier that day.

**Impact:** 847 customers affected. Approximately 12,400 failed queries during the window. No data loss.

## Timeline

- **14:00** — Deploy of context-engine v2.14.3 to production (contained batch embedding optimization)
- **14:23** — Alerting fires: `context_engine_error_rate > 5%`
- **14:25** — On-call engineer (Alex Rivera) acknowledges, begins investigation
- **14:32** — Identified that 3 of 8 Context Engine pods are in OOMKilled state
- **14:38** — Attempted rolling restart of pods — new pods also OOM within minutes
- **14:45** — Escalated to senior engineer (Lisa Morrison). Suspected the new batch optimization code.
- **14:52** — Decision to rollback to v2.14.2
- **15:05** — Rollback deployed to staging, verified healthy
- **15:12** — Rollback deployed to production
- **15:30** — Error rate dropping, pods stabilizing
- **15:47** — All pods healthy, error rate back to baseline. Incident resolved.

## Root Cause

The batch embedding optimization in v2.14.3 introduced a code path where large documents (>10K tokens) were loaded entirely into memory for batch processing instead of streaming. For tenants with many large documents, this caused memory usage to spike beyond the pod's 4GB limit.

The change had unit tests but the test documents were all small (<1K tokens). No integration test with realistic document sizes existed.

## Remediation

1. ✅ Reverted the batch optimization
2. ✅ Added memory profiling to the CI pipeline for the Context Engine
3. ✅ Created integration tests with documents up to 50K tokens
4. ✅ Added pod memory usage alerts at 70% threshold (early warning)
5. 🔄 Reworking the batch optimization to use streaming (target: v2.14.4)

## Lessons Learned

- Our test data is not representative of real-world document sizes. We need a test corpus that matches production distributions.
- The canary deployment should have caught this, but the canary tenant happened to have small documents. We should route canary traffic from a diverse set of tenants.
- Rollback took 23 minutes from decision to resolution. We should pre-build rollback artifacts to cut this to <10 minutes.
