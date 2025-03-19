#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME=${1:-myapp}  # Default to myapp if not specified
ENVIRONMENT=${2:-dev}  # Default to dev if not specified
REGION=${3:-us-east-1}  # Default to us-east-1 if not specified

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo "Error: Environment must be one of: dev, staging, prod"
    exit 1
fi

# Validate app name
if [[ ! "$APP_NAME" =~ ^[a-z0-9-]+$ ]]; then
    echo "Error: App name must contain only lowercase letters, numbers, and hyphens"
    exit 1
fi

# Set resource names with app and environment prefix
BUCKET_NAME="${APP_NAME}-${ENVIRONMENT}-terraformik-state"
DYNAMODB_TABLE="${APP_NAME}-${ENVIRONMENT}-terraformik-locks"

# Create S3 bucket
echo "Creating S3 bucket for ${APP_NAME} in ${ENVIRONMENT} environment..."
aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION

# Enable versioning on the bucket
echo "Enabling versioning on S3 bucket..."
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled

# Enable server-side encryption
echo "Enabling server-side encryption..."
aws s3api put-bucket-encryption \
    --bucket $BUCKET_NAME \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Create DynamoDB table for state locking
echo "Creating DynamoDB table for state locking..."
aws dynamodb create-table \
    --table-name $DYNAMODB_TABLE \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $REGION

echo "Provisioning completed successfully for ${APP_NAME} in ${ENVIRONMENT} environment!" 