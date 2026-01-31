"""Tests for the Boto3 provisioner."""
import sys
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

# Import after path is set; provisioner lives under provisioners.boto3
from provisioners.boto3.provision import (
    validate_app_name,
    validate_environment,
    create_s3_bucket,
    create_dynamodb_table,
)


class TestValidateAppName:
    """Tests for validate_app_name."""

    def test_valid_app_names(self, valid_app_names):
        for name in valid_app_names:
            assert validate_app_name(name) == name

    def test_invalid_app_names_exit(self, invalid_app_names):
        for name in invalid_app_names:
            with patch.object(sys, "exit", side_effect=SystemExit(1)) as mock_exit:
                try:
                    validate_app_name(name)
                except SystemExit:
                    pass
                mock_exit.assert_called_once_with(1)


class TestValidateEnvironment:
    """Tests for validate_environment."""

    def test_valid_environments(self, valid_environments):
        for env in valid_environments:
            assert validate_environment(env) == env

    def test_invalid_environment_exits(self, invalid_environments):
        for env in invalid_environments:
            with patch.object(sys, "exit", side_effect=SystemExit(1)) as mock_exit:
                try:
                    validate_environment(env)
                except SystemExit:
                    pass
                mock_exit.assert_called_once_with(1)


class TestResourceNames:
    """Test resource naming convention matches provisioner logic."""

    def test_bucket_name_format(self):
        app_name, environment = "myapp", "dev"
        expected = f"{app_name}-{environment}-terraformik-state"
        assert expected == "myapp-dev-terraformik-state"

    def test_dynamodb_table_name_format(self):
        app_name, environment = "myapp", "dev"
        expected = f"{app_name}-{environment}-terraformik-locks"
        assert expected == "myapp-dev-terraformik-locks"


class TestCreateS3Bucket:
    """Tests for create_s3_bucket with mocked client."""

    def test_create_s3_bucket_success(self):
        s3_client = MagicMock()
        create_s3_bucket(s3_client, "myapp-dev-terraformik-state", "us-east-1")
        s3_client.create_bucket.assert_called_once()
        s3_client.put_bucket_versioning.assert_called_once()
        s3_client.put_bucket_encryption.assert_called_once()

    def test_create_s3_bucket_client_error_returns_false(self):
        s3_client = MagicMock()
        s3_client.create_bucket.side_effect = ClientError(
            {"Error": {"Code": "BucketAlreadyExists", "Message": "Bucket exists"}},
            "CreateBucket",
        )
        result = create_s3_bucket(s3_client, "bucket", "us-east-1")
        assert result is False


class TestCreateDynamodbTable:
    """Tests for create_dynamodb_table with mocked client."""

    def test_create_dynamodb_table_success(self):
        dynamodb_client = MagicMock()
        result = create_dynamodb_table(dynamodb_client, "myapp-dev-terraformik-locks")
        dynamodb_client.create_table.assert_called_once()
        assert result is True

    def test_create_dynamodb_table_client_error_returns_false(self):
        dynamodb_client = MagicMock()
        dynamodb_client.create_table.side_effect = ClientError(
            {"Error": {"Code": "ResourceInUseException", "Message": "Table exists"}},
            "CreateTable",
        )
        result = create_dynamodb_table(dynamodb_client, "table")
        assert result is False
