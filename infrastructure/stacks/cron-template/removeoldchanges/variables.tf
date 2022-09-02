# ##############
# # LAMBDA
# ##############

variable "s3_tf_state_key" {
  description = "State store for s3 stack terraform"
}

variable "image_version" {
  description = "The version of the Lambda docker image"
}

variable "aws_ecr" {
  description = "ECR repository to store lambda docker images"
}

variable "vpc_terraform_state_key" {
  description = "State store for VPC stack terraform"
}

variable "security_groups_tf_state_key" {
  description = "State store for security groups stack terraform"
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

variable "schedule_removeoldchanges" {
  description = "Schedule for remove old changes job"
  default     = "cron(2 1 * * ? *)"
}
