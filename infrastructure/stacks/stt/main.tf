module "stt_lambda" {
  source             = "../../modules/lambda"
  name               = "hk-stt"
  image_uri          = "${var.aws_ecr}/${var.project_group_short}/${var.project_name_short}/hk-stt:${var.image_version}"
  subnet_ids         = local.private_subnets
  security_group_ids = [data.aws_security_group.lambda_sg.id]
  s3_bucket_arn      = data.aws_s3_bucket.housekeeping_bucket.arn
  timeout            = "900"

  splunk_firehose_subscription = var.splunk_firehose_subscription
  splunk_firehose_role         = var.splunk_firehose_role

  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  service_prefix = var.service_prefix
  tags           = local.standard_tags

  env_vars = {
    "TASK"              = "stt"
    "PROFILE"           = var.profile,
    "SERVICE"           = var.service_tag_common,
    "SECRET_STORE"      = var.deployment_secrets,
    "SLACK_WEBHOOK_URL" = var.slack_webhook_url,
  }
}
