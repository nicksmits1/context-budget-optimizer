---
title: "Testing Strategy"
department: "engineering"
doc_type: "technical"
created: "2025-05-20"
sensitivity: "internal"
---

# Testing Strategy

## Testing Pyramid

We follow the classic testing pyramid: many unit tests, a moderate number of integration tests, and a small number of end-to-end tests.

### Unit Tests
- **Coverage target:** 80% for new code, 70% overall
- **Framework:** pytest (Python), Jest (TypeScript)
- **Speed target:** Full unit test suite should run in <2 minutes
- Mock external dependencies (databases, APIs, third-party services)
- Every bug fix must include a regression test

### Integration Tests
- Test API endpoints with a real database and Redis (via Docker Compose)
- Test connector integrations against sandbox accounts (Google Drive sandbox, Salesforce dev org)
- Test the full retrieval pipeline: ingest → chunk → embed → retrieve → rank
- Run in CI on every PR, timeout of 10 minutes

### End-to-End Tests
- Playwright for web UI testing
- Test critical user flows: login, connect data source, run query, view results
- Run nightly, not on every PR (too slow)
- Maintained by the QA team, written in TypeScript

## Testing the Context Engine

The Context Engine has its own specialized test suite:

1. **Retrieval Quality Tests:** A curated set of 200 query-expected_results pairs. Run nightly and after any embedding model change. Measures recall@10 and NDCG@10.

2. **Context Budget Tests:** Verify that each strategy respects token budgets and produces valid output. Test edge cases: very small budgets, very large budgets, queries with no relevant results.

3. **Latency Benchmarks:** Measure p50/p95/p99 latency for retrieval at various corpus sizes (1K, 10K, 100K, 1M documents). Run weekly on a dedicated benchmark environment.

4. **Permission Tests:** Verify that context retrieval respects access controls. Tests include: user A should see docs they own, user A should not see user B's private docs, admin override works correctly.

## Test Data

- Unit tests use factory functions to generate test data (no shared fixtures across test files)
- Integration tests use a seeded test database, refreshed before each test run
- Never use production data in tests (even anonymized). Generate synthetic data instead.

## Flaky Test Policy

Flaky tests are quarantined immediately and tracked in Jira with the `flaky-test` label. If a test has been flaky for >2 weeks without a fix, it gets deleted. Flaky tests are worse than no tests because they erode trust in the test suite.
