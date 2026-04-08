---
title: "API Design Guidelines"
department: "engineering"
doc_type: "technical"
created: "2025-05-10"
sensitivity: "internal"
---

# API Design Guidelines

## General Principles

All public APIs follow REST conventions. We use JSON for request and response bodies. API versioning is done via URL path (`/v1/`, `/v2/`). Breaking changes require a new version; additive changes can go in the current version.

## Authentication

All API requests require a Bearer token in the Authorization header. Tokens are issued via the `/v1/auth/token` endpoint using OAuth 2.0 client credentials flow. Tokens expire after 1 hour and should be refreshed proactively.

For server-to-server integrations, we also support API keys passed via the `X-API-Key` header. API keys don't expire but can be revoked by the customer admin.

## Rate Limiting

Default rate limits:
- Standard tier: 100 requests/minute, 10,000 requests/day
- Enterprise tier: 1,000 requests/minute, 100,000 requests/day
- Enterprise Plus: Custom limits negotiated per contract

Rate limit headers are returned on every response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

When rate limited, the API returns HTTP 429 with a `Retry-After` header. Clients should implement exponential backoff.

## Error Handling

Error responses follow a consistent format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable description",
    "details": [{"field": "query", "issue": "Required field missing"}]
  }
}
```

Standard error codes: `INVALID_REQUEST` (400), `UNAUTHORIZED` (401), `FORBIDDEN` (403), `NOT_FOUND` (404), `RATE_LIMITED` (429), `INTERNAL_ERROR` (500).

## Pagination

List endpoints use cursor-based pagination. Response includes `next_cursor` and `has_more`. Page size defaults to 20, max 100.

## Context Retrieval Endpoint

The primary endpoint for context retrieval:

```
POST /v1/context/retrieve
{
  "query": "What is our parental leave policy?",
  "max_tokens": 4096,
  "strategy": "auto",
  "filters": {
    "departments": ["hr", "legal"],
    "sensitivity_max": "internal"
  }
}
```

Response includes the selected context chunks, total token count, and metadata about the retrieval strategy used.
