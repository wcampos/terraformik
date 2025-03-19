# Terraformik

A collection of AWS provisioners for Terraform backend configuration, providing both AWS CLI and Boto3 implementations for setting up S3 and DynamoDB resources.

## Features

- AWS S3 bucket creation with versioning and encryption
- DynamoDB table for state locking
- Environment-specific resource management
- App-specific resource naming
- Multiple provisioner implementations (AWS CLI and Boto3)
- Makefile for easy provisioning and development

## Installation

```bash
pip install terraformik
```

## Usage

### Using Makefile (Recommended)

The project includes a Makefile for easy provisioning and development tasks:

```bash
# Show available commands
make help

# Provision resources using both methods
make provision-all APP_NAME=myapp ENVIRONMENT=dev

# Provision using specific method
make provision-cli APP_NAME=myapp ENVIRONMENT=dev
make provision-boto3 APP_NAME=myapp ENVIRONMENT=dev

# Provision for specific environment
make provision-dev APP_NAME=myapp
make provision-staging APP_NAME=myapp
make provision-prod APP_NAME=myapp

# Development tasks
make dev-setup
make test
make build
```

### Direct Usage

#### AWS CLI Provisioner

```bash
# Using the installed package
terraformik-cli myapp dev

# Or using the script directly
./provisioners/cli/provision.sh myapp dev
```

#### Boto3 Provisioner

```bash
# Using the installed package
terraformik-boto3 --app-name myapp --environment dev

# Or using the script directly
./provisioners/boto3/provision.py --app-name myapp --environment dev
```

## Workflows

The `workflows` directory contains GitHub Actions workflows that you can use as templates for your own projects:

- `terraform.yml`: Reusable workflow for Terraform operations
- `feature-branch.yml`: Workflow for feature branch pull requests
- `main-branch.yml`: Workflow for main branch merges

To use these workflows:

1. Copy the workflows to your project:
   ```bash
   make workflow-copy
   ```
   Or manually copy files from `workflows/` to `.github/workflows/`

2. Configure the required secrets in your GitHub repository
3. Customize the workflow parameters as needed

## Development

### Prerequisites

- Python 3.8 or higher
- AWS CLI (for CLI provisioner)
- AWS credentials configured
- Appropriate AWS permissions
- Make (for using Makefile)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/terraformik.git
   cd terraformik
   ```

2. Set up development environment:
   ```bash
   make dev-setup
   ```

3. Run tests:
   ```bash
   make test
   ```

### Building

```bash
make build
```

## Release Process

This project uses GitHub Actions for automated releases. When changes are pushed to the main branch:

1. A new version tag is automatically created
2. The package is built and published to PyPI
3. A GitHub release is created with release notes

### Required Secrets

- `PYPI_API_TOKEN`: PyPI API token for package publishing
- `GITHUB_TOKEN`: GitHub token for release creation (automatically provided)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 