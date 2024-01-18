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
