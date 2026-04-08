---
title: "Security Incident Response Plan"
department: "security"
doc_type: "policy"
created: "2025-03-15"
sensitivity: "internal"
---

# Security Incident Response Plan

## Severity Levels

**SEV-1 (Critical):** Active data breach, production system compromise, or customer data exposure. Response time: 15 minutes. Incident commander is the on-call security engineer + VP of Engineering.

**SEV-2 (High):** Vulnerability with known exploit in production, unauthorized access attempt detected, or third-party vendor breach affecting our data. Response time: 1 hour.

**SEV-3 (Medium):** Vulnerability identified but not yet exploitable, suspicious activity in logs, or failed penetration test finding. Response time: 24 hours.

**SEV-4 (Low):** Policy violations, minor misconfigurations, or informational security advisories. Response time: 1 week.

## Response Process

### 1. Detection & Triage
All security alerts funnel through the #security-alerts Slack channel and PagerDuty. The on-call security engineer triages within the response time SLA and assigns a severity level.

### 2. Containment
For SEV-1 and SEV-2: immediately isolate affected systems. This may include revoking API keys, blocking IPs at the WAF level, or taking a service offline. Document all containment actions in the incident timeline.

### 3. Investigation
Gather logs from Datadog, CloudTrail, and application audit logs. Determine root cause, blast radius, and whether customer data was accessed. For data breaches, engage outside counsel immediately.

### 4. Remediation
Fix the root cause. Deploy patches through the normal CI/CD pipeline (expedited review for SEV-1). Update WAF rules, rotate credentials, and patch affected systems.

### 5. Communication
- **Internal:** Post updates to #security-incidents every 30 minutes during active SEV-1/2 incidents
- **Customers:** If customer data is affected, notify impacted customers within 72 hours per our DPA commitments
- **Regulatory:** GDPR notification within 72 hours if EU personal data is involved

### 6. Post-Mortem
Conduct a blameless post-mortem within 5 business days. Document findings in Confluence under Security > Post-Mortems. Required sections: timeline, root cause, impact, remediation, and preventive measures.

## Escalation Contacts

| Role | Primary | Backup |
|------|---------|--------|
| Security Lead | Sarah Chen | Marcus Williams |
| VP Engineering | David Park | Lisa Morrison |
| Legal Counsel | Jennifer Adams | External: Wilson & Associates |
| Comms/PR | Michael Torres | Rachel Kim |

## Annual Testing

We conduct tabletop exercises quarterly and a full red team engagement annually. The next red team exercise is scheduled for November 2025 with CrowdStrike.
