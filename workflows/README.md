# Terraform GitHub Actions Workflows

This repository contains reusable GitHub Actions workflows for Terraform operations. The workflows are designed to handle different scenarios in your Terraform deployment process.

## Available Workflows

### 1. Reusable Terraform Workflow (`terraform.yml`)
This is the main reusable workflow that contains all the Terraform operations. It can be called by other workflows with different parameters.

#### Input Parameters
- `terraform_version`: Version of Terraform to use
- `working_directory`: Directory containing Terraform configuration
- `terraform_workspace`: Terraform workspace to use
- `tf_vars_file`: (Optional) Terraform variables file
- `backend_config`: (Optional) Terraform backend configuration file
- `action`: Action to perform (validate, plan, or apply)

#### Required Secrets
- `TF_VAR_aws_access_key`: AWS access key
- `TF_VAR_aws_secret_key`: AWS secret key
- `TF_VAR_aws_region`: AWS region

### 2. Feature Branch Workflow (`feature-branch.yml`)
This workflow runs on pull requests to the main branch. It performs:
- Terraform format check
- Terraform initialization
- Terraform validation
- Terraform plan

### 3. Main Branch Workflow (`main-branch.yml`)
This workflow runs on pushes to the main branch. It performs:
- Terraform format check
- Terraform initialization
- Terraform validation
- Terraform plan
- Terraform apply

## How to Use

1. Copy the workflow files to your repository's `.github/workflows` directory.

2. Configure the required secrets in your repository:
   - Go to Settings > Secrets and variables > Actions
   - Add the following secrets:
     - `TF_VAR_aws_access_key`
     - `TF_VAR_aws_secret_key`
     - `TF_VAR_aws_region`

3. Customize the workflow parameters in `feature-branch.yml` and `main-branch.yml`:
   - `terraform_version`
   - `working_directory`
   - `terraform_workspace`
   - `tf_vars_file`
   - `backend_config`

## Workflow Behavior

### Feature Branches
- When a pull request is created against main:
  - Runs format check
  - Initializes Terraform
  - Validates configuration
  - Creates a plan
  - Does NOT apply changes

### Main Branch
- When changes are merged to main:
  - Runs format check
  - Initializes Terraform
  - Validates configuration
  - Creates a plan
  - Automatically applies changes

## Best Practices

1. Always review the plan output in pull requests before merging
2. Use different workspaces for different environments (dev, staging, prod)
3. Keep your Terraform version consistent across all environments
4. Use variables files to manage environment-specific configurations
5. Configure backend settings appropriately for your state management

## Troubleshooting

Common issues and solutions:

1. **Workflow fails to initialize**
   - Check if backend configuration is correct
   - Verify AWS credentials are valid
   - Ensure working directory is correct

2. **Plan/Apply fails**
   - Review the error messages in the workflow logs
   - Check if all required variables are provided
   - Verify AWS region and credentials

3. **Format check fails**
   - Run `terraform fmt` locally to fix formatting issues
   - Commit the formatted files 