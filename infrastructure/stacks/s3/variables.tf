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

# ##############
# # TEXAS COMMON
# ##############

variable "profile" {
  description = "The tag used to identify profile e.g. dev, test, live, ..."
}

variable "terraform_platform_state_store" {
  description = "The Texas terraform state store bucket"
}

variable "texas_s3_logs_bucket" {
  description = "Texas logs bucket"
}

# ############################
# # S3
# ############################

variable "service_prefix" {
  description = "Name for the Service prefix"
}

variable "project_group_short" {
  description = "Short name for the project group"
}

variable "project_name_short" {
  description = "Short name of the project"
}

variable "programme" {
  description = "Shorthand name of the project programme"
}

variable "environment_list" {
  description = "List of environments"
  type        = list(string)
}
