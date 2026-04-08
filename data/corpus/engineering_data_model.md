---
title: "Core Data Model"
department: "engineering"
doc_type: "technical"
created: "2025-04-10"
sensitivity: "internal"
---

# Core Data Model

## Overview

This document describes the core data model for the platform. All tables use UUID primary keys and include `created_at` and `updated_at` timestamps.

## Tenants

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan_tier VARCHAR(50) NOT NULL, -- starter, business, enterprise, enterprise_plus
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

All data is tenant-scoped. Every query includes a tenant_id filter to enforce data isolation.

## Documents

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    source_id UUID REFERENCES data_sources(id),
    external_id VARCHAR(500), -- ID in the source system
    title VARCHAR(1000),
    content TEXT,
    metadata JSONB DEFAULT '{}', -- department, doc_type, sensitivity, etc.
    content_hash VARCHAR(64), -- SHA-256 for dedup and integrity
    status VARCHAR(50) DEFAULT 'active', -- active, archived, deleted
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Chunks

```sql
CREATE TABLE chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    embedding vector(384), -- pgvector, dimension matches model
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 200);
```

## Data Sources

```sql
CREATE TABLE data_sources (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    type VARCHAR(50) NOT NULL, -- google_drive, confluence, slack, notion, salesforce, etc.
    name VARCHAR(255) NOT NULL,
    config JSONB DEFAULT '{}', -- encrypted connection details
    status VARCHAR(50) DEFAULT 'active',
    last_sync_at TIMESTAMPTZ,
    sync_frequency_minutes INTEGER DEFAULT 60,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Queries (Analytics)

```sql
CREATE TABLE query_log (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID,
    query_text TEXT NOT NULL,
    strategy_used VARCHAR(50),
    token_budget INTEGER,
    tokens_used INTEGER,
    chunks_retrieved INTEGER,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

This table is append-only and used for analytics. Retained for 90 days, then aggregated and purged.
