---
title: "Permissions System Design"
department: "engineering"
doc_type: "technical"
created: "2025-06-15"
sensitivity: "internal"
---

# Permissions System Design

## Overview

The permissions system controls who can access which documents in the context engine. It's inspired by Google Zanzibar and uses a relationship-based access control (ReBAC) model.

## Core Concepts

**Object:** A document or chunk in the system. Each object has a type (document, folder, workspace) and an ID.

**Relation:** A named relationship between a user/group and an object. Examples: `owner`, `editor`, `viewer`.

**Tuple:** A permission fact: `(user:alice, viewer, document:budget_2025)`. This means Alice can view the 2025 budget document.

**Permission inheritance:** Permissions flow through the object hierarchy. If Alice is a viewer of workspace:finance, she can view all documents in that workspace unless explicitly denied.

## Access Check Flow

When the Context Engine retrieves chunks for a query:

1. Retrieve candidate chunks based on similarity
2. For each chunk, resolve the parent document
3. Check if the requesting user has at least `viewer` relation on the document
4. Filter out chunks the user can't access
5. Pass only authorized chunks to the context selection strategy

This happens synchronously on every query. Target latency for permissions checks: <10ms for up to 100 chunks.

## Permission Sources

Permissions can come from three sources, merged in order of priority:

1. **Source system ACLs:** When we ingest from Google Drive or Confluence, we import the existing permissions. If Alice can view a Google Doc, she can view the corresponding chunks in our system.
2. **Workspace-level rules:** Admins can set default permissions at the workspace level (e.g., "all engineers can view the engineering workspace").
3. **Explicit overrides:** Admins can grant or revoke access to specific documents regardless of inherited permissions.

## Caching

Permission tuples are cached in Redis with a 5-minute TTL. Cache invalidation happens on:
- User permission changes (immediate invalidation)
- Source system sync (on next connector refresh, typically every 15 minutes)
- Admin override (immediate invalidation)

## Sensitivity Levels

Documents have a sensitivity field: `public`, `internal`, `confidential`, `restricted`. The context engine can filter by sensitivity level in addition to user-specific permissions. This is useful for use cases like: "retrieve context but exclude confidential documents" for a lower-trust AI workflow.

## Known Limitations

- Group nesting is limited to 3 levels deep (performance constraint)
- Permission checks add ~5-8ms to each query at current scale
- The Salesforce connector doesn't yet support fine-grained record-level permissions (planned for Q4)
