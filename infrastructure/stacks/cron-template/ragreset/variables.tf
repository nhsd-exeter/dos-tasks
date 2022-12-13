# ##############
# # LAMBDA
# ##############

variable "image_version" {
  description = "The version of the Lambda docker image"
}

variable "aws_ecr" {
  description = "ECR repository to store lambda docker images"
}

variable "slack_webhook_url" {
  description = "Webhook for slack notifications"
}

variable "deployment_secrets" {
  description = "Deployment secret store"
}

variable "splunk_firehose_subscription" {
  description = "Name of splunk firehose subscription"
}

variable "splunk_firehose_role" {
  description = "Name of splunk firehose IAM role"
}

variable "schedule_ragreset" {
  description = "Schedule for reset rag status job"
  default     = "rate(5 minutes)"
}
