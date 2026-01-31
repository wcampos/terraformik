# Backend Module

Creates the AWS resources required for a Terraform S3 backend with DynamoDB state locking:

- **S3 bucket** – versioning and server-side encryption (AES256) enabled
- **DynamoDB table** – pay-per-request, single attribute `LockID` (String) as hash key

Naming matches the provisioners: `{app_name}-{environment}-terraformik-state` and `{app_name}-{environment}-terraformik-locks`.

## Usage

Use this module in a one-off “bootstrap” configuration (e.g. in a separate repo or directory that does not use this backend):

```hcl
module "backend" {
  source = "git::https://github.com/wcampos/terraformik.git//modules/backend?ref=main"

  app_name     = "myapp"
  environment  = "dev"
  tags         = { Project = "myapp", Env = "dev" }
}

output "backend_config" {
  value = module.backend.backend_config_hcl
}
```

Then run `terraform apply` once (with local or another backend), and use the outputs to configure your main Terraform backend (e.g. in GitHub Actions with Terraformik workflows).

## Requirements

- Terraform >= 1.0
- AWS provider

## Inputs

| Name         | Description                                           | Type           | Default |
|--------------|-------------------------------------------------------|----------------|---------|
| app_name     | Application name (lowercase, numbers, hyphens only)  | string         | -       |
| environment  | Environment: dev, staging, or prod                    | string         | -       |
| tags         | Tags for S3 bucket and DynamoDB table                | map(string)    | {}      |

## Outputs

| Name                 | Description                                  |
|----------------------|----------------------------------------------|
| s3_bucket_name       | S3 bucket name for state                     |
| dynamodb_table_name  | DynamoDB table name for locking              |
| backend_config_hcl   | Example backend config snippet (HCL)         |

## Notes

- Run this module with a backend that already exists (e.g. local or another S3 backend), or with `-backend=false` and then migrate state if needed.
- After applying, set your main Terraform config (or GitHub secrets) to use the output bucket, key, region, and dynamodb_table.
