---
title: "Product Roadmap H2 2025"
department: "product"
doc_type: "roadmap"
created: "2025-07-01"
sensitivity: "confidential"
---

# Product Roadmap — H2 2025

## Theme: Enterprise Readiness & AI-Native Workflows

Our H2 roadmap focuses on three pillars: making the platform enterprise-grade, deepening AI integrations, and reducing time-to-value for new customers.

## P0 — Must Ship

### Advanced Permissions (Q3)
Ship granular document-level and field-level permissions. Support for permission inheritance from source systems (Google Drive ACLs, Confluence spaces). This is the #1 blocker for three enterprise deals in the pipeline worth $1.2M combined ARR.

### Context Budget API (Q3-Q4)
Expose a public API that lets developers set token budgets for context retrieval. The API returns optimized context within the budget, balancing relevance, diversity, and recency. This is the core differentiator — no other vendor offers this level of control.

### SOC 2 Type II Certification (Q3)
Complete the audit and obtain certification. Required for financial services customers. Audit is already underway with Vanta.

## P1 — Should Ship

### Agentic Workflow Support (Q4)
Allow AI agents to iteratively query the context engine, refining their retrieval as they work through multi-step tasks. This requires a stateful session API and support for feedback loops where the agent can signal which context was useful.

### Connector Marketplace (Q4)
Launch a self-serve marketplace where third-party developers can publish data source connectors. Start with 5 partner-built connectors (Jira, HubSpot, Zendesk, Box, SharePoint).

### Analytics Dashboard (Q4)
Give admins visibility into context usage: which documents are retrieved most, which queries fail to find relevant context, and per-team usage breakdowns.

## P2 — Nice to Have

### On-Prem Deployment Option
Package the platform for on-prem deployment (Docker Compose + Helm). Several healthcare and government prospects require this. Estimated effort: 6-8 weeks of platform engineering work.

### Multi-Language Support
Extend embedding and retrieval to support non-English documents. Priority languages: Spanish, French, German, Japanese. Requires multilingual embedding models and language-aware chunking.

## Success Metrics

- Ship all P0 items by end of Q3
- Close 5+ enterprise deals unblocked by permissions and SOC 2
- Context Budget API adopted by 20+ customers within 60 days of launch
- Reduce median TTFT by 30% through context optimization improvements
