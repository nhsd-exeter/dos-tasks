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

# ##############
# # LAMBDA
# ##############

variable "image_version" {
  description = "The version of the Lambda docker image"
}

variable "aws_lambda_ecr" {
  description = "ECR repository to store lambda docker images"
}

variable "s3_bucket_id" {
  description = "The ID of the HK S3 bucket"
}

variable "s3_tf_state_key" {
  description = "State store for s3 stack terraform"
}

variable "vpc_terraform_state_key" {
  description = "State store for VPC stack terraform"
}

variable "security_groups_tf_state_key" {
  description = "State store for security groups stack terraform"
}

variable "tags" { description = "A set of predefined variables coming from the Make DevOps automation scripts and shared by the means of the context.tf file in each individual stack" }

# ##############
# # Inputs
# ##############

# Required
variable "name" {
  description = "Name of the lambda function"
}

# Optional
variable "environment" {
  description = "Map of environment variables"
  type        = Map
  default = {
    "Service" = "core-dos"
  }
}

variable "timeout" {
  description = "Timeout of the lambda function"
  default     = "30"
}

variable "retry_attempts" {
  description = "Number of retries for the lamdba"
  default     = 0
}

variable "log_retention" {
  description = "Length of timeto keep the logs in cloudwatch"
  default     = "0"
}

variable "memory_size" {
  description = "Amount of memory in MB your Lambda Function can use at runtime"
  default     = "128"
}
