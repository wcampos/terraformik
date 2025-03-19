bucket         = "${TF_VAR_app_name}-${TF_VAR_environment}-terraformik-state"
key            = "${TF_VAR_app_name}/${TF_VAR_environment}/terraform.tfstate"
region         = "${TF_VAR_aws_region}"
dynamodb_table = "${TF_VAR_app_name}-${TF_VAR_environment}-terraformik-locks"
encrypt        = true 