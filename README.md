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
- Early validation on branch pushes
- Conventional commit validation
- Automated semantic versioning and releases

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

3. **Configure Conventional Commits**
   Add the following labels to your repository:
   - `feat`: New features
   - `fix`: Bug fixes
   - `docs`: Documentation changes
   - `style`: Code style changes
   - `refactor`: Code refactoring
   - `perf`: Performance improvements
   - `test`: Test changes
   - `build`: Build system changes
   - `ci`: CI configuration changes
   - `chore`: Maintenance tasks
   - `revert`: Reverted changes
   - `major`: Breaking changes
   - `minor`: New features
   - `patch`: Bug fixes

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
    uses: wcampos/terraformik/workflows/terraform.yml@main
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
    uses: wcampos/terraformik/workflows/terraform.yml@main
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
    uses: wcampos/terraformik/workflows/terraform.yml@main
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

### 4. Validate Branch Workflow
Validates and plans on any branch push:
- Runs format check
- Validates configuration
- Generates plan
- Excludes main branch

**Usage in your workflow:**
```yaml
name: Validate Branch Workflow

on:
  push:
    branches-ignore:
      - main

jobs:
  terraform:
    uses: wcampos/terraformik/workflows/terraform.yml@main
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

### 5. Conventional Commit Workflow
Validates commit messages against conventional commit format:
- Enforces commit message format
- Categorizes changes
- Supports semantic versioning

**Usage in your workflow:**
```yaml
name: Conventional Commit Check

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  conventional-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Conventional Commit Check
        uses: amannn/action-semantic-pull-request@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          types: |
            feat
            fix
            docs
            style
            refactor
            perf
            test
            build
            ci
            chore
            revert
```

### 6. Release Workflow
Automatically creates releases based on conventional commits:
- Generates semantic version numbers
- Creates release notes
- Tags releases
- Publishes releases

**Usage in your workflow:**
```yaml
name: Release

on:
  push:
    branches:
      - main

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Release
        uses: release-drafter/release-drafter@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          config-name: release-drafter.yml
          publish: true
          prerelease: false
          draft: false
          name-template: 'v$RESOLVED_VERSION'
          tag-template: 'v$RESOLVED_VERSION'
          categories:
            - title: '🚀 Features'
              labels:
                - 'feat'
                - 'enhancement'
            - title: '🐛 Bug Fixes'
              labels:
                - 'fix'
                - 'bugfix'
                - 'bug'
            - title: '🧰 Maintenance'
              labels:
                - 'chore'
                - 'documentation'
                - 'ci'
                - 'build'
                - 'perf'
                - 'refactor'
                - 'style'
                - 'test'
            - title: '📦 Dependencies'
              labels:
                - 'dependencies'
                - 'deps'
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
   - Validate changes early with branch push workflow
   - Follow conventional commit format for all commits

3. **Security**
   - Use GitHub environments for secrets
   - Rotate AWS credentials regularly
   - Use minimal required permissions
   - Keep sensitive configuration in environment secrets

4. **Versioning**
   - Use semantic versioning for releases
   - Tag commits with version numbers
   - Include detailed release notes
   - Categorize changes in releases

## Troubleshooting

1. **Workflow Failures**
   - Check AWS credentials
   - Verify backend configuration
   - Ensure required secrets are set in the correct environment
   - Verify environment protection rules
   - Check commit message format

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

4. **Release Issues**
   - Verify commit message format
   - Check release labels
   - Validate version numbers
   - Review release notes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
5. Follow conventional commit format
6. Add appropriate labels

## License

This project is licensed under the MIT License - see the LICENSE file for details. 