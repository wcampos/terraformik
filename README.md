# Terraformik

A collection of reusable GitHub Actions workflows for Terraform operations with AWS backend support.

## Features

- Reusable Terraform workflows for different scenarios
- AWS S3 backend for state storage
- DynamoDB for state locking
- Automated validation and deployment
- Feature branch protection
- Main branch automation
- Supporting provisioners for AWS infrastructure setup
- GitHub environments support for configuration

## Quick Start

1. **Set up the backend infrastructure**
   ```bash
   # Clone this repository
   git clone https://github.com/yourusername/terraformik.git
   cd terraformik

   # Use the provisioners to create required AWS resources
   make provision-all APP_NAME=myapp ENVIRONMENT=dev
   ```

2. **Configure GitHub Environments**
   Create environments in your repository (e.g., `dev`, `staging`, `prod`) and add the following secrets:
   - `AWS_ACCESS_KEY_ID`: AWS access key
   - `AWS_SECRET_ACCESS_KEY`: AWS secret key
   - `TF_VAR_app_name`: Your application name
   - `TF_VAR_environment`: Environment name (dev, staging, prod)
   - `TF_VAR_aws_region`: AWS region
   - `TF_BACKEND_BUCKET`: S3 bucket name
   - `TF_BACKEND_KEY`: State file key
   - `TF_BACKEND_REGION`: AWS region
   - `TF_BACKEND_DYNAMODB_TABLE`: DynamoDB table name

## Available Workflows

### 1. Reusable Terraform Workflow
A reusable workflow that handles Terraform operations:
- Initialization
- Format checking
- Plan generation
- Apply execution
- State management

**Usage in your workflow:**
```yaml
name: Terraform Operations

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  terraform:
    uses: wcampos/terraformik/.github/workflows/terraform.yml@main
    environment: ${{ github.ref_name == 'main' && 'prod' || 'dev' }}
    with:
      terraform_version: '1.5.0'
      working_directory: 'terraform'
      terraform_workspace: ${{ github.ref_name == 'main' && 'prod' || 'dev' }}
      tf_vars_file: '${{ github.ref_name == 'main' && 'prod' || 'dev' }}.tfvars'
      backend_config: |
        bucket = "${{ secrets.TF_BACKEND_BUCKET }}"
        key = "${{ secrets.TF_BACKEND_KEY }}"
        region = "${{ secrets.TF_BACKEND_REGION }}"
        dynamodb_table = "${{ secrets.TF_BACKEND_DYNAMODB_TABLE }}"
        encrypt = true
      action: ${{ github.ref_name == 'main' && 'apply' || 'plan' }}
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### 2. Feature Branch Workflow
Handles pull requests to feature branches:
- Runs Terraform plan
- Validates changes
- Prevents direct applies

**Usage in your workflow:**
```yaml
name: Feature Branch Terraform

on:
  pull_request:
    branches: [ main ]

jobs:
  terraform:
    uses: wcampos/terraformik/.github/workflows/terraform.yml@main
    environment: dev
    with:
      terraform_version: '1.5.0'
      working_directory: 'terraform'
      terraform_workspace: 'dev'
      tf_vars_file: 'dev.tfvars'
      backend_config: |
        bucket = "${{ secrets.TF_BACKEND_BUCKET }}"
        key = "${{ secrets.TF_BACKEND_KEY }}"
        region = "${{ secrets.TF_BACKEND_REGION }}"
        dynamodb_table = "${{ secrets.TF_BACKEND_DYNAMODB_TABLE }}"
        encrypt = true
      action: 'plan'
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### 3. Main Branch Workflow
Manages merges to main branch:
- Runs Terraform plan
- Applies changes automatically
- Updates state files

**Usage in your workflow:**
```yaml
name: Main Branch Terraform

on:
  push:
    branches: [ main ]

jobs:
  terraform:
    uses: wcampos/terraformik/.github/workflows/terraform.yml@main
    environment: prod
    with:
      terraform_version: '1.5.0'
      working_directory: 'terraform'
      terraform_workspace: 'prod'
      tf_vars_file: 'prod.tfvars'
      backend_config: |
        bucket = "${{ secrets.TF_BACKEND_BUCKET }}"
        key = "${{ secrets.TF_BACKEND_KEY }}"
        region = "${{ secrets.TF_BACKEND_REGION }}"
        dynamodb_table = "${{ secrets.TF_BACKEND_DYNAMODB_TABLE }}"
        encrypt = true
      action: 'apply'
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Workflow Configuration

### Input Parameters

The reusable workflow accepts the following parameters:

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `terraform_version` | Version of Terraform to use | Yes | - |
| `working_directory` | Directory containing Terraform files | Yes | - |
| `terraform_workspace` | Terraform workspace to use | No | 'default' |
| `tf_vars_file` | Path to tfvars file | No | - |
| `backend_config` | Backend configuration | Yes | - |
| `action` | Action to perform (plan/apply) | Yes | - |

### Required Secrets

Each GitHub environment should have the following secrets:
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `TF_VAR_app_name`: Application name
- `TF_VAR_environment`: Environment name
- `TF_VAR_aws_region`: AWS region
- `TF_BACKEND_BUCKET`: S3 bucket name
- `TF_BACKEND_KEY`: State file key
- `TF_BACKEND_REGION`: AWS region
- `TF_BACKEND_DYNAMODB_TABLE`: DynamoDB table name

## Best Practices

1. **State Management**
   - Use separate state files for each environment
   - Enable state locking with DynamoDB
   - Use S3 for state storage
   - Use GitHub environments for environment-specific configurations

2. **Workflow Usage**
   - Always run plans on pull requests
   - Only apply changes on main branch
   - Use environment-specific variables
   - Use GitHub environments for secrets management

3. **Security**
   - Use GitHub environments for secrets
   - Rotate AWS credentials regularly
   - Use minimal required permissions
   - Keep sensitive configuration in environment secrets

## Troubleshooting

1. **Workflow Failures**
   - Check AWS credentials
   - Verify backend configuration
   - Ensure required secrets are set in the correct environment
   - Verify environment protection rules

2. **State Issues**
   - Verify S3 bucket exists
   - Check DynamoDB table
   - Validate state file permissions
   - Check environment-specific backend configuration

3. **Permission Issues**
   - Review AWS IAM roles
   - Check GitHub permissions
   - Verify environment secrets
   - Check environment protection rules

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 