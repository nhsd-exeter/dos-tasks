resource "aws_secretsmanager_secrets" "deployment_secrets" {
  name = "${var.service_prefix}/deployment"
}
