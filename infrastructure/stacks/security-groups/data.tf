data "aws_security_group" "datastore" {
  name = var.db_security_group_name
}

data "aws_security_group" "datastore_performance" {
  count = var.add_perf_security_group ? 1 : 0
  name = var.db_performance_security_group_name
}

data "aws_security_group" "datastore_regression" {
  count = var.add_regression_security_group ? 1 : 0
  name = var.db_regression_security_group_name
}
