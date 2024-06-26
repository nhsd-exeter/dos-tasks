# ==============================================================================
# Platform variables set by the Make DevOps automation scripts
variable "aws_account_id" {}
variable "aws_account_name" {}
variable "aws_region" {}
variable "aws_profile" {}

# ==============================================================================
# Project variables set by the Make DevOps automation scripts

variable "programme" {}
variable "project_group" {}
variable "project_group_short" {}
variable "project_name" {}
variable "project_name_short" {}
variable "service_tag" {}
variable "service_tag_common" {}
variable "project_tag" {}
variable "profile" {}
variable "service_prefix" {}
variable "environment" {}

# ==============================================================================
# Texas variables set by the Make DevOps automation scripts

variable "texas_terraform_state_store" {}
variable "terraform_platform_state_store" {}

variable "vpc_name" {
  description = "Name of vpc"
}

variable "housekeeping_bucket_name" {
  description = "Name of housekeeping bucket"
}

variable "housekeeping_role_name" {
  description = "Name of housekeeping role"
}
