# tfk User Guide

A comprehensive guide to using the Terraformik CLI (tfk) for managing Terraform infrastructure.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Commands](#basic-commands)
4. [Working with Workspaces](#working-with-workspaces)
5. [Terraform Cloud](#terraform-cloud)
6. [Multi-Workspace Operations](#multi-workspace-operations)
7. [Using Hooks](#using-hooks)
8. [Configuration](#configuration)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Installation

### Requirements

- Python 3.8 or higher
- Terraform 1.0 or higher
- AWS CLI (for AWS backend provisioning)

### Install via pip

```bash
# Install from PyPI
pip install terraformik

# Or install from source
git clone https://github.com/wcampos/terraformik.git
cd terraformik
pip install -e .
```

### Install via pipx (Recommended)

```bash
# Install isolated CLI
pipx install terraformik

# Upgrade
pipx upgrade terraformik
```

### Verify Installation

```bash
# Check version
tfk version

# Check Terraform is accessible
tfk doctor
```

### Shell Completion

```bash
# Bash
tfk --install-completion bash

# Zsh
tfk --install-completion zsh

# Fish
tfk --install-completion fish
```

---

## Quick Start

### 1. Initialize Configuration

```bash
# Create a new tfk configuration
tfk config init

# This creates tfk.yaml with default settings
```

### 2. Provision Backend (Optional)

```bash
# Provision AWS backend (S3 + DynamoDB)
tfk provision aws \
  --app-name myapp \
  --environment dev \
  --region us-east-1
```

### 3. Initialize Terraform

```bash
# Initialize with backend configuration
tfk init --backend-config=backend.hcl

# Or use auto-detected configuration
tfk init
```

### 4. Plan Changes

```bash
# Create execution plan
tfk plan --var-file=dev.tfvars

# Save plan to file
tfk plan --var-file=dev.tfvars --out=plan.tfplan
```

### 5. Apply Changes

```bash
# Apply saved plan
tfk apply plan.tfplan

# Or plan and apply interactively
tfk apply --var-file=dev.tfvars
```

---

## Basic Commands

### Initialize (`tfk init`)

Initialize a Terraform working directory.

```bash
# Basic initialization
tfk init

# With backend configuration
tfk init --backend-config=backend.hcl

# Reconfigure backend
tfk init --reconfigure

# Upgrade providers and modules
tfk init --upgrade

# Specify working directory
tfk init --chdir=./infrastructure
```

**Options:**

| Option | Description |
|--------|-------------|
| `--backend-config` | Path to backend configuration file |
| `--reconfigure` | Reconfigure backend, ignoring saved configuration |
| `--upgrade` | Upgrade modules and plugins |
| `--chdir` | Switch to directory before running |
| `--skip-hooks` | Skip pre/post hooks |

### Plan (`tfk plan`)

Generate and show an execution plan.

```bash
# Basic plan
tfk plan

# With variable file
tfk plan --var-file=dev.tfvars

# With inline variables
tfk plan --var="environment=dev" --var="region=us-east-1"

# Save plan to file
tfk plan --out=plan.tfplan

# Target specific resources
tfk plan --target=aws_instance.web

# Plan for destruction
tfk plan --destroy

# Show detailed output
tfk plan --verbose
```

**Options:**

| Option | Description |
|--------|-------------|
| `--var-file` | Path to variable definitions file |
| `--var` | Set a variable (can be used multiple times) |
| `--out` | Save plan to file |
| `--target` | Target specific resource (can be used multiple times) |
| `--destroy` | Create plan to destroy resources |
| `--refresh-only` | Only refresh state, don't plan changes |
| `--verbose` | Show detailed output |

### Apply (`tfk apply`)

Apply Terraform changes.

```bash
# Apply with confirmation
tfk apply

# Apply saved plan
tfk apply plan.tfplan

# Auto-approve (no confirmation)
tfk apply --auto-approve

# Apply with variable file
tfk apply --var-file=prod.tfvars

# Target specific resources
tfk apply --target=aws_instance.web
```

**Options:**

| Option | Description |
|--------|-------------|
| `--auto-approve` | Skip interactive approval |
| `--var-file` | Path to variable definitions file |
| `--var` | Set a variable (can be used multiple times) |
| `--target` | Target specific resource |
| `--parallelism` | Limit concurrent operations (default: 10) |

### Destroy (`tfk destroy`)

Destroy Terraform-managed infrastructure.

```bash
# Destroy with confirmation
tfk destroy

# Auto-approve destruction
tfk destroy --auto-approve

# Target specific resources
tfk destroy --target=aws_instance.web

# With variable file
tfk destroy --var-file=dev.tfvars
```

**Options:**

| Option | Description |
|--------|-------------|
| `--auto-approve` | Skip interactive approval |
| `--var-file` | Path to variable definitions file |
| `--target` | Target specific resource |

### Format (`tfk fmt`)

Format Terraform configuration files.

```bash
# Format current directory
tfk fmt

# Format recursively
tfk fmt --recursive

# Check formatting (don't modify)
tfk fmt --check

# Show diff of changes
tfk fmt --diff

# Format specific directory
tfk fmt ./modules
```

### Validate (`tfk validate`)

Validate Terraform configuration.

```bash
# Validate configuration
tfk validate

# JSON output
tfk validate --json

# Validate specific directory
tfk validate ./modules/network
```

### Output (`tfk output`)

Display Terraform outputs.

```bash
# Show all outputs
tfk output

# Show specific output
tfk output vpc_id

# JSON format
tfk output --json

# Raw value (no quotes)
tfk output --raw vpc_id
```

---

## Working with Workspaces

Terraform workspaces allow managing multiple environments with the same configuration.

### List Workspaces

```bash
tfk workspace list
```

Output:
```
  default
* dev
  staging
  prod
```

### Create Workspace

```bash
# Create new workspace
tfk workspace new staging

# Create and switch to workspace
tfk workspace new prod
```

### Select Workspace

```bash
# Switch to workspace
tfk workspace select prod

# Show current workspace
tfk workspace show
```

### Delete Workspace

```bash
# Delete workspace (must not be current)
tfk workspace delete old-workspace

# Force delete with state
tfk workspace delete --force old-workspace
```

### Workspace-Specific Operations

```bash
# Plan for specific workspace
tfk plan --workspace=staging --var-file=staging.tfvars

# Apply to specific workspace
tfk apply --workspace=prod --var-file=prod.tfvars
```

---

## Terraform Cloud

### Authentication

```bash
# Interactive login
tfk cloud login

# Login with token
tfk cloud login --token=$TFC_TOKEN

# Login to Terraform Enterprise
tfk cloud login --hostname=terraform.company.com

# Logout
tfk cloud logout
```

### Workspace Management

```bash
# List workspaces in organization
tfk cloud workspaces list --organization=my-org

# Show workspace details
tfk cloud workspaces show my-workspace

# Create workspace
tfk cloud workspaces create my-workspace \
  --organization=my-org \
  --execution-mode=remote \
  --vcs-repo=github/my-org/my-repo

# Delete workspace
tfk cloud workspaces delete my-workspace
```

### Run Management

```bash
# List recent runs
tfk cloud runs list --workspace=my-workspace

# Trigger a new run
tfk cloud runs trigger --workspace=my-workspace \
  --message="Deploy v1.2.3"

# Trigger with auto-apply
tfk cloud runs trigger --workspace=my-workspace \
  --auto-apply

# Show run details
tfk cloud runs show run-abc123

# Apply a pending run
tfk cloud runs apply run-abc123 \
  --comment="Approved by CI"

# Discard a pending run
tfk cloud runs discard run-abc123

# Cancel an in-progress run
tfk cloud runs cancel run-abc123
```

### Variable Management

```bash
# List variables
tfk cloud variables list --workspace=my-workspace

# Set terraform variable
tfk cloud variables set \
  --workspace=my-workspace \
  --key=environment \
  --value=production

# Set sensitive variable
tfk cloud variables set \
  --workspace=my-workspace \
  --key=db_password \
  --value=secret123 \
  --sensitive

# Set environment variable
tfk cloud variables set \
  --workspace=my-workspace \
  --key=AWS_REGION \
  --value=us-east-1 \
  --category=env

# Set HCL variable
tfk cloud variables set \
  --workspace=my-workspace \
  --key=tags \
  --value='{"env":"prod","team":"platform"}' \
  --hcl

# Delete variable
tfk cloud variables delete \
  --workspace=my-workspace \
  --key=old_variable
```

### State Operations

```bash
# Download current state
tfk cloud state pull --workspace=my-workspace > state.json

# List state versions
tfk cloud state list --workspace=my-workspace

# Show specific state version
tfk cloud state show sv-abc123
```

---

## Multi-Workspace Operations

Orchestrate operations across multiple workspaces with dependency management.

### Configuration

Define workspaces in `tfk.yaml`:

```yaml
orchestration:
  workspaces:
    - name: network
      path: ./infrastructure/network
      dependencies: []

    - name: security
      path: ./infrastructure/security
      dependencies: [network]

    - name: database
      path: ./infrastructure/database
      dependencies: [network, security]

    - name: application
      path: ./infrastructure/application
      dependencies: [database]
```

### Plan Multiple Workspaces

```bash
# Plan all workspaces
tfk multi plan

# Plan specific workspaces
tfk multi plan --workspaces=network,security

# Plan with specific config
tfk multi plan --config=workspaces.yaml

# Dry run (show execution order)
tfk multi plan --dry-run
```

Output:
```
Execution Order:
  1. network (no dependencies)
  2. security (depends on: network)
  3. database (depends on: network, security)
  4. application (depends on: database)

Planning workspaces...

[1/4] network
  Plan: 5 to add, 0 to change, 0 to destroy

[2/4] security
  Plan: 3 to add, 0 to change, 0 to destroy

[3/4] database
  Plan: 2 to add, 0 to change, 0 to destroy

[4/4] application
  Plan: 8 to add, 0 to change, 0 to destroy

Summary:
  Total: 18 to add, 0 to change, 0 to destroy
```

### Apply Multiple Workspaces

```bash
# Apply all workspaces (sequential)
tfk multi apply

# Apply with parallelism
tfk multi apply --parallel=2

# Auto-approve all
tfk multi apply --auto-approve

# Stop on first failure
tfk multi apply --fail-fast

# Continue on failure
tfk multi apply --continue-on-error
```

### Check Status

```bash
# Show status of all workspaces
tfk multi status
```

Output:
```
Workspace Status:

  network      [healthy]  Last apply: 2 hours ago
  security     [healthy]  Last apply: 2 hours ago
  database     [drift]    Last apply: 1 day ago (changes detected)
  application  [healthy]  Last apply: 30 minutes ago
```

### Destroy Multiple Workspaces

```bash
# Destroy in reverse dependency order
tfk multi destroy

# Destroy specific workspaces
tfk multi destroy --workspaces=application,database
```

---

## Using Hooks

Hooks allow running validations and scripts before and after Terraform operations.

### Built-in Hooks

#### Format Check

```bash
# Run format check before plan
tfk plan --run-hooks

# Configuration in tfk.yaml
hooks:
  pre_plan:
    - name: check_format
      enabled: true
```

#### Variable Validation

```yaml
hooks:
  pre_plan:
    - name: validate_variables
      config:
        required:
          - environment
          - region
        patterns:
          environment: "^(dev|staging|prod)$"
```

#### Security Scanning

```yaml
hooks:
  pre_apply:
    - name: security_scan
      config:
        scanner: tfsec
        severity_threshold: high
```

#### Cost Estimation

```yaml
hooks:
  pre_apply:
    - name: estimate_cost
      config:
        provider: infracost
        threshold_monthly: 1000
```

### Hook Commands

```bash
# List configured hooks
tfk hooks list

# Run specific hook
tfk hooks run validate_variables

# Validate hook configuration
tfk hooks validate

# Skip hooks for a command
tfk apply --skip-hooks
```

### Custom Hooks

Create custom hooks in `hooks/` directory:

```python
# hooks/my_validator.py
from terraformik.hooks import Hook, HookResult

class MyValidator(Hook):
    name = "my_validator"
    hook_type = "pre_apply"

    def execute(self, context):
        # Custom validation logic
        if self.validate(context):
            return HookResult(success=True)
        return HookResult(
            success=False,
            message="Validation failed"
        )
```

Register in configuration:

```yaml
hooks:
  pre_apply:
    - name: my_validator
      path: ./hooks/my_validator.py
      enabled: true
```

---

## Configuration

### Initialize Configuration

```bash
# Create default configuration
tfk config init

# Create with specific template
tfk config init --template=aws

# Show current configuration
tfk config show

# Show specific value
tfk config show backend.type
```

### Set Configuration Values

```bash
# Set a value
tfk config set terraform.version 1.6.0

# Set nested value
tfk config set backend.config.region us-west-2

# Set from environment
tfk config set cloud.organization $TFC_ORG
```

### Configuration File Example

```yaml
# tfk.yaml
version: "1"

terraform:
  version: "1.5.0"
  working_directory: "."

backend:
  type: s3
  config:
    bucket: myapp-dev-terraformik-state
    key: myapp/dev/terraform.tfstate
    region: us-east-1
    dynamodb_table: myapp-dev-terraformik-locks
    encrypt: true

cloud:
  enabled: false
  organization: my-org

workspaces:
  default: dev
  environments:
    dev:
      var_file: environments/dev.tfvars
      auto_approve: true
    staging:
      var_file: environments/staging.tfvars
    prod:
      var_file: environments/prod.tfvars
      require_approval: true

hooks:
  enabled: true
  pre_plan:
    - check_format
    - validate_variables
  pre_apply:
    - security_scan

output:
  format: text
  color: auto
```

### Environment Variables

```bash
# Override configuration via environment
export TFK_CONFIG=./custom-config.yaml
export TFK_LOG_LEVEL=debug
export TFK_NO_COLOR=true
export TFC_TOKEN=your-token
export TFC_ORGANIZATION=your-org
```

---

## Best Practices

### 1. Project Structure

```
infrastructure/
├── tfk.yaml              # tfk configuration
├── backend.hcl           # Backend configuration
├── main.tf               # Main Terraform configuration
├── variables.tf          # Variable definitions
├── outputs.tf            # Output definitions
├── versions.tf           # Provider versions
├── environments/
│   ├── dev.tfvars        # Dev variables
│   ├── staging.tfvars    # Staging variables
│   └── prod.tfvars       # Production variables
├── modules/
│   ├── network/
│   ├── compute/
│   └── database/
└── hooks/
    └── custom_validator.py
```

### 2. State Management

- Always use remote state (S3, GCS, Azure Blob)
- Enable state locking (DynamoDB, etc.)
- Enable state encryption
- Use separate state per environment

```bash
# Provision backend first
tfk provision aws --app-name=myapp --environment=dev
```

### 3. Workspace Strategy

Use workspaces for environments:

```bash
# Create workspaces
tfk workspace new dev
tfk workspace new staging
tfk workspace new prod

# Use appropriate workspace
tfk workspace select prod
tfk apply --var-file=environments/prod.tfvars
```

### 4. CI/CD Integration

```yaml
# .github/workflows/terraform.yml
name: Terraform
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup tfk
        run: pip install terraformik

      - name: Terraform Plan
        run: |
          tfk init
          tfk plan --var-file=dev.tfvars
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### 5. Security

- Never commit secrets to version control
- Use sensitive variables in Terraform Cloud
- Enable security scanning hooks
- Review plans before applying

```yaml
hooks:
  pre_apply:
    - name: security_scan
      config:
        scanner: tfsec
        fail_on_high: true
```

---

## Troubleshooting

### Common Issues

#### Backend Not Initialized

```
Error: Backend not initialized

Run 'tfk init' to initialize the backend.
```

**Solution:**
```bash
tfk init --backend-config=backend.hcl
```

#### State Lock Error

```
Error: Error acquiring the state lock

Lock Info:
  ID:        abc-123
  Path:      terraform.tfstate
  Operation: OperationTypePlan
```

**Solution:**
```bash
# Force unlock (use with caution)
terraform force-unlock abc-123
```

#### Terraform Cloud Authentication

```
Error: Terraform Cloud authentication failed

No valid credentials found.
```

**Solution:**
```bash
# Re-authenticate
tfk cloud login

# Or set token via environment
export TFC_TOKEN=your-token
```

#### Hook Failure

```
Error: Pre-apply hook 'security_scan' failed

Found 3 HIGH severity issues.
```

**Solution:**
```bash
# View detailed hook output
tfk hooks run security_scan --verbose

# Skip hooks if needed (not recommended)
tfk apply --skip-hooks
```

### Debug Mode

```bash
# Enable debug logging
export TFK_LOG_LEVEL=debug
tfk plan

# Or use verbose flag
tfk plan --verbose
```

### Getting Help

```bash
# Show help
tfk --help

# Command-specific help
tfk plan --help

# Check system status
tfk doctor
```

### Reporting Issues

If you encounter a bug:

1. Check existing issues: https://github.com/wcampos/terraformik/issues
2. Collect debug information:
   ```bash
   tfk version
   tfk doctor
   terraform version
   ```
3. Create a new issue with reproduction steps

---

## Next Steps

- [API Reference](./api.md) - Detailed API documentation
- [Configuration Reference](./configuration.md) - All configuration options
- [Hooks Reference](./hooks.md) - Complete hooks documentation
- [Terraform Cloud Guide](./terraform-cloud.md) - Advanced TFC usage
- [Contributing](./contributing.md) - How to contribute
