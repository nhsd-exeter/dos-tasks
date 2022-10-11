module "integration_test_lambda" {
  source                       = "../../modules/lambda-zip"
  name                         = "hk-integration-tester-zip"
  subnet_ids                   = [data.terraform_remote_state.vpc.outputs.private_subnets[0], data.terraform_remote_state.vpc.outputs.private_subnets[1], data.terraform_remote_state.vpc.outputs.private_subnets[2]]
  security_group_ids           = [data.terraform_remote_state.security_groups.outputs.lambda_security_group_id]
  s3_bucket_arn                = data.terraform_remote_state.s3.outputs.s3_bucket_arn
  timeout                      = "900"
  splunk_firehose_subscription = var.splunk_firehose_subscription
  splunk_firehose_role         = var.splunk_firehose_role
  aws_region                   = var.aws_region
  aws_account_id               = var.aws_account_id
  service_prefix               = var.service_prefix
  tags                         = local.standard_tags
  layers                       = [data.aws_lambda_layer_version.uec_dos_tasks_python_libs.arn]
  env_vars = {
    "TASK"              = "integration",
    "PROFILE"           = var.profile,
    "SERVICE"           = var.service_tag_common,
    "SECRET_STORE"      = var.deployment_secrets,
    "SLACK_WEBHOOK_URL" = var.slack_webhook_url,
  }
}
