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
