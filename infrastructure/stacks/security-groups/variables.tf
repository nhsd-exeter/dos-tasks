##########################
# INFRASTRUCTURE COMPONENT
##########################

variable "vpc_terraform_state_key" {
  description = "State store for vpc terraform stack"
}

# ##############
# # SG
# ##############

variable "db_identifier" {
  description = "Identifer of RDS instance from which to extract the security group"
}
