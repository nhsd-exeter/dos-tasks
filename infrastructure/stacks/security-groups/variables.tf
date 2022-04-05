##########################
# INFRASTRUCTURE COMPONENT
##########################

############
# AWS COMMON
############

variable "aws_profile" {
  description = "The AWS profile"
}

variable "aws_region" {
  description = "The AWS region"
}

variable "aws_account_id" {
  description = "AWS account Number for Athena log location"
}

variable "terraform_platform_state_store" {
  description = "State store for Texas"
}

variable "vpc_terraform_state_key" {
  description = "State store for vpc terraform stack"
}

# ##############
# # UEC COMMON
# ##############

variable "profile" {
  description = "The tag used to identify profile e.g. dev, test, live, ..."
}

variable "programme" {
  description = "The programme in which the service belongs to"
}

variable "service_prefix" {
  description = "The service prefix for the application"
}

# ##############
# # UEC COMMON
# ##############

variable "core_dos_db_sg" {
  description = "The ID of the Core DoS sg database"
}
