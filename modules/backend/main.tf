# Terraform backend bootstrap: S3 bucket + DynamoDB table for state and locking.
# Use this module once per app/environment to create backend resources, then point
# your Terraform backend config at the outputs.

data "aws_region" "current" {}

resource "aws_s3_bucket" "state" {
  bucket = "${var.app_name}-${var.environment}-terraformik-state"

  tags = var.tags
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "locks" {
  name         = "${var.app_name}-${var.environment}-terraformik-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = var.tags
}
