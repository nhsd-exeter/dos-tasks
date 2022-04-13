resource "aws_security_group" "hk_lambda_sg" {
  name        = "${var.service_prefix}-hk-sg"
  description = "Generic SG for HK tasks"
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
  egress {
    description     = "Core DoS DB Access"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.core_dos_db_sg]
  }
  egress {
    description = "AWS API Outbound Access"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = local.standard_tags
}
