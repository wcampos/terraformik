# Terraformik CLI (tfk) - Technical Design Document

## Overview

**tfk** is a Python CLI application designed to streamline Terraform operations by providing a unified interface for local Terraform commands, Terraform Cloud API integration, multi-workspace orchestration, and pre-execution validation hooks.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Core Features](#core-features)
3. [CLI Structure](#cli-structure)
4. [Module Design](#module-design)
5. [Terraform Cloud Integration](#terraform-cloud-integration)
6. [Pre-Hooks System](#pre-hooks-system)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)
9. [Security Considerations](#security-considerations)
10. [Development Roadmap](#development-roadmap)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              tfk CLI                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Commands   │  │   Pre-Hooks  │  │  TF Cloud    │  │   Config     │ │
│  │   Handler    │  │   Engine     │  │  Client      │  │   Manager    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │                 │          │
│         └─────────────────┴────────┬────────┴─────────────────┘          │
│                                    │                                     │
│                          ┌─────────▼─────────┐                          │
│                          │   Core Engine     │                          │
│                          └─────────┬─────────┘                          │
│                                    │                                     │
├────────────────────────────────────┼────────────────────────────────────┤
│                                    │                                     │
│  ┌─────────────────────────────────▼─────────────────────────────────┐  │
│  │                         Execution Layer                            │  │
│  │                                                                    │  │
│  │   ┌─────────────────┐   ┌─────────────────┐   ┌────────────────┐  │  │
│  │   │  Local Terraform │   │  Terraform Cloud │   │   HCL Parser   │  │  │
│  │   │     Executor     │   │   API Client     │   │   & Generator  │  │  │
│  │   └─────────────────┘   └─────────────────┘   └────────────────┘  │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │                        External Systems                           │
    │                                                                   │
    │   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
    │   │  Terraform  │   │  Terraform  │   │  Cloud Providers    │   │
    │   │   Binary    │   │    Cloud    │   │  (AWS, GCP, Azure)  │   │
    │   └─────────────┘   └─────────────┘   └─────────────────────┘   │
    │                                                                   │
    └───────────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
                    ┌─────────────────────────────────────────┐
                    │               User Input                 │
                    │         (CLI Arguments/Config)           │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │            tfk CLI Entry Point           │
                    │              (Click/Typer)               │
                    └─────────────────┬───────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │  Config Loader  │     │  Hook Manager   │     │ Command Router  │
    │                 │     │                 │     │                 │
    │ - tfk.yaml      │     │ - pre_init      │     │ - init          │
    │ - tfk.json      │     │ - pre_plan      │     │ - plan          │
    │ - env vars      │     │ - pre_apply     │     │ - apply         │
    │ - .tfkrc        │     │ - post_*        │     │ - destroy       │
    └────────┬────────┘     └────────┬────────┘     │ - workspace     │
             │                       │              │ - cloud         │
             │                       │              └────────┬────────┘
             │                       │                       │
             └───────────────────────┴───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │           Execution Pipeline             │
                    │                                         │
                    │  1. Load Configuration                  │
                    │  2. Validate Environment                │
                    │  3. Run Pre-Hooks                       │
                    │  4. Execute Terraform Command           │
                    │  5. Run Post-Hooks                      │
                    │  6. Report Results                      │
                    └─────────────────────────────────────────┘
```

---

## Core Features

### 1. Terraform Command Wrapper

Wraps native Terraform commands with enhanced functionality:

| Command | Description |
|---------|-------------|
| `tfk init` | Initialize Terraform with backend configuration |
| `tfk plan` | Generate execution plan with formatted output |
| `tfk apply` | Apply changes with confirmation and hooks |
| `tfk destroy` | Destroy infrastructure with safety checks |
| `tfk fmt` | Format Terraform files recursively |
| `tfk validate` | Validate Terraform configuration |
| `tfk output` | Display Terraform outputs |

### 2. Terraform Cloud Integration

Direct API integration with Terraform Cloud/Enterprise:

| Command | Description |
|---------|-------------|
| `tfk cloud login` | Authenticate with Terraform Cloud |
| `tfk cloud workspaces` | List/manage workspaces |
| `tfk cloud runs` | Trigger and monitor runs |
| `tfk cloud variables` | Manage workspace variables |
| `tfk cloud state` | State management operations |

### 3. Multi-Workspace Orchestration

Execute operations across multiple workspaces:

| Command | Description |
|---------|-------------|
| `tfk multi plan` | Plan across multiple workspaces |
| `tfk multi apply` | Apply across workspaces with dependency order |
| `tfk multi status` | Check status of all workspaces |

### 4. Pre-Hooks System

Validation and preparation hooks:

| Hook Type | Purpose |
|-----------|---------|
| `pre_init` | Validate backend configuration |
| `pre_plan` | Check variable files, lint HCL |
| `pre_apply` | Security scanning, cost estimation |
| `post_apply` | Notifications, documentation |

---

## CLI Structure

### Command Hierarchy

```
tfk
├── init          # Initialize Terraform working directory
├── plan          # Generate and show execution plan
├── apply         # Apply Terraform changes
├── destroy       # Destroy Terraform-managed infrastructure
├── fmt           # Format Terraform configuration files
├── validate      # Validate Terraform configuration
├── output        # Show Terraform outputs
│
├── workspace     # Workspace management commands
│   ├── list      # List workspaces
│   ├── select    # Select a workspace
│   ├── new       # Create new workspace
│   └── delete    # Delete a workspace
│
├── cloud         # Terraform Cloud commands
│   ├── login     # Authenticate with Terraform Cloud
│   ├── logout    # Remove stored credentials
│   ├── workspaces
│   │   ├── list  # List workspaces in organization
│   │   ├── show  # Show workspace details
│   │   └── create # Create new workspace
│   ├── runs
│   │   ├── list  # List runs for workspace
│   │   ├── show  # Show run details
│   │   ├── trigger # Trigger a new run
│   │   ├── apply # Apply a pending run
│   │   ├── discard # Discard a pending run
│   │   └── cancel # Cancel an in-progress run
│   ├── variables
│   │   ├── list  # List workspace variables
│   │   ├── set   # Set a variable
│   │   └── delete # Delete a variable
│   └── state
│       ├── pull  # Download current state
│       ├── push  # Upload state file
│       └── list  # List state versions
│
├── multi         # Multi-workspace operations
│   ├── plan      # Plan multiple workspaces
│   ├── apply     # Apply multiple workspaces
│   └── status    # Status of multiple workspaces
│
├── hooks         # Hook management
│   ├── list      # List configured hooks
│   ├── run       # Run specific hook
│   └── validate  # Validate hook configuration
│
├── provision     # Backend provisioning
│   ├── aws       # Provision AWS backend (S3 + DynamoDB)
│   ├── gcp       # Provision GCP backend
│   └── azure     # Provision Azure backend
│
├── config        # Configuration management
│   ├── init      # Initialize tfk configuration
│   ├── show      # Show current configuration
│   └── set       # Set configuration value
│
└── version       # Show tfk version
```

### Usage Examples

```bash
# Basic Terraform operations
tfk init --backend-config=backend.hcl
tfk plan --var-file=dev.tfvars --out=plan.tfplan
tfk apply plan.tfplan

# Workspace operations
tfk workspace list
tfk workspace select production

# Terraform Cloud operations
tfk cloud login --token=$TFC_TOKEN
tfk cloud workspaces list --organization=my-org
tfk cloud runs trigger --workspace=my-workspace --message="Deploy v1.2.3"

# Multi-workspace operations
tfk multi plan --config=workspaces.yaml
tfk multi apply --parallel=3 --auto-approve

# Pre-hooks validation
tfk plan --run-hooks
tfk apply --skip-hooks  # Skip hooks if needed
```

---

## Module Design

### Package Structure

```
terraformik/
├── __init__.py
├── __main__.py              # Entry point: python -m terraformik
├── cli/
│   ├── __init__.py
│   ├── main.py              # Main CLI application
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── init.py          # tfk init command
│   │   ├── plan.py          # tfk plan command
│   │   ├── apply.py         # tfk apply command
│   │   ├── destroy.py       # tfk destroy command
│   │   ├── workspace.py     # tfk workspace commands
│   │   ├── cloud.py         # tfk cloud commands
│   │   ├── multi.py         # tfk multi commands
│   │   ├── hooks.py         # tfk hooks commands
│   │   ├── provision.py     # tfk provision commands
│   │   └── config.py        # tfk config commands
│   └── utils/
│       ├── __init__.py
│       ├── output.py        # Console output formatting
│       └── prompts.py       # Interactive prompts
│
├── core/
│   ├── __init__.py
│   ├── engine.py            # Core execution engine
│   ├── terraform.py         # Terraform binary wrapper
│   ├── workspace.py         # Workspace management
│   └── state.py             # State management utilities
│
├── cloud/
│   ├── __init__.py
│   ├── client.py            # Terraform Cloud API client
│   ├── auth.py              # Authentication handling
│   ├── workspaces.py        # Workspace API operations
│   ├── runs.py              # Run API operations
│   ├── variables.py         # Variable API operations
│   └── state.py             # State version operations
│
├── hooks/
│   ├── __init__.py
│   ├── manager.py           # Hook execution manager
│   ├── registry.py          # Built-in hooks registry
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── backend.py       # Backend validation
│   │   ├── variables.py     # Variable validation
│   │   ├── security.py      # Security scanning
│   │   └── format.py        # Format checking
│   └── builtins/
│       ├── __init__.py
│       ├── lint.py          # HCL linting
│       ├── cost.py          # Cost estimation
│       └── docs.py          # Documentation generation
│
├── hcl/
│   ├── __init__.py
│   ├── parser.py            # HCL parsing utilities
│   ├── generator.py         # HCL generation
│   └── validator.py         # HCL validation
│
├── config/
│   ├── __init__.py
│   ├── loader.py            # Configuration loading
│   ├── schema.py            # Configuration schema
│   └── defaults.py          # Default configuration
│
├── provisioners/
│   ├── __init__.py
│   ├── base.py              # Base provisioner class
│   ├── aws.py               # AWS backend provisioner
│   ├── gcp.py               # GCP backend provisioner
│   └── azure.py             # Azure backend provisioner
│
├── utils/
│   ├── __init__.py
│   ├── logging.py           # Logging configuration
│   ├── process.py           # Subprocess handling
│   ├── paths.py             # Path utilities
│   └── version.py           # Version utilities
│
└── exceptions/
    ├── __init__.py
    ├── terraform.py         # Terraform-related exceptions
    ├── cloud.py             # Cloud API exceptions
    └── hooks.py             # Hook execution exceptions
```

### Core Classes

#### TerraformExecutor

```python
class TerraformExecutor:
    """Wrapper for Terraform binary execution."""

    def __init__(
        self,
        working_dir: Path,
        terraform_path: str = "terraform",
        env: dict[str, str] | None = None
    ):
        self.working_dir = working_dir
        self.terraform_path = terraform_path
        self.env = env or {}

    def init(
        self,
        backend_config: dict | None = None,
        reconfigure: bool = False,
        upgrade: bool = False
    ) -> ExecutionResult:
        """Initialize Terraform working directory."""
        ...

    def plan(
        self,
        var_file: Path | None = None,
        variables: dict | None = None,
        out: Path | None = None,
        target: list[str] | None = None,
        destroy: bool = False
    ) -> PlanResult:
        """Create execution plan."""
        ...

    def apply(
        self,
        plan_file: Path | None = None,
        auto_approve: bool = False,
        target: list[str] | None = None
    ) -> ApplyResult:
        """Apply Terraform changes."""
        ...

    def destroy(
        self,
        auto_approve: bool = False,
        target: list[str] | None = None
    ) -> DestroyResult:
        """Destroy Terraform-managed infrastructure."""
        ...
```

#### TerraformCloudClient

```python
class TerraformCloudClient:
    """Client for Terraform Cloud API."""

    BASE_URL = "https://app.terraform.io/api/v2"

    def __init__(
        self,
        token: str,
        organization: str,
        base_url: str | None = None
    ):
        self.token = token
        self.organization = organization
        self.base_url = base_url or self.BASE_URL
        self._session = self._create_session()

    # Workspace operations
    def list_workspaces(self) -> list[Workspace]:
        """List all workspaces in organization."""
        ...

    def get_workspace(self, name: str) -> Workspace:
        """Get workspace by name."""
        ...

    def create_workspace(self, config: WorkspaceConfig) -> Workspace:
        """Create a new workspace."""
        ...

    # Run operations
    def trigger_run(
        self,
        workspace_id: str,
        message: str | None = None,
        auto_apply: bool = False
    ) -> Run:
        """Trigger a new run."""
        ...

    def get_run(self, run_id: str) -> Run:
        """Get run details."""
        ...

    def apply_run(self, run_id: str, comment: str | None = None) -> Run:
        """Apply a pending run."""
        ...

    # Variable operations
    def list_variables(self, workspace_id: str) -> list[Variable]:
        """List workspace variables."""
        ...

    def set_variable(
        self,
        workspace_id: str,
        key: str,
        value: str,
        category: str = "terraform",
        sensitive: bool = False,
        hcl: bool = False
    ) -> Variable:
        """Create or update a variable."""
        ...
```

#### HookManager

```python
class HookManager:
    """Manages pre and post execution hooks."""

    def __init__(self, config: HookConfig):
        self.config = config
        self.registry = HookRegistry()

    def run_pre_hooks(
        self,
        command: str,
        context: ExecutionContext
    ) -> HookResult:
        """Run pre-command hooks."""
        hooks = self.config.get_hooks(f"pre_{command}")
        results = []

        for hook in hooks:
            result = self._execute_hook(hook, context)
            results.append(result)

            if not result.success and hook.fail_on_error:
                return HookResult(
                    success=False,
                    message=f"Hook '{hook.name}' failed: {result.message}",
                    results=results
                )

        return HookResult(success=True, results=results)

    def run_post_hooks(
        self,
        command: str,
        context: ExecutionContext,
        command_result: ExecutionResult
    ) -> HookResult:
        """Run post-command hooks."""
        ...
```

---

## Terraform Cloud Integration

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/organizations/{org}/workspaces` | GET | List workspaces |
| `/workspaces/{id}` | GET | Get workspace |
| `/organizations/{org}/workspaces` | POST | Create workspace |
| `/workspaces/{id}/runs` | POST | Create run |
| `/runs/{id}` | GET | Get run details |
| `/runs/{id}/actions/apply` | POST | Apply run |
| `/runs/{id}/actions/cancel` | POST | Cancel run |
| `/workspaces/{id}/vars` | GET | List variables |
| `/workspaces/{id}/vars` | POST | Create variable |
| `/vars/{id}` | PATCH | Update variable |

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Authentication Flow                               │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────┐                                      ┌──────────────────┐
    │   User   │                                      │ Terraform Cloud  │
    └────┬─────┘                                      └────────┬─────────┘
         │                                                      │
         │  1. tfk cloud login                                  │
         │─────────────────────────────────────────────────────>│
         │                                                      │
         │  2. Enter API Token (or use TFC_TOKEN env)           │
         │<─────────────────────────────────────────────────────│
         │                                                      │
         │  3. Validate token via API                           │
         │─────────────────────────────────────────────────────>│
         │                                                      │
         │  4. Token valid, return user info                    │
         │<─────────────────────────────────────────────────────│
         │                                                      │
         │  5. Store credentials in ~/.tfk/credentials.json     │
         │                                                      │
         │  6. Subsequent commands use stored token             │
         │─────────────────────────────────────────────────────>│
         │                                                      │

Token Sources (in priority order):
1. --token CLI argument
2. TFC_TOKEN environment variable
3. ~/.tfk/credentials.json
4. ~/.terraform.d/credentials.tfrc.json (Terraform native)
```

### Run Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Terraform Cloud Run Workflow                        │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────┐     ┌───────────────────┐     ┌──────────────────┐
    │   tfk    │     │  Terraform Cloud  │     │  Cloud Provider  │
    └────┬─────┘     └─────────┬─────────┘     └────────┬─────────┘
         │                      │                        │
         │  1. Trigger Run      │                        │
         │─────────────────────>│                        │
         │                      │                        │
         │  2. Run Created      │                        │
         │<─────────────────────│                        │
         │                      │                        │
         │  3. Poll for status  │                        │
         │─────────────────────>│                        │
         │                      │  4. Run Planning       │
         │  Status: planning    │─────────────────────-->│
         │<─────────────────────│                        │
         │                      │                        │
         │  5. Poll for status  │                        │
         │─────────────────────>│                        │
         │                      │                        │
         │  Status: planned     │                        │
         │<─────────────────────│                        │
         │                      │                        │
         │  6. Confirm Apply    │                        │
         │─────────────────────>│                        │
         │                      │                        │
         │  7. Poll for status  │                        │
         │─────────────────────>│                        │
         │                      │  8. Run Applying       │
         │  Status: applying    │─────────────────────-->│
         │<─────────────────────│                        │
         │                      │                        │
         │  9. Poll for status  │                        │
         │─────────────────────>│                        │
         │                      │                        │
         │  Status: applied     │                        │
         │<─────────────────────│                        │
         │                      │                        │
```

---

## Pre-Hooks System

### Hook Types

| Type | Trigger | Purpose |
|------|---------|---------|
| `pre_init` | Before `terraform init` | Validate backend, check dependencies |
| `pre_plan` | Before `terraform plan` | Lint, validate vars, security scan |
| `pre_apply` | Before `terraform apply` | Cost estimation, approval gates |
| `pre_destroy` | Before `terraform destroy` | Backup state, confirm destruction |
| `post_init` | After `terraform init` | Setup providers, cache modules |
| `post_plan` | After `terraform plan` | Save plan, notify team |
| `post_apply` | After `terraform apply` | Update docs, notify, tag resources |
| `post_destroy` | After `terraform destroy` | Cleanup, archive state |

### Built-in Hooks

#### Validation Hooks

```yaml
# Backend Validation
- name: validate_backend
  type: pre_init
  description: Ensure backend resources exist
  config:
    check_s3_bucket: true
    check_dynamodb_table: true
    check_permissions: true

# Variable Validation
- name: validate_variables
  type: pre_plan
  description: Validate required variables are set
  config:
    required:
      - environment
      - region
    patterns:
      environment: "^(dev|staging|prod)$"

# Format Check
- name: check_format
  type: pre_plan
  description: Ensure Terraform files are formatted
  config:
    recursive: true
    check_only: true
```

#### Security Hooks

```yaml
# Security Scanning
- name: security_scan
  type: pre_apply
  description: Scan for security issues
  config:
    scanner: tfsec
    severity_threshold: medium
    fail_on_warnings: false

# Sensitive Data Check
- name: check_secrets
  type: pre_plan
  description: Check for hardcoded secrets
  config:
    patterns:
      - "password\\s*=\\s*\"[^\"]+\""
      - "secret\\s*=\\s*\"[^\"]+\""
      - "api_key\\s*=\\s*\"[^\"]+\""
```

#### Cost Hooks

```yaml
# Cost Estimation
- name: estimate_cost
  type: pre_apply
  description: Estimate infrastructure cost
  config:
    provider: infracost
    threshold_monthly: 1000
    require_approval_above: 500
```

### Hook Configuration

```yaml
# tfk.yaml
hooks:
  enabled: true
  fail_fast: true  # Stop on first failure

  pre_init:
    - name: validate_backend
      enabled: true
      fail_on_error: true

  pre_plan:
    - name: check_format
      enabled: true
      fail_on_error: true
    - name: validate_variables
      enabled: true
      fail_on_error: true
    - name: check_secrets
      enabled: true
      fail_on_error: true

  pre_apply:
    - name: security_scan
      enabled: true
      fail_on_error: true
    - name: estimate_cost
      enabled: true
      fail_on_error: false

  post_apply:
    - name: notify_slack
      enabled: true
      fail_on_error: false
      config:
        webhook_url: ${SLACK_WEBHOOK_URL}
        channel: "#infrastructure"
```

### Custom Hook Definition

```python
# hooks/custom/my_hook.py
from terraformik.hooks import Hook, HookResult, ExecutionContext

class MyCustomHook(Hook):
    """Custom pre-apply validation hook."""

    name = "my_custom_hook"
    description = "Custom validation before apply"
    hook_type = "pre_apply"

    def execute(self, context: ExecutionContext) -> HookResult:
        """Execute the hook logic."""

        # Access Terraform state
        state = context.get_state()

        # Access planned changes
        plan = context.get_plan()

        # Perform custom validation
        if self._validate(plan):
            return HookResult(
                success=True,
                message="Validation passed"
            )
        else:
            return HookResult(
                success=False,
                message="Validation failed: reason..."
            )

    def _validate(self, plan: TerraformPlan) -> bool:
        """Custom validation logic."""
        # Check for specific resource types
        for resource in plan.resource_changes:
            if resource.type == "aws_instance":
                if not self._check_instance_tags(resource):
                    return False
        return True
```

---

## Configuration

### Configuration File Schema

```yaml
# tfk.yaml - Project configuration
version: "1"

# Default Terraform settings
terraform:
  version: "1.5.0"
  working_directory: "."

# Backend configuration
backend:
  type: s3
  config:
    bucket: "${app_name}-${environment}-terraformik-state"
    key: "${app_name}/${environment}/terraform.tfstate"
    region: "${aws_region}"
    dynamodb_table: "${app_name}-${environment}-terraformik-locks"
    encrypt: true

# Terraform Cloud settings
cloud:
  enabled: false
  organization: "my-org"
  hostname: "app.terraform.io"

# Workspaces configuration
workspaces:
  default: dev
  environments:
    dev:
      var_file: "environments/dev.tfvars"
      auto_approve: true
    staging:
      var_file: "environments/staging.tfvars"
      auto_approve: false
    prod:
      var_file: "environments/prod.tfvars"
      auto_approve: false
      require_approval: true

# Multi-workspace orchestration
orchestration:
  workspaces:
    - name: network
      path: ./modules/network
      dependencies: []
    - name: compute
      path: ./modules/compute
      dependencies: [network]
    - name: database
      path: ./modules/database
      dependencies: [network]
    - name: application
      path: ./modules/application
      dependencies: [compute, database]

# Hooks configuration
hooks:
  enabled: true
  pre_init:
    - validate_backend
  pre_plan:
    - check_format
    - validate_variables
  pre_apply:
    - security_scan
    - estimate_cost
  post_apply:
    - notify_slack

# Output configuration
output:
  format: text  # text, json, yaml
  color: auto   # auto, always, never
  verbose: false
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TFK_CONFIG` | Path to configuration file | `./tfk.yaml` |
| `TFK_WORKING_DIR` | Working directory | `.` |
| `TFK_LOG_LEVEL` | Log level (debug, info, warn, error) | `info` |
| `TFK_NO_COLOR` | Disable colored output | `false` |
| `TFC_TOKEN` | Terraform Cloud API token | - |
| `TFC_ORGANIZATION` | Terraform Cloud organization | - |
| `TFK_SKIP_HOOKS` | Skip all hooks | `false` |
| `TFK_AUTO_APPROVE` | Auto-approve applies | `false` |

### Configuration Precedence

```
1. CLI Arguments (highest priority)
2. Environment Variables
3. Project Configuration (tfk.yaml)
4. User Configuration (~/.tfk/config.yaml)
5. Default Values (lowest priority)
```

---

## Error Handling

### Exception Hierarchy

```
TerraformikError (base)
├── ConfigurationError
│   ├── InvalidConfigError
│   ├── MissingConfigError
│   └── ConfigValidationError
├── TerraformError
│   ├── InitError
│   ├── PlanError
│   ├── ApplyError
│   ├── StateError
│   └── WorkspaceError
├── CloudError
│   ├── AuthenticationError
│   ├── AuthorizationError
│   ├── RateLimitError
│   ├── WorkspaceNotFoundError
│   └── RunError
├── HookError
│   ├── HookExecutionError
│   ├── HookTimeoutError
│   └── HookValidationError
└── ProvisionerError
    ├── ResourceCreationError
    └── ResourceValidationError
```

### Error Output Format

```
Error: Failed to execute terraform plan

Context:
  Command: terraform plan -var-file=dev.tfvars
  Working Directory: /path/to/terraform
  Exit Code: 1

Details:
  Error: Missing required variable "environment"

  on main.tf line 15, in variable "environment":
   15: variable "environment" {

  The variable "environment" is required but was not provided.

Suggestions:
  - Add the variable to your tfvars file: environment = "dev"
  - Set the environment variable: TF_VAR_environment=dev
  - Pass it via CLI: --var="environment=dev"

Documentation: https://terraformik.dev/docs/errors/missing-variable
```

---

## Security Considerations

### Credential Management

| Credential Type | Storage | Encryption |
|-----------------|---------|------------|
| TFC API Token | `~/.tfk/credentials.json` | AES-256 (keyring) |
| AWS Credentials | AWS credential chain | Native |
| State Encryption | Backend native | S3 SSE/KMS |

### Security Best Practices

1. **Never store secrets in configuration files**
   - Use environment variables
   - Use secret management tools (Vault, AWS Secrets Manager)

2. **Encrypt state files**
   - Enable backend encryption
   - Use customer-managed KMS keys

3. **Audit logging**
   - Log all operations
   - Track who applied what changes

4. **Access control**
   - Use Terraform Cloud teams
   - Implement approval workflows

### Security Scanning Integration

```yaml
security:
  scanners:
    - name: tfsec
      enabled: true
      config:
        exclude:
          - AWS006  # Specific rule to exclude
    - name: checkov
      enabled: true
      config:
        framework: terraform
    - name: terrascan
      enabled: false
```

---

## Development Roadmap

### Phase 1: Core CLI (MVP)

- [ ] Project structure and packaging
- [ ] Basic CLI framework (Typer)
- [ ] Terraform command wrapper
  - [ ] init, plan, apply, destroy
  - [ ] fmt, validate, output
- [ ] Configuration loading
- [ ] Basic error handling
- [ ] Logging and output formatting

### Phase 2: Terraform Cloud Integration

- [ ] Authentication flow
- [ ] Workspace management
- [ ] Run management
- [ ] Variable management
- [ ] State operations

### Phase 3: Pre-Hooks System

- [ ] Hook manager implementation
- [ ] Built-in validators
  - [ ] Backend validation
  - [ ] Variable validation
  - [ ] Format checking
- [ ] Security scanning integration
- [ ] Cost estimation integration
- [ ] Custom hook support

### Phase 4: Multi-Workspace Orchestration

- [ ] Workspace dependency graph
- [ ] Parallel execution
- [ ] Cross-workspace state references
- [ ] Orchestration configuration

### Phase 5: Advanced Features

- [ ] HCL parsing and generation
- [ ] State management utilities
- [ ] Migration tools
- [ ] Plugin system
- [ ] IDE integrations

---

## Dependencies

### Runtime Dependencies

```toml
[project]
dependencies = [
    "typer>=0.9.0",          # CLI framework
    "rich>=13.0.0",          # Terminal formatting
    "httpx>=0.24.0",         # HTTP client
    "pydantic>=2.0.0",       # Data validation
    "pyyaml>=6.0",           # YAML configuration
    "python-dotenv>=1.0.0",  # Environment loading
    "boto3>=1.28.0",         # AWS SDK
    "keyring>=24.0.0",       # Credential storage
]
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "mypy>=1.5.0",
    "ruff>=0.0.290",
    "black>=23.9.0",
    "pre-commit>=3.4.0",
]
```

---

## Testing Strategy

### Test Categories

| Category | Description | Tools |
|----------|-------------|-------|
| Unit Tests | Test individual components | pytest |
| Integration Tests | Test component interactions | pytest, testcontainers |
| E2E Tests | Full workflow testing | pytest, Terraform |
| Security Tests | Vulnerability scanning | bandit, safety |

### Test Structure

```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_terraform.py
│   ├── test_cloud_client.py
│   └── test_hooks.py
├── integration/
│   ├── test_terraform_execution.py
│   ├── test_cloud_api.py
│   └── test_hook_pipeline.py
├── e2e/
│   ├── test_full_workflow.py
│   └── test_multi_workspace.py
└── fixtures/
    ├── terraform/
    └── configs/
```

---

## Contributing

See [contributing.md](./contributing.md) for development setup and contribution guidelines.

---

## License

MIT License - See [LICENSE](../LICENSE) for details.
