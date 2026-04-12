# CI/CD Setup Guide

## Branch Strategy

```
main (DEV) ──promote──> staging (PRE-PROD) ──promote──> PRODUCTION
```

| Branch | Environment | Endpoint | Auto-Deploy |
|--------|-------------|----------|-------------|
| `main` | DEV | dev-api.CarbonScope.com | ✅ On push |
| `staging` | STAGING | staging-api.CarbonScope.com | ✅ On push |
| `PRODUCTION` | PRODUCTION | api.CarbonScope.com | ✅ On push |

## Workflow

1. **Development**: Work on feature branches, merge PRs to `main`
2. **Testing**: `main` auto-deploys to DEV for testing
3. **Pre-prod**: Promote `main` → `staging` when ready for QA
4. **Production**: Promote `staging` → `PRODUCTION` when approved

## GitHub Secrets (Repository Level)

All secrets are configured at the repository level:

### DEV Environment
- `AWS_DEV_HOST`: `52.24.67.100`
- `AWS_DEV_USERNAME`: `ubuntu`
- `AWS_DEV_KEY`: SSH private key for dev instance

### STAGING Environment
- `AWS_STAGING_HOST`: `54.184.54.33`
- `AWS_STAGING_USERNAME`: `ubuntu`
- `AWS_STAGING_KEY`: SSH private key for staging instance

### PRODUCTION Environment
- `AWS_PRODUCTION_HOST`: `54.148.221.72`
- `AWS_PRODUCTION_USERNAME`: `ubuntu`
- `AWS_PRODUCTION_KEY`: SSH private key for prod Lightsail
- `AWS_DEPLOYMENT_ROLE`: IAM role ARN for ECS deployment

## GitHub Environments

Three environments are configured for deployment protection:
- `dev` - No protection (auto-deploy)
- `staging` - No protection (auto-deploy)
- `production` - Add required reviewers for extra safety

## Branch Protection Rules

### `main` branch
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass (optional)
- ❌ Do not require linear history (allow merges)

### `staging` branch
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Restrict who can push: Only via promote workflow

### `PRODUCTION` branch
- ✅ Require pull request before merging
- ✅ Require approvals: 2
- ✅ Require review from code owners
- ✅ Restrict who can push: Only via promote workflow
- ✅ Lock branch (only allow promotions)

## Promoting Changes

### Option 1: Manual (GitHub UI)
1. Go to Actions → "Promote Branch"
2. Click "Run workflow"
3. Select promotion path:
   - `main → staging` (for pre-prod)
   - `staging → PRODUCTION` (for production)
4. Type "promote" to confirm
5. Click "Run workflow"

### Option 2: Scheduled (Automatic)
- Every Monday at 23:59 UTC: `staging → PRODUCTION`
- Disable in workflow if not needed

## Infrastructure Mapping

| Environment | Instance | IP | Tunnel ID |
|-------------|----------|-----|-----------|
| DEV | carbonscope-dev | 52.24.67.100 | 3a533a53-67d0-487c-b716-261c863270ee |
| STAGING | carbonscope-staging | 54.184.54.33 | 503813f5-2426-401a-b72f-15bd11d4b4ba |
| PRODUCTION | carbonscope-prod | 54.148.221.72 | f4125d84-33d5-424d-ae6b-2b84b790392b |
| PRODUCTION (ECS) | carbonscope-ecs | ALB | N/A |

## Pulumi Stacks

```bash
# View stack outputs
cd infra/environments/dev && pulumi stack output
cd infra/environments/staging && pulumi stack output
cd infra/environments/prod && pulumi stack output
```

Pulumi Cloud: https://app.pulumi.com/CarbonScope
