
# Look up for rds instance
# data "aws_db_instance" "rds_instance" {
#   db_instance_identifier = var.db_identifier
# }

data "aws_security_group" "datastore" {
  name = var.db_security_group_name
}
