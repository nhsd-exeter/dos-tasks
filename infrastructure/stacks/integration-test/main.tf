module "integration_test_lambda" {
  source                = "../../modules/lambda"
  name                  = "hk-integration-tester"
  housekeeping_role_arn = data.aws_iam_role.housekeeping_role.arn
  image_uri             = "${var.aws_ecr}/${var.project_group_short}/${var.project_name_short}/hk-integration-tester:${var.image_version}"
  subnet_ids            = local.private_subnets
  security_group_ids    = [data.aws_security_group.lambda_sg.id]
  timeout               = "900"

  splunk_firehose_subscription = var.splunk_firehose_subscription
  splunk_firehose_role         = var.splunk_firehose_role

  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  service_prefix = var.service_prefix
  tags           = local.standard_tags

  env_vars = {
    "TASK"              = "integration"
    "PROFILE"           = var.profile,
    "SERVICE"           = var.service_tag_common,
    "SECRET_STORE"      = var.deployment_secrets,
    "SLACK_WEBHOOK_URL" = var.slack_webhook_url,
  }
}
