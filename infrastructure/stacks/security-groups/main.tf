resource "aws_security_group" "hk_lambda_sg" {
  name        = "${var.service_prefix}-hk-sg"
  description = "Generic SG for HK tasks"
  vpc_id      = data.aws_vpc.vpc[0].id
  egress {
    description     = "Core DoS DB Access"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [data.aws_security_group.datastore.id]
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

resource "aws_security_group_rule" "db_sg_ingress" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = data.aws_security_group.datastore.id
  source_security_group_id = aws_security_group.hk_lambda_sg.id
  description              = "A rule to allow incoming connections from hk lambda to RDS Security Group"
}
