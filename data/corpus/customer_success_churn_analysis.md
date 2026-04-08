---
title: "Customer Churn Analysis Q2-Q3 2025"
department: "customer_success"
doc_type: "report"
created: "2025-10-01"
sensitivity: "internal"
---

# Customer Churn Analysis — Q2-Q3 2025

## Summary

We lost 38 customers in Q2-Q3 2025, representing $2.1M in churned ARR. Gross retention for the period was 91.2%. While this is above our 90% target, the trend is concerning in the SMB segment where retention dropped to 82%.

## Churn Breakdown by Segment

| Segment | Customers Lost | ARR Lost | Retention Rate |
|---------|---------------|----------|----------------|
| Enterprise | 2 | $380K | 97.8% |
| Mid-Market | 11 | $820K | 91.0% |
| SMB | 25 | $900K | 82.0% |

## Root Causes

Based on exit interviews and usage data analysis, the top churn reasons were:

1. **Insufficient ROI perceived (34%):** Customers couldn't quantify the value. Most common in companies that connected fewer than 3 data sources — they never hit the "aha moment" of cross-source context.

2. **Integration complexity (22%):** Connector setup was too painful. Particularly for Salesforce and custom API integrations. Average time to first value was 3.2 weeks for churned customers vs 1.1 weeks for retained ones.

3. **Budget cuts (19%):** AI/ML budgets were reduced across several industries in Q2. Not much we can do here except prove ROI faster.

4. **Switched to competitor (14%):** Lost 5 customers to Glean and 3 to internal solutions. Common feedback: Glean's out-of-the-box experience was simpler for non-technical users.

5. **Product gaps (11%):** Missing features cited: on-prem deployment (3 customers), multi-language support (2), advanced analytics (2).

## Retention Strategies

### Already Implemented
- **Health Score Model:** Launched a customer health score in Gainsight based on login frequency, query volume, and data source count. CSMs now get alerts when health drops below 70.
- **Onboarding Revamp:** Reduced time-to-first-value from 2.5 weeks to 1.4 weeks with guided setup wizards and pre-built connector templates.

### Proposed
- **Quarterly Business Reviews:** Mandate QBRs for all customers >$50K ARR. Present usage metrics and ROI calculations.
- **Free Connector Setup:** Offer white-glove connector setup for the first 5 data sources on Enterprise plans.
- **SMB Self-Serve Improvements:** Invest in the PLG motion. If we can't reduce SMB churn to 88%+ by Q1 2026, recommend sunsetting the segment.

## Expansion Revenue

Despite churn, net revenue retention was 112% in Q2 and 118% in Q3, driven by seat expansion in enterprise accounts. The top 10 enterprise accounts expanded by an average of 34% in the period.
