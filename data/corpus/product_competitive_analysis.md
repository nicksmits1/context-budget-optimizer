---
title: "Competitive Analysis 2025"
department: "product"
doc_type: "report"
created: "2025-05-15"
sensitivity: "confidential"
---

# Competitive Analysis — 2025

## Market Landscape

The enterprise knowledge management and AI context space is rapidly evolving. We track three categories of competitors: direct competitors, adjacent players, and build-vs-buy alternatives.

## Direct Competitors

### Glean
- **Funding:** $360M total, Series D at $2.2B valuation
- **Strengths:** Polished UX, strong Google Workspace integration, large sales team
- **Weaknesses:** Closed ecosystem, no public API, limited customization, treats context as a black box
- **Our edge:** API-first approach, context budget control, developer tools

### Guru
- **Funding:** $90M total
- **Strengths:** Simple wiki-like UX, good for non-technical teams, Slack integration
- **Weaknesses:** Not really an AI-native platform, limited to structured knowledge bases, no document ingestion from arbitrary sources
- **Our edge:** We handle unstructured data, multi-source context, and serve it programmatically

### Dashworks
- **Funding:** $7M Seed
- **Strengths:** Fast-moving startup, good AI chat interface
- **Weaknesses:** Early stage, limited enterprise features, no permissions model
- **Our edge:** Enterprise readiness (SOC 2, permissions, SSO), scale, and funding

## Adjacent Players

### Notion AI / Confluence AI
These are adding AI features to existing productivity tools. They only search within their own platform, which limits usefulness for companies using 10+ SaaS tools. We complement rather than compete with these.

### Vector Database Companies (Pinecone, Weaviate)
Infrastructure-level tools. They provide the building blocks but don't solve the full context management problem. Some customers try to build in-house using these and eventually switch to us when they realize the complexity of connectors, permissions, and optimization.

## Win/Loss Analysis (Q1-Q2 2025)

| Competitor | Wins | Losses | Win Rate |
|-----------|------|--------|----------|
| Glean | 8 | 12 | 40% |
| Guru | 6 | 2 | 75% |
| In-house | 11 | 7 | 61% |
| No decision | - | 15 | - |

Against Glean, we win on technical depth and lose on brand recognition. The biggest loss category is "no decision" — prospects that stall in evaluation. We need to reduce friction in the POC process.

## Strategic Recommendations

1. Double down on developer experience — this is where Glean can't follow us
2. Publish benchmarks showing our context optimization vs naive RAG approaches
3. Build case studies with 3 flagship enterprise customers by Q4
4. Consider strategic partnerships with vector DB companies rather than competing
