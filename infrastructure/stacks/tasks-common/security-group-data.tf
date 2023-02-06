data "aws_security_group" "lambda_sg" {
  name = "${var.service_prefix}-hk-sg"
}
