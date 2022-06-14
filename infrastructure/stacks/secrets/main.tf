resource "aws_secretsmanager_secret" "deployment_secrets" {
  tags = local.standard_tags
}
