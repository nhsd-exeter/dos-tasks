resource "aws_lambda_function" "db_check_lambda_function" {
  filename         = data.archive_file.db_check_sql_scripts_lambda_function_archive.output_path
  function_name    = var.db_checks_lambda_function_name
  description      = var.db_checks_lambda_description
  role             = aws_iam_role.lambda_iam_role.arn
  handler          = "run_check_sql.lambda_handler"
  source_code_hash = data.archive_file.db_check_sql_scripts_lambda_function_archive.output_base64sha256
  runtime          = var.lambda_runtime
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size
  publish          = false
  tags             = local.context.tags
  layers           = [data.aws_lambda_layer_version.dos_python_libs.arn]
  environment {
    variables = {
      USERNAME                     = "${var.source_master_db_r53_record_name}.${var.db_hosted_zone}"
      TARGET_ENDPOINT              = "${var.master_db_r53_record_name}.${var.db_hosted_zone}"
      FALLBACK_ENDPOINT            = "${var.fallback_db_r53_record_name}.${var.db_hosted_zone}"
      PORT                         = var.db_port
      REGION                       = var.aws_region
      SECRET_NAME                  = var.source_db_secret_manager
      SECRET_KEY                   = var.db_secret_key
      MINIMUM_SEQUENCE_INCREMENT   = var.minimum_sequence_increment
      REPLICATION_MAX_NO_POLLS     = var.replication_max_no_polls
      REPLICATION_POLLING_INTERVAL = var.replication_polling_interval
    }
  }
  vpc_config {
    subnet_ids = [
      data.terraform_remote_state.vpc.outputs.private_subnets[0],
      data.terraform_remote_state.vpc.outputs.private_subnets[1],
      data.terraform_remote_state.vpc.outputs.private_subnets[2]
    ]
    security_group_ids = [aws_security_group.migration_lambda_security_group.id]
  }
}
