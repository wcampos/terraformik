# tfk Configuration Reference

Complete reference for all tfk configuration options.

---

## Table of Contents

1. [Configuration Files](#configuration-files)
2. [Schema Reference](#schema-reference)
3. [Environment Variables](#environment-variables)
4. [Configuration Precedence](#configuration-precedence)
5. [Templates](#templates)
6. [Examples](#examples)

---

## Configuration Files

### Supported Formats

tfk supports multiple configuration file formats:

| Format | File Names |
|--------|------------|
| YAML | `tfk.yaml`, `tfk.yml` |
| JSON | `tfk.json` |
| TOML | `tfk.toml` |

### Search Paths

Configuration files are searched in this order:

1. Path specified via `--config` CLI argument
2. Path specified via `TFK_CONFIG` environment variable
3. `./tfk.yaml` (current directory)
4. `./tfk.yml`
5. `./tfk.json`
6. `./.tfk/config.yaml`
7. `~/.tfk/config.yaml` (user home)

### Initializing Configuration

```bash
# Create default configuration
tfk config init

# Create with specific template
tfk config init --template=aws
tfk config init --template=gcp
tfk config init --template=azure
tfk config init --template=terraform-cloud

# Create at specific path
tfk config init --output=./custom-config.yaml
```

---

## Schema Reference

### Root Schema

```yaml
# tfk.yaml
version: "1"                    # Schema version (required)

terraform: {}                   # Terraform settings
backend: {}                     # Backend configuration
cloud: {}                       # Terraform Cloud settings
workspaces: {}                  # Workspace configuration
orchestration: {}               # Multi-workspace orchestration
hooks: {}                       # Hook configuration
output: {}                      # Output settings
```

---

### `terraform` Section

Terraform binary and execution settings.

```yaml
terraform:
  # Path to Terraform binary (default: "terraform")
  path: /usr/local/bin/terraform

  # Required Terraform version constraint
  version: "~> 1.5.0"

  # Working directory for Terraform operations
  working_directory: ./infrastructure

  # Default parallelism for operations
  parallelism: 10

  # Enable/disable color output
  color: auto  # auto, always, never

  # Environment variables for Terraform
  env:
    TF_LOG: INFO
    TF_INPUT: "false"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | string | `terraform` | Path to Terraform binary |
| `version` | string | - | Version constraint |
| `working_directory` | string | `.` | Working directory |
| `parallelism` | integer | `10` | Concurrent operations |
| `color` | string | `auto` | Color output mode |
| `env` | map | `{}` | Environment variables |

---

### `backend` Section

Terraform state backend configuration.

```yaml
backend:
  # Backend type
  type: s3  # s3, gcs, azurerm, remote, local, etc.

  # Backend-specific configuration
  config:
    bucket: myapp-terraform-state
    key: terraform.tfstate
    region: us-east-1
    dynamodb_table: myapp-terraform-locks
    encrypt: true

  # Use partial configuration (load from file)
  partial: true
  partial_config_file: backend.hcl
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | string | - | Backend type |
| `config` | map | `{}` | Backend configuration |
| `partial` | boolean | `false` | Use partial configuration |
| `partial_config_file` | string | - | Partial config file path |

#### S3 Backend Configuration

```yaml
backend:
  type: s3
  config:
    bucket: terraform-state-bucket
    key: path/to/terraform.tfstate
    region: us-east-1
    dynamodb_table: terraform-locks
    encrypt: true
    kms_key_id: alias/terraform
    workspace_key_prefix: env
    acl: bucket-owner-full-control
    skip_metadata_api_check: false
    sse_customer_key: ""
```

#### GCS Backend Configuration

```yaml
backend:
  type: gcs
  config:
    bucket: terraform-state-bucket
    prefix: terraform/state
    credentials: /path/to/credentials.json
    encryption_key: ""
```

#### Azure Backend Configuration

```yaml
backend:
  type: azurerm
  config:
    resource_group_name: terraform-state-rg
    storage_account_name: tfstate
    container_name: tfstate
    key: terraform.tfstate
    use_azuread_auth: true
```

#### Remote Backend (Terraform Cloud)

```yaml
backend:
  type: remote
  config:
    hostname: app.terraform.io
    organization: my-org
    workspaces:
      name: my-workspace
      # OR use prefix for multiple workspaces
      # prefix: myapp-
```

---

### `cloud` Section

Terraform Cloud/Enterprise integration settings.

```yaml
cloud:
  # Enable Terraform Cloud integration
  enabled: true

  # Terraform Cloud hostname
  hostname: app.terraform.io

  # Organization name
  organization: my-organization

  # Default workspace (optional)
  workspace: production

  # API token (prefer environment variable)
  # token: ${TFC_TOKEN}

  # Run settings
  runs:
    # Default auto-apply setting
    auto_apply: false

    # Queue all runs (vs speculative)
    queue_all: false

    # Poll interval for run status (seconds)
    poll_interval: 5

    # Timeout for waiting on runs (seconds)
    timeout: 3600

  # Variable settings
  variables:
    # Sync local variables to cloud
    sync: false

    # Variable files to sync
    var_files:
      - terraform.tfvars
      - secrets.tfvars
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable TFC integration |
| `hostname` | string | `app.terraform.io` | TFC/TFE hostname |
| `organization` | string | - | Organization name |
| `workspace` | string | - | Default workspace |
| `runs.auto_apply` | boolean | `false` | Auto-apply runs |
| `runs.poll_interval` | integer | `5` | Status poll interval |
| `runs.timeout` | integer | `3600` | Run timeout |

---

### `workspaces` Section

Workspace management configuration.

```yaml
workspaces:
  # Default workspace to use
  default: dev

  # Workspace naming pattern
  # Available variables: {environment}, {region}, {app}
  naming_pattern: "{app}-{environment}"

  # Environment-specific settings
  environments:
    dev:
      # Variable file for this environment
      var_file: environments/dev.tfvars

      # Additional variable files
      var_files:
        - common.tfvars
        - dev.tfvars

      # Inline variables
      variables:
        environment: dev

      # Auto-approve applies
      auto_approve: true

      # Backend configuration overrides
      backend:
        key: dev/terraform.tfstate

    staging:
      var_file: environments/staging.tfvars
      auto_approve: false

    prod:
      var_file: environments/prod.tfvars
      auto_approve: false

      # Require manual approval
      require_approval: true

      # Approval settings
      approval:
        # Minimum approvers
        min_approvers: 2

        # Allowed approvers
        approvers:
          - user@example.com
          - admin@example.com
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `default` | string | - | Default workspace |
| `naming_pattern` | string | - | Workspace naming pattern |
| `environments` | map | `{}` | Environment configurations |
| `environments.*.var_file` | string | - | Variable file |
| `environments.*.var_files` | list | `[]` | Additional var files |
| `environments.*.variables` | map | `{}` | Inline variables |
| `environments.*.auto_approve` | boolean | `false` | Auto-approve |
| `environments.*.require_approval` | boolean | `false` | Require approval |

---

### `orchestration` Section

Multi-workspace orchestration settings.

```yaml
orchestration:
  # Workspace definitions
  workspaces:
    - name: network
      # Path to Terraform configuration
      path: ./infrastructure/network

      # Dependencies (run these first)
      dependencies: []

      # Workspace-specific settings
      var_file: network.tfvars

      # Tags for filtering
      tags:
        - networking
        - core

    - name: security
      path: ./infrastructure/security
      dependencies:
        - network
      tags:
        - security

    - name: database
      path: ./infrastructure/database
      dependencies:
        - network
        - security
      tags:
        - data

    - name: application
      path: ./infrastructure/application
      dependencies:
        - database
      tags:
        - app

  # Execution settings
  execution:
    # Maximum parallel executions
    parallelism: 3

    # Stop on first failure
    fail_fast: true

    # Continue even if workspace fails
    continue_on_error: false

    # Retry failed workspaces
    retry:
      enabled: true
      max_attempts: 3
      delay_seconds: 30
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `workspaces` | list | `[]` | Workspace definitions |
| `workspaces.*.name` | string | - | Workspace name |
| `workspaces.*.path` | string | - | Configuration path |
| `workspaces.*.dependencies` | list | `[]` | Dependency names |
| `workspaces.*.tags` | list | `[]` | Tags for filtering |
| `execution.parallelism` | integer | `3` | Max parallel |
| `execution.fail_fast` | boolean | `true` | Stop on failure |
| `execution.retry.enabled` | boolean | `false` | Enable retry |

---

### `hooks` Section

Pre and post execution hooks configuration.

```yaml
hooks:
  # Enable/disable all hooks
  enabled: true

  # Stop execution on first hook failure
  fail_fast: true

  # Global timeout for hooks (seconds)
  timeout: 300

  # Pre-init hooks
  pre_init:
    - name: validate_backend
      enabled: true
      fail_on_error: true
      config:
        check_s3_bucket: true
        check_dynamodb_table: true

  # Post-init hooks
  post_init: []

  # Pre-plan hooks
  pre_plan:
    - name: check_format
      enabled: true
      fail_on_error: true
      config:
        recursive: true

    - name: validate_variables
      enabled: true
      fail_on_error: true
      config:
        required:
          - environment
          - region
        patterns:
          environment: "^(dev|staging|prod)$"

    - name: check_secrets
      enabled: true
      fail_on_error: true

  # Post-plan hooks
  post_plan:
    - name: save_plan_output
      enabled: true
      fail_on_error: false
      config:
        output_dir: ./plans

  # Pre-apply hooks
  pre_apply:
    - name: security_scan
      enabled: true
      fail_on_error: true
      config:
        scanner: tfsec
        severity_threshold: high
        exclude_rules:
          - AWS006

    - name: estimate_cost
      enabled: true
      fail_on_error: false
      config:
        provider: infracost
        threshold_monthly: 1000
        require_approval_above: 500

  # Post-apply hooks
  post_apply:
    - name: notify_slack
      enabled: true
      fail_on_error: false
      config:
        webhook_url: ${SLACK_WEBHOOK_URL}
        channel: "#infrastructure"

    - name: update_documentation
      enabled: false
      config:
        output_file: ./docs/infrastructure.md

  # Pre-destroy hooks
  pre_destroy:
    - name: backup_state
      enabled: true
      config:
        backup_dir: ./state-backups

  # Post-destroy hooks
  post_destroy: []

  # Custom hooks directory
  custom_hooks_dir: ./hooks

  # External hooks (shell commands)
  external:
    - name: custom_validator
      hook_type: pre_apply
      command: ./scripts/validate.sh
      timeout: 60
      fail_on_error: true
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable hooks |
| `fail_fast` | boolean | `true` | Stop on failure |
| `timeout` | integer | `300` | Global timeout |
| `pre_init` | list | `[]` | Pre-init hooks |
| `post_init` | list | `[]` | Post-init hooks |
| `pre_plan` | list | `[]` | Pre-plan hooks |
| `post_plan` | list | `[]` | Post-plan hooks |
| `pre_apply` | list | `[]` | Pre-apply hooks |
| `post_apply` | list | `[]` | Post-apply hooks |
| `custom_hooks_dir` | string | - | Custom hooks path |

#### Hook Configuration

Each hook supports these fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | - | Hook identifier |
| `enabled` | boolean | `true` | Enable this hook |
| `fail_on_error` | boolean | `true` | Fail on error |
| `timeout` | integer | `60` | Hook timeout |
| `config` | map | `{}` | Hook-specific config |
| `path` | string | - | Custom hook path |
| `command` | string | - | External command |

---

### `output` Section

Output and display settings.

```yaml
output:
  # Output format
  format: text  # text, json, yaml

  # Color output
  color: auto  # auto, always, never

  # Verbose output
  verbose: false

  # Show timestamps
  timestamps: false

  # Log settings
  log:
    # Log level
    level: info  # debug, info, warn, error

    # Log file path
    file: ./tfk.log

    # Log format
    format: text  # text, json

    # Rotate logs
    rotate:
      enabled: true
      max_size_mb: 10
      max_files: 5

  # Plan output settings
  plan:
    # Show resource details in plan
    detailed: true

    # Show unchanged resources
    show_unchanged: false

    # Diff format
    diff_format: unified  # unified, side-by-side

  # Progress display
  progress:
    # Show spinner
    spinner: true

    # Show progress bar
    bar: true

    # Refresh rate (ms)
    refresh_ms: 100
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | string | `text` | Output format |
| `color` | string | `auto` | Color mode |
| `verbose` | boolean | `false` | Verbose output |
| `timestamps` | boolean | `false` | Show timestamps |
| `log.level` | string | `info` | Log level |
| `log.file` | string | - | Log file path |

---

## Environment Variables

All configuration values can be overridden via environment variables.

### Naming Convention

Environment variables use the format: `TFK_<SECTION>_<KEY>`

Nested keys use double underscores: `TFK_<SECTION>__<NESTED>__<KEY>`

### Core Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TFK_CONFIG` | Configuration file path | `/path/to/tfk.yaml` |
| `TFK_WORKING_DIR` | Working directory | `./infrastructure` |
| `TFK_LOG_LEVEL` | Log level | `debug` |
| `TFK_NO_COLOR` | Disable colors | `true` |
| `TFK_VERBOSE` | Verbose output | `true` |

### Terraform Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TFK_TERRAFORM__PATH` | Terraform binary path | `/usr/bin/terraform` |
| `TFK_TERRAFORM__VERSION` | Version constraint | `~> 1.5.0` |
| `TFK_TERRAFORM__PARALLELISM` | Parallelism | `20` |

### Backend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TFK_BACKEND__TYPE` | Backend type | `s3` |
| `TFK_BACKEND__CONFIG__BUCKET` | S3 bucket | `my-bucket` |
| `TFK_BACKEND__CONFIG__REGION` | AWS region | `us-east-1` |

### Terraform Cloud Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TFC_TOKEN` | API token | `token...` |
| `TFC_ORGANIZATION` | Organization | `my-org` |
| `TFK_CLOUD__ENABLED` | Enable TFC | `true` |
| `TFK_CLOUD__HOSTNAME` | TFC hostname | `terraform.company.com` |

### Hook Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TFK_HOOKS__ENABLED` | Enable hooks | `true` |
| `TFK_HOOKS__FAIL_FAST` | Fail fast | `false` |
| `TFK_SKIP_HOOKS` | Skip all hooks | `true` |

### Variables in Configuration

You can reference environment variables in configuration files:

```yaml
cloud:
  organization: ${TFC_ORGANIZATION}

backend:
  config:
    bucket: ${APP_NAME}-${ENVIRONMENT}-state

hooks:
  post_apply:
    - name: notify_slack
      config:
        webhook_url: ${SLACK_WEBHOOK_URL}
```

---

## Configuration Precedence

Configuration values are resolved in this order (highest to lowest):

1. **CLI Arguments**
   ```bash
   tfk plan --var-file=override.tfvars
   ```

2. **Environment Variables**
   ```bash
   export TFK_TERRAFORM__PARALLELISM=20
   ```

3. **Project Configuration** (`./tfk.yaml`)
   ```yaml
   terraform:
     parallelism: 15
   ```

4. **User Configuration** (`~/.tfk/config.yaml`)
   ```yaml
   terraform:
     parallelism: 10
   ```

5. **Default Values**
   ```yaml
   terraform:
     parallelism: 10  # Default
   ```

---

## Templates

### AWS Template

```bash
tfk config init --template=aws
```

```yaml
# tfk.yaml (AWS template)
version: "1"

terraform:
  version: "~> 1.5.0"

backend:
  type: s3
  config:
    bucket: ${APP_NAME}-terraform-state
    key: ${APP_NAME}/terraform.tfstate
    region: ${AWS_REGION:-us-east-1}
    dynamodb_table: ${APP_NAME}-terraform-locks
    encrypt: true

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
```

### GCP Template

```bash
tfk config init --template=gcp
```

```yaml
# tfk.yaml (GCP template)
version: "1"

terraform:
  version: "~> 1.5.0"

backend:
  type: gcs
  config:
    bucket: ${PROJECT_ID}-terraform-state
    prefix: terraform/state

workspaces:
  default: dev
  environments:
    dev:
      var_file: environments/dev.tfvars
    prod:
      var_file: environments/prod.tfvars

hooks:
  enabled: true
  pre_plan:
    - check_format
```

### Terraform Cloud Template

```bash
tfk config init --template=terraform-cloud
```

```yaml
# tfk.yaml (Terraform Cloud template)
version: "1"

terraform:
  version: "~> 1.5.0"

cloud:
  enabled: true
  organization: ${TFC_ORGANIZATION}
  hostname: app.terraform.io
  runs:
    auto_apply: false
    poll_interval: 5

workspaces:
  default: dev
  environments:
    dev:
      workspace: ${APP_NAME}-dev
    staging:
      workspace: ${APP_NAME}-staging
    prod:
      workspace: ${APP_NAME}-prod
      require_approval: true

hooks:
  enabled: true
  pre_plan:
    - check_format
    - validate_variables
```

---

## Examples

### Minimal Configuration

```yaml
version: "1"

backend:
  type: local
```

### Development Configuration

```yaml
version: "1"

terraform:
  version: "~> 1.5.0"

backend:
  type: s3
  config:
    bucket: myapp-dev-terraform-state
    key: terraform.tfstate
    region: us-east-1

workspaces:
  default: dev
  environments:
    dev:
      var_file: dev.tfvars
      auto_approve: true

hooks:
  enabled: true
  pre_plan:
    - check_format

output:
  verbose: true
  log:
    level: debug
```

### Production Configuration

```yaml
version: "1"

terraform:
  version: "1.5.7"  # Exact version for consistency
  parallelism: 5    # Reduced for safety

backend:
  type: s3
  config:
    bucket: myapp-prod-terraform-state
    key: prod/terraform.tfstate
    region: us-east-1
    dynamodb_table: myapp-prod-terraform-locks
    encrypt: true
    kms_key_id: alias/terraform-prod

workspaces:
  default: prod
  environments:
    prod:
      var_file: environments/prod.tfvars
      auto_approve: false
      require_approval: true
      approval:
        min_approvers: 2

hooks:
  enabled: true
  fail_fast: true
  pre_init:
    - validate_backend
  pre_plan:
    - check_format
    - validate_variables
    - check_secrets
  pre_apply:
    - name: security_scan
      config:
        scanner: tfsec
        severity_threshold: high
        fail_on_high: true
    - name: estimate_cost
      config:
        threshold_monthly: 5000
        require_approval_above: 1000
  post_apply:
    - name: notify_slack
      config:
        webhook_url: ${SLACK_WEBHOOK_URL}
        channel: "#prod-deploys"

output:
  format: text
  log:
    level: info
    file: /var/log/tfk/terraform.log
    rotate:
      enabled: true
      max_size_mb: 50
      max_files: 10
```

### Multi-Environment with Orchestration

```yaml
version: "1"

terraform:
  version: "~> 1.5.0"

backend:
  type: s3
  partial: true
  partial_config_file: backend.hcl

workspaces:
  default: dev
  naming_pattern: "{app}-{environment}-{component}"
  environments:
    dev:
      auto_approve: true
    staging:
      auto_approve: false
    prod:
      auto_approve: false
      require_approval: true

orchestration:
  workspaces:
    - name: network
      path: ./modules/network
      dependencies: []
      tags: [core, network]
    - name: security
      path: ./modules/security
      dependencies: [network]
      tags: [core, security]
    - name: database
      path: ./modules/database
      dependencies: [network, security]
      tags: [data]
    - name: cache
      path: ./modules/cache
      dependencies: [network, security]
      tags: [data]
    - name: application
      path: ./modules/application
      dependencies: [database, cache]
      tags: [app]
  execution:
    parallelism: 2
    fail_fast: true
    retry:
      enabled: true
      max_attempts: 2

hooks:
  enabled: true
  pre_plan:
    - check_format
    - validate_variables
  pre_apply:
    - security_scan
  post_apply:
    - notify_slack
```

---

## See Also

- [User Guide](./user-guide.md)
- [API Reference](./api.md)
- [Hooks Reference](./hooks.md)
