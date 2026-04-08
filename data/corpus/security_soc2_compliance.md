---
title: "SOC 2 Compliance Status"
department: "security"
doc_type: "report"
created: "2025-09-01"
sensitivity: "internal"
---

# SOC 2 Type II Compliance Status

## Overview

We are pursuing SOC 2 Type II certification, which requires demonstrating that security controls are not only designed properly (Type I) but have been operating effectively over a minimum 6-month observation period.

Audit firm: Deloitte
Observation period: March 1 - August 31, 2025
Expected report delivery: October 2025

## Trust Service Criteria Status

### Security (Common Criteria) — ON TRACK
- Access controls: Role-based access implemented across all systems ✓
- Network security: WAF, VPN, network segmentation all in place ✓
- Encryption: At-rest (AES-256) and in-transit (TLS 1.3) ✓
- Vulnerability management: Weekly Snyk scans, quarterly pen tests ✓
- Incident response: Plan documented and tested ✓

### Availability — ON TRACK
- 99.95% uptime SLA for enterprise customers
- Actual uptime during observation: 99.97%
- DR plan: multi-AZ deployment, automated failover tested monthly
- Backup: daily database backups, 30-day retention, tested quarterly

### Confidentiality — ON TRACK
- Data classification policy in place (public, internal, confidential)
- Document-level access controls in the Context Engine
- Tenant data isolation verified by third-party pen test
- Data retention and deletion procedures documented

### Processing Integrity — MINOR GAP
- One finding: the embedding pipeline doesn't currently log checksums for input documents. This means we can't cryptographically verify that the indexed content matches the source.
- Remediation: Add SHA-256 checksums to the ingestion pipeline. Engineering ticket filed (PLAT-4521), target completion: September 15.

### Privacy — ON TRACK
- Privacy policy published and reviewed by legal
- Data Processing Agreement template available for all customers
- GDPR data subject request workflow implemented and tested
- No personal data used for model training

## Outstanding Items

1. Complete the checksum remediation (PLAT-4521)
2. Final evidence collection for August
3. Management assertion letter (CFO to sign)
4. Deloitte on-site visit scheduled for September 18-19

## Impact

SOC 2 certification is a blocker for 3 enterprise deals worth $1.2M combined ARR. It's also a prerequisite for the financial services vertical where 5 prospects are waiting for certification before proceeding with evaluation.
