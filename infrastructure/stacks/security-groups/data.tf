data "aws_security_group" "datastore" {
  name = var.db_security_group_name
}

data "aws_security_group" "datastore_performance" {
  name = var.db_performance_security_group_name
}

data "aws_security_group" "datastore_regression" {
  name = var.db_regression_security_group_name
}
