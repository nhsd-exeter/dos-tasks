##########################
# INFRASTRUCTURE COMPONENT
##########################

variable "vpc_terraform_state_key" {
  description = "State store for vpc terraform stack"
}

# ##############
# # SG
# ##############

# variable "core_dos_db_sg" {
#   description = "The ID of the Core DoS sg database"
# }

variable "db_identifier" {
  description = "Identifer of RDS instance from which to extract the security group"
}
