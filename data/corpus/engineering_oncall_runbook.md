---
title: "On-Call Runbook"
department: "engineering"
doc_type: "runbook"
created: "2025-04-20"
sensitivity: "internal"
---

# On-Call Runbook

## Rotation Schedule

On-call rotations run Monday 9am PT to Monday 9am PT. The primary on-call engineer is responsible for all production alerts during their shift. A secondary on-call provides backup and handles escalations if the primary is unavailable.

Current rotation is managed in PagerDuty under the "Engineering Primary" schedule.

## Alert Triage

### Critical Alerts (page immediately)
- `context_engine_error_rate > 5%` — Context Engine returning errors above threshold
- `api_latency_p99 > 2000ms` — API response times degraded
- `database_connections_exhausted` — PostgreSQL connection pool full
- `embedding_service_down` — ML inference service unreachable

### Warning Alerts (Slack notification, respond within 1 hour)
- `context_engine_error_rate > 1%` — Elevated error rate
- `disk_usage > 85%` — Storage filling up
- `queue_depth > 10000` — Message queue backing up
- `certificate_expiry < 14 days` — TLS cert expiring soon

## Common Issues and Fixes

### Context Engine High Error Rate
1. Check if it's a specific tenant: `kubectl logs -l app=context-engine | grep ERROR | awk '{print $5}' | sort | uniq -c`
2. If single tenant: likely a malformed document causing embedding failures. Quarantine the document via admin API
3. If all tenants: check the embedding model service health. Restart if needed: `kubectl rollout restart deployment/embedding-service`

### Database Connection Exhaustion
1. Check for long-running queries: `SELECT pid, duration, query FROM pg_stat_activity WHERE duration > interval '5 minutes'`
2. Kill stuck queries if safe: `SELECT pg_terminate_backend(pid)`
3. If recurring, check if a recent deploy introduced a connection leak

### High API Latency
1. Check Datadog APM for the slowest endpoints
2. Common cause: cache miss storm after a Redis restart. Cache usually warms within 10 minutes
3. If it's the search service: check Elasticsearch cluster health (`GET _cluster/health`)

## Escalation

If you can't resolve an issue within 30 minutes, escalate to the secondary on-call. For SEV-1 incidents, immediately page the VP of Engineering and follow the Incident Response Plan.

## Post-Shift Handoff

Write a brief handoff note in #oncall-handoff Slack channel covering: any active incidents, unresolved alerts, and anything the next on-call should watch for.
