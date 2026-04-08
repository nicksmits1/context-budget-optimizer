---
title: "CI/CD Pipeline Documentation"
department: "engineering"
doc_type: "technical"
created: "2025-06-01"
sensitivity: "internal"
---

# CI/CD Pipeline Documentation

## Overview

We use GitHub Actions for CI and ArgoCD for CD. Every push to a feature branch triggers CI. Merges to `main` trigger automatic deployment to staging. Production deployments happen twice daily via scheduled ArgoCD syncs.

## CI Pipeline (GitHub Actions)

### On Pull Request
1. **Lint & Format:** `ruff check` and `ruff format --check` for Python, `eslint` for TypeScript
2. **Unit Tests:** `pytest` with 80% minimum coverage threshold
3. **Integration Tests:** Spin up a PostgreSQL + Redis test environment via Docker Compose, run API integration tests
4. **Security Scan:** Snyk for dependency vulnerabilities, Semgrep for code patterns
5. **Build:** Docker image build (no push, just verify it builds)

Average CI time: 8 minutes. Target: <10 minutes.

### On Merge to Main
1. All PR checks run again
2. Docker images built and pushed to ECR with `main-{sha}` tag
3. ArgoCD application manifest updated with new image tag
4. Staging deployment triggers automatically

## CD Pipeline (ArgoCD)

### Staging
- Auto-sync enabled: any change to the staging application manifests deploys immediately
- Health checks run after deploy (HTTP readiness probes)
- Slack notification to #deploys on success/failure

### Production
- Syncs run at 10:00 AM PT and 3:00 PM PT (configurable via cron in ArgoCD)
- Requires the staging deployment to be healthy for at least 2 hours
- Canary deployment: new version serves 10% of traffic for 15 minutes before full rollout
- Automatic rollback if error rate exceeds 2% during canary

## Hotfix Process

For urgent production fixes:
1. Create a branch from `main`, implement fix, open PR with `[HOTFIX]` prefix
2. Get expedited review (1 reviewer, can be any senior engineer)
3. Merge to `main`
4. Manually trigger production sync in ArgoCD (bypasses the 2-hour staging soak)
5. Monitor closely for 30 minutes post-deploy

## Environment Variables

Secrets are stored in AWS Secrets Manager and injected into pods via External Secrets Operator. Never commit secrets to the repo. For local development, use the `.env.example` template and populate with dev credentials from 1Password.
