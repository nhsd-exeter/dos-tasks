##########################
# INFRASTRUCTURE COMPONENT
##########################

############
# AWS COMMON
############

variable "aws_region" {
  description = "The AWS region"
}

variable "aws_account_id" {
  description = "AWS account"
}

# ##############
# # UEC COMMON
# ##############

variable "service_prefix" {
  description = "The service prefix for the application"
}

# ##############
# # Lambda
# ##############

variable "s3_bucket_arn" {
  description = "ARN of Housekeeping bucket"
}


# ##############
# # Inputs
# ##############

# Required
variable "name" {
  description = "Name of the iam role"
}

variable "tags" {
  description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack"
}

# Optional
variable "env_vars" {
  description = "Map of environment variables"
  type        = map
  default = {
    "service" = "core-dos",
    "profile" = "nonprod"
  }
}
