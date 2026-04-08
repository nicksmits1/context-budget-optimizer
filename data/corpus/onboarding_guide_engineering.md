---
title: "Engineering Onboarding Guide"
department: "engineering"
doc_type: "guide"
created: "2025-08-15"
sensitivity: "internal"
---

# Engineering Onboarding Guide

Welcome to the engineering team! This guide will get you up and running in your first two weeks.

## Week 1: Setup & Orientation

### Day 1
- IT will provision your laptop (MacBook Pro M3) and accounts (GitHub, AWS, Slack, Datadog, Jira)
- Set up your local development environment using the `dev-setup` repo: `git clone github.com/company/dev-setup && make bootstrap`
- Meet your onboarding buddy (assigned by your manager)

### Day 2-3
- Complete the Architecture Deep Dive self-paced course in Confluence (takes ~4 hours)
- Read the Engineering Architecture Overview doc
- Set up local Kubernetes (minikube) and deploy the platform locally: `make deploy-local`
- Get access to the staging environment and make a test API call to the Context Engine

### Day 4-5
- Pick up your first starter ticket from the "Good First Issue" board in Jira
- Expected scope: small bug fix or minor feature addition, typically 1-2 days of work
- Your buddy will review your first PR. Target: ship your first commit by end of Week 1

## Week 2: Deep Dives & Team Integration

- Attend team stand-up, sprint planning, and retro (your manager will add you to calendar invites)
- Schedule 1:1s with your team lead, product manager, and 2-3 team members
- Complete the Security Training module in KnowBe4 (mandatory, takes ~1 hour)
- Read the Incident Response Plan and join the on-call rotation shadow for one week
- Start working on your first full-sized ticket

## Development Practices

- **Git workflow:** Feature branches off `main`, squash-merge PRs, conventional commit messages
- **Code review:** All PRs require 1 approval. For critical paths (auth, permissions, billing), require 2 approvals
- **Testing:** Minimum 80% coverage for new code. Integration tests required for API endpoints
- **Deployments:** Continuous deployment to staging. Production deploys happen twice daily (10am and 3pm PT) via ArgoCD
- **On-call:** Engineers join the rotation after their first month. Week-long shifts, PagerDuty for alerts

## Key Repos

| Repo | Description | Language |
|------|-------------|----------|
| `context-engine` | Core retrieval and context serving | Python |
| `auth-service` | Authentication and authorization | Go |
| `web-app` | Customer-facing dashboard | TypeScript/React |
| `connectors` | Data source integrations | Python |
| `infra` | Terraform and Helm charts | HCL/YAML |

## Who to Ask

- Codebase questions: Your buddy or the #engineering Slack channel
- Infrastructure/deploy issues: #platform-eng
- Product questions: Your team's PM
- HR/benefits: #ask-hr
