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
    description     = "Core DoS Performance DB Access"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [data.aws_security_group.datastore_performance.id]
  }

  egress {
    description     = "Core DoS Regression DB Access"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [data.aws_security_group.datastore_regression.id]
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
  description              = "A rule to allow incoming connections from hk lambda to Datastore Security Group"
}

resource "aws_security_group_rule" "db_perf_sg_ingress" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = data.aws_security_group.datastore_performance.id
  source_security_group_id = aws_security_group.hk_lambda_sg.id
  description              = "A rule to allow incoming connections from hk lambda to Performance Datastore Security Group"
}

resource "aws_security_group_rule" "db_regression_sg_ingress" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = data.aws_security_group.datastore.id
  source_security_group_id = aws_security_group.hk_lambda_sg.id
  description              = "A rule to allow incoming connections from hk lambda to Regression Datastore Security Group"
}
