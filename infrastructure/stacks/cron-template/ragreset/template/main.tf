module "ragreset_lambda" {
  source                = "../../modules/lambda"
  name                  = "cron-ragreset-DB_NAME_TO_REPLACE"
  image_uri             = "${var.aws_ecr}/${var.project_group_short}/${var.project_name_short}/cron-ragreset:${var.image_version}"
  subnet_ids            = local.private_subnets
  security_group_ids    = [data.aws_security_group.lambda_sg.id]
  housekeeping_role_arn = data.aws_iam_role.housekeeping_role.arn
  timeout               = "900"

  splunk_firehose_subscription = var.splunk_firehose_subscription
  splunk_firehose_role         = var.splunk_firehose_role

  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  service_prefix = var.service_prefix
  tags           = local.standard_tags
  env_vars = {
    "TASK"              = "ragreset"
    "DB_NAME"           = "DB_NAME_TO_REPLACE"
    "TASK_TYPE"         = "cron"
    "PROFILE"           = var.profile,
    "SERVICE"           = var.service_tag_common,
    "SECRET_STORE"      = var.deployment_secrets,
    "SLACK_WEBHOOK_URL" = var.slack_webhook_url,
  }
}

resource "aws_cloudwatch_event_rule" "scheduled_event_rule" {
  name                = "${var.project_group_short}-${var.project_name_short}-ragreset-DB_NAME_TO_REPLACE-rule"
  description         = "Schedule for ragreset"
  schedule_expression = var.schedule_ragreset
}

resource "aws_cloudwatch_event_target" "check_frequency" {
  rule      = aws_cloudwatch_event_rule.scheduled_event_rule.name
  target_id = "lambda"
  arn       = module.ragreset_lambda.lambda_arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  action        = "lambda:InvokeFunction"
  function_name = module.ragreset_lambda.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled_event_rule.arn
}
