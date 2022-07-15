# Lambda
data "archive_file" "db_check_sql_scripts_lambda_function_archive" {
  type        = "zip"
  source_dir  = "${path.module}/functions/db-check-sql-scripts"
  output_path = "${path.module}/functions_zip/${var.db_checks_lambda_function_name}.zip"
}

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.terraform_platform_state_store
    key    = var.vpc_terraform_state_key
    region = var.aws_region
  }
}

data "aws_iam_policy" "iam_policy" {
  name = var.dos_service_policy_name
}

data "aws_security_group" "db_security_group" {
  name = var.security_group_name
}

data "aws_lambda_layer_version" "dos_python_libs" {
  layer_name = var.core_dos_python_libs
}
