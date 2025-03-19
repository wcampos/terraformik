#!/usr/bin/env python3

import boto3
import sys
import argparse
import re
from botocore.exceptions import ClientError

def validate_environment(env):
    """Validate the environment name."""
    valid_envs = ['dev', 'staging', 'prod']
    if env not in valid_envs:
        print(f"Error: Environment must be one of: {', '.join(valid_envs)}")
        sys.exit(1)
    return env

def validate_app_name(app_name):
    """Validate the application name."""
    if not re.match(r'^[a-z0-9-]+$', app_name):
        print("Error: App name must contain only lowercase letters, numbers, and hyphens")
        sys.exit(1)
    return app_name

def create_s3_bucket(s3_client, bucket_name, region):
    """Create an S3 bucket with versioning and encryption enabled."""
    try:
        # Create bucket
        print(f"Creating S3 bucket {bucket_name}...")
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        
        # Enable versioning
        print("Enabling versioning...")
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        # Enable encryption
        print("Enabling server-side encryption...")
        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }
                ]
            }
        )
        
        print(f"Successfully created and configured S3 bucket {bucket_name}")
        return True
    except ClientError as e:
        print(f"Error creating S3 bucket: {e}")
        return False

def create_dynamodb_table(dynamodb_client, table_name):
    """Create a DynamoDB table for state locking."""
    try:
        print(f"Creating DynamoDB table {table_name}...")
        dynamodb_client.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'LockID',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'LockID',
                    'KeyType': 'HASH'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait for table to be created
        waiter = dynamodb_client.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        print(f"Successfully created DynamoDB table {table_name}")
        return True
    except ClientError as e:
        print(f"Error creating DynamoDB table: {e}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Provision AWS resources for Terraform backend')
    parser.add_argument('--app-name', '-a', default='myapp',
                      help='Application name (lowercase letters, numbers, and hyphens only)')
    parser.add_argument('--environment', '-e', default='dev',
                      help='Environment name (dev, staging, prod)')
    parser.add_argument('--region', '-r', default='us-east-1',
                      help='AWS region')
    args = parser.parse_args()

    # Validate inputs
    app_name = validate_app_name(args.app_name)
    environment = validate_environment(args.environment)
    region = args.region

    # Set resource names with app and environment prefix
    bucket_name = f"{app_name}-{environment}-terraformik-state"
    dynamodb_table = f"{app_name}-{environment}-terraformik-locks"
    
    # Initialize AWS clients
    session = boto3.Session(region_name=region)
    s3_client = session.client('s3')
    dynamodb_client = session.client('dynamodb')
    
    # Create resources
    s3_success = create_s3_bucket(s3_client, bucket_name, region)
    dynamodb_success = create_dynamodb_table(dynamodb_client, dynamodb_table)
    
    if s3_success and dynamodb_success:
        print(f"\nProvisioning completed successfully for {app_name} in {environment} environment!")
    else:
        print("\nProvisioning failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 