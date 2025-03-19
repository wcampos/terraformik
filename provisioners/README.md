# Terraform Backend Provisioners

This directory contains different provisioners for setting up AWS resources required for Terraform state management. Each provisioner implements the same functionality but uses different tools and approaches.

## Quick Start

The easiest way to use these provisioners is through the Makefile:

```bash
# Show available commands
make help

# Provision resources using both methods
make provision-all APP_NAME=myapp ENVIRONMENT=dev

# Or use specific provisioner
make provision-cli APP_NAME=myapp ENVIRONMENT=dev
make provision-boto3 APP_NAME=myapp ENVIRONMENT=dev
```

## Available Provisioners

### 1. AWS CLI Provisioner (`cli/`)
A shell script-based provisioner that uses AWS CLI commands to create and configure resources.

**Usage:**
```bash
# Using Makefile (recommended)
make provision-cli APP_NAME=myapp ENVIRONMENT=dev

# Direct usage
./cli/provision.sh myapp dev
```

### 2. Boto3 Provisioner (`boto3/`)
A Python-based provisioner that uses the boto3 SDK to create and configure resources.

**Usage:**
```bash
# Using Makefile (recommended)
make provision-boto3 APP_NAME=myapp ENVIRONMENT=dev

# Direct usage
./boto3/provision.py --app-name myapp --environment dev
```

## Resources Created

Both provisioners create the following resources for each app and environment:

1. **S3 Bucket**
   - Name: `{app_name}-{environment}-terraformik-state` (e.g., `myapp-dev-terraformik-state`)
   - Region: Configurable (default: `us-east-1`)
   - Features:
     - Versioning enabled
     - Server-side encryption enabled (AES256)

2. **DynamoDB Table**
   - Name: `{app_name}-{environment}-terraformik-locks` (e.g., `myapp-dev-terraformik-locks`)
   - Purpose: State locking
   - Configuration:
     - Primary key: `LockID` (String)
     - Read capacity: 5 units
     - Write capacity: 5 units

## Prerequisites

### AWS CLI Provisioner
- AWS CLI installed
- AWS credentials configured
- Appropriate AWS permissions

### Boto3 Provisioner
- Python 3.x installed
- boto3 package installed (`pip install boto3`)
- AWS credentials configured
- Appropriate AWS permissions

## Environment Variables

The backend configuration uses the following environment variables:
- `TF_VAR_app_name`: Application name (lowercase letters, numbers, and hyphens only)
- `TF_VAR_environment`: Environment name (dev, staging, prod)
- `TF_VAR_aws_region`: AWS region

These variables should be set in your GitHub repository secrets for each environment.

## Error Handling

Both provisioners include error handling and will:
- Display detailed error messages if something goes wrong
- Exit with a non-zero status code on failure
- Continue with remaining operations even if one fails
- Validate environment names before proceeding
- Validate app names to ensure they contain only valid characters

## Security Considerations

1. The S3 bucket is created with:
   - Server-side encryption enabled
   - Versioning enabled for state file history
   - Region-specific configuration
   - App and environment-specific naming

2. The DynamoDB table is created with:
   - Minimal required capacity units
   - Simple key schema for state locking
   - App and environment-specific naming

## Customization

You can modify the following variables in either provisioner:
- Application name (lowercase letters, numbers, and hyphens only)
- Environment name (dev, staging, prod)
- AWS region
- Resource naming patterns

## Cleanup

To remove the created resources for a specific app and environment:

```bash
# Delete DynamoDB table
aws dynamodb delete-table --table-name {app_name}-{environment}-terraformik-locks

# Delete S3 bucket (must be empty)
aws s3 rb s3://{app_name}-{environment}-terraformik-state --force
```

## Troubleshooting

1. **Permission Issues**
   - Ensure AWS credentials are properly configured
   - Verify IAM permissions include:
     - `s3:CreateBucket`
     - `s3:PutBucketVersioning`
     - `s3:PutBucketEncryption`
     - `dynamodb:CreateTable`

2. **Resource Already Exists**
   - The provisioners will fail if resources already exist
   - Use the cleanup commands above to remove existing resources

3. **Region Issues**
   - Ensure the region is available in your AWS account
   - Some regions may require special configuration

4. **Environment Issues**
   - Verify environment name is one of: dev, staging, prod
   - Check if environment variables are properly set
   - Ensure GitHub environment secrets are configured

5. **App Name Issues**
   - Verify app name contains only lowercase letters, numbers, and hyphens
   - Check if app name is properly set in environment variables
   - Ensure app name is consistent across all configurations 