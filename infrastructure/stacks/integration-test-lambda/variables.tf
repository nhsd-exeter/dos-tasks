
# === Common ===================================================================

variable "terraform_platform_state_store" { description = "Name of the S3 bucket used to store the platform infrastructure terraform state" }

variable "vpc_terraform_state_key" { description = "The VPC key in the terraform state bucket" }

# === Stack Specific ============================================================



variable "security_group_name" { description = "The security group for the database" }

variable "source_db_secret_manager" { description = "Secret name where database secrets are stored" }

variable "db_secret_key" { description = "Secret key where database secrets are stored" }

variable "db_username" { description = "Database user name" }

variable "core_dos_python_libs" { description = "Core dos python library layer" }

variable "dos_service_policy_name" { description = "Name of the DoS Service policy to attach to the Lambda" }

variable "master_db_r53_record_name" { description = "Route 53 record for target database" }

variable "fallback_db_r53_record_name" { description = "Route 53 record for fallback database" }

variable "source_master_db_r53_record_name" { description = "Route 53 record for source database" }
variable "db_hosted_zone" { description = "Hosted zone for database" }

variable "lambda_security_group_name" { description = "The security group for the lambdas" }
variable "db_checks_lambda_function_name" { description = "Database checks Lambda function name" }
variable "db_checks_lambda_description" { description = "Description of Lambda function to run database checks" }
variable "db_prep_lambda_function_name" { description = "Advance sequences Lambda function name" }
variable "db_prep_lambda_description" { description = "Description of advance sequences Lambda function" }

variable "db_check_login_lambda_function_name" { description = "Database check login Lambda function name" }
variable "db_check_login_lambda_description" { description = "Description of Lambda function to run database login checks" }

variable "db_post_mig_clean_lambda_function_name" { description = "Database post migration cleanup Lambda function name" }
variable "db_post_mig_clean_lambda_description" { description = "Description of Lambda function to run post migration clean up" }
variable "db_post_mig_scripts_lambda_function_name" { description = "Database post migration scripts Lambda function name" }
variable "db_post_mig_scripts_lambda_description" { description = "Description of Lambda function to run post migration scripts" }
variable "lambda_runtime" { description = "Runtime environment" }

variable "post_mig_script_lambda_timeout" { description = "Lambda environment" }

variable "lambda_timeout" { description = "Lambda timeout" }
variable "lambda_memory_size" { description = "Memory size for Lambda" }

variable "db_port" { description = "Database port" }

variable "migration_lambda_iam_name" { description = "IAM name for role attached to migration lambda" }

variable "minimum_sequence_increment" {
  description = "Minimum number that target sequence should be ahead of source"
  default     = 500
}

variable "replication_max_no_polls" {
  description = "Maximum number of times to poll the target database to see if the change has been replicated."
  default     = 6
}

variable "replication_polling_interval" {
  description = "The time (in seconds) to wait before the next poll on the target database to see if the change has been replicated."
  default     = 5
}
