resource "aws_secretsmanager_secret" "deployment_secrets" {
  name = "${var.service_prefix}/deployment"
  tags = local.standard_tags
}
