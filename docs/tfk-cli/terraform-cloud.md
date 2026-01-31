# tfk Terraform Cloud Guide

Complete guide for integrating tfk with Terraform Cloud and Terraform Enterprise.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Workspace Management](#workspace-management)
4. [Run Management](#run-management)
5. [Variable Management](#variable-management)
6. [State Management](#state-management)
7. [Policy Enforcement](#policy-enforcement)
8. [VCS Integration](#vcs-integration)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

---

## Overview

tfk provides native integration with Terraform Cloud (TFC) and Terraform Enterprise (TFE), allowing you to:

- Manage workspaces programmatically
- Trigger and monitor runs
- Manage variables securely
- Download and upload state
- Integrate with VCS providers
- Enforce policies with Sentinel

### Terraform Cloud vs Enterprise

| Feature | Terraform Cloud | Terraform Enterprise |
|---------|-----------------|----------------------|
| Hosting | SaaS (app.terraform.io) | Self-hosted |
| Authentication | API tokens | API tokens, SAML, SSO |
| API Endpoint | `app.terraform.io` | Custom hostname |
| Features | Standard features | Additional enterprise features |

---

## Authentication

### API Token Types

| Token Type | Scope | Use Case |
|------------|-------|----------|
| User Token | User's permissions | Personal automation |
| Team Token | Team's permissions | Team automation |
| Organization Token | Organization-wide | CI/CD pipelines |

### Login Methods

#### Interactive Login

```bash
# Login to Terraform Cloud
tfk cloud login

# Login to Terraform Enterprise
tfk cloud login --hostname=terraform.company.com
```

This opens a browser for authentication and stores the token securely.

#### Token-Based Login

```bash
# Using CLI argument
tfk cloud login --token=<your-token>

# Using environment variable
export TFC_TOKEN=<your-token>
tfk cloud workspaces list
```

#### Configuration File

```yaml
# tfk.yaml
cloud:
  enabled: true
  hostname: app.terraform.io
  organization: my-org
  # Token is read from TFC_TOKEN env var or credential store
```

### Credential Storage

Credentials are stored in order of preference:

1. **Environment Variable**: `TFC_TOKEN`
2. **tfk Credential Store**: `~/.tfk/credentials.json` (encrypted)
3. **Terraform Credentials**: `~/.terraform.d/credentials.tfrc.json`

```bash
# View stored credentials (masked)
tfk cloud credentials show

# Remove stored credentials
tfk cloud logout
```

### Verifying Authentication

```bash
# Check current authentication status
tfk cloud whoami
```

Output:
```
Authenticated to Terraform Cloud

  Hostname:     app.terraform.io
  Organization: my-org
  User:         john@example.com
  Teams:        platform-team, developers
  Token Type:   user
  Expires:      Never
```

---

## Workspace Management

### List Workspaces

```bash
# List all workspaces
tfk cloud workspaces list

# List with search filter
tfk cloud workspaces list --search=prod

# List with tag filter
tfk cloud workspaces list --tag=production

# JSON output
tfk cloud workspaces list --format=json
```

Output:
```
Workspaces in organization 'my-org':

  NAME                 EXECUTION    LAST RUN        STATUS
  myapp-dev            remote       2 hours ago     applied
  myapp-staging        remote       1 day ago       applied
  myapp-prod           remote       3 days ago      applied
  infrastructure       remote       1 week ago      applied

Total: 4 workspaces
```

### Show Workspace Details

```bash
tfk cloud workspaces show myapp-prod
```

Output:
```
Workspace: myapp-prod

  ID:              ws-abc123xyz
  Organization:    my-org
  Execution Mode:  remote
  Auto Apply:      false
  Terraform:       ~> 1.5.0
  Working Dir:     /infrastructure

VCS Repository:
  Provider:        github
  Repository:      my-org/infrastructure
  Branch:          main
  Path:            /terraform/prod

Current Run:
  ID:              run-xyz789
  Status:          applied
  Created:         2024-01-15 10:30:00 UTC
  Message:         Update security groups

Variables:
  environment      terraform    dev
  region           terraform    us-east-1
  AWS_ACCESS_KEY   env          (sensitive)
  AWS_SECRET_KEY   env          (sensitive)

Tags:
  production, aws, us-east-1
```

### Create Workspace

```bash
# Basic creation
tfk cloud workspaces create myapp-staging \
  --organization=my-org

# With configuration
tfk cloud workspaces create myapp-staging \
  --organization=my-org \
  --description="Staging environment for myapp" \
  --execution-mode=remote \
  --terraform-version="~> 1.5.0" \
  --working-directory=/infrastructure \
  --auto-apply=false \
  --tags=staging,aws

# With VCS integration
tfk cloud workspaces create myapp-staging \
  --organization=my-org \
  --vcs-provider=github \
  --vcs-repo=my-org/infrastructure \
  --vcs-branch=main \
  --vcs-path=/terraform/staging
```

### Update Workspace

```bash
# Update settings
tfk cloud workspaces update myapp-staging \
  --auto-apply=true \
  --terraform-version="1.6.0"

# Update VCS settings
tfk cloud workspaces update myapp-staging \
  --vcs-branch=develop

# Add tags
tfk cloud workspaces update myapp-staging \
  --add-tags=updated,reviewed

# Remove tags
tfk cloud workspaces update myapp-staging \
  --remove-tags=deprecated
```

### Delete Workspace

```bash
# Delete (requires confirmation)
tfk cloud workspaces delete myapp-old

# Force delete
tfk cloud workspaces delete myapp-old --force
```

### Lock/Unlock Workspace

```bash
# Lock workspace
tfk cloud workspaces lock myapp-prod \
  --reason="Maintenance window"

# Unlock workspace
tfk cloud workspaces unlock myapp-prod
```

---

## Run Management

### Understanding Run States

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Run Lifecycle                                   │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌──────────────┐     ┌──────────┐     ┌─────────────┐
  │ pending  │────>│ plan_queued  │────>│ planning │────>│   planned   │
  └──────────┘     └──────────────┘     └──────────┘     └──────┬──────┘
                                                                │
       ┌────────────────────────────────────────────────────────┤
       │                                                        │
       │   ┌────────────────┐     ┌──────────────────┐          │
       │   │ cost_estimated │<────│ cost_estimating  │<─────────┤
       │   └───────┬────────┘     └──────────────────┘          │
       │           │                                            │
       │   ┌───────▼────────┐     ┌──────────────────┐          │
       │   │ policy_checked │<────│ policy_checking  │<─────────┤
       │   └───────┬────────┘     └──────────────────┘          │
       │           │                                            │
       │           ▼                                            │
       │   ┌───────────────┐                                    │
       └──>│   confirmed   │ (manual approval or auto-apply)    │
           └───────┬───────┘                                    │
                   │                                            │
           ┌───────▼───────┐     ┌─────────────┐                │
           │ apply_queued  │────>│  applying   │                │
           └───────────────┘     └──────┬──────┘                │
                                        │                       │
                                 ┌──────▼──────┐                │
                                 │   applied   │                │
                                 └─────────────┘                │
                                                                │
  Terminal States:                                              │
  ┌───────────┐  ┌───────────┐  ┌───────────┐                  │
  │ discarded │  │  errored  │  │ canceled  │<─────────────────┘
  └───────────┘  └───────────┘  └───────────┘
```

### List Runs

```bash
# List recent runs
tfk cloud runs list --workspace=myapp-prod

# Filter by status
tfk cloud runs list --workspace=myapp-prod --status=applied

# Limit results
tfk cloud runs list --workspace=myapp-prod --limit=5
```

Output:
```
Runs for workspace 'myapp-prod':

  ID             STATUS     CREATED              MESSAGE
  run-xyz789     applied    2024-01-15 10:30    Update security groups
  run-abc456     applied    2024-01-14 15:00    Add new instance
  run-def123     discarded  2024-01-14 14:30    Test changes
  run-ghi890     applied    2024-01-13 09:00    Initial deployment

Total: 4 runs
```

### Show Run Details

```bash
tfk cloud runs show run-xyz789
```

Output:
```
Run: run-xyz789

  Workspace:       myapp-prod
  Status:          applied
  Created:         2024-01-15 10:30:00 UTC
  Started:         2024-01-15 10:30:05 UTC
  Finished:        2024-01-15 10:35:42 UTC
  Duration:        5m 37s

  Message:         Update security groups
  Source:          tfe-ui
  Triggered By:    john@example.com

Plan Summary:
  Resources:       12 total
  To Add:          2
  To Change:       1
  To Destroy:      0

Apply Summary:
  Added:           2
  Changed:         1
  Destroyed:       0

Cost Estimation:
  Monthly:         $523.00 (+$45.00)
  Hourly:          $0.72 (+$0.06)
```

### Trigger Run

```bash
# Basic run
tfk cloud runs trigger --workspace=myapp-prod

# With message
tfk cloud runs trigger --workspace=myapp-prod \
  --message="Deploy v1.2.3"

# Auto-apply (skip confirmation)
tfk cloud runs trigger --workspace=myapp-prod \
  --message="Hotfix" \
  --auto-apply

# Destroy run
tfk cloud runs trigger --workspace=myapp-prod \
  --destroy \
  --message="Teardown staging"

# Target specific resources
tfk cloud runs trigger --workspace=myapp-prod \
  --target=aws_instance.web \
  --target=aws_security_group.web

# Replace resources
tfk cloud runs trigger --workspace=myapp-prod \
  --replace=aws_instance.web[0]

# Plan-only (speculative)
tfk cloud runs trigger --workspace=myapp-prod \
  --plan-only
```

### Approve Run

```bash
# Apply a planned run
tfk cloud runs apply run-xyz789

# With comment
tfk cloud runs apply run-xyz789 \
  --comment="Approved by platform team"
```

### Discard Run

```bash
# Discard a planned run
tfk cloud runs discard run-xyz789

# With comment
tfk cloud runs discard run-xyz789 \
  --comment="Changes no longer needed"
```

### Cancel Run

```bash
# Cancel an in-progress run
tfk cloud runs cancel run-xyz789

# Force cancel (may leave resources in unknown state)
tfk cloud runs cancel run-xyz789 --force
```

### Wait for Run

```bash
# Wait for run to complete
tfk cloud runs wait run-xyz789

# Wait with timeout
tfk cloud runs wait run-xyz789 --timeout=1800

# Wait for specific status
tfk cloud runs wait run-xyz789 --status=planned
```

### Stream Run Logs

```bash
# Stream plan/apply logs
tfk cloud runs logs run-xyz789

# Follow mode (stream as logs appear)
tfk cloud runs logs run-xyz789 --follow

# Show only plan output
tfk cloud runs logs run-xyz789 --phase=plan

# Show only apply output
tfk cloud runs logs run-xyz789 --phase=apply
```

---

## Variable Management

### List Variables

```bash
# List all variables
tfk cloud variables list --workspace=myapp-prod

# Filter by category
tfk cloud variables list --workspace=myapp-prod --category=terraform
tfk cloud variables list --workspace=myapp-prod --category=env
```

Output:
```
Variables for workspace 'myapp-prod':

  KEY              CATEGORY    SENSITIVE    VALUE
  environment      terraform   no           prod
  region           terraform   no           us-east-1
  instance_count   terraform   no           3
  db_password      terraform   yes          (sensitive)
  AWS_ACCESS_KEY   env         yes          (sensitive)
  AWS_SECRET_KEY   env         yes          (sensitive)

Total: 6 variables
```

### Set Variable

```bash
# Set terraform variable
tfk cloud variables set --workspace=myapp-prod \
  --key=environment \
  --value=prod

# Set sensitive variable
tfk cloud variables set --workspace=myapp-prod \
  --key=db_password \
  --value=secret123 \
  --sensitive

# Set environment variable
tfk cloud variables set --workspace=myapp-prod \
  --key=AWS_REGION \
  --value=us-east-1 \
  --category=env

# Set HCL variable
tfk cloud variables set --workspace=myapp-prod \
  --key=tags \
  --value='{"env":"prod","team":"platform"}' \
  --hcl

# Set with description
tfk cloud variables set --workspace=myapp-prod \
  --key=instance_count \
  --value=3 \
  --description="Number of web instances"

# Set from file
tfk cloud variables set --workspace=myapp-prod \
  --key=ssh_public_key \
  --value-file=~/.ssh/id_rsa.pub
```

### Update Variable

```bash
# Update value
tfk cloud variables update --workspace=myapp-prod \
  --key=instance_count \
  --value=5

# Make sensitive
tfk cloud variables update --workspace=myapp-prod \
  --key=api_key \
  --sensitive=true
```

### Delete Variable

```bash
tfk cloud variables delete --workspace=myapp-prod \
  --key=old_variable
```

### Sync Variables from File

```bash
# Sync from tfvars file
tfk cloud variables sync --workspace=myapp-prod \
  --var-file=prod.tfvars

# Sync with sensitive values from env
tfk cloud variables sync --workspace=myapp-prod \
  --var-file=prod.tfvars \
  --sensitive-from-env \
  --sensitive-keys=db_password,api_key
```

### Variable Sets

```bash
# List variable sets
tfk cloud varsets list

# Show variable set
tfk cloud varsets show global-aws-credentials

# Create variable set
tfk cloud varsets create global-aws-credentials \
  --description="AWS credentials for all workspaces" \
  --global

# Add variable to set
tfk cloud varsets add-var global-aws-credentials \
  --key=AWS_ACCESS_KEY \
  --value=$AWS_ACCESS_KEY_ID \
  --category=env \
  --sensitive

# Apply to workspace
tfk cloud varsets apply global-aws-credentials \
  --workspace=myapp-prod
```

---

## State Management

### Download State

```bash
# Download current state
tfk cloud state pull --workspace=myapp-prod > state.json

# Download specific version
tfk cloud state pull --workspace=myapp-prod \
  --version=sv-abc123 > state-v1.json

# Download to file
tfk cloud state pull --workspace=myapp-prod \
  --output=terraform.tfstate
```

### List State Versions

```bash
tfk cloud state list --workspace=myapp-prod
```

Output:
```
State Versions for workspace 'myapp-prod':

  ID           SERIAL    CREATED              RUN ID
  sv-xyz789    15        2024-01-15 10:35    run-xyz789
  sv-abc456    14        2024-01-14 15:05    run-abc456
  sv-def123    13        2024-01-13 09:10    run-ghi890

Total: 3 state versions
```

### Show State Version

```bash
tfk cloud state show sv-xyz789
```

Output:
```
State Version: sv-xyz789

  Workspace:       myapp-prod
  Serial:          15
  Created:         2024-01-15 10:35:42 UTC
  Terraform:       1.5.7
  Run:             run-xyz789

Resources:
  Total:           12

  aws_instance.web[0]
  aws_instance.web[1]
  aws_instance.web[2]
  aws_security_group.web
  aws_lb.main
  ...

Outputs:
  vpc_id           = "vpc-abc123"
  load_balancer_dns = "myapp-123.elb.amazonaws.com"
```

### Upload State (Advanced)

```bash
# Upload state (use with caution)
tfk cloud state push --workspace=myapp-prod \
  --state-file=terraform.tfstate \
  --force
```

### Lock/Unlock State

```bash
# Lock state
tfk cloud state lock --workspace=myapp-prod \
  --reason="Manual state manipulation"

# Unlock state
tfk cloud state unlock --workspace=myapp-prod

# Force unlock (use with caution)
tfk cloud state unlock --workspace=myapp-prod --force
```

---

## Policy Enforcement

### Sentinel Policies

Terraform Cloud/Enterprise supports Sentinel policies for compliance.

### List Policy Sets

```bash
tfk cloud policies list
```

Output:
```
Policy Sets in organization 'my-org':

  NAME                    SCOPE       ENFORCEMENT
  security-baseline       global      hard-mandatory
  cost-controls           global      soft-mandatory
  tagging-requirements    workspace   advisory

Total: 3 policy sets
```

### Show Policy Results

```bash
tfk cloud runs policies run-xyz789
```

Output:
```
Policy Check Results for run 'run-xyz789':

  POLICY SET             POLICY                  RESULT
  security-baseline      no-public-ingress       passed
  security-baseline      encryption-required     passed
  cost-controls          monthly-limit           passed
  tagging-requirements   required-tags           failed (advisory)

Overall: passed (1 advisory failure)
```

### Override Policy (Soft-Mandatory)

```bash
tfk cloud runs override run-xyz789 \
  --comment="Approved exception for testing"
```

---

## VCS Integration

### Connecting VCS

```bash
# List VCS connections
tfk cloud vcs list

# Show VCS connection details
tfk cloud vcs show github-oauth
```

### Configure Workspace VCS

```bash
# Connect workspace to VCS
tfk cloud workspaces update myapp-prod \
  --vcs-provider=github-oauth \
  --vcs-repo=my-org/infrastructure \
  --vcs-branch=main \
  --vcs-path=/terraform/prod

# Set trigger patterns
tfk cloud workspaces update myapp-prod \
  --vcs-trigger-patterns="/terraform/prod/**/*" \
  --vcs-trigger-patterns="/modules/**/*"

# Enable/disable auto-trigger
tfk cloud workspaces update myapp-prod \
  --vcs-auto-trigger=true
```

### Manual VCS Trigger

```bash
# Trigger run from specific commit
tfk cloud runs trigger --workspace=myapp-prod \
  --vcs-commit=abc123def

# Trigger run from branch
tfk cloud runs trigger --workspace=myapp-prod \
  --vcs-branch=feature/new-feature
```

---

## API Reference

### Direct API Access

```bash
# Make direct API call
tfk cloud api GET /organizations/my-org/workspaces

# POST with data
tfk cloud api POST /workspaces/ws-abc123/runs \
  --data='{"data":{"type":"runs","attributes":{"message":"API run"}}}'

# With query parameters
tfk cloud api GET /organizations/my-org/workspaces \
  --query="search[name]=prod" \
  --query="page[size]=10"
```

### API Response Formats

```bash
# JSON output (default)
tfk cloud workspaces list --format=json

# Table output
tfk cloud workspaces list --format=table

# YAML output
tfk cloud workspaces list --format=yaml

# Raw API response
tfk cloud workspaces list --raw
```

### Pagination

```bash
# First page
tfk cloud workspaces list --page=1 --page-size=20

# All pages (automatically paginated)
tfk cloud workspaces list --all
```

---

## Troubleshooting

### Authentication Issues

```
Error: Unauthorized (401)
  The API token is invalid or expired.
```

**Solution:**
```bash
# Re-authenticate
tfk cloud logout
tfk cloud login

# Or check token
echo $TFC_TOKEN | cut -c1-10
```

### Rate Limiting

```
Error: Rate limit exceeded (429)
  Too many requests. Retry after 60 seconds.
```

**Solution:**
```bash
# tfk automatically handles rate limiting
# For manual retries:
tfk cloud workspaces list --retry-delay=60
```

### Workspace Locked

```
Error: Workspace locked
  The workspace is currently locked by another process.
```

**Solution:**
```bash
# Check lock status
tfk cloud workspaces show myapp-prod

# Unlock if safe
tfk cloud workspaces unlock myapp-prod

# Force unlock (use with caution)
tfk cloud workspaces unlock myapp-prod --force
```

### Run Errors

```
Error: Run failed
  The run encountered an error during planning.
```

**Solution:**
```bash
# View run logs
tfk cloud runs logs run-xyz789

# View detailed error
tfk cloud runs show run-xyz789 --verbose
```

### State Lock Errors

```
Error: Error acquiring state lock
  State is locked by another operation.
```

**Solution:**
```bash
# Check state lock
tfk cloud state show --workspace=myapp-prod

# Force unlock (use with caution)
tfk cloud state unlock --workspace=myapp-prod --force
```

### Debug Mode

```bash
# Enable debug output
export TFK_LOG_LEVEL=debug
tfk cloud workspaces list

# Verbose API responses
tfk cloud workspaces list --verbose

# Show request/response details
tfk cloud workspaces list --debug
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired token | Re-authenticate with `tfk cloud login` |
| 403 Forbidden | Insufficient permissions | Check token permissions, use correct token type |
| 404 Not Found | Wrong org/workspace name | Verify organization and workspace names |
| 409 Conflict | Resource already exists | Use update instead of create |
| 422 Unprocessable | Invalid request data | Check request parameters |
| 429 Rate Limited | Too many requests | Wait and retry, or reduce request frequency |

---

## Best Practices

### 1. Use Organization Tokens for CI/CD

```yaml
# CI/CD configuration
env:
  TFC_TOKEN: ${{ secrets.TFC_ORG_TOKEN }}

steps:
  - name: Trigger Terraform Run
    run: |
      tfk cloud runs trigger --workspace=myapp-prod \
        --message="Deploy from CI: ${{ github.sha }}"
```

### 2. Implement Approval Workflows

```yaml
# tfk.yaml
cloud:
  enabled: true
  organization: my-org
  runs:
    auto_apply: false  # Require manual approval

workspaces:
  environments:
    prod:
      workspace: myapp-prod
      require_approval: true
      approval:
        min_approvers: 2
```

### 3. Use Variable Sets for Shared Credentials

```bash
# Create organization-wide credentials
tfk cloud varsets create aws-credentials \
  --global \
  --description="Shared AWS credentials"

tfk cloud varsets add-var aws-credentials \
  --key=AWS_ACCESS_KEY_ID \
  --value=$AWS_ACCESS_KEY_ID \
  --category=env \
  --sensitive
```

### 4. Monitor Runs Programmatically

```python
from terraformik.cloud import TerraformCloudClient

client = TerraformCloudClient(token, organization)

# Trigger run
run = client.create_run(
    workspace_id="ws-abc123",
    message="Automated deployment"
)

# Wait for completion
run = client.wait_for_run(
    run.id,
    callback=lambda r: print(f"Status: {r.status}")
)

if run.status == "applied":
    print("Deployment successful!")
else:
    print(f"Deployment failed: {run.status}")
```

### 5. Use Workspaces for Environment Isolation

```
Organization: my-org
├── myapp-dev         (development)
├── myapp-staging     (staging)
├── myapp-prod        (production)
└── shared-services   (shared infrastructure)
```

---

## See Also

- [User Guide](./user-guide.md)
- [API Reference](./api.md)
- [Configuration Reference](./configuration.md)
- [Terraform Cloud Documentation](https://developer.hashicorp.com/terraform/cloud-docs)
