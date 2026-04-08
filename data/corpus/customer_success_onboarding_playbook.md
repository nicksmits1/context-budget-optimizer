---
title: "Customer Onboarding Playbook"
department: "customer_success"
doc_type: "playbook"
created: "2025-04-15"
sensitivity: "internal"
---

# Customer Onboarding Playbook

## Goal

Get every new customer to their "aha moment" within 14 days of contract signing. The aha moment: running a query against their own data and getting a useful, contextual answer from an AI assistant.

## Onboarding Timeline

### Day 1-2: Kickoff
- Send welcome email with account setup instructions
- Schedule kickoff call with customer champion and IT contact
- In kickoff: align on success criteria, identify top 3 data sources to connect first

### Day 3-7: Data Source Connection
- CSM guides the customer through connecting their first 3 data sources
- Technical support available via dedicated Slack channel (Enterprise) or email (Mid-Market)
- Target: first data source connected and indexed within 48 hours of kickoff
- Common blockers: SSO configuration, firewall allowlisting, connector permissions

### Day 8-10: Validation
- Run test queries together with the customer to validate retrieval quality
- Fine-tune connector settings (folder filters, file type filters, refresh frequency)
- Connect additional data sources if the initial three went smoothly

### Day 11-14: Rollout
- Help customer create an internal announcement about the tool
- Provide training materials (video walkthrough, cheat sheet)
- Set up the admin dashboard for the customer's IT admin
- Schedule a 30-day check-in call

## Health Metrics to Track

| Metric | Healthy | At Risk |
|--------|---------|---------|
| Data sources connected | 3+ | <2 |
| Days to first query | <7 | >14 |
| Weekly active users (week 3) | >30% of seats | <10% of seats |
| Queries per user per week | >5 | <2 |
| CSM engagement (calls) | 2+ in first month | 0 after kickoff |

## Common Failure Modes

1. **Champion leaves:** If the internal champion changes roles or leaves, onboarding stalls. Identify a secondary champion during kickoff.
2. **IT blockers:** Firewall rules, SSO misconfig, or long approval chains. Escalate to our solutions engineering team on day 3 if no data source is connected.
3. **Low query quality:** If the customer's documents are poorly structured or mostly PDFs with scanned images, retrieval quality suffers. Offer OCR enhancement and document structure recommendations.
4. **Scope creep:** Customer wants to connect 15 data sources in week 1. Focus on the top 3, get the aha moment, then expand.
