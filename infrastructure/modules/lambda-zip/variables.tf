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

# variable "image_uri" {
#   description = "Docker image URI"
# }

variable "subnet_ids" {
  description = "List of subnet IDs"
}

variable "security_group_ids" {
  description = "List of security group IDs"
}

variable "s3_bucket_arn" {
  description = "ARN of Housekeeping bucket"
}

variable "splunk_firehose_subscription" {
  description = "Name of splunk firehose subscription"
}

variable "splunk_firehose_role" {
  description = "Name of splunk firehose IAM role"
}

# ##############
# # Inputs
# ##############

# Required
variable "name" {
  description = "Name of the lambda function"
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

variable "timeout" {
  description = "Timeout of the lambda function in seconds"
  default     = "900"
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

variable "layers" {
  description = "ARN of any lambda layers to be linked"
}
