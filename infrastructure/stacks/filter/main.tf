module "filter_lambda" {
  source                = "../../modules/lambda"
  name                  = "hk-filter"
  housekeeping_role_arn = data.aws_iam_role.housekeeping_role.arn
  image_uri             = "${var.aws_ecr}/${var.project_group_short}/${var.project_name_short}/hk-filter:${var.image_version}"
  subnet_ids            = local.private_subnets
  security_group_ids    = [data.aws_security_group.lambda_sg.id]
  timeout               = "20"

  splunk_firehose_subscription = var.splunk_firehose_subscription
  splunk_firehose_role         = var.splunk_firehose_role

  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
  service_prefix = var.service_prefix
  tags           = local.standard_tags

  env_vars = {
    "TASK"              = "filter"
    "PROFILE"           = var.profile,
    "SERVICE"           = var.service_tag_common,
    "SECRET_STORE"      = var.deployment_secrets,
    "SLACK_WEBHOOK_URL" = var.slack_webhook_url,
  }
}

resource "aws_lambda_permission" "hk_bucket_trigger" {
  statement_id   = "AllowExecutionFromS3Bucket"
  action         = "lambda:InvokeFunction"
  function_name  = module.filter_lambda.lambda_arn
  principal      = "s3.amazonaws.com"
  source_account = var.aws_account_id
  source_arn     = data.aws_s3_bucket.housekeeping_bucket.arn
}

resource "aws_s3_bucket_notification" "hk_bucket_notification" {
  bucket = data.aws_s3_bucket.housekeeping_bucket.id

  lambda_function {
    lambda_function_arn = module.filter_lambda.lambda_arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.hk_bucket_trigger]
}
