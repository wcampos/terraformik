variable "app_name" {
  description = "Application name (lowercase letters, numbers, hyphens only)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.app_name))
    error_message = "app_name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "tags" {
  description = "Tags to apply to S3 bucket and DynamoDB table"
  type        = map(string)
  default     = {}
}
