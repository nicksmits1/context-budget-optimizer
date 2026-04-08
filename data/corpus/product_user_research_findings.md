---
title: "User Research Findings — Context Budget Feature"
department: "product"
doc_type: "report"
created: "2025-07-20"
sensitivity: "internal"
---

# User Research Findings — Context Budget Feature

## Study Overview

Conducted 12 user interviews with developer users (7 from enterprise accounts, 5 from mid-market) to understand how they think about context management and what controls they want.

## Key Findings

### 1. Developers Want Token Budget Control
9 out of 12 participants said they want to specify a token budget for context retrieval. The main reason: they're building apps with specific cost constraints and need predictable LLM input sizes.

"Right now I retrieve 20 chunks and hope it fits. If it doesn't, I truncate from the end, which is the worst possible strategy." — Developer at a Series B startup

### 2. Quality vs Speed is the Core Tradeoff
Participants described two usage modes:
- **Interactive (chat):** Latency is king. Users expect responses in <2 seconds. They'll sacrifice some context quality for speed.
- **Batch (reports, analysis):** Quality is king. Users will wait 10+ seconds if the answer is more comprehensive and accurate.

Most want a simple knob: fast vs thorough. Under the hood, this maps to different context budget strategies.

### 3. Metadata Awareness Matters for Enterprise
Enterprise users care deeply about which documents are included in context:
- Recency: "Don't give me the 2023 policy — I need the current one"
- Source authority: "Board-approved documents should rank higher than Slack messages"
- Permissions: "If someone on my team queries this, they shouldn't see documents they don't have access to"

### 4. Transparency Builds Trust
8 out of 12 participants want to see which documents contributed to an answer. Not just citations — they want to understand the selection process. "Why did the system choose these 5 chunks out of 50 candidates?"

### 5. Summary/Compression is Controversial
Mixed reactions to the idea of summarizing context before sending to the LLM:
- Pro: "If it means I can fit more relevant info into the budget, yes"
- Con: "Summarization loses nuance. I'd rather have fewer full chunks than many summarized ones"
- Consensus: Make it opt-in, not default

## Recommendations for Product

1. Default to budget-aware top-k (simple, fast, predictable)
2. Offer MMR as a "diversity" toggle for broad queries
3. Make importance weighting configurable per customer (they all weight metadata differently)
4. Summary strategy should be opt-in via the API, clearly labeled as "experimental"
5. Return chunk selection metadata in every response for transparency
