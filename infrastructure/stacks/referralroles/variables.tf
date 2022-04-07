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
  description = "AWS account"
}

variable "texas_terraform_state_store" {
  description = "State store for Texas"
}

variable "terraform_platform_state_store" {
  description = "State store for Texas"
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

variable "project_group_short" {
  description = "Short name for project group"
}

variable "project_name_short" {
  description = "Short name for project"
}

# ##############
# # LAMBDA
# ##############

variable "s3_tf_state_key" {
  description = "State store for s3 stack terraform"
}

variable "image_version" {
  description = "The version of the Lambda docker image"
}

variable "aws_lambda_ecr" {
  description = "ECR repository to store lambda docker images"
}

variable "vpc_terraform_state_key" {
  description = "State store for VPC stack terraform"
}

variable "security_groups_tf_state_key" {
  description = "State store for security groups stack terraform"
}
