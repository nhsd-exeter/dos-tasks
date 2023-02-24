data "aws_security_group" "datastore" {
  name = var.db_security_group_name
}
