---
title: "Analytics Dashboard Requirements"
department: "product"
doc_type: "requirements"
created: "2025-08-01"
sensitivity: "internal"
---

# Analytics Dashboard — Product Requirements

## Problem Statement

Admin users have no visibility into how their team uses the platform. They can't answer basic questions like: "Which data sources are most queried?", "Which queries fail to find relevant context?", or "How much is each team using the product?"

This lack of visibility makes it hard for champions to justify the investment and for CSMs to identify at-risk accounts.

## User Personas

- **Admin:** Wants to see org-wide usage metrics, manage team permissions, and export reports
- **Team Lead:** Wants to see their team's usage and identify knowledge gaps
- **CSM (internal):** Wants health score inputs and early warning signals for churn

## Requirements

### P0 — Must Have
1. **Usage Overview:** Total queries, unique users, queries per day (time series chart)
2. **Top Queries:** Most common queries across the org (anonymized where needed)
3. **Data Source Analytics:** Queries per data source, most-retrieved documents, coverage gaps
4. **Failed Queries:** Queries where no relevant context was found (low similarity scores)
5. **Per-Team Breakdown:** Usage metrics broken down by team/department

### P1 — Should Have
6. **Context Budget Analytics:** Distribution of token budgets used, strategy selection frequency
7. **Latency Metrics:** p50/p95/p99 retrieval latency over time
8. **Export:** CSV export for all tables and charts
9. **Alerts:** Configurable alerts for usage drops (potential churn signal)

### P2 — Nice to Have
10. **Query Clustering:** Automatically group similar queries to identify common themes
11. **A/B Testing Dashboard:** Compare context strategies side-by-side for specific queries
12. **API Access:** Expose analytics data via API for custom dashboards

## Design Notes

- Use our existing charting library (Recharts)
- Aggregate data hourly, store in a dedicated analytics table (not the main transactional DB)
- Respect permissions: admins see org-wide, team leads see their team only
- Data retention: 90 days of detailed data, 1 year of aggregated data

## Success Metrics

- 60% of admin users view the dashboard at least monthly
- CSMs use analytics data in 80% of QBR presentations
- Failed query rate provides actionable signal that leads to 5+ new data source connections per quarter
