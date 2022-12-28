resource "aws_lambda_function" "lambda" {
  function_name = "${var.service_prefix}-${var.name}-lambda"
  role          = var.houskeeping_role
  publish       = true
  package_type  = "Image"
  image_uri     = var.image_uri

  timeout     = var.timeout
  memory_size = var.memory_size

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.tags
  tracing_config {
    mode = "Active"
  }
  environment {
    variables = var.env_vars
  }
  depends_on = [
    var.housekeeping_role_name,
    aws_iam_role_policy.lambda_role_policy,
    aws_cloudwatch_log_group.lambda_log_group
  ]
}

resource "aws_lambda_function_event_invoke_config" "lambda_invoke_config" {
  function_name          = aws_lambda_function.lambda.function_name
  maximum_retry_attempts = var.retry_attempts
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.service_prefix}-${var.name}-lambda"
  retention_in_days = var.log_retention
  tags              = var.tags
}

resource "aws_cloudwatch_log_subscription_filter" "splunk_firehose_subscription" {
  name            = "${var.service_prefix}-${var.name}-log-subscription"
  role_arn        = "arn:aws:iam::${var.aws_account_id}:role/${var.splunk_firehose_role}"
  filter_pattern  = ""
  log_group_name  = aws_cloudwatch_log_group.lambda_log_group.name
  destination_arn = "arn:aws:firehose:${var.aws_region}:${var.aws_account_id}:deliverystream/${var.splunk_firehose_subscription}"
}
