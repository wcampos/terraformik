output "s3_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.state.id
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.locks.name
}

output "backend_config_hcl" {
  description = "Example backend config snippet (bucket, key, region, dynamodb_table, encrypt)"
  value       = <<-EOT
    bucket         = "${aws_s3_bucket.state.id}"
    key            = "${var.app_name}/${var.environment}/terraform.tfstate"
    region         = "${data.aws_region.current.name}"
    dynamodb_table = "${aws_dynamodb_table.locks.name}"
    encrypt        = true
  EOT
}
