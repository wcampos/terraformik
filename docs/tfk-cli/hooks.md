# tfk Hooks Reference

Complete reference for the tfk pre and post execution hooks system.

---

## Table of Contents

1. [Overview](#overview)
2. [Hook Types](#hook-types)
3. [Built-in Hooks](#built-in-hooks)
4. [Custom Hooks](#custom-hooks)
5. [External Hooks](#external-hooks)
6. [Hook Configuration](#hook-configuration)
7. [Execution Context](#execution-context)
8. [Best Practices](#best-practices)

---

## Overview

Hooks allow you to run validation, security scanning, cost estimation, and other tasks before and after Terraform operations. They help enforce standards, catch issues early, and automate workflows.

### Hook Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         tfk Command Execution                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │      Load Configuration       │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       Run Pre-Hooks           │
                    │                               │
                    │  ┌─────────────────────────┐  │
                    │  │   validate_backend      │  │
                    │  │   check_format          │  │
                    │  │   validate_variables    │  │
                    │  │   security_scan         │  │
                    │  │   estimate_cost         │  │
                    │  └─────────────────────────┘  │
                    │                               │
                    │   ✓ All pass? Continue       │
                    │   ✗ Any fail? Stop           │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │    Execute Terraform Command  │
                    │                               │
                    │    terraform init/plan/apply  │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       Run Post-Hooks          │
                    │                               │
                    │  ┌─────────────────────────┐  │
                    │  │   save_plan_output      │  │
                    │  │   notify_slack          │  │
                    │  │   update_documentation  │  │
                    │  └─────────────────────────┘  │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │         Return Result         │
                    └───────────────────────────────┘
```

---

## Hook Types

### Pre-Hooks

Run before Terraform commands.

| Hook Type | Trigger | Common Uses |
|-----------|---------|-------------|
| `pre_init` | Before `terraform init` | Validate backend, check dependencies |
| `pre_plan` | Before `terraform plan` | Lint, format check, variable validation |
| `pre_apply` | Before `terraform apply` | Security scan, cost estimation, approval |
| `pre_destroy` | Before `terraform destroy` | Backup state, confirmation |

### Post-Hooks

Run after Terraform commands complete.

| Hook Type | Trigger | Common Uses |
|-----------|---------|-------------|
| `post_init` | After `terraform init` | Cache modules, verify providers |
| `post_plan` | After `terraform plan` | Save plan, notify team |
| `post_apply` | After `terraform apply` | Notify, update docs, tag resources |
| `post_destroy` | After `terraform destroy` | Cleanup, archive state |

---

## Built-in Hooks

### Validation Hooks

#### `validate_backend`

Validates that backend resources exist and are accessible.

**Type:** `pre_init`

**Configuration:**
```yaml
hooks:
  pre_init:
    - name: validate_backend
      enabled: true
      fail_on_error: true
      config:
        # Check S3 bucket exists
        check_s3_bucket: true

        # Check DynamoDB table exists
        check_dynamodb_table: true

        # Verify IAM permissions
        check_permissions: true

        # AWS region (optional, uses default)
        region: us-east-1
```

**Output:**
```
[validate_backend] Validating backend configuration...
  ✓ S3 bucket 'myapp-terraform-state' exists
  ✓ DynamoDB table 'myapp-terraform-locks' exists
  ✓ IAM permissions verified
[validate_backend] Backend validation passed
```

---

#### `check_format`

Checks that Terraform files are properly formatted.

**Type:** `pre_plan`

**Configuration:**
```yaml
hooks:
  pre_plan:
    - name: check_format
      enabled: true
      fail_on_error: true
      config:
        # Check files recursively
        recursive: true

        # Check only (don't modify)
        check_only: true

        # Paths to check
        paths:
          - .
          - ./modules

        # Files to exclude
        exclude:
          - .terraform
          - vendor
```

**Output:**
```
[check_format] Checking Terraform formatting...
  ✗ main.tf - needs formatting
  ✗ modules/network/main.tf - needs formatting
[check_format] 2 files need formatting

Run 'tfk fmt' to fix formatting issues.
```

---

#### `validate_variables`

Validates that required variables are set and match patterns.

**Type:** `pre_plan`

**Configuration:**
```yaml
hooks:
  pre_plan:
    - name: validate_variables
      enabled: true
      fail_on_error: true
      config:
        # Required variables
        required:
          - environment
          - region
          - app_name

        # Variable patterns (regex)
        patterns:
          environment: "^(dev|staging|prod)$"
          region: "^[a-z]{2}-[a-z]+-[0-9]$"
          app_name: "^[a-z][a-z0-9-]{2,30}$"

        # Variable types
        types:
          instance_count: integer
          enable_monitoring: boolean

        # Variable ranges
        ranges:
          instance_count:
            min: 1
            max: 100
```

**Output:**
```
[validate_variables] Validating variables...
  ✓ environment = "dev" (matches pattern)
  ✓ region = "us-east-1" (matches pattern)
  ✗ app_name = "My App" (does not match pattern ^[a-z][a-z0-9-]{2,30}$)
[validate_variables] Validation failed
```

---

#### `check_secrets`

Scans for hardcoded secrets in Terraform files.

**Type:** `pre_plan`

**Configuration:**
```yaml
hooks:
  pre_plan:
    - name: check_secrets
      enabled: true
      fail_on_error: true
      config:
        # Patterns to detect (regex)
        patterns:
          - name: password
            pattern: 'password\s*=\s*"[^"]+(?<!var\.password)"'
            severity: high

          - name: api_key
            pattern: 'api_key\s*=\s*"[A-Za-z0-9]{20,}"'
            severity: high

          - name: secret
            pattern: 'secret\s*=\s*"[^"]+(?<!var\.secret)"'
            severity: high

          - name: aws_access_key
            pattern: 'AKIA[0-9A-Z]{16}'
            severity: critical

        # Files to scan
        include:
          - "**/*.tf"
          - "**/*.tfvars"

        # Files to exclude
        exclude:
          - "**/*.tfvars.example"
          - "**/test/**"

        # Severity threshold
        fail_on_severity: high  # critical, high, medium, low
```

**Output:**
```
[check_secrets] Scanning for secrets...
  ✗ HIGH: Hardcoded password found in main.tf:15
    password = "mysecret123"
  ✗ CRITICAL: AWS access key found in providers.tf:8
    AKIAIOSFODNN7EXAMPLE
[check_secrets] Found 2 potential secrets
```

---

### Security Hooks

#### `security_scan`

Runs security scanning tools on Terraform code.

**Type:** `pre_apply`

**Configuration:**
```yaml
hooks:
  pre_apply:
    - name: security_scan
      enabled: true
      fail_on_error: true
      config:
        # Scanner to use: tfsec, checkov, terrascan
        scanner: tfsec

        # Severity threshold
        severity_threshold: medium  # critical, high, medium, low

        # Fail on specific severities
        fail_on_critical: true
        fail_on_high: true
        fail_on_medium: false
        fail_on_low: false

        # Rules to exclude
        exclude_rules:
          - AWS006  # Specific tfsec rule
          - CKV_AWS_1  # Specific checkov rule

        # Custom rules directory
        custom_rules_dir: ./security-rules

        # Output format
        output_format: text  # text, json, sarif

        # Save report
        save_report: true
        report_path: ./security-report.json

        # Scanner-specific options
        tfsec_options:
          minimum_severity: MEDIUM
          include_passed: false

        checkov_options:
          framework: terraform
          compact: true
```

**Output:**
```
[security_scan] Running tfsec security scan...

Results:
  CRITICAL: 1
  HIGH: 3
  MEDIUM: 5
  LOW: 2

Critical Issues:
  ✗ AWS017: IAM policy allows all actions
    Location: iam.tf:25-35

High Issues:
  ✗ AWS002: S3 bucket does not have logging enabled
    Location: s3.tf:10-20
  ✗ AWS004: S3 bucket does not have versioning enabled
    Location: s3.tf:10-20
  ✗ AWS009: Security group allows ingress from 0.0.0.0/0
    Location: security_groups.tf:15-25

[security_scan] Scan failed: Found 1 CRITICAL and 3 HIGH severity issues
```

---

### Cost Hooks

#### `estimate_cost`

Estimates infrastructure costs using Infracost or similar tools.

**Type:** `pre_apply`

**Configuration:**
```yaml
hooks:
  pre_apply:
    - name: estimate_cost
      enabled: true
      fail_on_error: false
      config:
        # Cost estimation provider
        provider: infracost

        # API key (use environment variable)
        api_key: ${INFRACOST_API_KEY}

        # Monthly cost threshold (fail if exceeded)
        threshold_monthly: 1000

        # Require manual approval above this amount
        require_approval_above: 500

        # Show cost breakdown
        show_breakdown: true

        # Compare with current costs
        show_diff: true

        # Currency
        currency: USD

        # Save cost report
        save_report: true
        report_path: ./cost-report.json

        # Infracost-specific options
        infracost_options:
          usage_file: infracost-usage.yml
          show_skipped: false
```

**Output:**
```
[estimate_cost] Estimating infrastructure costs...

Project: myapp-infrastructure

Monthly Cost Estimate:
┌─────────────────────────────────────────────────────────────┐
│ Resource                        │ Monthly Cost │ Change    │
├─────────────────────────────────┼──────────────┼───────────┤
│ aws_instance.web (x3)           │ $125.00      │ +$125.00  │
│ aws_db_instance.main            │ $350.00      │ -         │
│ aws_lb.main                     │ $25.00       │ -         │
│ aws_s3_bucket.assets            │ $5.00        │ +$5.00    │
│ aws_cloudwatch_log_group.app    │ $10.00       │ +$10.00   │
├─────────────────────────────────┼──────────────┼───────────┤
│ Total                           │ $515.00      │ +$140.00  │
└─────────────────────────────────────────────────────────────┘

⚠ Monthly cost ($515.00) exceeds approval threshold ($500.00)
  Manual approval required to proceed.

[estimate_cost] Cost estimation completed
```

---

### Notification Hooks

#### `notify_slack`

Sends notifications to Slack.

**Type:** `post_apply`, `post_destroy`

**Configuration:**
```yaml
hooks:
  post_apply:
    - name: notify_slack
      enabled: true
      fail_on_error: false
      config:
        # Slack webhook URL
        webhook_url: ${SLACK_WEBHOOK_URL}

        # Channel to post to
        channel: "#infrastructure"

        # Bot username
        username: "Terraformik"

        # Bot icon
        icon_emoji: ":terraform:"

        # Message template (supports variables)
        message_template: |
          *Terraform Apply Completed*

          Environment: `{{ environment }}`
          Workspace: `{{ workspace }}`
          User: `{{ user }}`

          Changes:
          • Added: {{ changes.add }}
          • Changed: {{ changes.change }}
          • Destroyed: {{ changes.destroy }}

        # Include plan details
        include_plan: false

        # Include resource list
        include_resources: true
        max_resources: 10

        # Notify on success only
        notify_on_success: true

        # Notify on failure
        notify_on_failure: true

        # Mention users on failure
        mention_on_failure:
          - "@oncall"
```

---

#### `notify_teams`

Sends notifications to Microsoft Teams.

**Type:** `post_apply`, `post_destroy`

**Configuration:**
```yaml
hooks:
  post_apply:
    - name: notify_teams
      enabled: true
      fail_on_error: false
      config:
        # Teams webhook URL
        webhook_url: ${TEAMS_WEBHOOK_URL}

        # Card title
        title: "Terraform Apply Completed"

        # Theme color (hex)
        theme_color: "00FF00"

        # Include facts
        include_facts:
          - name: Environment
            value: "{{ environment }}"
          - name: Workspace
            value: "{{ workspace }}"
          - name: Changes
            value: "+{{ changes.add }} ~{{ changes.change }} -{{ changes.destroy }}"
```

---

### Documentation Hooks

#### `update_documentation`

Auto-generates documentation from Terraform code.

**Type:** `post_apply`

**Configuration:**
```yaml
hooks:
  post_apply:
    - name: update_documentation
      enabled: true
      fail_on_error: false
      config:
        # Tool to use: terraform-docs
        tool: terraform-docs

        # Output file
        output_file: ./docs/INFRASTRUCTURE.md

        # Documentation format
        format: markdown table

        # Include sections
        sections:
          - header
          - requirements
          - providers
          - modules
          - resources
          - inputs
          - outputs

        # Sort items
        sort_by: name  # name, required, type

        # Include descriptions
        include_descriptions: true

        # terraform-docs options
        terraform_docs_options:
          indent: 2
          hide_empty: true
          escape: true
```

---

### State Hooks

#### `backup_state`

Backs up Terraform state before destructive operations.

**Type:** `pre_destroy`

**Configuration:**
```yaml
hooks:
  pre_destroy:
    - name: backup_state
      enabled: true
      fail_on_error: true
      config:
        # Backup directory
        backup_dir: ./state-backups

        # Backup filename pattern
        filename_pattern: "terraform-{{ workspace }}-{{ timestamp }}.tfstate"

        # Compress backups
        compress: true

        # Retention policy
        retention:
          max_backups: 10
          max_age_days: 30

        # Upload to S3
        upload_s3:
          enabled: true
          bucket: myapp-state-backups
          prefix: terraform/
```

---

## Custom Hooks

### Python Hook

Create custom hooks in Python:

```python
# hooks/tag_validator.py
from terraformik.hooks import Hook, HookResult, ExecutionContext, HookType


class TagValidatorHook(Hook):
    """
    Validates that all AWS resources have required tags.
    """

    name = "tag_validator"
    description = "Ensure all resources have required tags"
    hook_type = HookType.PRE_APPLY
    fail_on_error = True

    def __init__(self, required_tags: list[str] | None = None):
        self.required_tags = required_tags or ["Environment", "Owner", "CostCenter"]

    def execute(self, context: ExecutionContext) -> HookResult:
        """Execute tag validation."""
        plan = context.get_plan()

        if not plan:
            return HookResult(
                success=False,
                message="No plan available for validation"
            )

        violations = []

        for change in plan.resource_changes:
            # Only check creates and updates
            if change.action not in ("create", "update"):
                continue

            # Skip resources that don't support tags
            if not self._supports_tags(change.type):
                continue

            # Get tags from the planned resource
            tags = change.after.get("tags", {}) or {}

            # Check for required tags
            missing = [tag for tag in self.required_tags if tag not in tags]

            if missing:
                violations.append({
                    "resource": change.address,
                    "missing_tags": missing
                })

        if violations:
            message = "Missing required tags:\n"
            for v in violations:
                message += f"  - {v['resource']}: {', '.join(v['missing_tags'])}\n"

            return HookResult(
                success=False,
                message=message,
                data={"violations": violations}
            )

        return HookResult(
            success=True,
            message=f"All resources have required tags: {', '.join(self.required_tags)}"
        )

    def _supports_tags(self, resource_type: str) -> bool:
        """Check if resource type supports tags."""
        # AWS resources that support tags
        taggable_prefixes = [
            "aws_instance",
            "aws_vpc",
            "aws_subnet",
            "aws_security_group",
            "aws_s3_bucket",
            "aws_db_instance",
            "aws_lambda_function",
            "aws_ecs_",
            "aws_eks_",
        ]
        return any(resource_type.startswith(prefix) for prefix in taggable_prefixes)
```

### Register Custom Hook

```yaml
# tfk.yaml
hooks:
  pre_apply:
    - name: tag_validator
      path: ./hooks/tag_validator.py
      enabled: true
      fail_on_error: true
      config:
        required_tags:
          - Environment
          - Owner
          - CostCenter
          - Project
```

### Hook Class Reference

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HookType(str, Enum):
    PRE_INIT = "pre_init"
    POST_INIT = "post_init"
    PRE_PLAN = "pre_plan"
    POST_PLAN = "post_plan"
    PRE_APPLY = "pre_apply"
    POST_APPLY = "post_apply"
    PRE_DESTROY = "pre_destroy"
    POST_DESTROY = "post_destroy"


@dataclass
class HookResult:
    """Result of hook execution."""
    success: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0


@dataclass
class ExecutionContext:
    """Context passed to hooks."""
    command: str
    working_dir: Path
    config: TfkConfig
    terraform: TerraformExecutor
    state: dict | None = None
    plan: TerraformPlan | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    environment: str = ""
    workspace: str = ""
    user: str = ""

    def get_state(self) -> dict:
        """Get current Terraform state."""
        ...

    def get_plan(self) -> TerraformPlan | None:
        """Get current plan if available."""
        ...

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable value."""
        ...

    def get_output(self, name: str) -> Any:
        """Get a Terraform output value."""
        ...


class Hook(ABC):
    """Base class for hooks."""

    # Hook identifier
    name: str

    # Human-readable description
    description: str = ""

    # When the hook runs
    hook_type: HookType

    # Whether failure stops execution
    fail_on_error: bool = True

    # Timeout in seconds
    timeout: int = 60

    @abstractmethod
    def execute(self, context: ExecutionContext) -> HookResult:
        """
        Execute the hook.

        Args:
            context: Execution context with state, plan, and config

        Returns:
            HookResult indicating success or failure
        """
        pass

    def validate_config(self, config: dict) -> bool:
        """
        Validate hook configuration.

        Override to add custom validation.
        """
        return True
```

---

## External Hooks

Run external scripts or commands as hooks.

### Shell Script Hook

```yaml
hooks:
  pre_apply:
    - name: custom_validation
      type: external
      command: ./scripts/validate.sh
      timeout: 120
      fail_on_error: true
      config:
        # Pass arguments
        args:
          - --environment
          - "{{ environment }}"
          - --workspace
          - "{{ workspace }}"

        # Environment variables
        env:
          TF_VAR_environment: "{{ environment }}"
          PLAN_FILE: "{{ plan_file }}"

        # Working directory
        working_dir: ./scripts

        # Expected exit codes for success
        success_exit_codes:
          - 0
          - 2  # Custom success code
```

### Script Example

```bash
#!/bin/bash
# scripts/validate.sh

set -e

ENVIRONMENT=""
WORKSPACE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Validating for environment: $ENVIRONMENT, workspace: $WORKSPACE"

# Custom validation logic
if [[ "$ENVIRONMENT" == "prod" ]]; then
    # Production-specific checks
    echo "Running production validations..."

    # Check if it's within deployment window
    HOUR=$(date +%H)
    if [[ $HOUR -lt 9 || $HOUR -gt 17 ]]; then
        echo "ERROR: Production deployments only allowed 9am-5pm"
        exit 1
    fi
fi

echo "Validation passed"
exit 0
```

### Docker Hook

Run hooks in Docker containers:

```yaml
hooks:
  pre_apply:
    - name: security_scan_docker
      type: docker
      image: aquasec/tfsec:latest
      command: /tfsec
      args:
        - --format=json
        - --out=/output/report.json
        - /src
      volumes:
        - ".:/src:ro"
        - "./reports:/output"
      timeout: 300
      fail_on_error: true
```

---

## Hook Configuration

### Global Settings

```yaml
hooks:
  # Enable/disable all hooks
  enabled: true

  # Stop on first hook failure
  fail_fast: true

  # Global timeout (seconds)
  timeout: 300

  # Custom hooks directory
  custom_hooks_dir: ./hooks

  # Hook execution order
  # Hooks run in the order listed, unless dependencies are specified

  # Parallel execution (experimental)
  parallel:
    enabled: false
    max_parallel: 3
```

### Per-Hook Settings

```yaml
hooks:
  pre_apply:
    - name: security_scan
      # Enable/disable this hook
      enabled: true

      # Fail operation if hook fails
      fail_on_error: true

      # Hook timeout (overrides global)
      timeout: 120

      # Conditions for running
      conditions:
        # Only run for specific environments
        environments:
          - staging
          - prod

        # Only run for specific workspaces
        workspaces:
          - "*-prod"

        # Only run if changes detected
        only_on_changes: true

        # Only run on specific resource types
        resource_types:
          - aws_security_group
          - aws_iam_*

      # Hook-specific configuration
      config:
        scanner: tfsec
        severity_threshold: high
```

### Conditional Execution

```yaml
hooks:
  pre_apply:
    # Run for all environments
    - name: check_format
      enabled: true

    # Run only for production
    - name: security_scan
      enabled: true
      conditions:
        environments: [prod]

    # Run only when specific resources change
    - name: database_validation
      enabled: true
      conditions:
        resource_types:
          - aws_db_instance
          - aws_rds_cluster

    # Run only on specific days
    - name: cost_estimation
      enabled: true
      conditions:
        schedule:
          days: [monday, wednesday, friday]

    # Run based on file changes
    - name: module_validation
      enabled: true
      conditions:
        file_patterns:
          - "modules/**/*.tf"
```

---

## Execution Context

### Available Variables

Hooks have access to these context variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ environment }}` | Current environment | `prod` |
| `{{ workspace }}` | Terraform workspace | `default` |
| `{{ working_dir }}` | Working directory | `/app/infrastructure` |
| `{{ user }}` | Current user | `john@example.com` |
| `{{ timestamp }}` | Current timestamp | `2024-01-15T10:30:00Z` |
| `{{ plan_file }}` | Plan file path | `./plan.tfplan` |
| `{{ changes.add }}` | Resources to add | `5` |
| `{{ changes.change }}` | Resources to change | `2` |
| `{{ changes.destroy }}` | Resources to destroy | `1` |

### Context Methods

In Python hooks:

```python
def execute(self, context: ExecutionContext) -> HookResult:
    # Get current state
    state = context.get_state()

    # Get plan (available in post_plan, pre_apply)
    plan = context.get_plan()

    # Get a variable
    env = context.get_variable("environment")

    # Get a Terraform output
    vpc_id = context.get_output("vpc_id")

    # Access configuration
    config = context.config

    # Access Terraform executor
    terraform = context.terraform
```

---

## Best Practices

### 1. Order Hooks Appropriately

```yaml
hooks:
  pre_plan:
    # 1. Format check (fast, no external deps)
    - check_format

    # 2. Variable validation (fast)
    - validate_variables

    # 3. Secret scanning (medium)
    - check_secrets

  pre_apply:
    # 1. Security scan (important, may be slow)
    - security_scan

    # 2. Cost estimation (informational)
    - name: estimate_cost
      fail_on_error: false
```

### 2. Use Appropriate Fail Behavior

```yaml
hooks:
  pre_apply:
    # Critical - must pass
    - name: security_scan
      fail_on_error: true

    # Informational - shouldn't block
    - name: estimate_cost
      fail_on_error: false

    # Warning only
    - name: best_practices_check
      fail_on_error: false
```

### 3. Set Reasonable Timeouts

```yaml
hooks:
  pre_apply:
    # Quick validation
    - name: validate_variables
      timeout: 10

    # Security scan may take longer
    - name: security_scan
      timeout: 300

    # Cost estimation with API calls
    - name: estimate_cost
      timeout: 120
```

### 4. Use Conditions Wisely

```yaml
hooks:
  pre_apply:
    # Always run format check
    - name: check_format

    # Only run expensive scans in CI or for prod
    - name: security_scan
      conditions:
        environments: [staging, prod]

    # Cost estimation only for significant changes
    - name: estimate_cost
      conditions:
        only_on_changes: true
        min_changes: 5
```

### 5. Provide Clear Error Messages

```python
class MyHook(Hook):
    def execute(self, context: ExecutionContext) -> HookResult:
        if not self.validate():
            return HookResult(
                success=False,
                message="""
Validation failed: Missing required tags

The following resources are missing required tags:
  - aws_instance.web: missing 'Owner', 'CostCenter'
  - aws_s3_bucket.data: missing 'Environment'

To fix this, add the following tags to each resource:
  tags = {
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
  }

Documentation: https://docs.example.com/tagging-policy
                """.strip(),
                data={"violations": self.violations}
            )
```

### 6. Cache Hook Results

For expensive operations:

```python
class ExpensiveHook(Hook):
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes

    def execute(self, context: ExecutionContext) -> HookResult:
        cache_key = self._get_cache_key(context)

        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached['timestamp'] < self._cache_ttl:
                return cached['result']

        result = self._do_expensive_operation(context)

        self._cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }

        return result
```

---

## Troubleshooting

### View Hook Execution

```bash
# Run with verbose output
tfk plan --verbose

# Run specific hook
tfk hooks run security_scan --verbose

# List configured hooks
tfk hooks list
```

### Debug Hook Issues

```bash
# Enable debug logging
export TFK_LOG_LEVEL=debug
tfk plan

# Run hooks in isolation
tfk hooks run validate_variables --debug
```

### Skip Hooks

```bash
# Skip all hooks
tfk apply --skip-hooks

# Skip specific hook
tfk apply --skip-hook=estimate_cost
```

---

## See Also

- [Configuration Reference](./configuration.md)
- [API Reference](./api.md)
- [User Guide](./user-guide.md)
