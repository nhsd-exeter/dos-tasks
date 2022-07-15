resource "aws_security_group" "migration_lambda_security_group" {
  #context = local.context

  name        = var.lambda_security_group_name
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
  tags        = local.context.tags
  description = "Security group for the migration lambda functions."
}

resource "aws_security_group_rule" "mig_lambda_egress" {
  type                     = "egress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.migration_lambda_security_group.id
  source_security_group_id = data.aws_security_group.db_security_group.id
  description              = "A rule to allow outgoing connections to the Source RDS PostgreSQL SG from the migration lambda Security Group"
}

resource "aws_security_group_rule" "mig_lambda_egress_443" {
  type              = "egress"
  from_port         = "443"
  to_port           = "443"
  protocol          = "tcp"
  security_group_id = aws_security_group.migration_lambda_security_group.id
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "A rule to allow outgoing connections AWS APIs from the migration lambda Security Group"
}

resource "aws_security_group_rule" "mig_lambda_ingress" {
  type                     = "ingress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.migration_lambda_security_group.id
  source_security_group_id = data.aws_security_group.db_security_group.id
  description              = "A rule to allow incoming connections from the Source RDS PostgreSQL SG to the migration lambda Security Group"
}

# We assume that the SG for the source, target and fallback DBs is the same
resource "aws_security_group_rule" "db_sg_egress" {
  type                     = "egress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  security_group_id        = data.aws_security_group.db_security_group.id
  source_security_group_id = aws_security_group.migration_lambda_security_group.id
  description              = "A rule to allow outgoing connections to the Source RDS PostgreSQL SG from the migration lambda Security Group"
}

resource "aws_security_group_rule" "db_sg_ingress" {
  type                     = "ingress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  security_group_id        = data.aws_security_group.db_security_group.id
  source_security_group_id = aws_security_group.migration_lambda_security_group.id
  description              = "A rule to allow incoming connections from the Source RDS PostgreSQL SG to the migration lambda Security Group"
}
