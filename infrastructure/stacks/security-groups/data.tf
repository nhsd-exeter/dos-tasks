
# Look up for rds instance
data "aws_db_instance" "rds_instance" {
  db_instance_identifier = var.db_identifier
}
