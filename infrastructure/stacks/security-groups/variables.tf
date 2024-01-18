##########################
# INFRASTRUCTURE COMPONENT
##########################

variable "vpc_terraform_state_key" {
  description = "State store for vpc terraform stack"
}

# ##############
# # SG
# ##############

variable "db_security_group_name" {
  description = "Identifier of security group attached to datastore"
}

variable "db_regression_security_group_name" {
  description = "Identifier of security group attached to datastore for regression"
}

variable "db_performance_security_group_name" {
  description = "Identifier of security group attached to datastore for performance"
}

variable "add_perf_security_group" {
  default = false
}

variable "add_regression_security_group" {
  default = false
}

variable "add_perf_ingress" {
  default = false
}

variable "add_regression_ingress" {
  default = false
}

variable "add_perf_egress" {
  default = false
}

variable "add_regression_egress" {
  default = false
}
