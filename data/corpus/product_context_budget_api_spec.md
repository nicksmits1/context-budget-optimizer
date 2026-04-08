---
title: "Context Budget API Specification"
department: "engineering"
doc_type: "technical"
created: "2025-08-20"
sensitivity: "internal"
---

# Context Budget API Specification

## Overview

The Context Budget API allows developers to control how much context is sent to their LLM calls. Instead of dumping all retrieved chunks into the prompt, the API optimizes what gets included based on a token budget, relevance, diversity, and metadata signals.

## Endpoint

```
POST /v1/context/budget
```

## Request

```json
{
  "query": "string",
  "budget": {
    "max_tokens": 8192,
    "target_tokens": 6000,
    "strategy": "auto" | "topk" | "mmr" | "importance" | "summary"
  },
  "filters": {
    "departments": ["engineering", "product"],
    "doc_types": ["technical", "roadmap"],
    "date_range": {"after": "2025-01-01"},
    "sensitivity_max": "internal"
  },
  "options": {
    "include_metadata": true,
    "return_alternatives": false,
    "mmr_lambda": 0.7,
    "importance_weights": {
      "relevance": 0.5,
      "recency": 0.2,
      "source_type": 0.15,
      "sensitivity": 0.15
    }
  }
}
```

## Response

```json
{
  "context": {
    "chunks": [
      {
        "id": "doc_id::chunk_0",
        "content": "...",
        "score": 0.89,
        "tokens": 245,
        "metadata": {
          "title": "...",
          "department": "engineering",
          "doc_type": "technical",
          "created": "2025-08-20"
        }
      }
    ],
    "total_tokens": 5840,
    "strategy_used": "mmr",
    "chunks_considered": 45,
    "chunks_selected": 12
  },
  "performance": {
    "retrieval_ms": 42,
    "optimization_ms": 18,
    "total_ms": 60
  }
}
```

## Strategy Descriptions

- **auto:** The system picks the best strategy based on query characteristics and budget constraints. Uses MMR for broad queries, importance-weighted for specific lookups, and summary for very tight budgets.
- **topk:** Simple similarity-ranked selection. Fast but may include redundant chunks.
- **mmr:** Maximal Marginal Relevance. Balances relevance with diversity. Best for broad queries.
- **importance:** Weights chunks by metadata signals (recency, source type, sensitivity). Best for enterprise-aware retrieval.
- **summary:** Compresses lower-ranked chunks into summaries. Highest quality-per-token but adds latency.

## Rate Limits

Same as standard API rate limits. Each budget optimization call counts as 1 request. If the `summary` strategy is used, it counts as 2 requests due to the additional LLM call.
