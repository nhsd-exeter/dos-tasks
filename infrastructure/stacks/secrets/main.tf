resource "aws_secretsmanager_secret" "deployment_secrets" {
  name = "${var.service_prefix}/deployment"
  tags = local.standard_tags
}

resource "aws_secretsmanager_secret" "slack_secrets" {
  count = var.sm_required ? 1 : 0
  name  = "${var.service_prefix}/slack"
  tags  = local.standard_tags
}
