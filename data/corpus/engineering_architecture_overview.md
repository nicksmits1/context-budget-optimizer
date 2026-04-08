---
title: "Engineering Architecture Overview"
department: "engineering"
doc_type: "technical"
created: "2025-09-01"
sensitivity: "internal"
---

# Engineering Architecture Overview

## System Overview

Our platform runs as a distributed microservices architecture deployed on AWS, with Kubernetes (EKS) orchestrating all production workloads. The system processes approximately 2.3 million API requests daily and serves 847 active customer tenants.

## Core Services

**API Gateway (Kong):** All external traffic routes through Kong, which handles rate limiting, authentication token validation, and request routing. Average latency at the gateway is 12ms p50, 45ms p99.

**Auth Service:** Handles OAuth 2.0 / OIDC flows, SAML SSO for enterprise customers, and API key management. Built in Go. Integrates with Okta and Azure AD for federated identity.

**Context Engine:** The core product service. Ingests documents from connected data sources, chunks and embeds them, and serves relevant context to LLM queries. Built in Python (FastAPI). Uses pgvector for vector storage and Redis for caching hot embeddings.

**Search Service:** Hybrid search combining BM25 (Elasticsearch) with semantic search (pgvector). Reranking is done with a cross-encoder model hosted on a dedicated GPU node. Query latency target is <200ms p95.

**Permissions Service:** Row-level and document-level access control. Every context retrieval call passes through permissions checks. Built in Go. Uses a policy engine inspired by Google Zanzibar.

**Connector Service:** Manages integrations with external data sources (Google Drive, Slack, Confluence, Notion, Salesforce). Each connector runs as an isolated worker process with its own credential store.

## Data Layer

- **PostgreSQL 15** (RDS): Primary datastore for user data, tenant config, document metadata
- **pgvector**: Vector embeddings stored alongside document metadata
- **Elasticsearch 8**: Full-text search index, BM25 scoring
- **Redis Cluster**: Embedding cache, session store, rate limiting counters
- **S3**: Raw document storage, chunked content backups

## Infrastructure

- **Kubernetes (EKS):** 3 node groups — general (m6i.xlarge), compute (c6i.2xlarge), GPU (g5.xlarge for ML inference)
- **CI/CD:** GitHub Actions → ArgoCD for GitOps deployments
- **Monitoring:** Datadog for metrics/traces, PagerDuty for alerting
- **IaC:** Terraform for AWS resources, Helm charts for K8s workloads

## Current Tech Debt

1. The Context Engine still has some synchronous embedding calls that should be batched
2. Elasticsearch index mapping needs a v2 schema migration (planned Q4)
3. The permissions cache invalidation has a known race condition under high write loads
